"""
CasaCraft AI - Interior Image Generation

Real image-to-image generation using Hugging Face Diffusers.

This module:
- Builds room-specific interior prompts.
- Prioritizes user-selected furniture/fixtures.
- Loads the diffusion pipeline only once.
- Uses CUDA automatically when available.
- Uses CPU safely when CUDA is unavailable.
- Preserves the uploaded room architecture/camera as much as image-to-image
  diffusion allows.
- Does not silently return the original image if generation fails.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Any, Iterable
import re

import torch
from PIL import Image

from config import GENERATION_BACKEND, DIFFUSION_MODEL


def _clean_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    if isinstance(value, (list, tuple, set)):
        return ", ".join(
            str(item).strip()
            for item in value
            if str(item).strip()
        )
    text = str(value).strip()
    return text if text else default


def _unique_join(values: Iterable[Any]) -> str:
    seen = set()
    result = []
    for value in values:
        text = _clean_text(value)
        if not text:
            continue
        key = text.lower()
        if key not in seen:
            seen.add(key)
            result.append(text)
    return ", ".join(result)


def _extract_recommendation_values(
    recs: list[dict[str, Any]] | None,
    key: str,
) -> str:
    if not recs:
        return ""

    values = []
    for recommendation in recs:
        if not isinstance(recommendation, dict):
            continue
        values.append(recommendation.get(key, ""))

    return _unique_join(values)


def build_prompt(
    room: str,
    style: str,
    color: str,
    materials: str,
    recs: list[dict[str, Any]] | None = None,
    detected: Any = None,
    selected_elements: list[str] | None = None,
    plan_info: dict[str, Any] | None = None,
) -> str:
    """
    Build the main prompt.

    selected_elements is optional so the current app remains compatible.
    If the current app appends selected elements after build_prompt(), the
    generation function extracts that instruction and moves it to the front.
    """

    room = _clean_text(room, "room")
    style = _clean_text(style, "modern")
    color = _clean_text(color, "warm neutral")
    materials = _clean_text(materials, "wood and fabric")

    selected_text = _unique_join(selected_elements or [])
    furniture = _extract_recommendation_values(recs, "furniture")
    features = _extract_recommendation_values(recs, "features")
    lighting = _extract_recommendation_values(recs, "lighting")

    plan_guidance = ""
    if isinstance(plan_info, dict):
        try:
            width = float(plan_info.get("width", 0))
        except (TypeError, ValueError):
            width = 0.0
        try:
            height = float(plan_info.get("height", 0))
        except (TypeError, ValueError):
            height = 0.0
        try:
            line_segments = int(float(plan_info.get("line_segments", 0)))
        except (TypeError, ValueError):
            line_segments = 0
        try:
            edge_ratio = float(plan_info.get("edge_ratio", 0))
        except (TypeError, ValueError):
            edge_ratio = 0.0

        aspect = (width / height) if width > 0 and height > 0 else 1.0
        shape = (
            "wide layout" if aspect >= 1.20 else
            "deep layout" if aspect <= 0.83 else
            "near-square layout"
        )
        plan_guidance = (
            f"2D floor-plan guidance: {shape}, aspect ratio {aspect:.2f}, "
            f"{int(width) if width else 0}x{int(height) if height else 0}px, "
            f"{line_segments} structural line segments, edge ratio {edge_ratio:.3f}. "
            "Use these metrics to keep furniture proportions and circulation realistic; "
            "preserve major openings and do not invent extra rooms. "
            "These metrics are planning guidance, not exact object coordinates."
        )

    detected_items = ""
    if isinstance(detected, dict):
        detected_items = _unique_join(detected.keys())
    elif isinstance(detected, (list, tuple)):
        names = []
        for item in detected:
            if isinstance(item, dict):
                names.append(item.get("object", ""))
            else:
                names.append(item)
        detected_items = _unique_join(names)

    prompt_parts = []

    # Highest-priority user requirements go first.
    if selected_text:
        prompt_parts.append(f"MUST INCLUDE: {selected_text}")

    prompt_parts.extend(
        [
            f"{room} interior with clearly visible furniture and fixtures",
            "photorealistic professional interior design photograph",
            f"beautiful {room} interior",
            f"{style} interior design style",
            f"color palette: {color}",
            f"materials and finishes: {materials}",
            "fully furnished and decorated room",
            "realistic furniture at correct architectural scale",
            "cohesive premium residential interior",
            "natural realistic daylight",
            "warm layered architectural lighting",
            "realistic shadows and reflections",
            "high-end interior photography",
            "preserve the existing room architecture",
            "preserve windows, doors, walls, ceiling and floor geometry",
            "preserve original room proportions and camera viewpoint",
        ]
    )

    if furniture:
        prompt_parts.append(f"recommended furniture: {furniture}")
    if features:
        prompt_parts.append(f"recommended design features: {features}")
    if lighting:
        prompt_parts.append(f"recommended lighting: {lighting}")
    if detected_items:
        prompt_parts.append(
            f"respect existing detected elements: {detected_items}"
        )
    if plan_guidance:
        prompt_parts.append(plan_guidance)

    room_lower = room.lower()

    if "bedroom" in room_lower:
        prompt_parts.extend(
            [
                "bed is the main focal furniture and must be clearly visible",
                "place the bed against a suitable wall at realistic scale",
                "include bedroom storage and bedside furniture when selected",
            ]
        )
    elif "living" in room_lower:
        prompt_parts.extend(
            [
                "sofa seating is the main focal furniture and must be clearly visible",
                "arrange seating at realistic architectural scale",
                "include TV unit and coffee table when selected",
            ]
        )
    elif "kitchen" in room_lower:
        prompt_parts.extend(
            [
                "complete modular kitchen cabinetry must be clearly visible",
                "countertop and backsplash must be clearly visible",
                "realistic appliances and hardware must be present",
                "if selected, dining table and dining chairs must be clearly visible",
                "if selected, refrigerator, hob and chimney must be clearly identifiable",
                "if selected, kitchen island must be clearly identifiable",
            ]
        )
    elif "bathroom" in room_lower:
        prompt_parts.extend(
            [
                "vanity and sanitary fixtures must be clearly visible",
                "if selected, shower and bathtub must be clearly identifiable",
                "use realistic bathroom fixture scale and placement",
                "use a realistic glass shower partition when selected",
            ]
        )

    prompt_parts.extend(
        [
            "no empty-room appearance",
            "do not leave the room unfurnished",
            "realistic materials",
            "realistic proportions",
            "clean composition",
            "architectural visualization quality",
        ]
    )

    return ", ".join(part for part in prompt_parts if part)


ROOM_SCENE_RULES = {
    "bedroom": (
        "a complete residential BEDROOM, one clearly visible bed with a proper headboard "
        "as the main focal furniture, two bedside tables, wardrobe/storage and dressing area; "
        "this must read unmistakably as a bedroom"
    ),
    "living room": (
        "a complete residential LIVING ROOM, clearly visible sofa seating, coffee table, "
        "TV unit/feature wall and living-room decor; this must read unmistakably as a living room"
    ),
    "kitchen": (
        "a complete residential MODULAR KITCHEN, wall and base cabinets, continuous countertop, "
        "backsplash, sink with faucet, hob with chimney, refrigerator, tall unit and kitchen island; "
        "if selected, a separate dining table with dining chairs; this must read unmistakably as a kitchen"
    ),
    "bathroom": (
        "a complete residential BATHROOM, vanity with mirror, WC, clearly visible shower area, "
        "rain shower and glass partition; if selected, a clearly visible bathtub; this must read unmistakably as a bathroom"
    ),
}

ROOM_NEGATIVE_RULES = {
    "bedroom": "kitchen, sofa as main furniture, dining table as main furniture, bathtub, shower room",
    "living room": "bed, bedroom, bathtub, shower, kitchen cabinets, kitchen island, hob",
    "kitchen": "bedroom, bed, wardrobe as main furniture, sofa, living room, bathroom, bathtub, shower as main feature",
    "bathroom": "bedroom, bed, sofa, living room, kitchen cabinets, kitchen island, dining table",
}

NEGATIVE_PROMPT = (
    "empty room, vacant room, unfurnished room, missing furniture, missing fixtures, "
    "duplicate furniture, floating furniture, distorted furniture, deformed objects, "
    "warped architecture, changed windows, changed doors, extra rooms, fisheye, "
    "unrealistic proportions, people, faces, text, watermark, logo, blurry, low quality, "
    "cartoon, illustration, plastic CGI"
)



def _extract_priority_elements(prompt: str) -> tuple[str, str]:
    """
    Extract the room and selected elements from the prompt produced by app.py.

    The current app can append:
        Room: Kitchen
        Must include these selected furniture/fixtures: Dining Table, ...
    """
    text = str(prompt or "")
    room = ""

    room_match = re.search(
        r"(?i)\b(Bedroom|Living Room|Kitchen|Bathroom)\s+interior\s+design\b",
        text,
    )
    if room_match:
        room = room_match.group(1).strip()
    else:
        room_match = re.search(
            r"(?im)^\s*Room\s*:\s*([^\n]+)",
            text,
        )
        if room_match:
            room = room_match.group(1).strip()

    patterns = [
        r"(?i)Must include these selected furniture/fixtures\s*:\s*([^\n.]+)",
        r"(?i)MUST INCLUDE\s*:\s*([^\n.]+)",
        r"(?i)Must include\s*:\s*([^\n.]+)",
    ]

    selected = ""
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            selected = match.group(1).strip()
            break

    selected = re.sub(r"\s+", " ", selected).strip(" .")
    return room, selected


def _extract_preference(prompt: str, label: str, default: str) -> str:
    match = re.search(
        rf"(?i){re.escape(label)}\s*:\s*([^,\n]+)",
        str(prompt),
    )
    return match.group(1).strip() if match else default


def _make_generation_prompt(prompt: str) -> str:
    """Create a short, room-specific prompt with required objects first."""
    original = str(prompt or "").strip()
    room, selected = _extract_priority_elements(original)

    if not room:
        match = re.search(r"(?i)beautiful\s+(.+?)\s+interior", original)
        room = match.group(1).strip() if match else "interior room"

    style = _extract_preference(original, "style", "modern")
    color = _extract_preference(original, "color palette", "warm neutral")
    materials = _extract_preference(original, "materials and finishes", "wood and fabric")
    room_lower = room.lower()

    if "bedroom" in room_lower:
        room_key = "bedroom"
    elif "living" in room_lower:
        room_key = "living room"
    elif "kitchen" in room_lower:
        room_key = "kitchen"
    elif "bathroom" in room_lower:
        room_key = "bathroom"
    else:
        room_key = ""

    room_rule = ROOM_SCENE_RULES.get(room_key, "a complete furnished residential interior")

    parts = []
    if selected:
        parts.append(f"MUST INCLUDE THESE OBJECTS: {selected}")

    parts.extend([
        room_rule,
        f"{style} interior design",
        f"color palette {color}",
        f"materials {materials}",
        "photorealistic architectural visualization",
        "fully furnished, realistic object scale, realistic materials",
    ])

    # Repeat only the room-critical objects, not a huge prompt.
    if room_key == "bedroom":
        parts.append("bed and headboard clearly visible, wardrobe clearly visible when selected")
    elif room_key == "living room":
        parts.append("sofa and living-room seating clearly visible")
    elif room_key == "kitchen":
        parts.append("cabinets, countertop, sink, hob, chimney, refrigerator and island clearly visible; dining table and chairs clearly visible when selected")
    elif room_key == "bathroom":
        parts.append("vanity, WC and shower clearly visible; bathtub clearly visible when selected")

    plan_match = re.search(
        r"(?is)2D floor-plan guidance:\s*(.*?)(?:\n\n|$)",
        original,
    )
    if plan_match:
        parts.append("2D FLOOR PLAN CONSTRAINT: " + re.sub(r"\s+", " ", plan_match.group(1)).strip())

    parts.extend([
        "preserve existing walls, windows, doors, floor and camera perspective",
        "preserve major architectural openings",
        "no empty room",
    ])

    return ", ".join(parts)


@lru_cache(maxsize=1)
def _load_pipeline():
    """Load and cache the image-to-image diffusion pipeline."""

    if str(GENERATION_BACKEND).lower().strip() != "diffusers":
        raise RuntimeError(
            f"Unsupported GENERATION_BACKEND={GENERATION_BACKEND!r}. "
            "Set GENERATION_BACKEND='diffusers' in config.py."
        )

    if not DIFFUSION_MODEL:
        raise RuntimeError(
            "DIFFUSION_MODEL is empty. Set a valid Hugging Face model ID "
            "or local diffusion model path in config.py."
        )

    try:
        from diffusers import AutoPipelineForImage2Image
    except ImportError as exc:
        raise RuntimeError(
            "Diffusers is not installed in the active .venv. Run:\n\n"
            r".\.venv\Scripts\python.exe -m pip install "
            "diffusers transformers accelerate safetensors"
        ) from exc

    use_cuda = torch.cuda.is_available()
    dtype = torch.float16 if use_cuda else torch.float32
    device = "cuda" if use_cuda else "cpu"

    try:
        pipe = AutoPipelineForImage2Image.from_pretrained(
            DIFFUSION_MODEL,
            torch_dtype=dtype,
            use_safetensors=True,
        )

        if use_cuda:
            try:
                pipe.enable_model_cpu_offload()
            except Exception:
                pipe = pipe.to(device)
        else:
            pipe = pipe.to(device)

        try:
            pipe.enable_attention_slicing()
        except Exception:
            pass

        return pipe

    except Exception as exc:
        raise RuntimeError(
            "Could not load the diffusion model.\n\n"
            f"Model: {DIFFUSION_MODEL}\n"
            f"Device: {device}\n"
            f"Original error: {type(exc).__name__}: {exc}"
        ) from exc


def _prepare_image(
    image: Image.Image,
    max_side: int | None = None,
) -> Image.Image:
    """Prepare uploaded image while preserving its aspect ratio."""

    if not isinstance(image, Image.Image):
        raise TypeError("generate_concept() expects a PIL.Image.Image.")

    image = image.convert("RGB")

    if max_side is None:
        max_side = 768 if torch.cuda.is_available() else 512

    width, height = image.size
    if width <= 0 or height <= 0:
        raise ValueError("Uploaded image has invalid dimensions.")

    scale = min(1.0, max_side / max(width, height))

    new_width = max(64, int(width * scale))
    new_height = max(64, int(height * scale))

    new_width = max(64, (new_width // 8) * 8)
    new_height = max(64, (new_height // 8) * 8)

    if (new_width, new_height) != image.size:
        image = image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS,
        )

    return image


def generate_concept(
    image: Image.Image,
    prompt: str,
    title: str,
) -> Image.Image:
    """
    Generate a real interior concept.

    The function intentionally does not return the original image if
    generation fails.
    """

    if str(GENERATION_BACKEND).lower().strip() != "diffusers":
        raise RuntimeError(
            "AI generation is disabled because GENERATION_BACKEND is not "
            "'diffusers'. Set GENERATION_BACKEND='diffusers' in config.py."
        )

    if not prompt or not str(prompt).strip():
        raise ValueError("Generation prompt is empty.")

    source = _prepare_image(image)
    pipe = _load_pipeline()

    use_cuda = torch.cuda.is_available()

    # Critical improvement: move selected furniture to the front and shorten
    # the prompt before passing it to CLIP.
    generation_prompt = _make_generation_prompt(prompt)

    # Room transformation needs more freedom than a simple color/style edit.
    # 0.74 is a compromise: enough change to add furniture while retaining
    # the major architecture. Diffusers documents that higher strength adds
    # more noise and makes the result less tied to the source image.
    strength = 0.74

    # More denoising steps generally improve quality, at the cost of speed.
    # Keep CPU testing reasonable while avoiding the very soft 12-step output.
    steps = 18 if not use_cuda else 28
    guidance = 7.5

    try:
        with torch.inference_mode():
            room_for_negative, _ = _extract_priority_elements(prompt)
            room_negative = ROOM_NEGATIVE_RULES.get(room_for_negative.lower(), "")
            effective_negative = NEGATIVE_PROMPT + (f", {room_negative}" if room_negative else "")

            result = pipe(
                prompt=generation_prompt,
                negative_prompt=effective_negative,
                image=source,
                strength=strength,
                guidance_scale=guidance,
                num_inference_steps=steps,
            )

        if not hasattr(result, "images") or not result.images:
            raise RuntimeError("Diffusion pipeline returned no image.")

        generated = result.images[0].convert("RGB")

        if generated.size[0] < 64 or generated.size[1] < 64:
            raise RuntimeError(
                f"Generated image has an invalid size: {generated.size}"
            )

        return generated

    except torch.cuda.OutOfMemoryError as exc:
        if use_cuda:
            raise RuntimeError(
                "GPU memory is not sufficient for this generation. "
                "Close other GPU-heavy applications and try a smaller image/model."
            ) from exc
        raise RuntimeError("PyTorch ran out of memory during generation.") from exc

    except Exception as exc:
        raise RuntimeError(
            "AI image generation failed.\n\n"
            f"Original error: {type(exc).__name__}: {exc}\n\n"
            "The app did NOT fall back to the empty room image."
        ) from exc


def get_generation_status() -> dict[str, Any]:
    """Return useful information for the Streamlit UI."""

    return {
        "backend": str(GENERATION_BACKEND),
        "model": str(DIFFUSION_MODEL),
        "cuda_available": bool(torch.cuda.is_available()),
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "torch_version": torch.__version__,
    }

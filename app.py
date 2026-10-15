import io

import sqlite3

import json

from pathlib import Path
import textwrap



import pandas as pd

import plotly.express as px

import streamlit as st



from database import init_db, save_project, get_projects





def _get_detector_class():

    from detector import InteriorDetector

    return InteriorDetector





def _get_recommender_class():

    from recommender import DesignRecommender

    return DesignRecommender





def analyze_plan(image):

    from plan_analyzer import analyze_plan as _analyze_plan

    return _analyze_plan(image)





def _build_plan_context(plan_info, room):
    """Convert floor-plan analysis metrics into compact AI layout guidance."""
    if not isinstance(plan_info, dict):
        return ""

    def num(key, default=0.0):
        try:
            return float(plan_info.get(key, default))
        except (TypeError, ValueError):
            return float(default)

    width = num("width")
    height = num("height")
    segments = int(num("line_segments"))
    edge_ratio = num("edge_ratio")
    aspect = width / height if width > 0 and height > 0 else 1.0
    shape = "wide horizontal layout" if aspect >= 1.20 else "deep vertical layout" if aspect <= 0.83 else "near-square layout"
    density = "low" if segments < 15 else "medium" if segments < 35 else "high"

    room_rules = {
        "Bedroom": "keep the bed zone dominant and maintain clear circulation to wardrobe/storage",
        "Living Room": "keep the main seating zone open and preserve a practical TV/focal wall",
        "Kitchen": "organize cabinets, counter, sink, hob and refrigerator into a practical work zone; keep island/dining circulation clear",
        "Bathroom": "separate wet and dry zones and preserve practical clearance around vanity, WC and shower",
    }

    return (
        f"2D FLOOR PLAN CONSTRAINTS: {room} has a {shape}, aspect ratio {aspect:.2f}, "
        f"plan size {int(width) if width else 0}x{int(height) if height else 0}px, "
        f"{segments} detected line segments, edge ratio {edge_ratio:.3f}, "
        f"structural-line density {density}. "
        f"Use these measurements to guide furniture proportions and circulation; "
        f"{room_rules.get(room, 'maintain realistic circulation and proportions')}. "
        "Preserve major architectural openings and do not invent extra rooms. "
        "These are planning constraints, not exact object coordinates."
    )


def build_prompt(*args, **kwargs):

    from generation import build_prompt as _build_prompt

    return _build_prompt(*args, **kwargs)





def generate_concept(*args, **kwargs):

    from generation import generate_concept as _generate_concept

    return _generate_concept(*args, **kwargs)





def render_3d_room(*args, **kwargs):

    from three_d_planner import render_3d_room as _render_3d_room

    return _render_3d_room(*args, **kwargs)





# ============================================================

# PAGE CONFIG

# ============================================================



st.set_page_config(

    page_title="CasaCraft AI",

    page_icon="🏠",

    layout="wide",

    initial_sidebar_state="expanded",

)





# ============================================================

# Render CasaCraft HTML safely with Streamlit's HTML renderer.
# Using st.html() for unsafe_allow_html blocks prevents multiline HTML
# from being interpreted as a Markdown code block.
_original_st_markdown = st.markdown

def _casacraft_markdown(body="", *args, **kwargs):
    if isinstance(body, str):
        body = textwrap.dedent(body).strip()
    unsafe = kwargs.get("unsafe_allow_html", False)
    if unsafe and isinstance(body, str):
        # st.html is the reliable renderer for the custom HTML used by CasaCraft.
        return st.html(body)
    return _original_st_markdown(body, *args, **kwargs)

st.markdown = _casacraft_markdown

# PREMIUM UI

# ============================================================



st.markdown(

    """

<style>



/* ---------- GLOBAL ---------- */



.stApp {

    background: #f5f1eb;

    color: #29231f;

}



.block-container {

    max-width: 1480px;

    padding-top: 1.4rem;

    padding-bottom: 3rem;

}



h1, h2, h3, h4 {

    color: #302923 !important;

}



h1 {

    font-size: 42px !important;

    font-weight: 750 !important;

    letter-spacing: -1px;

}



h2 {

    font-size: 30px !important;

}



h3 {

    font-size: 23px !important;

}



p, label {

    color: #4d433b;

}





/* ---------- SIDEBAR ---------- */



section[data-testid="stSidebar"] {

    background: #24201e !important;

    border-right: 1px solid #39312c;

}



section[data-testid="stSidebar"] * {

    color: #f8f4ee !important;

}



section[data-testid="stSidebar"] h1,

section[data-testid="stSidebar"] h2,

section[data-testid="stSidebar"] h3 {

    color: #ffffff !important;

}



.sidebar-brand {

    padding: 8px 2px 18px;

}



.sidebar-title {

    font-size: 27px;

    font-weight: 800;

    color: #ffffff !important;

}



.sidebar-subtitle {

    color: #bdb1a7 !important;

    font-size: 13px;

    margin-top: 4px;

}





/* ---------- HERO ---------- */



.hero {

    background: linear-gradient(

        110deg,

        #302923 0%,

        #6f503d 100%

    );



    border-radius: 22px;



    padding: 30px 34px;



    margin-bottom: 24px;



    box-shadow:

        0 10px 30px rgba(48,41,35,.12);

}



.hero h1,

.hero h2,

.hero p,

.hero span {

    color: #ffffff !important;

}



.hero h1 {

    margin-bottom: 8px;

}



.hero-subtitle {

    color: #f4ebe2 !important;

    font-size: 16px;

}



.hero-meta {

    color: #dfd1c4 !important;

    font-size: 13px;

    margin-top: 12px;

}





/* ---------- CARDS ---------- */



.casa-card {

    background: #ffffff;

    border: 1px solid #e7ddd3;

    border-radius: 18px;

    padding: 20px;

    box-shadow: 0 7px 25px rgba(55,40,28,.06);

}





/* ---------- BUTTONS ---------- */



.stButton > button {

    background: #5f4637 !important;

    color: #ffffff !important;

    border: none !important;

    border-radius: 11px !important;

    min-height: 44px;

    font-weight: 700 !important;

}



.stButton > button:hover {

    background: #7a5b47 !important;

    color: #ffffff !important;

}



.stDownloadButton > button {

    background: #302923 !important;

    color: #ffffff !important;

    border-radius: 11px !important;

    font-weight: 700 !important;

}





/* ---------- FILE UPLOADER ---------- */



section[data-testid="stFileUploaderDropzone"] {

    background: #ffffff !important;

    border: 2px dashed #cdbda9 !important;

    border-radius: 15px !important;

}



section[data-testid="stFileUploaderDropzone"] * {

    color: #40362f !important;

}





/* ---------- INPUTS ---------- */



div[data-baseweb="select"] > div {

    background: #ffffff !important;

    border: 1px solid #d8cbbd !important;

    border-radius: 10px !important;

}



div[data-baseweb="select"] span {

    color: #302923 !important;

}



input {

    background: #ffffff !important;

    color: #302923 !important;

}





/* ---------- TABS ---------- */



button[data-baseweb="tab"] {

    color: #66584d !important;

    font-weight: 650 !important;

}



button[data-baseweb="tab"][aria-selected="true"] {

    color: #8a613e !important;

}





/* ---------- METRICS ---------- */



div[data-testid="stMetric"] {

    background: #ffffff;

    border: 1px solid #e8ded3;

    border-radius: 15px;

    padding: 16px;

    box-shadow: 0 5px 20px rgba(55,40,28,.05);

}



div[data-testid="stMetricLabel"] {

    color: #75685d !important;

}



div[data-testid="stMetricValue"] {

    color: #302923 !important;

}





/* ---------- IMAGE ---------- */



img {

    border-radius: 14px;

}





/* ---------- EXPANDER ---------- */



details {

    background: #ffffff !important;

    border: 1px solid #e7ddd3 !important;

    border-radius: 14px !important;

    margin-bottom: 10px !important;

}



details summary {

    color: #302923 !important;

    font-weight: 650 !important;

}





/* ---------- FOOTER ---------- */



.feature-strip {

    background: #302923;

    color: #ffffff;

    border-radius: 18px;

    padding: 18px 22px;

    margin-top: 30px;

}



.feature-strip b {

    color: #ffffff;

}



.feature-strip span {

    color: #d8cbc0 !important;

}







/* ---------- PROJECT DASHBOARD ---------- */

.project-header {

    background: linear-gradient(120deg, #302923 0%, #5f4637 55%, #8a6a50 100%);

    border-radius: 24px;

    padding: 28px 30px;

    color: #fff;

    margin-bottom: 18px;

    box-shadow: 0 14px 36px rgba(48,41,35,.16);

}

.project-header h1, .project-header h2, .project-header p, .project-header span { color:#fff !important; }

.project-kicker { text-transform:uppercase; letter-spacing:1.8px; font-size:11px; color:#e5d7ca !important; font-weight:800; }

.project-title { font-size:34px; font-weight:800; margin-top:6px; }

.project-sub { color:#eee2d7 !important; font-size:14px; margin-top:5px; }

.soft-card {

    background:#fff; border:1px solid #e7ddd3; border-radius:18px; padding:18px;

    box-shadow:0 7px 25px rgba(55,40,28,.055); height:100%;

}

.card-title { font-size:18px; font-weight:800; color:#302923; margin-bottom:5px; }

.card-sub { font-size:12px; color:#75685d; margin-bottom:12px; }

.price-big { font-size:28px; font-weight:850; color:#302923; }

.status-pill { display:inline-block; padding:6px 10px; border-radius:20px; background:#e8f4e9; color:#2d7040; font-weight:700; font-size:12px; }

.palette-dot { display:inline-block; width:24px; height:24px; border-radius:50%; margin-right:6px; border:2px solid #fff; box-shadow:0 0 0 1px #d8cbbd; }

.section-gap { margin-top:18px; }




/* CasaCraft AI Design Studio fixes */
.stDownloadButton > button {
    background: #6b4b3e !important;
    color: #ffffff !important;
    border: 1px solid #6b4b3e !important;
    border-radius: 10px !important;
    font-weight: 700 !important;
    min-height: 44px !important;
}
.stDownloadButton > button:hover {
    background: #4f372e !important;
    color: #ffffff !important;
    border-color: #4f372e !important;
}
[data-testid="stMetric"] {
    background: #ffffff;
    border: 1px solid #eadfd5;
    border-radius: 12px;
    padding: 14px 16px;
}

</style>

""",

    unsafe_allow_html=True,

)





# ============================================================

# AI COMPONENTS

# ============================================================



@st.cache_resource

def get_detector():

    return _get_detector_class()()





@st.cache_resource

def get_recommender():

    return _get_recommender_class()()





def build_project_recommendations(room, width, length, budget, style, furniture, wall_color, floor_color, accent_color, estimated_total):

    area = width * length

    recommendations = []



    palettes = {

        "Modern Minimalist": ("Warm ivory + taupe + natural wood", "Matte laminate, light oak/ash wood, quartz or sintered-stone accents", "3000K recessed lights with concealed cove lighting"),

        "Luxury Modern": ("Ivory + champagne + walnut", "Premium veneer/laminate, marble-look surfaces and brushed-metal accents", "3000K layered lighting with decorative pendants"),

        "Contemporary": ("Beige + greige + walnut", "Wood-texture laminates, textured panels and quartz surfaces", "3000K spotlights plus task lighting"),

        "Japandi": ("Sand + off-white + muted wood", "Oak/ash textures, linen-like finishes and natural stone", "2700–3000K soft indirect lighting"),

        "Modern Classic": ("Cream + beige + dark wood", "Fluted panels, classic profiles, marble-look surfaces and brass accents", "3000K chandeliers/pendants with warm ambient lighting"),

    }

    palette, materials, lighting = palettes.get(style, palettes["Modern Minimalist"])



    if area < 120:

        space_tip = "Keep circulation zones clear and prefer compact or wall-mounted furniture to preserve usable floor area."

    elif area < 250:

        space_tip = "Use balanced furniture sizes and keep approximately 3 ft of comfortable circulation around major furniture where possible."

    else:

        space_tip = "Create functional zones with rugs, lighting layers and furniture groupings rather than filling the room with large pieces."



    furniture_tips = {

        "Bedroom": "Use a storage bed or full-height wardrobe where storage is limited; keep bedside circulation practical.",

        "Living Room": "Anchor the sofa around the TV/focal wall and keep the coffee table proportionate to the seating group.",

        "Kitchen": "Maintain a clear work triangle and provide dedicated zones for prep, cooking and tall storage.",

        "Bathroom": "Use wall-mounted vanity/storage where possible and keep wet and dry zones clearly separated.",

    }



    budget_tip = (

        f"The current estimate is ₹{estimated_total:,.0f}, which is within the ₹{budget:,.0f} budget. "

        "Keep a small reserve for site variations and hardware changes."

        if estimated_total <= budget else

        f"The current estimate is ₹{estimated_total:,.0f}, about ₹{estimated_total-budget:,.0f} above the ₹{budget:,.0f} budget. "

        "Prioritize essential furniture first and reduce premium finishes or optional pieces before reducing core functionality."

    )



    recommendations.append(("🎨 Colour Palette", palette))

    recommendations.append(("🧱 Materials", materials))

    recommendations.append(("💡 Lighting", lighting))

    recommendations.append(("📐 Space Planning", space_tip))

    recommendations.append(("🪑 Furniture", furniture_tips.get(room, "Choose furniture that matches the room scale and maintain comfortable circulation.")))

    recommendations.append(("💰 Budget", budget_tip))

    recommendations.append(("🤖 Design Logic", f"{style} direction for a {area:,.0f} sq.ft. {room.lower()} using {len(furniture)} selected furniture/fixture items. Palette: {wall_color}, {floor_color}, {accent_color}."))

    return recommendations





# ============================================================

# DATABASE

# ============================================================



init_db()





# ============================================================

# SIDEBAR

# ============================================================



with st.sidebar:



    st.markdown(

        """

        <div class="sidebar-brand">

            <div class="sidebar-title">🏠 CasaCraft AI</div>

            <div class="sidebar-subtitle">

                Design Your Dream Space

            </div>

        </div>

        """,

        unsafe_allow_html=True,

    )



    st.markdown("### Navigation")



    page = st.radio(

        "Navigation",

        [

            "Project Dashboard",

            "AI Design Studio",

            "AI Design Suggestions",

            "3D Room Planner",

            "Style Gallery",

            "Cost Estimator",

            "Saved Projects",

        ],

        label_visibility="collapsed",

    )



    st.divider()



    st.markdown(

        """

        <div style="

            background:#30465a;

            border-radius:14px;

            padding:16px;

            line-height:1.7;

        ">

            <b>AI • Computer Vision • ML • 3D</b><br>

            <span style="color:#d9e3eb;">

                Data Science Interior Platform

            </span>

        </div>

        """,

        unsafe_allow_html=True,

    )





# ============================================================

# PROJECT DASHBOARD

# ============================================================



if page == "Project Dashboard":



    st.markdown(

        """

        <div class="project-header">

            <div class="project-kicker">CASACRAFT AI • INTERIOR DESIGN PLATFORM</div>

            <div class="project-title">Your Dream Space, Smarter.</div>

            <div class="project-sub">

                Design • Visualize • Estimate • Save • Bring to Life

            </div>

        </div>

        """,

        unsafe_allow_html=True,

    )



    try:

        rows = get_projects()

    except Exception:

        rows = []



    latest = rows[0] if rows else None

    latest_budget = float(latest[4]) if latest else 350000

    latest_area = float(latest[5]) if latest else 192



    a, b, c, d = st.columns(4)

    a.metric("Projects Saved", len(rows))

    b.metric("Latest Area", f"{latest_area:,.0f} sq.ft.")

    c.metric("Latest Budget", f"₹{latest_budget:,.0f}")

    d.metric("Platform Modules", "5")



    left, right = st.columns([2.2, 1], gap="large")



    with left:

        st.markdown(

            """

            <div class="soft-card">

                <div class="card-title">🏠 CasaCraft AI Workflow</div>

                <div class="card-sub">A complete academic interior-design pipeline</div>

            </div>

            """,

            unsafe_allow_html=True,

        )



        w1, w2, w3 = st.columns(3)

        w1.info("📷 **1. Analyse**\n\nUpload a room image or floor plan and detect interior elements.")

        w2.info("🧊 **2. Visualize**\n\nBuild and explore an interactive 3D room layout.")

        w3.info("💰 **3. Estimate**\n\nCalculate an academic project budget from area and furniture.")



        st.markdown("### Recent Project")

        if latest:

            st.markdown(

                f"""

                <div class="soft-card">

                    <div class="card-title">{latest[1]}</div>

                    <div class="card-sub">{latest[2]} • {latest[3]}</div>

                    <b>Budget:</b> ₹{float(latest[4]):,.0f}

                    &nbsp;&nbsp; <b>Area:</b> {float(latest[5]):,.0f} sq.ft.

                    <br><br><span class="status-pill">Saved Project</span>

                </div>

                """,

                unsafe_allow_html=True,

            )

        else:

            st.info("No project saved yet. Start with the 3D Room Planner.")



    with right:

        st.markdown(

            """

            <div class="soft-card">

                <div class="card-title">🤖 AI Capabilities</div>

                <div class="card-sub">Core Data Science components</div>

                <p>✓ YOLO computer vision</p>

                <p>✓ ML design recommender</p>

                <p>✓ Floor-plan analysis</p>

                <p>✓ AI concept generation</p>

                <p>✓ Interactive Three.js 3D</p>

                <p>✓ SQLite project database</p>

            </div>

            """,

            unsafe_allow_html=True,

        )



    st.markdown("### Start Designing")

    q1, q2, q3 = st.columns(3)

    with q1:

        st.markdown("<div class='soft-card'><div class='card-title'>🎨 AI Design Studio</div><div class='card-sub'>Analyse images and generate design concepts.</div></div>", unsafe_allow_html=True)

    with q2:

        st.markdown("<div class='soft-card'><div class='card-title'>🧊 3D Room Planner</div><div class='card-sub'>Arrange furniture and explore the room interactively.</div></div>", unsafe_allow_html=True)

    with q3:

        st.markdown("<div class='soft-card'><div class='card-title'>💰 Cost Estimator</div><div class='card-sub'>Estimate flooring, paint, furniture, labour and contingency.</div></div>", unsafe_allow_html=True)





# ============================================================

# AI DESIGN STUDIO

# ============================================================



if page == "AI Design Studio":



    st.markdown(

        """

        <div class="hero">

            <h1>AI Interior Design Studio</h1>

            <div class="hero-subtitle">

                Transform an empty room into a personalized interior with AI.

            </div>

            <div class="hero-meta">

                Upload a room image • YOLO detection • ML recommendations

                • AI visualization • Cost estimation

            </div>

        </div>

        """,

        unsafe_allow_html=True,

    )



    room_names = [

        "Bedroom",

        "Living Room",

        "Kitchen",

        "Bathroom",

    ]



    selected_room = st.radio(

        "Room Type",

        room_names,

        horizontal=True,

        index=room_names.index(

            st.session_state.get("selected_room", "Bedroom")

        ),

        label_visibility="collapsed",

    )



    # Clear any previous AI result when the user switches rooms.
    # Otherwise a Bedroom selection can keep showing an older room's image.
    previous_ai_room = st.session_state.get("ai_last_room")
    if previous_ai_room != selected_room:
        for _key in (
            "generated", "original_image", "annotated", "detections",
            "counts", "recommendations", "plan_info", "plan_context", "prompt",
        ):
            st.session_state.pop(_key, None)
        st.session_state["ai_last_room"] = selected_room

    st.session_state["selected_room"] = selected_room

    # Room-specific furniture and fixtures for AI generation
    ROOM_ELEMENTS = {
        "Bedroom": ["Bed", "Bedside Tables", "Wardrobe", "Dressing Table", "Study Desk", "TV Unit", "Storage"],
        "Living Room": ["L-Shape Sofa", "3-Seater Sofa", "Accent Chairs", "Coffee Table", "TV Unit", "Console", "Display Storage"],
        "Kitchen": ["Modular Cabinets", "Tall Unit", "Pantry", "Kitchen Island", "Dining Table", "Dining Chairs", "Refrigerator", "Hob", "Chimney", "Microwave/Oven", "Sink", "Countertop", "Backsplash"],
        "Bathroom": ["Vanity", "WC", "Shower", "Rain Shower", "Bathtub", "Glass Partition", "Shower Niche", "Backlit Mirror", "Storage", "Towel Rack"],
    }

    st.markdown("### 🪑 Furniture & Fixtures")
    selected_elements = st.multiselect(
        "Select elements to include in your AI design",
        ROOM_ELEMENTS[selected_room],
        default=ROOM_ELEMENTS[selected_room],
        key=f"ai_elements_{selected_room}",
    )
    st.session_state["selected_elements"] = selected_elements
    if selected_elements:
        st.caption("AI will prioritize: " + " • ".join(selected_elements))

    input_col, visual_col, insight_col = st.columns(

        [1.0, 1.75, 1.0],

        gap="large",

    )



    # --------------------------------------------------------

    # INPUT

    # --------------------------------------------------------



    with input_col:



        st.markdown(

            """

            <div class="casa-card">

            <h3>1. Upload Your Room</h3>

            </div>

            """,

            unsafe_allow_html=True,

        )



        room_file = st.file_uploader(

            "Empty room image",

            type=["jpg", "jpeg", "png", "webp"],

            key="room_image",

        )



        plan_file = st.file_uploader(

            "2D floor plan (optional)",

            type=["jpg", "jpeg", "png"],

            key="floor_plan",

        )



        st.markdown(

            """

            <div class="casa-card">

            <h3>Design Preferences</h3>

            </div>

            """,

            unsafe_allow_html=True,

        )



        style = st.selectbox(

            "Interior Style",

            [

                "Modern Minimalist",

                "Luxury Modern",

                "Contemporary",

                "Japanese Japandi",

                "Scandinavian",

                "Modern Classic",

                "Indian Contemporary",

            ],

        )



        budget = st.slider(

            "Budget (₹ Lakh)",

            1.0,

            50.0,

            5.0,

            0.5,

        )



        area = st.number_input(

            "Room Area (sq.ft.)",

            40,

            3000,

            250,

            10,

        )



        color = st.selectbox(

            "Color Palette",

            [

                "Beige Ivory",

                "Cream Gold",

                "Grey Walnut",

                "White Beige",

                "Sand Olive",

                "Taupe Gold",

                "Pastel Blue White",

            ],

        )



        materials = st.selectbox(

            "Preferred Material",

            [

                "Wood Laminate",

                "Marble",

                "Quartz",

                "Fluted Panel",

                "Oak Wood",

                "PU",

                "Veneer",

                "Matte Laminate",

            ],

        )



        generate_clicked = st.button(

            "✨ Generate AI Interior",

            use_container_width=True,

        )



    # --------------------------------------------------------

    # VISUALIZATION

    # --------------------------------------------------------



    with visual_col:



        st.markdown("### 2. AI Visualization")



        if room_file is None:



            st.info(

                "Upload an empty room image to begin."

            )



        else:



            from PIL import Image



            room_image = Image.open(

                room_file

            ).convert("RGB")



            if generate_clicked:



                with st.spinner(

                    "🔍 Detecting objects with YOLO..."

                ):



                    annotated, detections, counts = (

                        get_detector().detect(room_image)

                    )



                plan_info = None



                if plan_file is not None:



                    with st.spinner(

                        "📐 Analyzing 2D floor plan..."

                    ):



                        plan_image = Image.open(

                            plan_file

                        ).convert("RGB")



                        plan_info = analyze_plan(

                            plan_image

                        )



                with st.spinner(

                    "🧠 Running ML recommendation..."

                ):



                    recommendations = (

                        get_recommender().recommend(

                            selected_room,

                            style,

                            budget,

                            area,

                            color,

                            materials,

                        )

                    )



                plan_context = _build_plan_context(plan_info, selected_room)

                prompt = build_prompt(
                    selected_room,
                    style,
                    color,
                    materials,
                    recommendations,
                    counts,
                    selected_elements=selected_elements,
                    plan_info=plan_info,
                )

                selected_elements_text = ", ".join(selected_elements) if selected_elements else "none"

                # Stable Diffusion CLIP has a short text window. Put the
                # user's required furniture/fixtures FIRST so they survive
                # prompt truncation.
                room_layout_rules = {
                    "Bedroom": "BEDROOM MUST SHOW A CLEAR, FULL-SIZE BED as the main focal furniture, centered against the main wall or headboard wall; the bed must be visibly recognizable and not replaced by a chair or cabinet; place other selected bedroom furniture practically",
                    "Living Room": "arrange selected seating around the main focal/TV wall with realistic circulation space",
                    "Kitchen": "place selected cabinets and appliances in a realistic work triangle and place the dining set in a practical dining zone",
                    "Bathroom": "place selected sanitary fixtures against appropriate walls with realistic clearances; keep shower and bathtub clearly visible when selected",
                }

                priority_prompt = (
                    f"{selected_room} interior design. MUST INCLUDE: {selected_elements_text}. "
                    f"{room_layout_rules.get(selected_room, 'place all selected elements realistically')}. "
                    f"Style: {style}. Colors: {color}. Materials: {materials}. "
                    "Photorealistic interior, realistic proportions, coherent architecture, "
                    "do not omit required furniture or fixtures. "
                )
                prompt = priority_prompt + prompt

                if plan_context:
                    prompt += "\n\n" + plan_context

                with st.spinner(

                    "🎨 Creating AI interior concept..."

                ):



                    generated = generate_concept(

                        room_image,

                        prompt,

                        f"{selected_room} — {style}",

                    )



                st.session_state.update(

                    {

                        "original_image": room_image,

                        "generated": generated,

                        "annotated": annotated,

                        "detections": detections,

                        "counts": counts,

                        "recommendations": recommendations,

                        "plan_info": plan_info,
                        "plan_context": plan_context,

                        "selected_room": selected_room,

                        "style": style,

                        "budget": budget,

                        "area": area,

                        "color": color,

                        "materials": materials,
                        "selected_elements": selected_elements,

                        "prompt": prompt,

                    }

                )



            if "generated" in st.session_state:



                st.markdown(

                    "#### ✨ AI Generated Interior"

                )



                st.image(

                    st.session_state["generated"],

                    use_container_width=True,

                )



                image_buffer = io.BytesIO()



                st.session_state["generated"].save(

                    image_buffer,

                    format="PNG",

                )



                st.download_button(

                    "⬇️ Download Design",

                    image_buffer.getvalue(),

                    "casacraft_ai_design.png",

                    "image/png",

                    use_container_width=True,

                )



            else:



                st.image(

                    room_image,

                    caption="Uploaded Empty Room",

                    use_container_width=True,

                )





    # --------------------------------------------------------

    # INSIGHTS

    # --------------------------------------------------------



    with insight_col:



        st.markdown("### 3. Smart Insights")



        if "recommendations" in st.session_state:



            best = st.session_state[

                "recommendations"

            ][0]



            st.metric(

                "AI Match",

                f"{best['match_score']:.1f}%",

            )



            st.metric(

                "Reference Budget",

                f"₹{best['budget_lakh']:.1f} L",

            )



            st.write("**Recommended Style**")

            st.success(best["style"])



            st.write("**Materials**")

            st.write(best["materials"])



            st.write("**Lighting**")

            st.write(best["lighting"])



            st.write("**Furniture**")

            st.write(best["furniture"])



            st.write("**Features**")

            st.write(best["features"])



        else:



            st.info(

                "Generate a design to see AI recommendations."

            )



    # --------------------------------------------------------

    # YOLO / ML ANALYTICS

    # --------------------------------------------------------



    if "annotated" in st.session_state:



        st.divider()



        detection_col, variation_col = st.columns(

            [1.2, 1.0],

            gap="large",

        )



        with detection_col:



            st.markdown(

                """

                <div class="casa-card">

                <h3>👁️ YOLO Object Detection</h3>

                """,

                unsafe_allow_html=True,

            )



            st.image(

                st.session_state["annotated"],

                use_container_width=True,

            )



            counts = st.session_state.get(

                "counts",

                {},

            )



            if counts:



                chart_data = pd.DataFrame(

                    list(counts.items()),

                    columns=["Object", "Count"],

                )



                fig = px.bar(

                    chart_data,

                    x="Object",

                    y="Count",

                    title="Detected Interior Objects",

                )



                fig.update_layout(

                    paper_bgcolor="rgba(0,0,0,0)",

                    plot_bgcolor="rgba(0,0,0,0)",

                    margin=dict(

                        l=10,

                        r=10,

                        t=50,

                        b=10,

                    ),

                )



                st.plotly_chart(

                    fig,

                    use_container_width=True,

                )



            else:



                st.info(

                    "No objects detected above the confidence threshold."

                )



            st.markdown("</div>", unsafe_allow_html=True)



        with variation_col:



            st.markdown(

                """

                <div class="casa-card">

                <h3>🎨 Design Variations</h3>

                """,

                unsafe_allow_html=True,

            )



            for recommendation in st.session_state[

                "recommendations"

            ]:



                score_percent = max(

                    0.0,

                    min(

                        float(

                            recommendation["match_score"]

                        ),

                        100.0,

                    ),

                )



                st.write(

                    f"**{recommendation['style']}** "

                    f"— {score_percent:.1f}%"

                )



                st.progress(score_percent / 100.0)



            st.markdown("</div>", unsafe_allow_html=True)



        # ----------------------------------------------------

        # FLOOR PLAN

        # ----------------------------------------------------



        if st.session_state.get(

            "plan_info"

        ):



            st.markdown(

                """

                <div class="casa-card">

                <h3>📐 2D Floor Plan Analysis</h3>

                """,

                unsafe_allow_html=True,

            )



            info = st.session_state[

                "plan_info"

            ]



            c1, c2, c3 = st.columns(3)



            c1.metric(

                "Width",

                f"{info['width']} px",

            )



            c2.metric(

                "Height",

                f"{info['height']} px",

            )



            c3.metric(

                "Line Segments",

                info["line_segments"],

            )



            st.caption(

                f"Edge ratio: {info['edge_ratio']}"

            )

            plan_context_display = st.session_state.get("plan_context", "")
            if plan_context_display:
                st.info(
                    "🧠 **Plan-aware AI guidance:** "
                    + plan_context_display.replace("2D FLOOR PLAN CONSTRAINTS: ", "", 1)
                )



            st.markdown("</div>", unsafe_allow_html=True)



        # ----------------------------------------------------

        # RECOMMENDATIONS

        # ----------------------------------------------------



        st.subheader(

            "✨ AI Design Recommendations"

        )



        st.caption(

            "Reference images are matched using room type + design style "

            "from the new Kaggle room dataset. Budget, materials, colors "

            "and furniture details come from the project design dataset."

        )



        for index, recommendation in enumerate(

            st.session_state[

                "recommendations"

            ],

            start=1,

        ):



            with st.expander(

                f"{index}. "

                f"{recommendation['style']} "

                f"— "

                f"{recommendation['match_score']:.1f}% match"

            ):



                images = recommendation.get("images", [])



                if images:

                    st.markdown("#### 🖼️ Room + Style Reference Images")

                    image_cols = st.columns(min(3, len(images)))



                    for image_index, image_info in enumerate(images[:3]):

                        raw_path = str(

                            image_info.get("image_path", "")

                        ).strip()

                        image_path = Path(raw_path)



                        if not image_path.is_absolute():

                            image_path = (

                                Path(__file__).resolve().parent

                                / image_path

                            )



                        with image_cols[image_index % len(image_cols)]:

                            if image_path.exists():

                                st.image(

                                    str(image_path),

                                    use_container_width=True,

                                )

                                st.caption(

                                    f"Room: {recommendation.get('room_type', st.session_state.get('selected_room', 'Room'))} "

                                    f"• Style: {image_info.get('style_folder', recommendation.get('style', 'Style'))}"

                                )

                            else:

                                st.warning(

                                    f"Reference image not found: {image_path.name}"

                                )



                    st.caption(

                        recommendation.get(

                            "image_note",

                            "Reference images matched from the local dataset."

                        )

                    )

                else:

                    st.info(

                        "No matching room + style reference images were found."

                    )



                st.caption(

                    f"📚 Reference source: {recommendation.get('image_source', 'Local reference dataset')}"

                )



                c1, c2 = st.columns(2)



                with c1:



                    st.write(

                        f"🎨 **Color:** "

                        f"{recommendation['color']}"

                    )



                    st.write(

                        f"🧱 **Materials:** "

                        f"{recommendation['materials']}"

                    )



                    st.write(

                        f"💡 **Lighting:** "

                        f"{recommendation['lighting']}"

                    )



                with c2:



                    st.write(

                        f"🛋️ **Furniture:** "

                        f"{recommendation['furniture']}"

                    )



                    st.write(

                        f"✨ **Features:** "

                        f"{recommendation['features']}"

                    )



                    st.write(

                        f"💰 **Budget:** "

                        f"₹{recommendation['budget_lakh']:.1f} L"

                    )



        # ----------------------------------------------------

        # SAVE

        # ----------------------------------------------------



        st.divider()



        if st.button(

            "💾 Save This Interior Project",

            use_container_width=True,

        ):



            save_project(

                f"{st.session_state['selected_room']} Design",

                st.session_state["selected_room"],

                st.session_state["style"],

                st.session_state["budget"],

                st.session_state["area"],

                {

                    "color": st.session_state[

                        "color"

                    ],

                    "materials": st.session_state[

                        "materials"

                    ],

                    "recommendations":

                        st.session_state[

                            "recommendations"

                        ],

                },

            )



            st.success(

                "Project saved successfully."

            )





# ============================================================

# REAL INTERACTIVE 3D ROOM PLANNER

# ============================================================



if page == "AI Design Suggestions":

    st.markdown("""
    <div class="project-header">
      <div class="project-kicker">CASACRAFT AI • QUICK FURNITURE EXPLORER</div>
      <div class="project-title">Furniture Library & Design Ideas</div>
      <div class="project-sub">Browse design directions, finishes and indicative prices instantly — no AI model or room photo needed.</div>
    </div>
    """, unsafe_allow_html=True)

    # This page is intentionally rule-based and fast. Image generation remains
    # available in AI Design Studio only.
    furniture_catalog = {
        "Bedroom": {
            "Bed": [("Modern upholstered bed", "Fabric upholstery + engineered wood", "₹25,000–₹65,000", "🛏️"), ("Hydraulic storage bed", "BWP ply + laminate + hydraulic lift", "₹35,000–₹85,000", "🛏️"), ("Japandi low platform bed", "Natural wood finish + simple headboard", "₹28,000–₹70,000", "🪵"), ("Luxury curved headboard bed", "Upholstered headboard + premium fabric", "₹40,000–₹1,00,000", "✨")],
            "Wardrobe": [("Sliding shutter wardrobe", "BWP ply + 1 mm laminate", "₹1,200–₹1,900/sq.ft.", "🚪"), ("Hinged wardrobe with loft", "BWP ply + laminate + soft-close hinges", "₹1,100–₹1,800/sq.ft.", "🚪"), ("Fluted accent wardrobe", "Laminate + fluted detail", "₹1,400–₹2,200/sq.ft.", "〰️"), ("Mirror shutter wardrobe", "Mirror panel + laminate carcass", "₹1,500–₹2,300/sq.ft.", "🪞")],
            "Bedside Table": [("Floating bedside table", "BWP ply + laminate", "₹4,000–₹9,000", "🗄️"), ("Two-drawer bedside table", "Laminate finish + drawer channels", "₹5,000–₹12,000", "🗄️"), ("Round bedside table", "Wood finish + rounded profile", "₹4,500–₹10,000", "⭕")],
            "Dressing Table": [("Wall-mounted dressing unit", "Laminate + mirror + drawer", "₹10,000–₹22,000", "🪞"), ("Full-height mirror unit", "Mirror + storage drawers", "₹15,000–₹35,000", "🪞"), ("Fluted dressing unit", "Fluted finish + warm LED option", "₹18,000–₹40,000", "✨")],
        },
        "Living Room": {
            "Sofa": [("Three-seater sofa", "Fabric upholstery + hardwood frame", "₹28,000–₹65,000", "🛋️"), ("L-shaped sectional sofa", "Fabric upholstery + modular sections", "₹45,000–₹1,20,000", "🛋️"), ("Curved contemporary sofa", "Textured fabric + curved silhouette", "₹55,000–₹1,40,000", "✨"), ("Japandi linen sofa", "Linen-look fabric + wood legs", "₹35,000–₹85,000", "🛋️")],
            "TV Unit": [("Floating TV unit", "BWP ply + laminate", "₹18,000–₹40,000", "📺"), ("Marble-look feature unit", "Laminate/stone-look panel + storage", "₹30,000–₹75,000", "🪨"), ("Wood-slat TV panel", "Wood-finish slats + concealed wiring", "₹25,000–₹60,000", "🪵")],
            "Coffee Table": [("Round nesting tables", "Wood finish + metal/wood base", "₹6,000–₹18,000", "⭕"), ("Marble-top coffee table", "Stone-look top + sturdy base", "₹8,000–₹25,000", "🪨"), ("Minimal glass table", "Tempered glass + metal base", "₹5,000–₹16,000", "◻️")],
            "Storage Console": [("Closed storage console", "Laminate finish + concealed storage", "₹12,000–₹30,000", "🗄️"), ("Open display shelves", "Wood finish + open shelving", "₹8,000–₹22,000", "📚")],
        },
        "Kitchen": {
            "Kitchen Layout": [("L-shaped modular kitchen", "BWP/BWR ply + laminate shutters", "₹1.5–₹3.5 lakh", "🍽️"), ("Parallel modular kitchen", "BWP/BWR ply + laminate shutters", "₹1.8–₹4 lakh", "🍽️"), ("U-shaped modular kitchen", "BWP/BWR ply + laminate shutters", "₹2.2–₹5 lakh", "🍽️")],
            "Shutters": [("Matte beige shutters", "1 mm matte laminate", "₹900–₹1,600/sq.ft.", "🎨"), ("Glossy cream shutters", "Glossy laminate finish", "₹1,000–₹1,800/sq.ft.", "✨"), ("Walnut wood finish", "Wood-grain laminate", "₹1,000–₹1,800/sq.ft.", "🪵"), ("Handleless profile shutters", "Profile handle + laminate", "₹1,200–₹2,000/sq.ft.", "〰️")],
            "Storage Accessories": [("Tandem drawer unit", "Soft-close tandem channels", "₹8,000–₹20,000", "🗄️"), ("Bottle pull-out", "Metal pull-out basket", "₹3,000–₹8,000", "🧴"), ("Tall pantry unit", "Shelves + pull-out accessories", "₹15,000–₹45,000", "📦")],
        },
        "Bathroom": {
            "Vanity": [("Floating vanity", "Moisture-resistant board + laminate", "₹12,000–₹30,000", "🚿"), ("Wood-finish vanity", "Wood-look finish + storage", "₹15,000–₹35,000", "🪵")],
            "Mirror": [("Backlit round mirror", "LED mirror", "₹4,000–₹12,000", "🪞"), ("Medicine cabinet mirror", "Mirror + concealed storage", "₹6,000–₹18,000", "🪞")],
            "Shower Partition": [("Frameless glass partition", "Toughened glass + hardware", "₹12,000–₹30,000", "🚿"), ("Black-frame partition", "Toughened glass + black hardware", "₹15,000–₹35,000", "◻️")],
            "Tiles": [("Beige stone-look tiles", "Ceramic/porcelain tile", "₹60–₹180/sq.ft.", "🧱"), ("Marble-look wall tiles", "Glazed porcelain tile", "₹80–₹250/sq.ft.", "🧱"), ("Textured accent tiles", "Decorative tile finish", "₹100–₹300/sq.ft.", "🧱")],
        },
    }

    room_type = st.selectbox("Choose room", list(furniture_catalog.keys()), key="suggest_room_type")
    category = st.selectbox("Choose furniture category", list(furniture_catalog[room_type].keys()), key="suggest_furniture_category")
    style = st.selectbox("Preferred style", ["Modern Minimalist", "Luxury Contemporary", "Japandi", "Scandinavian", "Warm Contemporary"], key="suggest_style_fast")
    colours = st.multiselect("Preferred colours / finishes", ["Warm Beige", "Cream", "Ivory", "Walnut", "Light Oak", "Grey", "Sage Green", "Black Accents"], default=["Warm Beige", "Cream", "Walnut"], key="suggest_colours_fast")
    budget = st.selectbox("Budget range", ["Budget-friendly", "Mid-range", "Premium"], index=1, key="suggest_budget_fast")

    st.markdown("## Design options")
    options = furniture_catalog[room_type][category]
    cols = st.columns(min(3, len(options)))
    for idx, (name, material, price, emoji) in enumerate(options):
        with cols[idx % len(cols)]:
            colour_labels = " · ".join(colours) if colours else "No colour preference"
            st.markdown(
                f"<div class='soft-card' style='min-height:122px;padding:18px 16px;'>"
                f"<div style='font-size:38px;line-height:1.2;margin-bottom:10px'>{emoji}</div>"
                f"<div class='card-title'>{name}</div>"
                f"<div class='card-sub'>{style}</div>"
                f"<div style='font-size:12px;color:#78685d;margin-top:8px'>Finish palette: {colour_labels}</div>"
                f"</div>", unsafe_allow_html=True)
            st.write(f"**Material / finish:** {material}")
            st.write(f"**Indicative price:** {price}")
            st.caption("Concept estimate only. Final price depends on size, hardware, brand and site conditions.")
            if st.button("＋ Save this idea", key=f"save_idea_{room_type}_{category}_{idx}", use_container_width=True, type="primary"):
                saved = st.session_state.get("casacraft_saved_furniture_ideas", [])
                idea = {"room": room_type, "category": category, "design": name, "style": style, "colours": colours, "material": material, "indicative_price": price}
                if idea not in saved:
                    saved.append(idea)
                st.session_state["casacraft_saved_furniture_ideas"] = saved
                st.success("Idea saved for this session.")

    st.markdown("## Your selection summary")
    st.write(f"**Room:** {room_type}  ·  **Category:** {category}  ·  **Style:** {style}")
    st.write("**Preferred colours:** " + (", ".join(colours) if colours else "No colour preference selected"))
    st.write(f"**Budget preference:** {budget}")
    st.info("This page is designed for instant browsing. For an AI-generated visualization of your actual room photo, use **AI Design Studio**. Your existing 3D Room Planner remains separate.")

    saved_ideas = st.session_state.get("casacraft_saved_furniture_ideas", [])
    if saved_ideas:
        with st.expander(f"Saved ideas in this session ({len(saved_ideas)})"):
            st.dataframe(saved_ideas, use_container_width=True, hide_index=True)

elif page == "3D Room Planner":



    st.markdown(

        """

        <div class="project-header">

            <div class="project-kicker">CASACRAFT AI • 3D INTERIOR STUDIO</div>

            <div class="project-title">Design. Visualize. Estimate.</div>

            <div class="project-sub">

                Build your room in 3D, arrange furniture, explore finishes and keep the project budget in view.

            </div>

        </div>

        """,

        unsafe_allow_html=True,

    )



    # --------------------------------------------------------

    # PROJECT CONTROLS

    # --------------------------------------------------------

    control1, control2, control3, control4 = st.columns([1.1, 1.0, 1.0, 1.0])



    with control1:

        room = st.selectbox(

            "Room Type",

            ["Living Room", "Bedroom", "Kitchen", "Bathroom"],

            key="planner_room",

        )



    with control2:

        width = st.number_input(

            "Width (ft)",

            min_value=8.0,

            max_value=40.0,

            value=12.0,

            step=1.0,

            key="planner_width",

        )



    with control3:

        length = st.number_input(

            "Length (ft)",

            min_value=8.0,

            max_value=50.0,

            value=16.0,

            step=1.0,

            key="planner_length",

        )



    with control4:

        budget = st.number_input(

            "Project Budget (₹)",

            min_value=0,

            value=350000,

            step=10000,

            key="planner_budget",

        )



    area = width * length



    # Room-specific furniture

    room_furniture = {

        "Bedroom": ["Bed", "Wardrobe", "TV Unit", "Coffee Table"],

        "Living Room": ["Sofa", "TV Unit", "Coffee Table", "Dining Table"],

        "Kitchen": ["Kitchen Island", "Tall Unit", "Dining Table"],

        "Bathroom": ["Vanity", "Shower", "Bathtub", "Tall Unit"],

    }



    default_map = {

        "Bedroom": ["Bed", "Wardrobe"],

        "Living Room": ["Sofa", "TV Unit", "Coffee Table"],

        "Kitchen": ["Kitchen Island", "Tall Unit"],

        "Bathroom": ["Vanity", "Shower"],

    }



    furniture = st.multiselect(

        "Furniture / Fixtures",

        room_furniture[room],

        default=default_map[room],

        key="planner_furniture",

    )



    st.markdown("### 3D Materials & Finishes")



    material1, material2, material3, material4 = st.columns(4)



    with material1:

        wall_color = st.color_picker("Wall", "#e6ddd2", key="planner_wall")



    with material2:

        floor_color = st.color_picker("Floor", "#a88768", key="planner_floor")



    with material3:

        accent_color = st.color_picker("Furniture", "#80614d", key="planner_accent")



    with material4:

        style = st.selectbox(

            "Interior Style",

            ["Modern Minimalist", "Luxury Modern", "Contemporary", "Japandi", "Modern Classic"],

            key="planner_style",

        )



    # Approximate academic estimator for the dashboard.

    furniture_rates = {

        "Sofa": 55000,

        "Bed": 65000,

        "Wardrobe": 75000,

        "TV Unit": 35000,

        "Coffee Table": 18000,

        "Dining Table": 45000,

        "Kitchen Island": 65000,

        "Tall Unit": 30000,

        "Vanity": 28000,

        "Shower": 22000,

        "Bathtub": 55000,

    }



    furniture_cost = sum(furniture_rates.get(item, 0) for item in furniture)

    flooring_cost = area * 120

    paint_area = area * 2.5

    paint_cost = paint_area * 35

    lighting_points = max(6, int(round(area / 20)))

    lighting_cost = lighting_points * 1500

    material_cost = 25000 if furniture else 12000

    labour_cost = area * 70

    subtotal = furniture_cost + flooring_cost + paint_cost + lighting_cost + material_cost + labour_cost

    contingency = subtotal * 0.05

    estimated_total = subtotal + contingency

    remaining = budget - estimated_total



    # --------------------------------------------------------

    # SUMMARY STRIP

    # --------------------------------------------------------

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Room Area", f"{area:,.0f} sq.ft.")

    m2.metric("Furniture", f"{len(furniture)} items")

    m3.metric("Estimated Cost", f"₹{estimated_total:,.0f}")

    m4.metric("Budget Balance", f"₹{remaining:,.0f}")



    # --------------------------------------------------------

    # MAIN 3D + DETAILS

    # --------------------------------------------------------

    left, right = st.columns([3.1, 1.05], gap="large")



    if st.button("🧊 Create / Update 3D Project", use_container_width=True, type="primary"):

        st.session_state["show_3d"] = True

        st.session_state["3d_config"] = {

            "room": room,

            "width": width,

            "length": length,

            "furniture": furniture,

            "wall_color": wall_color,

            "floor_color": floor_color,

            "accent_color": accent_color,

            "style": style,

            "budget": budget,

            "estimated_total": estimated_total,

        }



    with left:

        st.markdown(

            f"""

            <div class="soft-card" style="padding:10px;">

                <div class="card-title" style="padding:8px 10px 0;">3D Room Preview</div>

                <div class="card-sub" style="padding:0 10px;">

                    {room} • {width:g} × {length:g} ft • {style}

                </div>

            </div>

            """,

            unsafe_allow_html=True,

        )



        if st.session_state.get("show_3d", False):

            config = st.session_state["3d_config"]

            render_3d_room(

                width_ft=config["width"],

                length_ft=config["length"],

                selected_furniture=config["furniture"],

                wall_color=config["wall_color"],

                floor_color=config["floor_color"],

                accent_color=config["accent_color"],

            )

        else:

            st.info("Choose your room settings and click Create / Update 3D Project.")



    with right:

        st.markdown(

            f"""

            <div class="soft-card">

                <div class="card-title">Project Summary</div>

                <div class="card-sub">Current design configuration</div>

                <b>Room</b><br>{room}<br><br>

                <b>Dimensions</b><br>{width:g} × {length:g} ft<br><br>

                <b>Style</b><br>{style}<br><br>

                <b>Furniture</b><br>{len(furniture)} selected<br><br>

                <b>Budget</b><br>₹{budget:,.0f}<br><br>

                <b>Estimated Cost</b><br>

                <span class="price-big">₹{estimated_total:,.0f}</span>

            </div>

            """,

            unsafe_allow_html=True,

        )



        st.markdown("<div class='section-gap'></div>", unsafe_allow_html=True)



        status = "Within Budget" if remaining >= 0 else "Over Budget"

        status_bg = "#e8f4e9" if remaining >= 0 else "#fde9e7"

        status_fg = "#2d7040" if remaining >= 0 else "#a33b2e"

        st.markdown(

            f"""

            <div class="soft-card">

                <div class="card-title">Budget Status</div>

                <div style="display:inline-block;padding:7px 12px;border-radius:20px;background:{status_bg};color:{status_fg};font-weight:800;font-size:12px;">

                    {status}

                </div>

                <p style="margin-top:12px;">Balance: <b>₹{remaining:,.0f}</b></p>

            </div>

            """,

            unsafe_allow_html=True,

        )



    # --------------------------------------------------------

    # COST + MATERIALS + SAVE

    # --------------------------------------------------------

    st.markdown("### Project Output")



    cost_col, details_col = st.columns([1.35, 1], gap="large")



    with cost_col:

        st.markdown(

            """

            <div class="soft-card">

                <div class="card-title">💰 Cost Estimator</div>

                <div class="card-sub">Academic estimate based on room area and selected furniture</div>

            </div>

            """,

            unsafe_allow_html=True,

        )

        cost_df = pd.DataFrame({

            "Item": [

                "Furniture",

                "Flooring",

                "Wall Paint",

                "Lighting",

                "Material / Hardware",

                "Labour",

                "Contingency (5%)",

            ],

            "Amount (₹)": [

                furniture_cost,

                flooring_cost,

                paint_cost,

                lighting_cost,

                material_cost,

                labour_cost,

                contingency,

            ],

        })

        st.dataframe(

            cost_df.style.format({"Amount (₹)": "₹{:,.0f}"}),

            use_container_width=True,

            hide_index=True,

        )

        st.metric("Total Estimated Cost", f"₹{estimated_total:,.0f}")



    with details_col:

        st.markdown(

            f"""

            <div class="soft-card">

                <div class="card-title">🎨 Design Details</div>

                <div class="card-sub">Materials, palette and AI-ready project metadata</div>

                <b>Selected Furniture</b><br>

                {', '.join(furniture) if furniture else 'No furniture selected'}

                <br><br>

                <b>Colour Palette</b><br>

                <span class="palette-dot" style="background:{wall_color};"></span>

                <span class="palette-dot" style="background:{floor_color};"></span>

                <span class="palette-dot" style="background:{accent_color};"></span>

                <br><br>

                <b>Finish Direction</b><br>

                {style} • warm neutral interior

            </div>

            """,

            unsafe_allow_html=True,

        )



    # --------------------------------------------------------

    # AI PROJECT RECOMMENDATIONS

    # --------------------------------------------------------

    st.markdown("### 🤖 AI Interior Recommendations")

    st.caption("Recommendations are generated from the current room configuration, style, furniture, dimensions and budget.")



    project_recommendations = build_project_recommendations(

        room, width, length, budget, style, furniture,

        wall_color, floor_color, accent_color, estimated_total

    )



    rec_cols = st.columns(2)

    for i, (title, text_value) in enumerate(project_recommendations):

        with rec_cols[i % 2]:

            st.markdown(

                f"""

                <div class='soft-card' style='margin-bottom:14px;'>

                    <div class='card-title'>{title}</div>

                    <div class='card-sub'>{text_value}</div>

                </div>

                """,

                unsafe_allow_html=True,

            )



    save_col, reset_col = st.columns([3, 1])



    with save_col:

        if st.button("💾 Save Complete Project", use_container_width=True):

            save_project(

                f"{room} • {style}",

                room,

                style,

                budget,

                area,

                {

                    "dimensions": {"width": width, "length": length},

                    "furniture": furniture,

                    "wall_color": wall_color,

                    "floor_color": floor_color,

                    "accent_color": accent_color,

                    "estimated_cost": estimated_total,

                    "furniture_cost": furniture_cost,

                    "flooring_cost": flooring_cost,

                    "paint_cost": paint_cost,

                    "lighting_cost": lighting_cost,

                    "material_cost": material_cost,

                    "labour_cost": labour_cost,

                    "contingency": contingency,

                },

            )

            st.success("Complete project saved — 3D settings, furniture, budget and estimate are stored.")



    with reset_col:

        if st.button("↺ Reset", use_container_width=True):

            st.session_state["show_3d"] = False

            st.session_state.pop("3d_config", None)

            st.rerun()



    st.info("🖱️ In the 3D view: click furniture to select, drag to move, rotate/resize/delete using the planner controls, then save the project from this page.")





# ============================================================

# STYLE GALLERY

# ============================================================



elif page == "Style Gallery":



    st.markdown(

        """

        <div class="hero">

            <h1>🎨 Interior Style Gallery</h1>

            <div class="hero-subtitle">

                Explore design styles used by the recommendation engine.

            </div>

        </div>

        """,

        unsafe_allow_html=True,

    )



    gallery = pd.DataFrame(

        {

            "Style": [

                "Modern Minimalist",

                "Luxury Modern",

                "Contemporary",

                "Japanese Japandi",

                "Scandinavian",

                "Modern Classic",

                "Indian Contemporary",

            ],

            "Character": [

                "Clean lines and calm colors",

                "Premium materials and hotel feel",

                "Functional modern forms",

                "Natural wood and simplicity",

                "Light, airy and practical",

                "Elegant mouldings and symmetry",

                "Indian details with contemporary forms",

            ],

        }

    )



    st.dataframe(

        gallery,

        use_container_width=True,

        hide_index=True,

    )





# ============================================================

# COST ESTIMATOR

# ============================================================



elif page == "Cost Estimator":



    st.markdown(

        """

        <div class="hero">

            <h1>💰 Smart Interior Cost Estimator</h1>

            <div class="hero-subtitle">

                Build a transparent academic estimate with room, finish and furniture costs.

            </div>

        </div>

        """,

        unsafe_allow_html=True,

    )



    st.markdown("### 1. Project Inputs")



    c1, c2, c3, c4 = st.columns(4)



    with c1:

        cost_room = st.selectbox(

            "Room",

            ["Bedroom", "Living Room", "Kitchen", "Bathroom"],

            key="cost_room",

        )



    with c2:

        cost_area = st.number_input(

            "Area (sq.ft.)",

            50,

            3000,

            250,

            10,

            key="cost_area",

        )



    with c3:

        finish = st.select_slider(

            "Finish Level",

            ["Basic", "Standard", "Premium", "Luxury"],

            value="Premium",

            key="cost_finish",

        )



    with c4:

        cost_budget = st.number_input(

            "Budget (₹)",

            min_value=50000,

            max_value=10000000,

            value=500000,

            step=25000,

            key="cost_budget",

        )



    room_furniture = {

        "Bedroom": ["Bed", "Wardrobe", "TV Unit", "Dressing Unit"],

        "Living Room": ["Sofa", "TV Unit", "Coffee Table", "Dining Table"],

        "Kitchen": ["Kitchen Island", "Tall Unit", "Base/Wall Units"],

        "Bathroom": ["Vanity", "Shower", "Bathtub"],

    }



    furniture_rates = {

        "Bed": 65000,

        "Wardrobe": 75000,

        "TV Unit": 35000,

        "Dressing Unit": 30000,

        "Sofa": 55000,

        "Coffee Table": 18000,

        "Dining Table": 45000,

        "Kitchen Island": 65000,

        "Tall Unit": 30000,

        "Base/Wall Units": 90000,

        "Vanity": 28000,

        "Shower": 22000,

        "Bathtub": 55000,

    }



    selected_cost_furniture = st.multiselect(

        "Furniture / Fixtures",

        room_furniture[cost_room],

        default=room_furniture[cost_room][:2],

        key="cost_furniture",

    )



    finish_rates = {

        "Basic": 1200,

        "Standard": 1800,

        "Premium": 2500,

        "Luxury": 3500,

    }



    # The finish rate is divided into transparent academic cost heads.

    finish_total = cost_area * finish_rates[finish]

    furniture_cost = sum(furniture_rates.get(x, 0) for x in selected_cost_furniture)

    flooring_cost = finish_total * 0.18

    paint_cost = finish_total * 0.08

    lighting_cost = finish_total * 0.07

    material_cost = finish_total * 0.12

    labour_cost = finish_total * 0.15

    base_interior_cost = finish_total * 0.40

    subtotal = base_interior_cost + furniture_cost + flooring_cost + paint_cost + lighting_cost + material_cost + labour_cost

    contingency = subtotal * 0.05

    estimated = subtotal + contingency

    balance = float(cost_budget) - estimated



    st.markdown("### 2. Estimate Summary")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Area", f"{cost_area:,.0f} sq.ft.")

    m2.metric("Finish", finish)

    m3.metric("Estimated Cost", f"₹{estimated:,.0f}")

    m4.metric("Budget Balance", f"₹{balance:,.0f}")



    cost_df = pd.DataFrame(

        {

            "Cost Head": [

                "Base Interior Finish",

                "Furniture / Fixtures",

                "Flooring",

                "Paint / Wall Finish",

                "Lighting",

                "Materials / Hardware",

                "Labour",

                "Contingency (5%)",

            ],

            "Amount (₹)": [

                base_interior_cost,

                furniture_cost,

                flooring_cost,

                paint_cost,

                lighting_cost,

                material_cost,

                labour_cost,

                contingency,

            ],

        }

    )



    left_cost, right_cost = st.columns([1.55, 1], gap="large")



    with left_cost:

        st.markdown("#### Cost Breakdown")

        st.dataframe(

            cost_df.style.format({"Amount (₹)": "₹{:,.0f}"}),

            use_container_width=True,

            hide_index=True,

        )

        st.metric("Total Estimated Cost", f"₹{estimated:,.0f}")



    with right_cost:

        status = "Within Budget" if balance >= 0 else "Over Budget"

        status_text = (

            f"₹{balance:,.0f} remaining"

            if balance >= 0

            else f"₹{abs(balance):,.0f} above budget"

        )

        st.markdown(

            f"""

            <div class="soft-card">

                <div class="card-title">📊 Budget Status</div>

                <div class="card-sub">{status}</div>

                <div class="price-big">₹{estimated:,.0f}</div>

                <p>{status_text}</p>

                <p><b>Room:</b> {cost_room}</p>

                <p><b>Finish:</b> {finish}</p>

                <p><b>Furniture:</b> {', '.join(selected_cost_furniture) if selected_cost_furniture else 'None selected'}</p>

            </div>

            """,

            unsafe_allow_html=True,

        )



    st.markdown("### 3. Export Estimate")



    estimate_text = "\n".join(

        [

            "CASACRAFT AI — INTERIOR COST ESTIMATE",

            "=" * 48,

            f"Room: {cost_room}",

            f"Area: {cost_area:,.0f} sq.ft.",

            f"Finish: {finish}",

            f"Budget: ₹{cost_budget:,.0f}",

            "",

            "COST BREAKDOWN",

            *[f"{row['Cost Head']}: ₹{row['Amount (₹)']:,.0f}" for _, row in cost_df.iterrows()],

            "",

            f"TOTAL ESTIMATED COST: ₹{estimated:,.0f}",

            f"BUDGET BALANCE: ₹{balance:,.0f}",

            "",

            "Academic estimate only. Actual project cost depends on materials, brands, labour, location and scope.",

        ]

    )



    estimate_csv = cost_df.to_csv(index=False).encode("utf-8")

    e1, e2 = st.columns(2)

    with e1:

        st.download_button(

            "⬇️ Download Estimate TXT",

            estimate_text,

            file_name="CasaCraft_Cost_Estimate.txt",

            mime="text/plain",

            use_container_width=True,

        )

    with e2:

        st.download_button(

            "⬇️ Download Cost CSV",

            estimate_csv,

            file_name="CasaCraft_Cost_Breakdown.csv",

            mime="text/csv",

            use_container_width=True,

        )



    st.info(

        "Academic estimate only. Actual cost varies by materials, labour, brand, location and project scope."

    )





# SAVED PROJECTS

# ============================================================



elif page == "Saved Projects":



    st.markdown(

        """

        <div class="hero">

            <h1>📁 Saved Interior Projects</h1>

            <div class="hero-subtitle">

                Review, inspect and export projects saved from CasaCraft AI.

            </div>

        </div>

        """,

        unsafe_allow_html=True,

    )



    try:

        rows = get_projects()



        if rows:

            columns = [

                "ID", "Name", "Room", "Style", "Budget", "Area", "Created At", "Metadata"

            ]

            projects = pd.DataFrame(rows, columns=columns)



            # Quick project statistics.

            s1, s2, s3, s4 = st.columns(4)

            s1.metric("Projects", len(projects))

            s2.metric("Rooms", projects["Room"].nunique())

            s3.metric("Average Area", f"{projects['Area'].astype(float).mean():,.0f} sq.ft.")

            s4.metric("Latest Budget", f"₹{float(projects.iloc[0]['Budget']):,.0f}")



            st.markdown("### Project Library")

            display_projects = projects[["ID", "Name", "Room", "Style", "Budget", "Area", "Created At"]].copy()

            display_projects["Budget"] = display_projects["Budget"].map(lambda x: f"₹{float(x):,.0f}")

            display_projects["Area"] = display_projects["Area"].map(lambda x: f"{float(x):,.0f} sq.ft.")

            st.dataframe(display_projects, use_container_width=True, hide_index=True)



            st.markdown("### Project Details & Downloads")

            for _, project in projects.iterrows():

                try:

                    metadata = json.loads(project["Metadata"]) if project["Metadata"] else {}

                except Exception:

                    metadata = {}



                estimated_cost = float(metadata.get("estimated_cost", project["Budget"]))

                furniture = metadata.get("furniture", [])

                dimensions = metadata.get("dimensions", {})

                width = dimensions.get("width", "—")

                length = dimensions.get("length", "—")



                with st.expander(f"#{int(project['ID'])}  •  {project['Name']}"):

                    d1, d2, d3, d4 = st.columns(4)

                    d1.metric("Room", project["Room"])

                    d2.metric("Style", project["Style"])

                    d3.metric("Estimated Cost", f"₹{estimated_cost:,.0f}")

                    d4.metric("Area", f"{float(project['Area']):,.0f} sq.ft.")



                    st.write(f"**Dimensions:** {width} × {length} ft")

                    st.write(f"**Furniture / Fixtures:** {', '.join(furniture) if furniture else 'Not specified'}")

                    st.write(f"**Saved:** {project['Created At']}")



                    summary = {

                        "project_id": int(project["ID"]),

                        "name": project["Name"],

                        "room": project["Room"],

                        "style": project["Style"],

                        "budget": float(project["Budget"]),

                        "area_sqft": float(project["Area"]),

                        "created_at": str(project["Created At"]),

                        "metadata": metadata,

                    }



                    summary_text = "\n".join(

                        [

                            "CASACRAFT AI — PROJECT SUMMARY",

                            "=" * 48,

                            f"Project: {summary['name']}",

                            f"Room: {summary['room']}",

                            f"Style: {summary['style']}",

                            f"Area: {summary['area_sqft']:,.0f} sq.ft.",

                            f"Dimensions: {width} × {length} ft",

                            f"Budget: ₹{summary['budget']:,.0f}",

                            f"Estimated Cost: ₹{estimated_cost:,.0f}",

                            f"Furniture: {', '.join(furniture) if furniture else 'Not specified'}",

                            f"Saved: {summary['created_at']}",

                            "",

                            "Academic project summary generated by CasaCraft AI.",

                        ]

                    )

                    summary_json = json.dumps(summary, indent=2, ensure_ascii=False).encode("utf-8")



                    b1, b2 = st.columns(2)

                    with b1:

                        st.download_button(

                            "⬇️ Download Summary",

                            summary_text,

                            file_name=f"CasaCraft_Project_{int(project['ID'])}.txt",

                            mime="text/plain",

                            key=f"download_txt_{int(project['ID'])}",

                            use_container_width=True,

                        )

                    with b2:

                        st.download_button(

                            "⬇️ Download Project JSON",

                            summary_json,

                            file_name=f"CasaCraft_Project_{int(project['ID'])}.json",

                            mime="application/json",

                            key=f"download_json_{int(project['ID'])}",

                            use_container_width=True,

                        )



        else:

            st.info("No saved projects yet. Create a project in the 3D Room Planner / AI Design Studio and click Save Complete Project.")



    except Exception as exc:

        st.error(f"Could not load saved projects: {exc}")





# FOOTER

# ============================================================



st.markdown(

    """

    <div class="feature-strip">

        <b>AI Powered Designs</b>

        &nbsp; <span>Smart & Realistic</span>

        &nbsp; • &nbsp;

        <b>Multiple Rooms</b>

        &nbsp; <span>Bedroom | Living | Kitchen | Bathroom</span>

        &nbsp; • &nbsp;

        <b>Computer Vision</b>

        &nbsp; <span>YOLO Object Detection</span>

        &nbsp; • &nbsp;

        <b>Data Science</b>

        &nbsp; <span>ML Recommendations</span>

    </div>

    """,

    unsafe_allow_html=True,

)

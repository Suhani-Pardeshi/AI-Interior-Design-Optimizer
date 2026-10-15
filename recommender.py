from pathlib import Path
import random
import numpy as np
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DESIGN_DATA = BASE_DIR / "data" / "interior_designs.csv"
IMAGE_DATA = BASE_DIR / "data" / "image_dataset.csv"


# ============================================================
# OLD STYLE DATASET MAPPING
# ============================================================

STYLE_FOLDER_MAP = {
    "Modern Minimalist": ["modern"],
    "Luxury Modern": ["modern"],
    "Japanese Japandi": ["scandinavian"],
    "Contemporary": ["contemporary"],
    "Industrial": ["industrial"],
    "Scandinavian": ["scandinavian"],
    "Traditional": ["traditional"],
    "Rustic": ["rustic"],
    "Farmhouse": ["farmhouse"],
    "Mediterranean": ["mediterranean"],
    "Coastal": ["coastal"],
    "Eclectic": ["eclectic"],
    "Mid-Century Modern": ["mid-century-modern"],
}


# ============================================================
# NEW ROOM + STYLE DATASET MAPPING
# ============================================================

ROOM_STYLE_MAP = {
    "Modern Minimalist": [
        "minimalist",
        "modern",
    ],

    "Luxury Modern": [
        "modern",
    ],

    "Japanese Japandi": [
        "scandinavian",
    ],

    "Contemporary": [
        "modern",
        "minimalist",
    ],

    "Industrial": [
        "industrial",
    ],

    "Scandinavian": [
        "scandinavian",
    ],

    "Traditional": [
        "traditional",
        "classic",
    ],

    "Rustic": [
        "rustic",
    ],

    "Farmhouse": [
        "farmhouse",
        "rustic",
    ],

    "Mediterranean": [
        "mediterranean",
    ],

    "Coastal": [
        "coastal",
    ],

    "Eclectic": [
        "eclectic",
    ],

    "Mid-Century Modern": [
        "modern",
    ],
}


# ============================================================
# ROOM NORMALIZATION
# ============================================================

ROOM_MAP = {
    "bedroom": "bedroom",
    "living room": "living_room",
    "living_room": "living_room",
    "kitchen": "kitchen",
    "bathroom": "bathroom",
}


class DesignRecommender:
    """
    Hybrid CasaCraft recommender.

    Dataset 1:
        data/interior_designs.csv
        -> budget, area, color, materials, furniture, features

    Dataset 2:
        data/image_dataset.csv
        -> broad style reference images

    Dataset 3:
        Pinterest Interior Design Images and Metadata
        -> room-specific + style-specific reference images
    """

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        # ----------------------------------------------------
        # Structured design dataset
        # ----------------------------------------------------

        if not DESIGN_DATA.exists():
            raise FileNotFoundError(
                f"Design dataset not found: {DESIGN_DATA}"
            )

        self.df = pd.read_csv(DESIGN_DATA)

        # ----------------------------------------------------
        # Existing 18,605-image dataset
        # ----------------------------------------------------

        if IMAGE_DATA.exists():
            self.image_df = pd.read_csv(IMAGE_DATA)
        else:
            self.image_df = pd.DataFrame(
                columns=["image_path", "style", "split"]
            )

        # ----------------------------------------------------
        # Validate structured dataset
        # ----------------------------------------------------

        required = [
            "room_type",
            "style",
            "budget_lakh",
            "area_sqft",
            "color",
            "materials",
            "lighting",
            "furniture",
            "features",
        ]

        missing = [
            c for c in required
            if c not in self.df.columns
        ]

        if missing:
            raise ValueError(
                "interior_designs.csv missing columns: "
                + ", ".join(missing)
            )

        # ----------------------------------------------------
        # Clean structured data
        # ----------------------------------------------------

        text_columns = [
            "room_type",
            "style",
            "color",
            "materials",
            "lighting",
            "furniture",
            "features",
        ]

        for column in text_columns:
            self.df[column] = (
                self.df[column]
                .fillna("")
                .astype(str)
                .str.strip()
            )

        self.df["budget_lakh"] = pd.to_numeric(
            self.df["budget_lakh"],
            errors="coerce"
        ).fillna(5.0)

        self.df["area_sqft"] = pd.to_numeric(
            self.df["area_sqft"],
            errors="coerce"
        ).fillna(200.0)

        # ----------------------------------------------------
        # Clean old image dataset
        # ----------------------------------------------------

        if not self.image_df.empty:

            for column in [
                "image_path",
                "style",
                "split",
            ]:
                if column not in self.image_df.columns:
                    self.image_df[column] = ""

                self.image_df[column] = (
                    self.image_df[column]
                    .fillna("")
                    .astype(str)
                    .str.strip()
                )

            self.image_df["style"] = (
                self.image_df["style"]
                .str.lower()
            )

            self.image_df["split"] = (
                self.image_df["split"]
                .str.lower()
            )

        # ----------------------------------------------------
        # Find the NEW room-specific dataset
        # ----------------------------------------------------

        self.room_dataset_root = None
        self.room_metadata = pd.DataFrame()

        self._find_room_dataset()

    # ========================================================
    # FIND NEW DATASET
    # ========================================================

    def _find_room_dataset(self):
        """
        Automatically finds metadata.csv containing:
            image_path, room_type, style

        This avoids hard-coding the Windows path.
        """

        candidates = list(
            BASE_DIR.rglob("metadata.csv")
        )

        for metadata_file in candidates:

            try:
                df = pd.read_csv(metadata_file)

                required_columns = {
                    "image_path",
                    "room_type",
                    "style",
                }

                if required_columns.issubset(
                    set(df.columns)
                ):

                    self.room_dataset_root = (
                        metadata_file.parent
                    )

                    self.room_metadata = df.copy()

                    # Clean columns
                    for column in [
                        "image_path",
                        "room_type",
                        "style",
                    ]:
                        self.room_metadata[column] = (
                            self.room_metadata[column]
                            .fillna("")
                            .astype(str)
                            .str.strip()
                        )

                    self.room_metadata["room_type"] = (
                        self.room_metadata["room_type"]
                        .str.lower()
                    )

                    self.room_metadata["style"] = (
                        self.room_metadata["style"]
                        .str.lower()
                    )

                    print(
                        "CasaCraft room dataset found:"
                    )
                    print(
                        self.room_dataset_root
                    )

                    return

            except Exception:
                continue

        print(
            "CasaCraft room-specific dataset "
            "not found. Using old style dataset only."
        )

    # ========================================================
    # TEXT MATCH
    # ========================================================

    @staticmethod
    def _text_match(value, query):

        value = str(value).lower()
        query = str(query).strip().lower()

        if not query:
            return 0.0

        if query in value:
            return 1.0

        q = set(
            query
            .replace(",", " ")
            .split()
        )

        v = set(
            value
            .replace(",", " ")
            .split()
        )

        return (
            len(q & v) / len(q)
            if q
            else 0.0
        )

    # ========================================================
    # ROOM NORMALIZATION
    # ========================================================

    @staticmethod
    def _normalize_room(room_type):

        room = str(room_type).strip().lower()

        return ROOM_MAP.get(
            room,
            room.replace(" ", "_")
        )

    # ========================================================
    # NEW ROOM-SPECIFIC IMAGES
    # ========================================================

    def get_room_style_images(
        self,
        room_type,
        style,
        max_images=6,
    ):
        """
        Get images from the NEW dataset.

        Example:

        Bedroom + Modern Minimalist
            ->
        bedroom/minimalist
        bedroom/modern

        Living Room + Industrial
            ->
        living_room/industrial
        """

        if (
            self.room_dataset_root is None
            or self.room_metadata.empty
        ):
            return []

        room = self._normalize_room(
            room_type
        )

        style_candidates = ROOM_STYLE_MAP.get(
            str(style).strip(),
            []
        )

        if not style_candidates:
            style_candidates = [
                str(style).strip().lower()
            ]

        # ----------------------------------------------------
        # Filter by ROOM first
        # ----------------------------------------------------

        room_df = self.room_metadata[
            self.room_metadata["room_type"]
            == room
        ].copy()

        if room_df.empty:
            return []

        # ----------------------------------------------------
        # Filter by STYLE
        # ----------------------------------------------------

        style_df = room_df[
            room_df["style"].isin(
                [
                    x.lower()
                    for x in style_candidates
                ]
            )
        ].copy()

        # ----------------------------------------------------
        # If exact style unavailable,
        # use all images from that room.
        # ----------------------------------------------------

        if style_df.empty:
            style_df = room_df

        # ----------------------------------------------------
        # Build actual file paths
        # ----------------------------------------------------

        valid_images = []

        for _, row in style_df.iterrows():

            metadata_path = str(
                row["image_path"]
            ).strip()

            if not metadata_path:
                continue

            # ------------------------------------------------
            # IMPORTANT:
            # metadata contains paths like:
            #
            # ../data/raw\bathroom\boho\image.jpg
            #
            # We DON'T use that broken path.
            #
            # Instead use:
            #
            # dataset_root / room / style / filename
            # ------------------------------------------------

            filename = Path(
                metadata_path.replace(
                    "\\",
                    "/"
                )
            ).name

            image_style = str(
                row["style"]
            ).strip().lower()

            image_path = (
                self.room_dataset_root
                / room
                / image_style
                / filename
            )

            if image_path.exists():

                valid_images.append(
                    {
                        "image_path": str(
                            image_path
                        ),
                        "style_folder": image_style,
                        "room_type": room,
                        "split": "room_dataset",
                        "source":
                            "Kaggle room + style dataset",
                    }
                )

        if not valid_images:
            return []

        count = min(
            max_images,
            len(valid_images)
        )

        return random.sample(
            valid_images,
            count
        )

    # ========================================================
    # OLD STYLE DATASET IMAGES
    # ========================================================

    def get_style_images(
        self,
        style,
        max_images=6,
    ):
        """
        Existing 18,605-image dataset.

        Used as a fallback / additional style reference.
        """

        if self.image_df.empty:
            return []

        folders = STYLE_FOLDER_MAP.get(
            str(style).strip(),
            []
        )

        if not folders:
            return []

        available = self.image_df[
            self.image_df["style"].isin(
                [
                    f.lower()
                    for f in folders
                ]
            )
        ].copy()

        if available.empty:
            return []

        test_images = available[
            available["split"] == "test"
        ]

        if len(test_images) >= max_images:
            available = test_images

        valid = []

        for _, row in available.iterrows():

            rel = str(
                row["image_path"]
            ).strip()

            if (
                rel
                and (
                    BASE_DIR / rel
                ).exists()
            ):

                valid.append(
                    {
                        "image_path": rel,
                        "style_folder":
                            row["style"],
                        "split":
                            row["split"],
                        "source":
                            "Kaggle style dataset",
                    }
                )

        if not valid:
            return []

        count = min(
            max_images,
            len(valid)
        )

        return random.sample(
            valid,
            count
        )

    # ========================================================
    # MAIN RECOMMENDER
    # ========================================================

    def recommend(
        self,
        room_type,
        style,
        budget,
        area,
        color,
        materials,
        top_n=6,
    ):

        room_type = str(
            room_type
        ).strip()

        style = str(
            style
        ).strip()

        color = str(
            color
        ).strip()

        materials = str(
            materials
        ).strip()

        # ----------------------------------------------------
        # Numeric inputs
        # ----------------------------------------------------

        try:
            budget = float(budget)
        except (
            TypeError,
            ValueError,
        ):
            budget = 5.0

        try:
            area = float(area)
        except (
            TypeError,
            ValueError,
        ):
            area = 200.0

        # ----------------------------------------------------
        # ROOM FILTER
        # ----------------------------------------------------

        room_df = self.df[
            self.df["room_type"]
            .str.lower()
            == room_type.lower()
        ].copy()

        if room_df.empty:
            room_df = self.df.copy()

        # ----------------------------------------------------
        # STYLE SCORE
        # ----------------------------------------------------

        requested_style = (
            style.lower()
        )

        room_df["style_score"] = (
            room_df["style"]
            .str.lower()
            .apply(
                lambda x:
                    1.0
                    if x == requested_style
                    else (
                        0.70
                        if requested_style in x
                        else 0.0
                    )
            )
        )

        # ----------------------------------------------------
        # BUDGET SCORE
        # ----------------------------------------------------

        room_df["budget_score"] = np.clip(
            1
            - abs(
                room_df["budget_lakh"]
                - budget
            )
            / max(budget, 0.5),
            0,
            1,
        )

        # ----------------------------------------------------
        # AREA SCORE
        # ----------------------------------------------------

        room_df["area_score"] = np.clip(
            1
            - abs(
                room_df["area_sqft"]
                - area
            )
            / max(area, 50),
            0,
            1,
        )

        # ----------------------------------------------------
        # COLOR SCORE
        # ----------------------------------------------------

        room_df["color_score"] = (
            room_df["color"]
            .apply(
                lambda x:
                    self._text_match(
                        x,
                        color
                    )
            )
        )

        # ----------------------------------------------------
        # MATERIAL SCORE
        # ----------------------------------------------------

        room_df["material_score"] = (
            room_df["materials"]
            .apply(
                lambda x:
                    self._text_match(
                        x,
                        materials
                    )
            )
        )

        # ----------------------------------------------------
        # FINAL MATCH SCORE
        # ----------------------------------------------------

        room_df["match_score"] = (
            0.55
            * room_df["style_score"]
            +
            0.20
            +
            0.10
            * room_df["budget_score"]
            +
            0.10
            * room_df["area_score"]
            +
            0.03
            * room_df["color_score"]
            +
            0.02
            * room_df["material_score"]
        )

        # ----------------------------------------------------
        # SORT
        # ----------------------------------------------------

        room_df = room_df.sort_values(
            [
                "match_score",
                "style_score",
                "budget_score",
                "area_score",
            ],
            ascending=False,
        ).head(top_n)

        # ====================================================
        # BUILD RECOMMENDATIONS
        # ====================================================

        recommendations = []

        for _, row in room_df.iterrows():

            item = row.to_dict()

            # Convert score to percentage
            item["match_score"] = round(
                float(
                    item["match_score"]
                )
                * 100,
                1,
            )

            # ------------------------------------------------
            # NEW DATASET:
            # ROOM + STYLE specific images
            # ------------------------------------------------

            room_images = (
                self.get_room_style_images(
                    room_type=room_type,
                    style=item["style"],
                    max_images=6,
                )
            )

            # ------------------------------------------------
            # OLD DATASET:
            # STYLE-only fallback
            # ------------------------------------------------

            old_style_images = []

            if not room_images:
                old_style_images = (
                    self.get_style_images(
                        item["style"],
                        max_images=6,
                    )
                )

            # Prefer the new room-specific dataset
            if room_images:

                item["images"] = room_images

                item["image_source"] = (
                    "Kaggle room + style dataset"
                )

                item["image_note"] = (
                    "Images are matched using "
                    "both room type and design style."
                )

            elif old_style_images:

                item["images"] = (
                    old_style_images
                )

                item["image_source"] = (
                    "Kaggle style dataset"
                )

                item["image_note"] = (
                    "Room-specific references "
                    "were unavailable, so a "
                    "style reference was used."
                )

            else:

                item["images"] = []

                item["image_source"] = (
                    "No reference images found"
                )

                item["image_note"] = (
                    "No matching reference "
                    "images were found."
                )

            recommendations.append(
                item
            )

        return recommendations
"""CasaCraft AI configuration."""
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
OUTPUT_DIR = BASE_DIR / "outputs"
for _p in (DATA_DIR, MODELS_DIR, OUTPUT_DIR): _p.mkdir(parents=True, exist_ok=True)
YOLO_MODEL = str(MODELS_DIR / "yolov8n.pt")
GENERATION_BACKEND = "diffusers"
DIFFUSION_MODEL = "runwayml/stable-diffusion-v1-5"
GENERATION_STRENGTH = 0.62
GENERATION_GUIDANCE = 7.5
GENERATION_STEPS = 30
GENERATION_MAX_SIZE = 512
APP_NAME = "CasaCraft AI"
APP_VERSION = "3.0"
DEFAULT_ROOM = "Bedroom"
DEFAULT_STYLE = "Modern Minimalist"
DEFAULT_BUDGET = 5.0
DEFAULT_AREA = 250
ROOM_TYPES = ["Bedroom", "Living Room", "Kitchen", "Bathroom"]
DESIGN_STYLES = ["Modern Minimalist", "Luxury Modern", "Japanese Japandi", "Contemporary", "Industrial", "Scandinavian", "Traditional", "Rustic", "Farmhouse", "Mediterranean", "Coastal", "Eclectic", "Mid-Century Modern"]
COLOR_PALETTES = ["Beige Ivory", "Taupe Gold", "Sand Olive", "Beige Cream", "Cream Gold", "Grey Walnut", "White Beige", "Champagne Ivory", "Grey White", "Travertine Gold"]
MATERIALS = ["Wood Laminate", "Fabric", "Wood Marble", "Oak Wood", "Fluted Panel", "Marble", "Veneer", "Brass", "Acrylic", "Quartz", "PU Finish", "Matte Laminate", "Porcelain", "Glass"]
LIGHTING_OPTIONS = ["Warm Cove LED", "Layered Warm Lighting", "Soft Warm Lighting", "Linear LED", "Under Cabinet LED", "Profile LED", "Pendant Lighting", "Chandelier", "Recessed LED", "Ambient Lighting"]
DATABASE_PATH = BASE_DIR / "casacraft.db"
PAGE_TITLE = "CasaCraft AI"
PAGE_ICON = "🏠"

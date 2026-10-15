# CasaCraft AI — 50% milestone package

This is a partial integration package based on the project files provided in this chat. It preserves the existing Streamlit app, recommender, generation module and 3D planner, and includes supporting config/database/detector/plan-analysis modules.

## Run on Windows (PowerShell)
1. Extract this folder. Open a terminal in the extracted `CasaCraft_AI_50_Percent_Project` folder.
2. `py -3.11 -m venv .venv`
3. `.\.venv\Scripts\Activate.ps1`
4. `python -m pip install --upgrade pip`
5. `pip install -r requirements.txt`
6. `python -m py_compile app.py config.py database.py detector.py plan_analyzer.py recommender.py generation.py three_d_planner.py`
7. `streamlit run app.py`

## Important scope notes
- This is a 50% milestone, not a verified final submission. Syntax compilation and recommender CSV initialization are the initial checks; full UI, detector, image generation and 3D browser testing depend on your machine and dependencies.
- AI image generation requires compatible PyTorch and Diffusers packages, model download/internet access, and substantial memory. It may be slow on CPU.
- YOLO requires the model weights at `models/yolov8n.pt` or a permitted download.
- The image CSV refers to dataset images in relative paths. The original image dataset files are not included in this ZIP, so reference image results may be empty until those images are placed at the expected paths.
- Do not copy this package over your original project without a backup.

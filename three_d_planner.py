import streamlit as st
import streamlit.components.v1 as components
import json


# ============================================================
# CASA CRAFT AI - INTERACTIVE 3D ROOM PLANNER
# ============================================================
# This version uses classic Three.js scripts instead of ES
# modules, which is more reliable inside Streamlit iframes.
# ============================================================


FURNITURE_LIBRARY = {
    "Sofa": {
        "type": "sofa",
        "width": 3.2,
        "depth": 1.0,
        "height": 0.85,
        "color": "#8d6e63",
    },
    "Bed": {
        "type": "bed",
        "width": 4.8,
        "depth": 6.4,
        "height": 0.65,
        "color": "#b59a7a",
    },
    "Wardrobe": {
        "type": "wardrobe",
        "width": 2.8,
        "depth": 0.7,
        "height": 2.5,
        "color": "#c7b299",
    },
    "TV Unit": {
        "type": "tv",
        "width": 3.5,
        "depth": 0.45,
        "height": 1.5,
        "color": "#6f503d",
    },
    "Coffee Table": {
        "type": "coffee_table",
        "width": 2.0,
        "depth": 1.1,
        "height": 0.45,
        "color": "#8d6e63",
    },
    "Dining Table": {
        "type": "dining",
        "width": 3.5,
        "depth": 2.0,
        "height": 0.8,
        "color": "#a98262",
    },
    "Kitchen Island": {
        "type": "island",
        "width": 3.0,
        "depth": 1.5,
        "height": 0.9,
        "color": "#d4c2ad",
    },
    "Tall Unit": {
        "type": "tall",
        "width": 1.2,
        "depth": 0.65,
        "height": 2.6,
        "color": "#9b7b63",
    },
    "Vanity": {
        "type": "vanity",
        "width": 1.8,
        "depth": 0.65,
        "height": 0.85,
        "color": "#d6c6b7",
    },
    "Shower": {
        "type": "shower",
        "width": 1.5,
        "depth": 1.5,
        "height": 2.2,
        "color": "#9ec5c9",
    },
    "Bathtub": {
        "type": "bathtub",
        "width": 2.3,
        "depth": 1.0,
        "height": 0.6,
        "color": "#eeeeee",
    },
}


def furniture_payload(selected_furniture):
    """Convert selected furniture names into JSON-safe objects."""
    return [
        {
            **FURNITURE_LIBRARY[name],
            "name": name,
        }
        for name in selected_furniture
        if name in FURNITURE_LIBRARY
    ]


def render_3d_room(
    width_ft=12,
    length_ft=16,
    selected_furniture=None,
    wall_color="#e8ded3",
    floor_color="#b59a7a",
    accent_color="#8d6e63",
):
    """
    Render an interactive 3D room inside Streamlit.

    No extra Python 3D package is required.
    Three.js and OrbitControls are loaded in the browser.
    """

    selected_furniture = selected_furniture or []

    furniture_data = furniture_payload(selected_furniture)
    furniture_json = json.dumps(furniture_data)

    html = f"""
<!DOCTYPE html>
<html lang="en">

<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0"
>

<title>CasaCraft AI 3D Room</title>

<style>

html,
body {{
    margin: 0;
    padding: 0;

    width: 100%;
    height: 100%;

    overflow: hidden;

    background: #171311;

    font-family:
        Arial,
        Helvetica,
        sans-serif;
}}

#scene {{
    position: relative;

    width: 100%;
    height: 100vh;

    overflow: hidden;
}}

canvas {{
    display: block;
}}

#loading {{
    position: absolute;

    inset: 0;

    z-index: 100;

    display: flex;

    align-items: center;

    justify-content: center;

    background: #171311;

    color: #ffffff;

    font-size: 17px;

    font-weight: 600;
}}

#info {{
    position: absolute;

    top: 16px;
    left: 16px;

    z-index: 20;

    padding: 14px 18px;

    border-radius: 15px;

    background:
        rgba(38, 29, 25, 0.92);

    color: #ffffff;

    box-shadow:
        0 8px 28px
        rgba(0, 0, 0, 0.35);

    backdrop-filter: blur(10px);
}}

#info .title {{
    font-size: 18px;

    font-weight: 700;

    margin-bottom: 5px;
}}

#info .sub {{
    font-size: 12px;

    color: #e8ded3;
}}

#toolbar {{
    position: absolute;
    right: 16px;
    top: 16px;
    z-index: 30;
    display: flex;
    gap: 7px;
    align-items: center;
    padding: 9px;
    border-radius: 14px;
    background: rgba(38, 29, 25, 0.92);
    box-shadow: 0 8px 25px rgba(0,0,0,.28);
}}

#toolbar button {{
    border: 0;
    border-radius: 9px;
    padding: 8px 11px;
    background: #6f503d;
    color: #fff;
    cursor: pointer;
    font-size: 12px;
}}

#toolbar button:hover {{
    background: #8d6e63;
}}

#selectedName {{
    color: #f5e9dc;
    font-size: 12px;
    min-width: 110px;
    text-align: center;
}}

#addPanel {{
    position: absolute;
    top: 16px;
    right: 16px;
    z-index: 30;
    display: flex;
    gap: 7px;
    align-items: center;
    padding: 10px;
    border-radius: 14px;
    background: rgba(38, 29, 25, 0.92);
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.35);
}}

#addFurniture {{
    border: 0;
    border-radius: 9px;
    padding: 8px 11px;
    background: #8d6e63;
    color: #fff;
    cursor: pointer;
    font-size: 12px;
    font-weight: 600;
}}

#addFurniture:hover {{
    background: #a98262;
}}

#furnitureType {{
    border: 1px solid #7f6b5c;
    border-radius: 9px;
    padding: 7px 9px;
    background: #241c18;
    color: #fff;
    font-size: 12px;
    outline: none;
}}

#countLabel {{
    color: #e8ded3;
    font-size: 11px;
    white-space: nowrap;
}}

#viewPanel {{
    position: absolute;
    top: 94px;
    right: 16px;
    z-index: 25;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 10px;
    border-radius: 13px;
    background: rgba(38, 29, 25, 0.88);
    box-shadow: 0 8px 24px rgba(0,0,0,0.25);
    backdrop-filter: blur(10px);
}}

.viewLabel {{
    color: #eadbcf;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-right: 2px;
}}

#viewPanel button {{
    border: 0;
    border-radius: 9px;
    padding: 7px 10px;
    background: #6f4d3b;
    color: #fff;
    font-weight: 600;
    cursor: pointer;
}}

#viewPanel button:hover {{
    background: #8a624c;
}}

#hint {{
    position: absolute;

    left: 50%;
    bottom: 16px;

    transform: translateX(-50%);

    z-index: 20;

    padding: 9px 16px;

    border-radius: 22px;

    background:
        rgba(38, 29, 25, 0.90);

    color: #ffffff;

    font-size: 12px;

    white-space: nowrap;

    box-shadow:
        0 6px 20px
        rgba(0, 0, 0, 0.25);
}}

#error {{
    display: none;

    position: absolute;

    left: 50%;
    top: 50%;

    transform: translate(-50%, -50%);

    z-index: 200;

    width: min(620px, 82%);

    padding: 24px;

    border-radius: 16px;

    background: #2d211d;

    color: #ffffff;

    text-align: center;

    box-shadow:
        0 15px 50px
        rgba(0, 0, 0, 0.5);
}}

#error b {{
    color: #ffd8a8;
}}

#errorText {{
    color: #e8ded3;

    font-size: 12px;

    word-break: break-word;
}}

</style>

</head>


<body>

<div id="scene">

    <div id="loading">
        Loading CasaCraft 3D Room...
    </div>

    <div id="error">

        <b>3D engine could not load.</b>

        <br><br>

        <span id="errorText">
            Three.js could not be loaded.
        </span>

        <br><br>

        <small>
            Check your internet connection and refresh the page.
        </small>

    </div>


    <div id="info">

        <div class="title">
            CasaCraft AI • Interactive 3D Room
        </div>

        <div class="sub">
            Room: {float(width_ft):g} ft × {float(length_ft):g} ft
            &nbsp; | &nbsp;
            Furniture: {len(selected_furniture)}
        </div>

    </div>


    <div id="toolbar">
        <span id="selectedName">Select furniture</span>
        <button id="scaleDown" type="button">− Size</button>
        <button id="scaleUp" type="button">＋ Size</button>
        <button id="rotateLeft" type="button">↶ Rotate</button>
        <button id="deleteItem" type="button">🗑 Delete</button>
        <button id="undoButton" type="button">↩ Undo</button>
        <button id="redoButton" type="button">↪ Redo</button>
        <button id="saveButton" type="button">💾 Save</button>
        <button id="resetButton" type="button">⟳ Reset</button>
        <button id="clearSelection" type="button">✕</button>
    </div>

    <div id="viewPanel">
        <span class="viewLabel">View</span>
        <button id="perspectiveView" type="button">Perspective</button>
        <button id="topView" type="button">Top</button>
        <button id="frontView" type="button">Front</button>
        <button id="presentationView" type="button">✨ Presentation</button>
    </div>

    <div id="addPanel">
        <select id="furnitureType">
            <option value="Sofa">Sofa</option>
            <option value="Bed">Bed</option>
            <option value="Wardrobe">Wardrobe</option>
            <option value="TV Unit">TV Unit</option>
            <option value="Coffee Table">Coffee Table</option>
            <option value="Dining Table">Dining Table</option>
            <option value="Kitchen Island">Kitchen Island</option>
            <option value="Tall Unit">Tall Unit</option>
            <option value="Vanity">Vanity</option>
            <option value="Shower">Shower</option>
            <option value="Bathtub">Bathtub</option>
        </select>
        <button id="addFurniture" type="button">＋ Add</button>
        <span id="countLabel">{len(selected_furniture)} items</span>
    </div>

    <div id="hint">
        🖱️ Click furniture to select • Drag selected furniture to move
        &nbsp; • &nbsp; Use Rotate / Delete
    </div>

</div>


<!-- ========================================================
     THREE.JS
     Classic scripts are intentionally used here.
     This avoids ES-module problems inside Streamlit.
     ======================================================== -->

<script
    src="https://cdn.jsdelivr.net/npm/three@0.128.0/build/three.min.js">
</script>

<script
    src="https://cdn.jsdelivr.net/npm/three@0.128.0/examples/js/controls/OrbitControls.js">
</script>


<script>

(function() {{

    "use strict";


    const loading =
        document.getElementById("loading");

    const errorBox =
        document.getElementById("error");

    const errorText =
        document.getElementById("errorText");


    function showError(message) {{

        loading.style.display =
            "none";

        errorBox.style.display =
            "block";

        errorText.textContent =
            message ||
            "Three.js could not be loaded.";

    }}


    try {{

        /* ====================================================
           CHECK THREE.JS
           ==================================================== */

        if (typeof THREE === "undefined") {{

            showError(
                "THREE is undefined. " +
                "The Three.js CDN could not be reached."
            );

            return;
        }}


        if (
            typeof THREE.OrbitControls ===
            "undefined"
        ) {{

            showError(
                "OrbitControls did not load. " +
                "Refresh the page and try again."
            );

            return;
        }}


        /* ====================================================
           MAIN SETTINGS
           ==================================================== */

        const container =
            document.getElementById("scene");


        const ROOM_WIDTH =
            {float(width_ft)};


        const ROOM_LENGTH =
            {float(length_ft)};


        const SCALE =
            2.0;


        const roomWidth =
            ROOM_WIDTH * SCALE;


        const roomLength =
            ROOM_LENGTH * SCALE;


        const wallHeight =
            5.5;


        const wallColor =
            "{wall_color}";


        const floorColor =
            "{floor_color}";


        const accentColor =
            "{accent_color}";


        const furnitureData =
            {furniture_json};


        /* ====================================================
           SCENE
           ==================================================== */

        const scene =
            new THREE.Scene();


        scene.background =
            new THREE.Color("#171311");


        /* ====================================================
           CAMERA
           ==================================================== */

        const camera =
            new THREE.PerspectiveCamera(
                45,
                window.innerWidth /
                    window.innerHeight,
                0.1,
                500
            );


        camera.position.set(
            roomWidth * 0.78,
            wallHeight * 0.72,
            roomLength * 0.82
        );


        /* ====================================================
           RENDERER
           ==================================================== */

        const renderer =
            new THREE.WebGLRenderer({{
                antialias: true
            }});


        renderer.setPixelRatio(
            Math.min(
                window.devicePixelRatio || 1,
                2
            )
        );


        renderer.setSize(
            window.innerWidth,
            window.innerHeight
        );


        renderer.shadowMap.enabled =
            true;


        renderer.shadowMap.type =
            THREE.PCFSoftShadowMap;

        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 0.82;
        renderer.outputEncoding = THREE.sRGBEncoding;


        container.appendChild(
            renderer.domElement
        );


        /* ====================================================
           CONTROLS
           ==================================================== */

        const controls =
            new THREE.OrbitControls(
                camera,
                renderer.domElement
            );


        controls.enableDamping =
            true;


        controls.dampingFactor =
            0.06;


        controls.minDistance =
            4;


        controls.maxDistance =
            70;


        controls.maxPolarAngle =
            Math.PI / 2.05;


        controls.target.set(
            0,
            1.35,
            0
        );


        /* ====================================================
           LIGHTING
           ==================================================== */

        const ambient =
            new THREE.HemisphereLight(
                "#fff8ed",
                "#55463d",
                0.55
            );


        scene.add(
            ambient
        );


        const mainLight =
            new THREE.DirectionalLight(
                "#fff4df",
                1.0
            );


        mainLight.position.set(
            4,
            10,
            5
        );


        mainLight.castShadow =
            true;


        mainLight.shadow.mapSize.width =
            2048;


        mainLight.shadow.mapSize.height =
            2048;


        scene.add(
            mainLight
        );


        const fillLight =
            new THREE.PointLight(
                "#fff1dc",
                0.22,
                40
            );


        fillLight.position.set(
            -4,
            4,
            -4
        );


        scene.add(
            fillLight
        );


        /* ====================================================
           MATERIAL
           ==================================================== */

        function material(
            color,
            roughness,
            metalness
        ) {{

            if (
                roughness === undefined
            ) {{
                roughness = 0.55;
            }}


            if (
                metalness === undefined
            ) {{
                metalness = 0.05;
            }}


            return new THREE.MeshStandardMaterial({{
                color: color,
                roughness: roughness,
                metalness: metalness
            }});

        }}


        /* ====================================================
           BOX
           ==================================================== */

        let currentFurnitureId = null;

        function box(
            width,
            height,
            depth,
            color,
            x,
            y,
            z
        ) {{

            const geometry =
                new THREE.BoxGeometry(
                    width,
                    height,
                    depth
                );


            const mesh =
                new THREE.Mesh(
                    geometry,
                    material(color)
                );


            mesh.position.set(
                x,
                y,
                z
            );


            mesh.castShadow =
                true;


            mesh.receiveShadow =
                true;


            if (currentFurnitureId !== null) {{
                mesh.userData.furnitureId = currentFurnitureId;
            }}


            scene.add(
                mesh
            );


            return mesh;

        }}


        /* ====================================================
           FLOOR
           ==================================================== */

        box(
            roomWidth,
            0.15,
            roomLength,
            floorColor,
            0,
            -0.075,
            0
        );


        /* ====================================================
           FLOOR BORDER
           ==================================================== */

        const floorBorder =
            new THREE.LineSegments(
                new THREE.EdgesGeometry(
                    new THREE.BoxGeometry(
                        roomWidth,
                        0.15,
                        roomLength
                    )
                ),
                new THREE.LineBasicMaterial({{
                    color: "#6f5a49"
                }})
            );


        floorBorder.position.y =
            0;


        scene.add(
            floorBorder
        );

        // Subtle floor plank/tile seams for a more architectural visualization.
        const seamMaterial = new THREE.MeshStandardMaterial({{
            color: "#8d725b",
            roughness: 0.9,
            metalness: 0
        }});
        const seamCountX = Math.max(2, Math.round(ROOM_WIDTH / 2));
        const seamCountZ = Math.max(2, Math.round(ROOM_LENGTH / 2));
        for (let i = 1; i < seamCountX; i++) {{
            const x = -roomWidth / 2 + (roomWidth * i / seamCountX);
            const seam = new THREE.Mesh(new THREE.BoxGeometry(0.018, 0.006, roomLength), seamMaterial);
            seam.position.set(x, 0.006, 0);
            scene.add(seam);
        }}
        for (let i = 1; i < seamCountZ; i++) {{
            const z = -roomLength / 2 + (roomLength * i / seamCountZ);
            const seam = new THREE.Mesh(new THREE.BoxGeometry(roomWidth, 0.006, 0.018), seamMaterial);
            seam.position.set(0, 0.007, z);
            scene.add(seam);
        }}


        /* ====================================================
           WALLS
           ==================================================== */

        const wallThickness =
            0.18;


        // Back wall

        box(
            roomWidth,
            wallHeight,
            wallThickness,
            wallColor,
            0,
            wallHeight / 2,
            -roomLength / 2
        );


        // Left wall

        box(
            wallThickness,
            wallHeight,
            roomLength,
            wallColor,
            -roomWidth / 2,
            wallHeight / 2,
            0
        );


        // Right wall

        box(
            wallThickness,
            wallHeight,
            roomLength,
            wallColor,
            roomWidth / 2,
            wallHeight / 2,
            0
        );

        // Minimal skirting and warm cove-light strips.
        const trimColor = "#d3c4b5";
        box(roomWidth, 0.12, 0.08, trimColor, 0, 0.06, -roomLength / 2 + 0.11);
        box(0.08, 0.12, roomLength, trimColor, -roomWidth / 2 + 0.11, 0.06, 0);
        box(0.08, 0.12, roomLength, trimColor, roomWidth / 2 - 0.11, 0.06, 0);

        const coveColor = new THREE.MeshStandardMaterial({{
            color: "#f4d3a1",
            emissive: "#f4b86a",
            emissiveIntensity: 0.7,
            roughness: 0.35
        }});
        const coveBack = new THREE.Mesh(new THREE.BoxGeometry(roomWidth - 0.25, 0.05, 0.08), coveColor);
        coveBack.position.set(0, wallHeight - 0.12, -roomLength / 2 + 0.15);
        scene.add(coveBack);
        const coveLeft = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.05, roomLength - 0.25), coveColor);
        coveLeft.position.set(-roomWidth / 2 + 0.15, wallHeight - 0.12, 0);
        scene.add(coveLeft);
        const coveLight = new THREE.PointLight("#ffd39a", 0.55, Math.max(roomWidth, roomLength) * 1.8);
        coveLight.position.set(0, wallHeight - 0.35, -roomLength / 2 + 0.45);
        scene.add(coveLight);


        /* ====================================================
           WINDOW
           ==================================================== */

        function createWindow() {{

            const windowWidth =
                Math.min(
                    roomWidth * 0.45,
                    5.5
                );


            const windowHeight =
                2.6;


            const windowZ =
                -roomLength / 2 + 0.13;


            const glass =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        windowWidth,
                        windowHeight,
                        0.06
                    ),
                    new THREE.MeshStandardMaterial({{
                        color: "#9cc9d7",
                        transparent: true,
                        opacity: 0.55,
                        roughness: 0.15,
                        metalness: 0.05
                    }})
                );


            glass.position.set(
                0,
                3.0,
                windowZ
            );


            scene.add(
                glass
            );


            const frameColor =
                "#6c5848";


            box(
                0.10,
                windowHeight,
                0.10,
                frameColor,
                -windowWidth / 2,
                3.0,
                windowZ
            );


            box(
                0.10,
                windowHeight,
                0.10,
                frameColor,
                windowWidth / 2,
                3.0,
                windowZ
            );


            box(
                windowWidth,
                0.10,
                0.10,
                frameColor,
                0,
                3.0 -
                    windowHeight / 2,
                windowZ
            );


            box(
                windowWidth,
                0.10,
                0.10,
                frameColor,
                0,
                3.0 +
                    windowHeight / 2,
                windowZ
            );


            box(
                0.07,
                windowHeight,
                0.08,
                frameColor,
                0,
                3.0,
                windowZ + 0.02
            );

        }}


        createWindow();


        /* ====================================================
           ARCHITECTURAL PRESENTATION LAYER
           ==================================================== */

        // A light ceiling tray gives the room a more realistic interior
        // presentation without blocking the camera view.
        const ceilingTrim = new THREE.MeshStandardMaterial({{
            color: "#f4eee7",
            roughness: 0.72,
            metalness: 0.02
        }});

        const trayY = wallHeight - 0.06;
        const trayDepth = 0.18;
        const trayOffset = 0.28;

        [
            [roomWidth - 0.5, trayDepth, trayOffset, 0, trayY, -roomLength / 2 + trayOffset],
            [roomWidth - 0.5, trayDepth, trayOffset, 0, trayY, roomLength / 2 - trayOffset],
            [trayOffset, trayDepth, roomLength - 0.5, -roomWidth / 2 + trayOffset, trayY, 0],
            [trayOffset, trayDepth, roomLength - 0.5, roomWidth / 2 - trayOffset, trayY, 0]
        ].forEach(function(spec) {{
            const trim = new THREE.Mesh(
                new THREE.BoxGeometry(spec[0], spec[1], spec[2]),
                ceilingTrim
            );
            trim.position.set(spec[3], spec[4], spec[5]);
            trim.castShadow = true;
            trim.receiveShadow = true;
            scene.add(trim);
        }});

        // Recessed downlights for a cleaner architectural visualization.
        const lightPositions = [
            [-roomWidth * 0.30, -roomLength * 0.22],
            [ roomWidth * 0.30, -roomLength * 0.22],
            [-roomWidth * 0.30,  roomLength * 0.22],
            [ roomWidth * 0.30,  roomLength * 0.22]
        ];

        lightPositions.forEach(function(pos) {{
            const disc = new THREE.Mesh(
                new THREE.CylinderGeometry(0.16, 0.16, 0.035, 24),
                new THREE.MeshStandardMaterial({{
                    color: "#fffaf2",
                    emissive: "#ffd9a3",
                    emissiveIntensity: 0.9,
                    roughness: 0.25
                }})
            );
            disc.position.set(pos[0], wallHeight - 0.12, pos[1]);
            scene.add(disc);

            const downLight = new THREE.PointLight("#ffe4bd", 0.32, 10);
            downLight.position.set(pos[0], wallHeight - 0.25, pos[1]);
            scene.add(downLight);
        }});

        // Simple architectural door on the right wall.
        const doorW = Math.min(3.0, roomWidth * 0.24);
        const doorH = 6.8;
        const doorZ = Math.min(roomLength * 0.22, 3.0);
        const doorX = roomWidth / 2 - 0.11;

        box(doorW, doorH, 0.06, "#8b6a50", doorX, doorH / 2, doorZ);
        box(0.09, doorH + 0.12, 0.08, "#5c4638", doorX, doorH / 2, doorZ - doorW / 2);
        box(0.09, doorH + 0.12, 0.08, "#5c4638", doorX, doorH / 2, doorZ + doorW / 2);
        box(0.08, 0.08, 0.08, "#d5b06e", doorX - 0.08, 3.15, doorZ - 0.55);


        /* ====================================================
           RUG
           ==================================================== */

        const rug =
            new THREE.Mesh(
                new THREE.BoxGeometry(
                    Math.min(
                        roomWidth * 0.55,
                        5.5
                    ),
                    0.025,
                    Math.min(
                        roomLength * 0.30,
                        4.5
                    )
                ),
                material(
                    "#cbb8a2",
                    0.95,
                    0
                )
            );


        rug.position.set(
            0,
            0.02,
            1.5
        );


        rug.receiveShadow =
            true;


        scene.add(
            rug
        );


        /* ====================================================
           PLANT
           ==================================================== */

        function createPlant(
            x,
            z
        ) {{

            const pot =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.35,
                        0.28,
                        0.6,
                        24
                    ),
                    material(
                        "#b58e70"
                    )
                );


            pot.position.set(
                x,
                0.3,
                z
            );


            pot.castShadow =
                true;


            scene.add(
                pot
            );


            for (
                let i = 0;
                i < 8;
                i++
            ) {{

                const leaf =
                    new THREE.Mesh(
                        new THREE.SphereGeometry(
                            0.30,
                            12,
                            12
                        ),
                        material(
                            "#64785d",
                            0.8,
                            0
                        )
                    );


                const angle =
                    i / 8 *
                    Math.PI *
                    2;


                leaf.scale.set(
                    0.55,
                    1.4,
                    0.35
                );


                leaf.position.set(
                    x +
                        Math.cos(angle) *
                        0.35,
                    1.0 +
                        (i % 2) *
                        0.2,
                    z +
                        Math.sin(angle) *
                        0.35
                );


                leaf.castShadow =
                    true;


                scene.add(
                    leaf
                );

            }}

        }}


        createPlant(
            roomWidth / 2 - 0.8,
            -roomLength / 2 + 1
        );


        /* ====================================================
           SOFA
           ==================================================== */

        function createSofa(
            x,
            z,
            color
        ) {{

            box(3.2, 0.42, 1.0, color, x, 0.48, z);
            box(3.2, 1.05, 0.28, color, x, 1.05, z - 0.36);
            box(0.28, 0.75, 1.0, color, x - 1.46, 0.70, z);
            box(0.28, 0.75, 1.0, color, x + 1.46, 0.70, z);

            // Cushions
            const cushionMat = material("#d8c6b3", 0.88, 0);
            [-0.95, 0, 0.95].forEach(function(dx) {{
                const cushion = new THREE.Mesh(new THREE.BoxGeometry(0.78, 0.55, 0.18), cushionMat);
                cushion.position.set(x + dx, 1.12, z - 0.20);
                cushion.rotation.x = -0.10;
                cushion.castShadow = true;
                cushion.userData.furnitureId = currentFurnitureId;
                scene.add(cushion);
            }});

            // Slim legs
            [-1.25, 1.25].forEach(function(dx) {{
                box(0.10, 0.18, 0.10, "#5a4638", x + dx, 0.09, z - 0.34);
                box(0.10, 0.18, 0.10, "#5a4638", x + dx, 0.09, z + 0.34);
            }});

        }}


        /* ====================================================
           BED
           ==================================================== */

        function createBed(
            x,
            z,
            color
        ) {{

            box(
                4.8,
                0.45,
                6.4,
                color,
                x,
                0.35,
                z
            );


            box(
                4.5,
                0.38,
                6.0,
                "#eee6dc",
                x,
                0.77,
                z
            );


            box(
                4.8,
                2.2,
                0.25,
                color,
                x,
                1.35,
                z - 3.0
            );

            const pillowMat = material("#f5eee5", 0.92, 0);
            [-1.15, 1.15].forEach(function(dx) {{
                const pillow = new THREE.Mesh(new THREE.BoxGeometry(1.65, 0.22, 0.72), pillowMat);
                pillow.position.set(x + dx, 0.98, z - 1.95);
                pillow.castShadow = true;
                pillow.userData.furnitureId = currentFurnitureId;
                scene.add(pillow);
            }});

            box(4.5, 0.05, 1.05, "#c7ad93", x, 0.99, z + 1.15);

        }}


        /* ====================================================
           WARDROBE
           ==================================================== */

        function createWardrobe(
            x,
            z,
            color
        ) {{

            box(
                2.8,
                2.5,
                0.7,
                color,
                x,
                1.25,
                z
            );


            for (
                let i = 0;
                i < 3;
                i++
            ) {{

                box(
                    0.88,
                    2.25,
                    0.04,
                    i === 1
                        ? "#b99e84"
                        : "#d3c0aa",
                    x -
                        0.92 +
                        i * 0.92,
                    1.25,
                    z - 0.38
                );

                box(0.04, 0.22, 0.05, "#b18a62", x - 0.92 + i * 0.92, 1.25, z - 0.42);
            }}

        }}


        /* ====================================================
           TV UNIT
           ==================================================== */

        function createTV(
            x,
            z,
            color
        ) {{

            box(
                3.5,
                0.45,
                0.45,
                color,
                x,
                0.35,
                z
            );


            box(
                3.0,
                1.75,
                0.12,
                "#111111",
                x,
                1.45,
                z
            );


            box(
                2.75,
                1.50,
                0.02,
                "#252525",
                x,
                1.45,
                z - 0.08
            );

        }}


        /* ====================================================
           COFFEE TABLE
           ==================================================== */

        function createCoffeeTable(
            x,
            z,
            color
        ) {{

            box(
                2.0,
                0.18,
                1.1,
                color,
                x,
                0.48,
                z
            );


            const legs = [
                [-0.75, -0.35],
                [ 0.75, -0.35],
                [-0.75,  0.35],
                [ 0.75,  0.35]
            ];


            legs.forEach(
                function(p) {{

                    box(
                        0.10,
                        0.45,
                        0.10,
                        "#5e4638",
                        x + p[0],
                        0.24,
                        z + p[1]
                    );

                }}
            );

        }}


        /* ====================================================
           DINING TABLE
           ==================================================== */

        function createDining(
            x,
            z,
            color
        ) {{

            box(
                3.5,
                0.16,
                2.0,
                color,
                x,
                0.82,
                z
            );


            const legs = [
                [-1.35, -0.65],
                [ 1.35, -0.65],
                [-1.35,  0.65],
                [ 1.35,  0.65]
            ];


            legs.forEach(
                function(p) {{

                    box(
                        0.15,
                        0.82,
                        0.15,
                        "#5d4738",
                        x + p[0],
                        0.41,
                        z + p[1]
                    );

                }}
            );

        }}


        /* ====================================================
           KITCHEN ISLAND
           ==================================================== */

        function createIsland(
            x,
            z,
            color
        ) {{

            box(
                3.0,
                0.9,
                1.5,
                color,
                x,
                0.45,
                z
            );


            box(
                3.15,
                0.10,
                1.65,
                "#eeeeea",
                x,
                0.94,
                z
            );

        }}


        /* ====================================================
           TALL UNIT
           ==================================================== */

        function createTall(
            x,
            z,
            color
        ) {{

            box(
                1.2,
                2.6,
                0.65,
                color,
                x,
                1.3,
                z
            );

        }}


        /* ====================================================
           VANITY
           ==================================================== */

        function createVanity(
            x,
            z,
            color
        ) {{

            box(
                1.8,
                0.85,
                0.65,
                color,
                x,
                0.43,
                z
            );


            box(
                1.5,
                1.5,
                0.08,
                "#dce8e7",
                x,
                1.55,
                z - 0.30
            );

        }}


        /* ====================================================
           SHOWER
           ==================================================== */

        function createShower(
            x,
            z,
            color
        ) {{

            const glass =
                new THREE.Mesh(
                    new THREE.BoxGeometry(
                        1.5,
                        2.2,
                        0.06
                    ),
                    new THREE.MeshStandardMaterial({{
                        color: color,
                        transparent: true,
                        opacity: 0.35,
                        roughness: 0.1
                    }})
                );


            glass.position.set(
                x,
                1.1,
                z
            );


            scene.add(
                glass
            );


            box(
                1.5,
                0.08,
                1.5,
                "#eeeeee",
                x,
                0.04,
                z
            );

        }}


        /* ====================================================
           BATHTUB
           ==================================================== */

        function createBathtub(
            x,
            z,
            color
        ) {{

            box(
                2.3,
                0.6,
                1.0,
                color,
                x,
                0.30,
                z
            );


            box(
                1.8,
                0.10,
                0.65,
                "#ffffff",
                x,
                0.60,
                z
            );

        }}


        /* ====================================================
           PLACE SELECTED FURNITURE
           ==================================================== */

        let furnitureIndex =
            0;


        furnitureData.forEach(
            function(item) {{

                currentFurnitureId =
                    (item.name || item.type) +
                    "_" +
                    (furnitureIndex + 1);

                const x =
                    -roomWidth / 2 +
                    2.0 +
                    (furnitureIndex % 3) *
                    3.2;


                const z =
                    -roomLength / 2 +
                    2.0 +
                    Math.floor(
                        furnitureIndex / 3
                    ) *
                    3.4;


                const color =
                    item.color ||
                    accentColor;


                switch(item.type) {{

                    case "sofa":

                        createSofa(
                            x,
                            z,
                            color
                        );

                        break;


                    case "bed":

                        createBed(
                            x,
                            z,
                            color
                        );

                        break;


                    case "wardrobe":

                        createWardrobe(
                            x,
                            z,
                            color
                        );

                        break;


                    case "tv":

                        createTV(
                            x,
                            z,
                            color
                        );

                        break;


                    case "coffee_table":

                        createCoffeeTable(
                            x,
                            z,
                            color
                        );

                        break;


                    case "dining":

                        createDining(
                            x,
                            z,
                            color
                        );

                        break;


                    case "island":

                        createIsland(
                            x,
                            z,
                            color
                        );

                        break;


                    case "tall":

                        createTall(
                            x,
                            z,
                            color
                        );

                        break;


                    case "vanity":

                        createVanity(
                            x,
                            z,
                            color
                        );

                        break;


                    case "shower":

                        createShower(
                            x,
                            z,
                            color
                        );

                        break;


                    case "bathtub":

                        createBathtub(
                            x,
                            z,
                            color
                        );

                        break;

                }}


                furnitureIndex++;

            }}
        );


        /* ====================================================
           CEILING LIGHTS
           ==================================================== */

        function createCeilingLight(
            x,
            z
        ) {{

            const fixture =
                new THREE.Mesh(
                    new THREE.CylinderGeometry(
                        0.18,
                        0.18,
                        0.08,
                        24
                    ),
                    material(
                        "#f7eee0",
                        0.25,
                        0.1
                    )
                );


            fixture.position.set(
                x,
                wallHeight - 0.08,
                z
            );


            scene.add(
                fixture
            );


            const light =
                new THREE.PointLight(
                    "#fff0d0",
                    0.45,
                    10
                );


            light.position.set(
                x,
                wallHeight - 0.20,
                z
            );


            scene.add(
                light
            );

        }}


        createCeilingLight(
            -roomWidth * 0.25,
            -roomLength * 0.20
        );


        createCeilingLight(
            roomWidth * 0.25,
            -roomLength * 0.20
        );


        createCeilingLight(
            -roomWidth * 0.25,
            roomLength * 0.25
        );


        createCeilingLight(
            roomWidth * 0.25,
            roomLength * 0.25
        );


        /* ====================================================
           GRID
           ==================================================== */

        const grid =
            new THREE.GridHelper(
                Math.max(
                    roomWidth,
                    roomLength
                ),
                Math.round(
                    Math.max(
                        roomWidth,
                        roomLength
                    )
                ),
                "#8a7667",
                "#6a594d"
            );


        grid.position.y =
            0.012;


        grid.material.transparent =
            true;


        grid.material.opacity =
            0.0;


        scene.add(
            grid
        );


        /* ====================================================
           CAMERA TARGET
           ==================================================== */

        controls.target.set(
            0,
            1.1,
            0
        );


        controls.update();


        /* ====================================================
           FURNITURE INTERACTION
           ==================================================== */

        const raycaster =
            new THREE.Raycaster();

        const mouse =
            new THREE.Vector2();

        const dragPlane =
            new THREE.Plane(
                new THREE.Vector3(0, 1, 0),
                0
            );

        const dragPoint =
            new THREE.Vector3();

        let selectedFurnitureId = null;
        let isDraggingFurniture = false;
        let selectionHelper = null;

        const selectedName =
            document.getElementById("selectedName");

        const rotateButton =
            document.getElementById("rotateLeft");

        const scaleDownButton =
            document.getElementById("scaleDown");

        const scaleUpButton =
            document.getElementById("scaleUp");

        const deleteButton =
            document.getElementById("deleteItem");

        const clearButton =
            document.getElementById("clearSelection");

        const undoButton =
            document.getElementById("undoButton");

        const redoButton =
            document.getElementById("redoButton");

        const saveButton =
            document.getElementById("saveButton");

        const resetButton =
            document.getElementById("resetButton");

        const furnitureType =
            document.getElementById("furnitureType");

        const addFurnitureButton =
            document.getElementById("addFurniture");

        const countLabel =
            document.getElementById("countLabel");

        const perspectiveView = document.getElementById("perspectiveView");
        const topView = document.getElementById("topView");
        const frontView = document.getElementById("frontView");

        let dynamicFurnitureIndex =
            furnitureIndex;

        function updateFurnitureCount() {{
            const ids = [];
            scene.children.forEach(function(obj) {{
                if (obj.userData && obj.userData.furnitureId) {{
                    if (ids.indexOf(obj.userData.furnitureId) === -1) {{
                        ids.push(obj.userData.furnitureId);
                    }}
                }}
            }});
            countLabel.textContent = ids.length + " items";
        }}

        function furnitureObjects(id) {{
            return scene.children.filter(function(obj) {{
                return obj.userData &&
                    obj.userData.furnitureId === id;
            }});
        }}
\n        /* ====================================================\n           SAVE / UNDO / REDO SYSTEM\n           ==================================================== */\n\n        let historyStack = [];\n        let redoStack = [];\n        let dragStartSnapshot = null;\n        let dragHistoryAdded = false;\n        let savedLayout = null;\n\n        function furnitureTypeFromName(name) {{\n            const typeMap = {{\n                "Sofa": "sofa",\n                "Bed": "bed",\n                "Wardrobe": "wardrobe",\n                "TV Unit": "tv",\n                "Coffee Table": "coffee_table",\n                "Dining Table": "dining",\n                "Kitchen Island": "island",\n                "Tall Unit": "tall",\n                "Vanity": "vanity",\n                "Shower": "shower",\n                "Bathtub": "bathtub"\n            }};\n            return typeMap[name] || null;\n        }}\n\n        function createFurnitureByName(name, x, z, color) {{\n            const type = furnitureTypeFromName(name);\n            if (!type) return;\n\n            switch(type) {{\n                case "sofa": createSofa(x,z,color); break;\n                case "bed": createBed(x,z,color); break;\n                case "wardrobe": createWardrobe(x,z,color); break;\n                case "tv": createTV(x,z,color); break;\n                case "coffee_table": createCoffeeTable(x,z,color); break;\n                case "dining": createDining(x,z,color); break;\n                case "island": createIsland(x,z,color); break;\n                case "tall": createTall(x,z,color); break;\n                case "vanity": createVanity(x,z,color); break;\n                case "shower": createShower(x,z,color); break;\n                case "bathtub": createBathtub(x,z,color); break;\n            }}\n        }}\n\n        function captureLayout() {{\n            const groups = {{}};\n\n            scene.children.forEach(function(obj) {{\n                if (!obj.userData || !obj.userData.furnitureId) return;\n\n                const id = obj.userData.furnitureId;\n                if (!groups[id]) groups[id] = [];\n\n                groups[id].push({{\n                    position: {{\n                        x: obj.position.x,\n                        y: obj.position.y,\n                        z: obj.position.z\n                    }},\n                    rotation: {{\n                        x: obj.rotation.x,\n                        y: obj.rotation.y,\n                        z: obj.rotation.z\n                    }},\n                    scale: {{\n                        x: obj.scale.x,\n                        y: obj.scale.y,\n                        z: obj.scale.z\n                    }}\n                }});\n            }});\n\n            return Object.keys(groups).map(function(id) {{\n                return {{\n                    id: id,\n                    name: id.replace(/_[0-9]+$/, ""),\n                    objects: groups[id]\n                }};\n            }});\n        }}\n\n        function cloneLayout(layout) {{\n            return JSON.parse(JSON.stringify(layout));\n        }}\n\n        function pushHistory(snapshot) {{\n            historyStack.push(cloneLayout(snapshot));\n            if (historyStack.length > 30) historyStack.shift();\n            redoStack = [];\n            updateHistoryButtons();\n        }}\n\n        function updateHistoryButtons() {{\n            undoButton.disabled = historyStack.length === 0;\n            redoButton.disabled = redoStack.length === 0;\n        }}\n\n        function removeAllFurniture() {{\n            const objects = scene.children.filter(function(obj) {{\n                return obj.userData && obj.userData.furnitureId;\n            }});\n\n            objects.forEach(function(obj) {{\n                scene.remove(obj);\n                if (obj.geometry) obj.geometry.dispose();\n                if (obj.material) {{\n                    if (Array.isArray(obj.material)) {{\n                        obj.material.forEach(function(m) {{ if (m.dispose) m.dispose(); }});\n                    }} else if (obj.material.dispose) {{\n                        obj.material.dispose();\n                    }}\n                }}\n            }});\n        }}\n\n        function restoreLayout(layout) {{\n            removeAllFurniture();\n            clearSelection();\n\n            let maxIndex = 0;\n\n            layout.forEach(function(record) {{\n                const match = record.id.match(/_(\\d+)$/);\n                if (match) maxIndex = Math.max(maxIndex, parseInt(match[1], 10));\n\n                const item = furnitureData.find(function(f) {{\n                    return f.name === record.name;\n                }});\n\n                const color = item && item.color ? item.color : accentColor;\n\n                currentFurnitureId = record.id;\n                createFurnitureByName(record.name, 0, 0, color);\n\n                const objects = furnitureObjects(record.id);\n\n                objects.forEach(function(obj, index) {{\n                    const state = record.objects[index];\n                    if (!state) return;\n\n                    obj.position.set(\n                        state.position.x,\n                        state.position.y,\n                        state.position.z\n                    );\n\n                    obj.rotation.set(\n                        state.rotation.x,\n                        state.rotation.y,\n                        state.rotation.z\n                    );\n\n                    obj.scale.set(\n                        state.scale.x,\n                        state.scale.y,\n                        state.scale.z\n                    );\n                }});\n            }});\n\n            dynamicFurnitureIndex = Math.max(dynamicFurnitureIndex, maxIndex);\n            currentFurnitureId = null;\n            updateFurnitureCount();\n            refreshSelectionHelper();\n        }}\n\n        function undoLayout() {{\n            if (historyStack.length === 0) return;\n\n            const current = captureLayout();\n            const previous = historyStack.pop();\n\n            redoStack.push(cloneLayout(current));\n            restoreLayout(previous);\n            updateHistoryButtons();\n        }}\n\n        function redoLayout() {{\n            if (redoStack.length === 0) return;\n\n            const current = captureLayout();\n            const next = redoStack.pop();\n\n            historyStack.push(cloneLayout(current));\n            restoreLayout(next);\n            updateHistoryButtons();\n        }}\n\n        function saveCurrentLayout() {{\n            savedLayout = cloneLayout(captureLayout());\n\n            try {{\n                localStorage.setItem(\n                    "casacraft_3d_layout",\n                    JSON.stringify(savedLayout)\n                );\n            }} catch (e) {{\n                console.warn("Could not use localStorage", e);\n            }}\n\n            saveButton.textContent = "✓ Saved";\n            setTimeout(function() {{\n                saveButton.textContent = "💾 Save";\n            }}, 1200);\n        }}\n\n        function loadSavedLayout() {{\n            try {{\n                const raw = localStorage.getItem("casacraft_3d_layout");\n                if (!raw) return false;\n\n                const parsed = JSON.parse(raw);\n                if (!Array.isArray(parsed)) return false;\n\n                savedLayout = parsed;\n                restoreLayout(parsed);\n                return true;\n            }} catch (e) {{\n                console.warn("Could not restore saved layout", e);\n                return false;\n            }}\n        }}\n
        function getFurnitureBounds(id) {{
            const objects = furnitureObjects(id);
            const bounds = new THREE.Box3();
            bounds.makeEmpty();

            objects.forEach(function(obj) {{
                bounds.expandByObject(obj);
            }});

            return bounds;
        }}

        function clampSelectedToRoom() {{
            if (!selectedFurnitureId) return;

            const objects = furnitureObjects(selectedFurnitureId);
            if (!objects.length) return;

            const margin = 0.35;
            const halfW = roomWidth / 2 - margin;
            const halfL = roomLength / 2 - margin;

            const bounds = getFurnitureBounds(selectedFurnitureId);

            let dx = 0;
            let dz = 0;

            if (bounds.min.x < -halfW) {{
                dx = -halfW - bounds.min.x;
            }} else if (bounds.max.x > halfW) {{
                dx = halfW - bounds.max.x;
            }}

            if (bounds.min.z < -halfL) {{
                dz = -halfL - bounds.min.z;
            }} else if (bounds.max.z > halfL) {{
                dz = halfL - bounds.max.z;
            }}

            if (dx !== 0 || dz !== 0) {{
                objects.forEach(function(obj) {{
                    obj.position.x += dx;
                    obj.position.z += dz;
                }});
            }}
        }}

        function refreshSelectionHelper() {{
            if (!selectedFurnitureId) return;

            if (selectionHelper) {{
                scene.remove(selectionHelper);
                selectionHelper = null;
            }}

            const objects = furnitureObjects(selectedFurnitureId);
            if (!objects.length) return;

            const bounds = getFurnitureBounds(selectedFurnitureId);
            selectionHelper = new THREE.Box3Helper(
                bounds,
                0xd6a56d
            );
            scene.add(selectionHelper);
        }}

        function clearSelection() {{
            selectedFurnitureId = null;
            selectedName.textContent = "Select furniture";

            if (selectionHelper) {{
                scene.remove(selectionHelper);
                selectionHelper = null;
            }}
        }}

        function selectFurniture(id) {{
            if (!id) return;

            selectedFurnitureId = id;
            selectedName.textContent =
                id.replace(/_[0-9]+$/, "") + " selected";

            if (selectionHelper) {{
                scene.remove(selectionHelper);
                selectionHelper = null;
            }}

            refreshSelectionHelper();
        }}

        function setPointer(event) {{
            const rect = renderer.domElement.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        }}

        function pickFurniture(event) {{
            setPointer(event);
            raycaster.setFromCamera(mouse, camera);

            const hits = raycaster.intersectObjects(
                scene.children.filter(function(obj) {{
                    return obj.userData && obj.userData.furnitureId;
                }}),
                false
            );

            if (!hits.length) return null;

            return hits[0].object;
        }}

        renderer.domElement.addEventListener("pointerdown", function(event) {{
            const picked = pickFurniture(event);

            if (!picked) return;

            selectFurniture(picked.userData.furnitureId);
            dragStartSnapshot = captureLayout();
            dragHistoryAdded = false;

            raycaster.setFromCamera(mouse, camera);

            if (raycaster.ray.intersectPlane(dragPlane, dragPoint)) {{
                isDraggingFurniture = true;
            }}

            controls.enabled = false;
        }});

        renderer.domElement.addEventListener("pointermove", function(event) {{
            if (!isDraggingFurniture || !selectedFurnitureId) return;

            setPointer(event);
            raycaster.setFromCamera(mouse, camera);

            if (!raycaster.ray.intersectPlane(dragPlane, dragPoint)) return;

            const objects = furnitureObjects(selectedFurnitureId);

            if (!objects.length) return;

            if (!dragHistoryAdded) {{
                pushHistory(dragStartSnapshot || captureLayout());
                dragHistoryAdded = true;
            }}

            const anchor = objects[0];
            const dx = dragPoint.x - anchor.position.x;
            const dz = dragPoint.z - anchor.position.z;

            objects.forEach(function(obj) {{
                obj.position.x += dx;
                obj.position.z += dz;
            }});

            clampSelectedToRoom();
            refreshSelectionHelper();
        }});

        window.addEventListener("pointerup", function() {{
            isDraggingFurniture = false;
            dragStartSnapshot = null;
            dragHistoryAdded = false;
            controls.enabled = true;
        }});

        function animateCameraTo(position, target) {{
            camera.position.copy(position);
            controls.target.copy(target);
            controls.update();
        }}

        perspectiveView.addEventListener("click", function() {{
            animateCameraTo(
                new THREE.Vector3(roomWidth * 0.78, wallHeight * 0.72, roomLength * 0.82),
                new THREE.Vector3(0, 1.25, 0)
            );
        }});

        topView.addEventListener("click", function() {{
            animateCameraTo(
                new THREE.Vector3(0, Math.max(roomWidth, roomLength) * 1.05, 0.01),
                new THREE.Vector3(0, 0, 0)
            );
        }});

        frontView.addEventListener("click", function() {{
            animateCameraTo(
                new THREE.Vector3(0, wallHeight * 0.55, roomLength * 0.92),
                new THREE.Vector3(0, 1.25, 0)
            );
        }});

        presentationView.addEventListener("click", function() {{
            animateCameraTo(
                new THREE.Vector3(roomWidth * 0.86, wallHeight * 0.68, roomLength * 0.98),
                new THREE.Vector3(0, 1.30, -roomLength * 0.06)
            );
            controls.autoRotate = true;
            controls.autoRotateSpeed = 0.55;
            setTimeout(function() {{
                controls.autoRotate = false;
            }}, 9000);
        }});

        function addFurnitureToRoom(name) {{

            pushHistory(captureLayout());

            const typeMap = {{
                "Sofa": "sofa",
                "Bed": "bed",
                "Wardrobe": "wardrobe",
                "TV Unit": "tv",
                "Coffee Table": "coffee_table",
                "Dining Table": "dining",
                "Kitchen Island": "island",
                "Tall Unit": "tall",
                "Vanity": "vanity",
                "Shower": "shower",
                "Bathtub": "bathtub"
            }};

            const type = typeMap[name];
            if (!type) return;

            dynamicFurnitureIndex += 1;
            currentFurnitureId =
                name + "_" + dynamicFurnitureIndex;

            const offset = dynamicFurnitureIndex % 4;
            const row = Math.floor(dynamicFurnitureIndex / 4);

            const x =
                -roomWidth / 2 +
                2.5 +
                offset * 2.7;

            const z =
                -roomLength / 2 +
                2.5 +
                row * 2.8;

            const item = furnitureData.find(function(f) {{
                return f.name === name;
            }});

            const color =
                item && item.color
                    ? item.color
                    : accentColor;

            switch(type) {{
                case "sofa": createSofa(x,z,color); break;
                case "bed": createBed(x,z,color); break;
                case "wardrobe": createWardrobe(x,z,color); break;
                case "tv": createTV(x,z,color); break;
                case "coffee_table": createCoffeeTable(x,z,color); break;
                case "dining": createDining(x,z,color); break;
                case "island": createIsland(x,z,color); break;
                case "tall": createTall(x,z,color); break;
                case "vanity": createVanity(x,z,color); break;
                case "shower": createShower(x,z,color); break;
                case "bathtub": createBathtub(x,z,color); break;
            }}

            selectFurniture(currentFurnitureId);
            updateFurnitureCount();
        }}

        addFurnitureButton.addEventListener("click", function() {{
            addFurnitureToRoom(furnitureType.value);
        }});

        rotateButton.addEventListener("click", function() {{
            if (!selectedFurnitureId) return;

            pushHistory(captureLayout());

            const objects = furnitureObjects(selectedFurnitureId);
            if (!objects.length) return;

            const bounds = getFurnitureBounds(selectedFurnitureId);
            const centerX = (bounds.min.x + bounds.max.x) / 2;
            const centerZ = (bounds.min.z + bounds.max.z) / 2;
            const angle = Math.PI / 8;

            objects.forEach(function(obj) {{
                const dx = obj.position.x - centerX;
                const dz = obj.position.z - centerZ;

                obj.position.x = centerX + dx * Math.cos(angle) - dz * Math.sin(angle);
                obj.position.z = centerZ + dx * Math.sin(angle) + dz * Math.cos(angle);
                obj.rotation.y += angle;
            }});

            clampSelectedToRoom();
            refreshSelectionHelper();
        }});

        function resizeSelected(multiplier) {{
            if (!selectedFurnitureId) return;

            pushHistory(captureLayout());

            const objects = furnitureObjects(selectedFurnitureId);
            if (!objects.length) return;

            const bounds = getFurnitureBounds(selectedFurnitureId);
            const centerX = (bounds.min.x + bounds.max.x) / 2;
            const centerZ = (bounds.min.z + bounds.max.z) / 2;

            objects.forEach(function(obj) {{
                obj.scale.multiplyScalar(multiplier);

                obj.position.x =
                    centerX + (obj.position.x - centerX) * multiplier;

                obj.position.z =
                    centerZ + (obj.position.z - centerZ) * multiplier;
            }});

            clampSelectedToRoom();
            refreshSelectionHelper();
        }}

        scaleUpButton.addEventListener("click", function() {{
            resizeSelected(1.10);
        }});

        scaleDownButton.addEventListener("click", function() {{
            resizeSelected(0.90);
        }});

        deleteButton.addEventListener("click", function() {{
            if (!selectedFurnitureId) return;

            pushHistory(captureLayout());

            furnitureObjects(selectedFurnitureId).forEach(function(obj) {{
                scene.remove(obj);
                if (obj.geometry) obj.geometry.dispose();
            }});

            clearSelection();
            updateFurnitureCount();
        }});

        clearButton.addEventListener("click", function() {{
            clearSelection();
        }});

        undoButton.addEventListener("click", function() {{
            undoLayout();
        }});

        redoButton.addEventListener("click", function() {{
            redoLayout();
        }});

        saveButton.addEventListener("click", function() {{
            saveCurrentLayout();
        }});

        resetButton.addEventListener("click", function() {{
            const current = captureLayout();
            pushHistory(current);

            if (savedLayout) {{
                restoreLayout(savedLayout);
            }} else {{
                restoreLayout([]);
            }}
        }});

        // The initial layout is the first undo/restore point.
        historyStack = [];
        redoStack = [];
        updateHistoryButtons();
        updateFurnitureCount();
        savedLayout = cloneLayout(captureLayout());

        /* ====================================================
           RESIZE
           ==================================================== */

        window.addEventListener(
            "resize",
            function() {{

                camera.aspect =
                    window.innerWidth /
                    window.innerHeight;


                camera.updateProjectionMatrix();


                renderer.setSize(
                    window.innerWidth,
                    window.innerHeight
                );

            }}
        );


        /* ====================================================
           ANIMATION
           ==================================================== */

        function animate() {{

            requestAnimationFrame(
                animate
            );


            controls.update();


            renderer.render(
                scene,
                camera
            );

        }}


        animate();


        /* ====================================================
           FINISH LOADING
           ==================================================== */

        setTimeout(
            function() {{

                loading.style.display =
                    "none";

            }},
            400
        );

    }}
    catch (error) {{

        console.error(
            "CasaCraft 3D Error:",
            error
        );


        showError(
            error.message ||
            String(error)
        );

    }}

}})();

</script>

</body>

</html>
"""

    components.html(
        html,
        height=720,
        scrolling=False
    )

    # ========================================================
    # AUTOMATIC INTERIOR COST ESTIMATOR
    # ========================================================

    furniture_rates = {
        "Sofa": 45000,
        "Bed": 55000,
        "Wardrobe": 70000,
        "TV Unit": 35000,
        "Coffee Table": 12000,
        "Dining Table": 45000,
        "Kitchen Island": 55000,
        "Tall Unit": 28000,
        "Vanity": 22000,
        "Shower": 30000,
        "Bathtub": 65000,
    }

    area_sqft = float(width_ft) * float(length_ft)
    wall_area_sqft = (2 * (float(width_ft) + float(length_ft))) * 10.0

    furniture_cost = sum(
        furniture_rates.get(name, 0)
        for name in selected_furniture
    )

    with st.expander("💰 Automatic Interior Cost Estimator", expanded=True):
        st.caption(
            "Indicative planning estimate only. Actual rates vary by city, brand, "
            "material, finish, site conditions and contractor."
        )

        c1, c2, c3, c4 = st.columns(4)

        with c1:
            flooring_rate = st.number_input(
                "Flooring ₹/sqft",
                min_value=50,
                max_value=1000,
                value=180,
                step=10,
                key="cc_flooring_rate"
            )

        with c2:
            paint_rate = st.number_input(
                "Paint ₹/sqft wall",
                min_value=15,
                max_value=250,
                value=45,
                step=5,
                key="cc_paint_rate"
            )

        with c3:
            lighting_rate = st.number_input(
                "Lighting ₹/sqft",
                min_value=20,
                max_value=500,
                value=120,
                step=10,
                key="cc_lighting_rate"
            )

        with c4:
            labour_percent = st.number_input(
                "Labour %",
                min_value=0,
                max_value=40,
                value=12,
                step=1,
                key="cc_labour_percent"
            )

        material_rate = st.number_input(
            "Misc. material / hardware ₹/sqft",
            min_value=0,
            max_value=1000,
            value=80,
            step=10,
            key="cc_material_rate"
        )

        contingency_percent = st.slider(
            "Contingency %",
            min_value=0,
            max_value=15,
            value=5,
            key="cc_contingency"
        )

        flooring_cost = area_sqft * flooring_rate
        paint_cost = wall_area_sqft * paint_rate
        lighting_cost = area_sqft * lighting_rate
        material_cost = area_sqft * material_rate

        base_cost = (
            furniture_cost
            + flooring_cost
            + paint_cost
            + lighting_cost
            + material_cost
        )

        labour_cost = base_cost * labour_percent / 100.0
        subtotal = base_cost + labour_cost
        contingency_cost = subtotal * contingency_percent / 100.0
        total_cost = subtotal + contingency_cost

        r1, r2, r3, r4 = st.columns(4)

        r1.metric("Room Area", f"{area_sqft:,.0f} sqft")
        r2.metric("Furniture", f"₹{furniture_cost:,.0f}")
        r3.metric("Labour", f"₹{labour_cost:,.0f}")
        r4.metric("Estimated Total", f"₹{total_cost:,.0f}")

        st.markdown("### Cost Breakdown")

        breakdown = {
            "Furniture": furniture_cost,
            "Flooring": flooring_cost,
            "Paint": paint_cost,
            "Lighting": lighting_cost,
            "Material / Hardware": material_cost,
            "Labour": labour_cost,
            "Contingency": contingency_cost,
        }

        cols = st.columns(2)
        for i, (label, amount) in enumerate(breakdown.items()):
            with cols[i % 2]:
                st.write(f"**{label}** — ₹{amount:,.0f}")

        budget = st.number_input(
            "Project Budget (₹)",
            min_value=0,
            value=500000,
            step=25000,
            key="cc_project_budget"
        )

        difference = float(budget) - total_cost

        if difference >= 0:
            st.success(
                f"Budget headroom: ₹{difference:,.0f}"
            )
        else:
            st.warning(
                f"Estimated over budget by: ₹{abs(difference):,.0f}"
            )

        st.session_state["last_cost_estimate"] = {
            "room_area_sqft": round(area_sqft, 2),
            "wall_area_sqft": round(wall_area_sqft, 2),
            "furniture_cost": round(furniture_cost, 2),
            "flooring_cost": round(flooring_cost, 2),
            "paint_cost": round(paint_cost, 2),
            "lighting_cost": round(lighting_cost, 2),
            "material_cost": round(material_cost, 2),
            "labour_cost": round(labour_cost, 2),
            "contingency_cost": round(contingency_cost, 2),
            "estimated_total": round(total_cost, 2),
            "budget": float(budget),
        }

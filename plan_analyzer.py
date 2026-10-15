"""Basic OpenCV floor-plan image metrics."""
def analyze_plan(image):
    import cv2
    import numpy as np
    if image is None: raise ValueError("No floor-plan image supplied")
    arr=np.asarray(image.convert("RGB") if hasattr(image, "convert") else image)
    if arr.ndim == 3: gray=cv2.cvtColor(arr, cv2.COLOR_RGB2GRAY)
    else: gray=arr
    edges=cv2.Canny(gray, 50, 150)
    lines=cv2.HoughLinesP(edges, 1, 3.141592653589793/180, threshold=50, minLineLength=25, maxLineGap=8)
    return {"width": int(gray.shape[1]), "height": int(gray.shape[0]), "line_segments": 0 if lines is None else int(len(lines)), "edge_ratio": float(np.count_nonzero(edges)/edges.size)}

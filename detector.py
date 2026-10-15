"""Optional YOLO room object detection; reports a clear error if unavailable."""
from config import YOLO_MODEL
class InteriorDetector:
    def __init__(self):
        try:
            from ultralytics import YOLO
        except ImportError as exc:
            raise RuntimeError("YOLO detection needs ultralytics. Install requirements.txt first.") from exc
        from pathlib import Path
        self.model = YOLO(YOLO_MODEL)
    def detect(self, image):
        results=self.model(image)
        if not results: return image, [], {}
        result=results[0]
        annotated=result.plot()
        detections=[]; counts={}
        names=getattr(result, "names", {})
        boxes=getattr(result, "boxes", None)
        if boxes is not None:
            for box in boxes:
                cls=int(box.cls[0].item()); label=str(names.get(cls, cls)); detections.append(label); counts[label]=counts.get(label,0)+1
        return annotated, detections, counts

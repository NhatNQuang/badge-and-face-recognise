from ultralytics import YOLO
from PIL import Image
import io
import numpy as np

model = YOLO("yolov8n.pt")
# ============================================================
# SUPPORT FUNCTIONS
# ============================================================
def check_image_bytes(image_bytes: bytes):
    if not image_bytes:
        raise ValueError("Empty image data")
    try: 
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise ValueError(f"Invalid image format: {e}")
    arr = np.array(img)
    if np.all(arr == arr[0, 0]):
        raise ValueError("Image contains only a single color(invalid content)")
    
    return img


# ============================================================
# Function 01: Detect Human From Image
# ============================================================
def detect_human_by_image(image_bytes: bytes):
    """
    Detect humans from image
    input: image, type: bytes
    Return: (annotated_image_bytes, detection_json)
    """
    img = check_image_bytes(image_bytes)
    img_np = np.array(img)

    results = model(img_np)

    annotated = results[0].plot() # numpy array

    # convert annotated array to JPEG bytes
    buf = io.BytesIO()
    Image.fromarray(annotated).save(buf, format="JPEG")
    buf.seek(0)

    # 5. Lấy detection data dạng JSON
    detections = results[0].boxes.xyxy.cpu().numpy().tolist()
    classes = results[0].boxes.cls.cpu().numpy().tolist()
    conf = results[0].boxes.conf.cpu().numpy().tolist()

    return buf.getvalue(), {
        "boxes_xyxy": detections,
        "classes": classes,
        "confidence": conf
    }
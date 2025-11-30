# ============================
# LOAD MODEL SAFELY - PATCH TORCH FIRST
# ============================
# Monkey patch torch.load để tương thích với PyTorch 2.6
# PHẢI PATCH TRƯỚC KHI IMPORT ULTRALYTICS
import torch

_original_torch_load = torch.load

def _patched_torch_load(f, *args, **kwargs):
    """Wrapper để set weights_only=False cho YOLO models"""
    # Nếu không có weights_only trong kwargs, set mặc định là False
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_torch_load(f, *args, **kwargs)

# Apply patch
torch.load = _patched_torch_load

# ============================
# NOW IMPORT ULTRALYTICS
# ============================
import ultralytics
import os
from ultralytics import YOLO
from PIL import Image
import io
import numpy as np
import cv2
import threading
import uuid
import time

# Check for GPU
device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Using device: {device}")

# Load YOLO model for human detection
model_path = os.path.join(os.path.dirname(__file__), "..", "models", "yolov8n.pt")
model = YOLO(model_path)
model.to(device)

# Load badge detection model
badge_model_path = os.path.join(os.path.dirname(__file__), "..", "models", "badge_detect.pt")
badge_model = YOLO(badge_model_path)
badge_model.to(device)
print(f"Badge detection model loaded from: {badge_model_path}")

# ============================================================
# CAMERA MANAGER
# ============================================================
class CameraManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(CameraManager, cls).__new__(cls)
                    cls._instance.cap = None
                    cls._instance.current_source = None
                    cls._instance.active_stream_id = None
                    cls._instance.camera_lock = threading.Lock()
        return cls._instance

    def start_stream(self, source):
        """
        Start a new stream. If source is different, release old camera and open new one.
        Returns a unique stream_id.
        """
        with self.camera_lock:
            new_stream_id = str(uuid.uuid4())
            self.active_stream_id = new_stream_id
            
            # Check if we need to re-open camera
            # Re-open if: source changed OR camera is not open
            if self.current_source != source or self.cap is None or not self.cap.isOpened():
                if self.cap is not None:
                    self.cap.release()
                
                print(f"Opening camera source: {source}")
                self.cap = cv2.VideoCapture(source)
                self.current_source = source
                
                if not self.cap.isOpened():
                    raise ValueError(f"Cannot open camera source: {source}")
            else:
                print(f"Reusing existing camera source: {source}")
            
            return new_stream_id

    def get_frame(self, stream_id):
        """
        Get frame for a specific stream_id.
        Returns None if stream_id is not active or camera error.
        """
        # Check if this stream is still the active one
        if stream_id != self.active_stream_id:
            return None
            
        if self.cap is None or not self.cap.isOpened():
            return None

        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def stop_stream(self, stream_id):
        """
        Stop a stream. If it's the active stream, release the camera.
        """
        with self.camera_lock:
            if self.active_stream_id == stream_id:
                print(f"Stopping active stream: {stream_id}. Releasing camera.")
                if self.cap is not None:
                    self.cap.release()
                    self.cap = None
                self.current_source = None
                self.active_stream_id = None
            else:
                print(f"Stream {stream_id} is no longer active. Ignoring stop request.")

    def force_release(self):
        """Force release camera resources"""
        with self.camera_lock:
            if self.cap is not None:
                self.cap.release()
                self.cap = None
            self.current_source = None
            self.active_stream_id = None
            print("Camera force released")

# Initialize global camera manager
camera_manager = CameraManager()

# ============================================================
# SUPPORT FUNCTIONS
# ============================================================
def check_image_bytes(image_bytes: bytes) -> Image.Image:
    """
    Kiểm tra và convert image bytes thành PIL Image
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        return img
    except Exception as e:
        raise ValueError(f"Invalid image data: {str(e)}")

# ============================================================
# HUMAN DETECTION FUNCTIONS
# ============================================================

# Function 01: Detect Human By Image
def detect_human_by_image(image_bytes: bytes):
    """
    Detect humans in an uploaded image
    """
    img = check_image_bytes(image_bytes)
    img_np = np.array(img)

    # Chạy YOLO detection - chỉ detect người (class 0)
    results = model(img_np, classes=[0])

    annotated = results[0].plot() # numpy array

    # Convert annotated image to bytes
    annotated_img = Image.fromarray(annotated)
    buf = io.BytesIO()
    annotated_img.save(buf, format='JPEG')

    # Extract detection data
    boxes = results[0].boxes
    detections = boxes.xyxy.cpu().numpy().tolist() if len(boxes) > 0 else []
    classes = boxes.cls.cpu().numpy().tolist() if len(boxes) > 0 else []
    conf = boxes.conf.cpu().numpy().tolist() if len(boxes) > 0 else []

    return buf.getvalue(), {
        "boxes_xyxy": detections,
        "classes": classes,
        "confidence": conf
    }

# Function 02: Detect Human From Real-time Camera
def detect_human_from_camera(camera_source=0, confidence_threshold=0.5):
    """
    Detect humans from real-time camera stream using CameraManager
    """
    stream_id = camera_manager.start_stream(camera_source)
    
    try:
        while True:
            frame = camera_manager.get_frame(stream_id)
            
            if frame is None:
                # Check if stream was preempted
                if stream_id != camera_manager.active_stream_id:
                    print("Stream preempted by new request")
                    break
                print("Cannot read frame from camera")
                break
            
            # Chạy YOLO detection - chỉ detect người (class 0)
            results = model(frame, conf=confidence_threshold, classes=[0])
            
            annotated_frame = results[0].plot()
            
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            
            # Lấy detection data - chỉ người (class 0)
            boxes = results[0].boxes
            detections = {
                "boxes_xyxy": boxes.xyxy.cpu().numpy().tolist() if len(boxes) > 0 else [],
                "classes": boxes.cls.cpu().numpy().tolist() if len(boxes) > 0 else [],
                "confidence": boxes.conf.cpu().numpy().tolist() if len(boxes) > 0 else [],
                "count": len(boxes)
            }
            
            yield frame_bytes, detections
            
    finally:
        # Release camera if this was the active stream
        camera_manager.stop_stream(stream_id)

# Function 03: Detect Human From Camera (Single Frame)
def detect_human_from_camera_single_frame(camera_source=0, confidence_threshold=0.5):
    """
    Capture single frame from camera and detect humans
    """
    # For single frame, we start and immediately stop
    stream_id = camera_manager.start_stream(camera_source)
    
    try:
        # Try to get a valid frame (retry a few times if needed for warmup)
        frame = None
        for _ in range(5):
            frame = camera_manager.get_frame(stream_id)
            if frame is not None:
                break
            time.sleep(0.1)
            
        if frame is None:
            raise ValueError("Cannot read frame from camera")
        
        # Chạy YOLO detection - chỉ detect người (class 0)
        results = model(frame, conf=confidence_threshold, classes=[0])
        
        annotated_frame = results[0].plot()
        
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret:
            raise ValueError("Cannot encode frame to JPEG")
        
        frame_bytes = buffer.tobytes()
        
        # Lấy detection data - chỉ người (class 0)
        boxes = results[0].boxes
        detections = {
            "boxes_xyxy": boxes.xyxy.cpu().numpy().tolist() if len(boxes) > 0 else [],
            "classes": boxes.cls.cpu().numpy().tolist() if len(boxes) > 0 else [],
            "confidence": boxes.conf.cpu().numpy().tolist() if len(boxes) > 0 else [],
            "count": len(boxes)
        }
        
        return frame_bytes, detections
        
    finally:
        camera_manager.stop_stream(stream_id)

# ============================================================
# BADGE DETECTION FUNCTIONS
# ============================================================

# Function 04: Detect Badge By Image
def detect_badge_by_image(image_bytes: bytes):
    """
    Detect badges in an uploaded image using trained badge model
    """
    img = check_image_bytes(image_bytes)
    img_np = np.array(img)

    # Chạy badge detection - detect tất cả classes từ trained model
    results = badge_model(img_np)

    annotated = results[0].plot() # numpy array

    # Convert annotated image to bytes
    annotated_img = Image.fromarray(annotated)
    buf = io.BytesIO()
    annotated_img.save(buf, format='JPEG')

    # Extract detection data
    boxes = results[0].boxes
    detections = boxes.xyxy.cpu().numpy().tolist() if len(boxes) > 0 else []
    classes = boxes.cls.cpu().numpy().tolist() if len(boxes) > 0 else []
    conf = boxes.conf.cpu().numpy().tolist() if len(boxes) > 0 else []

    return buf.getvalue(), {
        "boxes_xyxy": detections,
        "classes": classes,
        "confidence": conf
    }

# Function 05: Detect Badge From Real-time Camera
def detect_badge_from_camera(camera_source=0, confidence_threshold=0.5):
    """
    Detect badges from real-time camera stream using CameraManager
    """
    stream_id = camera_manager.start_stream(camera_source)
    
    try:
        while True:
            frame = camera_manager.get_frame(stream_id)
            
            if frame is None:
                if stream_id != camera_manager.active_stream_id:
                    print("Stream preempted by new request")
                    break
                print("Cannot read frame from camera")
                break
            
            # Chạy badge detection với confidence threshold
            results = badge_model(frame, conf=confidence_threshold)
            
            annotated_frame = results[0].plot()
            
            ret, buffer = cv2.imencode('.jpg', annotated_frame)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            
            # Lấy detection data
            boxes = results[0].boxes
            detections = {
                "boxes_xyxy": boxes.xyxy.cpu().numpy().tolist() if len(boxes) > 0 else [],
                "classes": boxes.cls.cpu().numpy().tolist() if len(boxes) > 0 else [],
                "confidence": boxes.conf.cpu().numpy().tolist() if len(boxes) > 0 else [],
                "count": len(boxes)
            }
            
            yield frame_bytes, detections
            
    finally:
        camera_manager.stop_stream(stream_id)

# Function 06: Detect Badge From Camera (Single Frame)
def detect_badge_from_camera_single_frame(camera_source=0, confidence_threshold=0.5):
    """
    Capture single frame from camera and detect badges using CameraManager
    """
    stream_id = camera_manager.start_stream(camera_source)
    
    try:
        frame = None
        for _ in range(5):
            frame = camera_manager.get_frame(stream_id)
            if frame is not None:
                break
            time.sleep(0.1)
            
        if frame is None:
            raise ValueError("Cannot read frame from camera")
        
        # Chạy badge detection với confidence threshold
        results = badge_model(frame, conf=confidence_threshold)
        
        annotated_frame = results[0].plot()
        
        ret, buffer = cv2.imencode('.jpg', annotated_frame)
        if not ret:
            raise ValueError("Cannot encode frame to JPEG")
        
        frame_bytes = buffer.tobytes()
        
        # Lấy detection data
        boxes = results[0].boxes
        detections = {
            "boxes_xyxy": boxes.xyxy.cpu().numpy().tolist() if len(boxes) > 0 else [],
            "classes": boxes.cls.cpu().numpy().tolist() if len(boxes) > 0 else [],
            "confidence": boxes.conf.cpu().numpy().tolist() if len(boxes) > 0 else [],
            "count": len(boxes)
        }
        
        return frame_bytes, detections
        
    finally:
        camera_manager.stop_stream(stream_id)

# ============================================================
# COMBINED DETECTION FUNCTION
# ============================================================

# Function 07: Detect Both Human and Badge From Camera (Combined)
def detect_combined_from_camera(camera_source=0, confidence_threshold=0.5):
    """
    Run both human and badge detection on same camera stream using CameraManager
    """
    stream_id = camera_manager.start_stream(camera_source)
    
    try:
        while True:
            frame = camera_manager.get_frame(stream_id)
            
            if frame is None:
                if stream_id != camera_manager.active_stream_id:
                    print("Stream preempted by new request")
                    break
                print("Cannot read frame from camera")
                break
            
            # Run both models on same frame
            human_results = model(frame, conf=confidence_threshold, classes=[0])
            badge_results = badge_model(frame, conf=confidence_threshold)
            
            # Start with original frame
            annotated = frame.copy()
            
            # Draw human boxes (GREEN)
            human_boxes = human_results[0].boxes
            for box in human_boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                conf = float(box.conf[0].cpu().numpy())
                
                # Green rectangle for humans
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Label with confidence
                label = f'Person {conf:.2f}'
                cv2.putText(annotated, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw badge boxes (BLUE)
            badge_boxes = badge_results[0].boxes
            for box in badge_boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].cpu().numpy())
                conf = float(box.conf[0].cpu().numpy())
                
                # Blue rectangle for badges
                cv2.rectangle(annotated, (x1, y1), (x2, y2), (255, 0, 0), 2)
                
                # Label with confidence
                label = f'Badge {conf:.2f}'
                cv2.putText(annotated, label, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
            
            # Convert to JPEG
            ret, buffer = cv2.imencode('.jpg', annotated)
            if not ret:
                continue
                
            frame_bytes = buffer.tobytes()
            
            # Combine detection data
            detections = {
                "humans": {
                    "count": len(human_boxes),
                    "boxes": human_boxes.xyxy.cpu().numpy().tolist() if len(human_boxes) > 0 else [],
                    "confidence": human_boxes.conf.cpu().numpy().tolist() if len(human_boxes) > 0 else []
                },
                "badges": {
                    "count": len(badge_boxes),
                    "boxes": badge_boxes.xyxy.cpu().numpy().tolist() if len(badge_boxes) > 0 else [],
                    "confidence": badge_boxes.conf.cpu().numpy().tolist() if len(badge_boxes) > 0 else []
                },
                "total_count": len(human_boxes) + len(badge_boxes)
            }
            
            yield frame_bytes, detections
            
    finally:
        camera_manager.stop_stream(stream_id)


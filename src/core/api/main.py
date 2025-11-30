from fastapi import FastAPI, File, UploadFile, Query
from fastapi.responses import JSONResponse, StreamingResponse, FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from api.functions import (
    detect_human_by_image, 
    detect_human_from_camera,
    detect_human_from_camera_single_frame,
    detect_badge_by_image,
    detect_badge_from_camera,
    detect_badge_from_camera_single_frame,
    detect_combined_from_camera
)
import base64
import os

# Khởi tạo FastAPI với metadata
app = FastAPI(
    title="Human Detection API",
    description="API để detect người trong ảnh và camera sử dụng YOLOv8",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Import camera manager
from api.functions import camera_manager

@app.on_event("shutdown")
def shutdown_event():
    """Release camera on shutdown"""
    print("Shutting down... Releasing camera resources")
    camera_manager.force_release()

# UI is now served by Nginx, so we don't need to mount static files here
# Mount UI directory
# ui_dir = "/ui"
# if os.path.exists(ui_dir):
#     app.mount("/ui", StaticFiles(directory=ui_dir, html=True), name="ui")

# Mount static files nếu folder tồn tại
static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    """Redirect to UI home page"""
    return RedirectResponse(url="/ui/index.html")

@app.get("/demo")
async def demo_page():
    """Serve camera demo HTML page"""
    demo_file = os.path.join(os.path.dirname(__file__), "..", "static", "camera_demo.html")
    if os.path.exists(demo_file):
        return FileResponse(demo_file)
    else:
        return JSONResponse(
            status_code=404,
            content={"error": "Demo page not found"}
        )

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "ai-processing"}

@app.post("/detect_human_by_image")
async def detect_human_by_image_api(file: UploadFile = File(...)):
    """
    Detect người trong ảnh
    
    - **file**: File ảnh upload (JPEG, PNG, etc.)
    
    Returns:
    - **annotated_image**: Ảnh đã được vẽ bounding boxes (base64 encoded)
    - **detections**: Danh sách các detection với boxes, classes, confidence
    """
    try:
        image_bytes = await file.read()
        
        annotated_bytes, result_json = detect_human_by_image(image_bytes)
        
        # Encode annotated image to base64 để trả về JSON
        annotated_base64 = base64.b64encode(annotated_bytes).decode('utf-8')
        
        return {
            "success": True,
            "annotated_image": annotated_base64,
            "detections": result_json,
            "total_detections": len(result_json.get("boxes_xyxy", []))
        }
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Internal server error: {str(e)}"}
        )

@app.get("/camera/stream")
async def camera_stream(
    source: int = Query(0, description="Camera source (0 for default webcam)"),
    confidence: float = Query(0.5, ge=0.0, le=1.0, description="Confidence threshold")
):
    """
    Stream real-time camera với human detection
    
    - **source**: Camera source (0 = webcam mặc định)
    - **confidence**: Ngưỡng confidence (0.0 - 1.0)
    
    Returns: MJPEG video stream
    
    Sử dụng trong HTML:
    ```html
    <img src="http://localhost:6033/camera/stream?source=0&confidence=0.5" />
    ```
    """
    def generate_frames():
        try:
            for frame_bytes, detections in detect_human_from_camera(source, confidence):
                # Tạo multipart response cho MJPEG stream
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error in camera stream: {e}")
    
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.get("/camera/snapshot")
async def camera_snapshot(
    source: int = Query(0, description="Camera source (0 for default webcam)"),
    confidence: float = Query(0.5, ge=0.0, le=1.0, description="Confidence threshold")
):
    """
    Capture một frame từ camera và detect người
    
    - **source**: Camera source (0 = webcam mặc định)
    - **confidence**: Ngưỡng confidence (0.0 - 1.0)
    
    Returns:
    - **annotated_image**: Ảnh đã được vẽ bounding boxes (base64 encoded)
    - **detections**: Danh sách các detection với boxes, classes, confidence, count
    """
    try:
        frame_bytes, detections = detect_human_from_camera_single_frame(source, confidence)
        
        # Encode to base64
        frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
        
        return {
            "success": True,
            "annotated_image": frame_base64,
            "detections": detections,
            "total_detections": detections.get("count", 0)
        }
    except ValueError as e:
        return JSONResponse(
            status_code=400,
            content={"success": False, "error": str(e)}
        )
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"success": False, "error": f"Internal server error: {str(e)}"}
        )

# ============================================================
# BADGE DETECTION ENDPOINTS
# ============================================================

@app.post("/detect_badge_by_image")
async def detect_badge_by_image_api(file: UploadFile = File(...)):
    """Detect badges in uploaded image"""
    try:
        image_bytes = await file.read()
        annotated_bytes, result_json = detect_badge_by_image(image_bytes)
        annotated_base64 = base64.b64encode(annotated_bytes).decode('utf-8')
        
        return {
            "success": True,
            "annotated_image": annotated_base64,
            "detections": result_json,
            "total_detections": len(result_json.get("boxes_xyxy", []))
        }
    except ValueError as e:
        return JSONResponse(status_code=400, content={"success": False, "error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

@app.get("/badge/stream")
async def badge_stream(source: int = Query(0), confidence: float = Query(0.5)):
    """Stream real-time badge detection from camera"""
    def generate_frames():
        try:
            for frame_bytes, detections in detect_badge_from_camera(source, confidence):
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error in badge stream: {e}")
    
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/badge/snapshot")
async def badge_snapshot(source: int = Query(0), confidence: float = Query(0.5)):
    """Capture single frame and detect badges"""
    try:
        frame_bytes, detections = detect_badge_from_camera_single_frame(source, confidence)
        frame_base64 = base64.b64encode(frame_bytes).decode('utf-8')
        
        return {
            "success": True,
            "annotated_image": frame_base64,
            "detections": detections,
            "total_detections": detections.get("count", 0)
        }
    except ValueError as e:
        return JSONResponse(status_code=400, content={"success": False, "error": str(e)})
    except Exception as e:
        return JSONResponse(status_code=500, content={"success": False, "error": str(e)})

# ============================================================
# COMBINED DETECTION ENDPOINT
# ============================================================

@app.get("/combined/stream")
async def combined_stream(source: int = Query(0), confidence: float = Query(0.5)):
    """Stream with both human and badge detection (green and blue boxes)"""
    def generate_frames():
        try:
            for frame_bytes, detections in detect_combined_from_camera(source, confidence):
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        except Exception as e:
            print(f"Error in combined stream: {e}")
    
    return StreamingResponse(generate_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

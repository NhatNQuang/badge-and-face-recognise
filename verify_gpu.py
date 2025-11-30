import torch
from ultralytics import YOLO
import sys

print("-" * 30)
print("GPU VERIFICATION")
print("-" * 30)

# Check CUDA
cuda_available = torch.cuda.is_available()
print(f"CUDA available: {cuda_available}")

if cuda_available:
    print(f"CUDA device count: {torch.cuda.device_count()}")
    print(f"Current device: {torch.cuda.current_device()}")
    print(f"Device name: {torch.cuda.get_device_name(0)}")
else:
    print("CUDA NOT AVAILABLE - Using CPU")

print("-" * 30)
print("MODEL VERIFICATION")
print("-" * 30)

# Load model
try:
    model = YOLO('yolov8n.pt')
    print(f"Model loaded successfully")
    print(f"Model device: {model.device}")
    
    # Check if model is on GPU
    is_gpu = str(model.device) != 'cpu'
    print(f"Is model on GPU? {is_gpu}")
    
    if cuda_available and not is_gpu:
        print("WARNING: CUDA is available but model is on CPU!")
    elif cuda_available and is_gpu:
        print("SUCCESS: Model is using GPU!")
        
except Exception as e:
    print(f"Error loading model: {e}")

print("-" * 30)

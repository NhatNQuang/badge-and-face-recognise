# 🤖 AI Human & Badge Detection System

A real-time AI-powered detection system for identifying humans and badges using YOLOv8, with GPU acceleration support and a beautiful web interface.

![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)
![Docker](https://img.shields.io/badge/docker-ready-blue.svg)
![GPU](https://img.shields.io/badge/GPU-CUDA-green.svg)

## ✨ Features

- 🎯 **Human Detection**: Detect people in images or live camera streams using YOLOv8
- 🎫 **Badge Detection**: Identify badges using custom-trained YOLO model
- 🔄 **Combined Detection**: Run both detections simultaneously with color-coded bounding boxes
- 📸 **Image Upload**: Drag & drop interface for single image processing
- 🎥 **Real-time Camera**: Live video stream with instant detection
- ⚡ **GPU Acceleration**: NVIDIA CUDA support for 60+ FPS performance
- 🌐 **REST API**: Complete FastAPI backend with Swagger documentation
- 💅 **Modern UI**: Beautiful glassmorphism design with smooth animations

## 🎬 Detection Modes

### 1. Human Detection
- Detects people using YOLOv8n pre-trained model
- Green bounding boxes
- Confidence scores displayed
- Upload images or use live camera

### 2. Badge Detection  
- Detects badges using custom-trained model
- Blue bounding boxes
- Real-time camera stream
- Image upload support

### 3. Combined Detection
- Runs both models simultaneously
- **Green boxes** = Humans
- **Blue boxes** = Badges
- Dual statistics panel
- GPU-optimized for smooth performance

## 📋 Prerequisites

### Required
- **Docker** (20.10+) and **Docker Compose** (2.0+)
- **Webcam** (for camera features)

### Optional but Recommended
- **NVIDIA GPU** (for GPU acceleration)
- **NVIDIA Container Toolkit** (for Docker GPU access)
- **CUDA 11.8+** compatible GPU

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/badge-and-face-recognise.git
cd badge-and-face-recognise
```

### 2. Start Services
```bash
docker-compose up -d
```

### 3. Access Application
Open your browser and navigate to:
- **Web Interface**: http://localhost:6033
- **API Documentation**: http://localhost:6033/docs

That's it! 🎉

## 🔧 Installation & Setup

### With GPU (Recommended)

#### 1. Install NVIDIA Container Toolkit

**Ubuntu/Debian:**
```bash
# Add NVIDIA package repositories
distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | \
  sudo tee /etc/apt/sources.list.d/nvidia-docker.list

# Install nvidia-container-toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Restart Docker
sudo systemctl restart docker
```

#### 2. Verify GPU Access
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

#### 3. Start with GPU
```bash
docker-compose up -d
```

The `docker-compose.yaml` is already configured for GPU access.

### Without GPU (CPU Only)

If you don't have an NVIDIA GPU, remove the GPU configuration from `docker-compose.yaml`:

```yaml
# Comment out or remove these lines:
# deploy:
#   resources:
#     reservations:
#       devices:
#         - driver: nvidia
#           count: 1
#           capabilities: [gpu]
```

Then start normally:
```bash
docker-compose up -d
```

**Note**: CPU mode will be slower (~50ms vs ~5ms per frame).

## 📖 Usage

### Web Interface

#### Home Page
Navigate to http://localhost:6033 to see:
- Feature overview
- Quick access to all detection modes
- Technology stack information

#### Human Detection
**URL**: http://localhost:6033/ui/upload.html

1. Drag & drop an image or click "Browse Files"
2. Preview your image
3. Click "Detect Humans"
4. View results with green bounding boxes
5. Download annotated image

#### Human Camera Stream
**URL**: http://localhost:6033/ui/camera.html

1. Select camera source
2. Adjust confidence threshold (0.0 - 1.0)
3. Click "Start Stream"
4. View real-time detection with green boxes
5. Take snapshots as needed

#### Badge Detection
**URL**: http://localhost:6033/ui/badge.html

- **Upload Tab**: Upload badge images for detection
- **Camera Tab**: Real-time badge detection stream
- Blue bounding boxes for badges
- Download results

#### Combined Detection
**URL**: http://localhost:6033/ui/combined.html

1. Start camera stream
2. See both detections simultaneously:
   - **Green boxes** = People
   - **Blue boxes** = Badges
3. Separate statistics for each type
4. GPU-accelerated for smooth 60+ FPS

### API Endpoints

Full API documentation available at: http://localhost:6033/docs

#### Human Detection

**Upload Image:**
```bash
curl -X POST "http://localhost:6033/detect_human_by_image" \
  -F "file=@image.jpg"
```

**Camera Stream:**
```bash
curl "http://localhost:6033/camera/stream?source=0&confidence=0.5"
```

**Snapshot:**
```bash
curl "http://localhost:6033/camera/snapshot?source=0&confidence=0.5"
```

#### Badge Detection

**Upload Image:**
```bash
curl -X POST "http://localhost:6033/detect_badge_by_image" \
  -F "file=@badge.jpg"
```

**Camera Stream:**
```bash
curl "http://localhost:6033/badge/stream?source=0&confidence=0.5"
```

#### Combined Detection

**Camera Stream:**
```bash
curl "http://localhost:6033/combined/stream?source=0&confidence=0.5"
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Web Browser (Port 6033)        │
│  ┌────────┐ ┌────────┐ ┌──────────────┐ │
│  │  Home  │ │ Upload │ │ Camera Stream│ │
│  └────────┘ └────────┘ └──────────────┘ │
└─────────────────┬───────────────────────┘
                  │ HTTP/REST
┌─────────────────▼───────────────────────┐
│         FastAPI Backend (Port 6034)      │
│  ┌──────────────────────────────────┐   │
│  │  Detection Functions              │   │
│  │  - Human (YOLOv8n)               │   │
│  │  - Badge (Custom Model)          │   │
│  │  - Combined (Both)               │   │
│  └──────────────┬───────────────────┘   │
└─────────────────┼───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│         NVIDIA GPU (CUDA)                │
│  - YOLOv8n Model (~6MB)                  │
│  - Badge Model (~5MB)                    │
│  - Inference: ~4-5ms per model           │
│  - Total: ~10ms → 60-100 FPS             │
└──────────────────────────────────────────┘
```

## 📁 Project Structure

```
badge-and-face-recognise/
├── src/core/                    # Backend application
│   ├── api/
│   │   ├── functions.py        # Detection functions
│   │   ├── main.py             # FastAPI application
│   │   └── __init__.py
│   ├── models/
│   │   └── badge_detect.pt     # Custom badge model (5.1MB)
│   ├── badge_detection/
│   │   └── train.py            # Training script
│   ├── requirements.txt        # Python dependencies
│   └── dockerfile              # Backend Dockerfile
├── ui/                          # Frontend application
│   ├── css/
│   │   └── style.css           # Styles
│   ├── js/
│   │   ├── utils.js            # Shared utilities
│   │   ├── badge.js            # Badge page logic
│   │   └── combined.js         # Combined page logic
│   ├── index.html              # Home page
│   ├── upload.html             # Human detection (upload)
│   ├── camera.html             # Human detection (camera)
│   ├── badge.html              # Badge detection
│   └── combined.html           # Combined detection
├── docker-compose.yaml         # Docker services configuration
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## ⚙️ Configuration

### Camera Source
Change camera source in the UI or via API:
- `0` = Default webcam
- `1` = Second camera
- `2` = Third camera

### Confidence Threshold
Adjust detection sensitivity (0.0 - 1.0):
- **0.3-0.4**: More detections, may include false positives
- **0.5-0.6**: Balanced (recommended)
- **0.7-0.8**: Fewer but more accurate detections

### GPU Memory
Models use approximately:
- YOLOv8n (human): ~200MB VRAM
- Badge model: ~50MB VRAM
- **Total**: ~250MB / 4GB (plenty of headroom)

## 🎯 Performance

### With GPU (NVIDIA RTX 3050 Ti)
- **Human Detection**: ~4-5ms per frame
- **Badge Detection**: ~4-5ms per frame
- **Combined Detection**: ~8-10ms per frame
- **Frame Rate**: 60-100 FPS
- **GPU Utilization**: 40-60%

### Without GPU (CPU Only)
- **Human Detection**: ~50ms per frame
- **Badge Detection**: ~80ms per frame
- **Combined Detection**: ~130ms per frame
- **Frame Rate**: ~7-15 FPS

## 🐛 Troubleshooting

### GPU Not Detected

**Check CUDA availability:**
```bash
docker exec ai-processing python -c "import torch; print(torch.cuda.is_available())"
```

**Verify NVIDIA Container Toolkit:**
```bash
docker run --rm --gpus all nvidia/cuda:11.8.0-base-ubuntu22.04 nvidia-smi
```

**Restart Docker:**
```bash
sudo systemctl restart docker
docker-compose restart
```

### Camera Not Working

**Check camera access:**
```bash
ls -l /dev/video0
```

**Verify Docker has camera access:**
```bash
docker exec ai-processing ls -l /dev/video0
```

**Grant permissions:**
```bash
sudo chmod 666 /dev/video0
```

### Port Already in Use

**Change ports in `docker-compose.yaml`:**
```yaml
ports:
  - "8033:6034"  # Change 6033 to 8033
```

### Slow Performance

1. **Enable GPU** (see GPU setup above)
2. **Lower confidence threshold**
3. **Reduce camera resolution**
4. **Close other GPU applications**

## 🔒 Security Notes

**For Production Deployment:**
- Change default ports
- Add authentication to API
- Use HTTPS/SSL
- Implement rate limiting
- Restrict CORS origins
- Use environment variables for secrets

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 👨‍💻 Author

Your Name - [@yourusername](https://github.com/yourusername)

## 🙏 Acknowledgments

- [Ultralytics YOLOv8](https://github.com/ultralytics/ultralytics) - Object detection framework
- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [Docker](https://www.docker.com/) - Containerization platform

## 📧 Support

For issues and questions:
- Open an [Issue](https://github.com/yourusername/badge-and-face-recognise/issues)
- Email: your.email@example.com

---

Made with ❤️ using YOLOv8, FastAPI, and Docker

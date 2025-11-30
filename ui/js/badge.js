// badge.js - JavaScript for badge detection page

let currentTab = 'upload';
let currentImageFile = null;
let currentResultData = null;
let currentSnapshotData = null;
let isStreaming = false;
let frameCount = 0;
let startTime = 0;

// Tab switching
function showTab(tab) {
    currentTab = tab;
    const uploadTab = document.getElementById('uploadTab');
    const cameraTab = document.getElementById('cameraTab');
    const uploadTabBtn = document.getElementById('uploadTabBtn');
    const cameraTabBtn = document.getElementById('cameraTabBtn');

    if (tab === 'upload') {
        uploadTab.classList.remove('hidden');
        cameraTab.classList.add('hidden');
        uploadTabBtn.classList.remove('btn-secondary');
        uploadTabBtn.classList.add('btn-primary');
        cameraTabBtn.classList.remove('btn-primary');
        cameraTabBtn.classList.add('btn-secondary');
    } else {
        uploadTab.classList.add('hidden');
        cameraTab.classList.remove('hidden');
        uploadTabBtn.classList.remove('btn-primary');
        uploadTabBtn.classList.add('btn-secondary');
        cameraTabBtn.classList.remove('btn-secondary');
        cameraTabBtn.classList.add('btn-primary');
    }
}

// ============================================================
// UPLOAD TAB FUNCTIONALITY
// ============================================================

const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadSection = document.getElementById('uploadSection');
const previewSection = document.getElementById('previewSection');
const resultsSection = document.getElementById('resultsSection');
const previewImage = document.getElementById('previewImage');
const detectBtn = document.getElementById('detectBtn');
const cancelBtn = document.getElementById('cancelBtn');
const uploadAnotherBtn = document.getElementById('uploadAnotherBtn');
const downloadBtn = document.getElementById('downloadBtn');

// Drag and drop handlers
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('dragover');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('dragover');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('dragover');

    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

// File input handler
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

// Handle file selection
function handleFileSelect(file) {
    try {
        utils.validateImageFile(file);
        currentImageFile = file;

        const reader = new FileReader();
        reader.onload = (e) => {
            previewImage.src = e.target.result;
            uploadSection.classList.add('hidden');
            previewSection.classList.remove('hidden');
            resultsSection.classList.add('hidden');
        };
        reader.readAsDataURL(file);

        utils.showToast('Image loaded successfully!', 'success');
    } catch (error) {
        utils.showToast(error.message, 'error');
    }
}

// Cancel button
cancelBtn.addEventListener('click', () => {
    resetUpload();
});

// Upload another button
uploadAnotherBtn.addEventListener('click', () => {
    resetUpload();
});

// Reset upload
function resetUpload() {
    currentImageFile = null;
    currentResultData = null;
    fileInput.value = '';
    uploadSection.classList.remove('hidden');
    previewSection.classList.add('hidden');
    resultsSection.classList.add('hidden');
}

// Detect button
detectBtn.addEventListener('click', async () => {
    if (!currentImageFile) {
        utils.showToast('No image selected', 'error');
        return;
    }

    try {
        utils.showLoading();
        detectBtn.disabled = true;
        startTime = Date.now();

        const formData = new FormData();
        formData.append('file', currentImageFile);

        const response = await fetch(`${API_BASE}/detect_badge_by_image`, {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            const processingTime = Date.now() - startTime;
            displayResults(data, processingTime);
            utils.showToast('Badge detection completed!', 'success');
        } else {
            throw new Error(data.error || 'Detection failed');
        }

    } catch (error) {
        utils.showToast(`Error: ${error.message}`, 'error');
        console.error('Detection error:', error);
    } finally {
        utils.hideLoading();
        detectBtn.disabled = false;
    }
});

// Display results
function displayResults(data, processingTime) {
    currentResultData = data;

    document.getElementById('resultImage').src = `data:image/jpeg;base64,${data.annotated_image}`;
    document.getElementById('totalDetections').textContent = data.total_detections;

    const avgConf = data.detections.confidence.length > 0
        ? utils.average(data.detections.confidence)
        : 0;
    document.getElementById('avgConfidence').textContent = utils.formatConfidence(avgConf);

    document.getElementById('processingTime').textContent = processingTime + 'ms';

    previewSection.classList.add('hidden');
    resultsSection.classList.remove('hidden');
}

// Download button
downloadBtn.addEventListener('click', () => {
    if (currentResultData) {
        utils.downloadImage(currentResultData.annotated_image, `badge_detection_${Date.now()}.jpg`);
        utils.showToast('Image downloaded!', 'success');
    }
});

// ============================================================
// CAMERA TAB FUNCTIONALITY
// ============================================================

const cameraSourceSelect = document.getElementById('cameraSource');
const confidenceSlider = document.getElementById('confidence');
const confidenceValue = document.getElementById('confidenceValue');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const snapshotBtn = document.getElementById('snapshotBtn');
const videoStream = document.getElementById('videoStream');
const streamPlaceholder = document.getElementById('streamPlaceholder');
const snapshotSection = document.getElementById('snapshotSection');

// Update confidence value display
confidenceSlider.addEventListener('input', (e) => {
    confidenceValue.textContent = parseFloat(e.target.value).toFixed(2);
    document.getElementById('confidenceInfo').textContent = parseFloat(e.target.value).toFixed(2);

    if (isStreaming) {
        stopStream();
        setTimeout(startStream, 500);
    }
});

// Camera source change
cameraSourceSelect.addEventListener('change', () => {
    if (isStreaming) {
        stopStream();
        setTimeout(startStream, 500);
    }
});

// Start stream
startBtn.addEventListener('click', startStream);

function startStream() {
    const source = cameraSourceSelect.value;
    const confidence = confidenceSlider.value;
    const streamUrl = `${API_BASE}/badge/stream?source=${source}&confidence=${confidence}`;

    videoStream.src = streamUrl;
    videoStream.style.display = 'block';
    streamPlaceholder.style.display = 'none';

    isStreaming = true;
    frameCount = 0;

    startBtn.disabled = true;
    stopBtn.disabled = false;
    snapshotBtn.disabled = false;
    cameraSourceSelect.disabled = true;

    document.getElementById('streamStatus').textContent = 'Active';
    document.getElementById('streamStatus').style.color = 'var(--success)';
    document.getElementById('cameraInfo').textContent = `Camera ${source}`;

    const frameCounter = setInterval(() => {
        if (!isStreaming) {
            clearInterval(frameCounter);
            return;
        }
        frameCount++;
        document.getElementById('totalFrames').textContent = frameCount;
    }, 100);

    utils.showToast('Badge detection stream started!', 'success');
}

// Stop stream
stopBtn.addEventListener('click', stopStream);

function stopStream() {
    videoStream.src = '';
    videoStream.style.display = 'none';
    streamPlaceholder.style.display = 'flex';

    isStreaming = false;

    startBtn.disabled = false;
    stopBtn.disabled = true;
    snapshotBtn.disabled = true;
    cameraSourceSelect.disabled = false;

    document.getElementById('streamStatus').textContent = 'Inactive';
    document.getElementById('streamStatus').style.color = 'var(--danger)';
    document.getElementById('currentDetections').textContent = '0';

    utils.showToast('Stream stopped', 'warning');
}

// Take snapshot - capture from current video stream
snapshotBtn.addEventListener('click', async () => {
    try {
        if (!isStreaming) {
            utils.showToast('Please start the stream first', 'warning');
            return;
        }

        utils.showLoading();

        const canvas = document.createElement('canvas');
        const context = canvas.getContext('2d');

        canvas.width = videoStream.naturalWidth || 640;
        canvas.height = videoStream.naturalHeight || 480;

        context.drawImage(videoStream, 0, 0, canvas.width, canvas.height);

        const base64Image = canvas.toDataURL('image/jpeg').split(',')[1];

        const snapshotData = {
            success: true,
            annotated_image: base64Image,
            total_detections: parseInt(document.getElementById('currentDetections').textContent) || 0
        };

        displaySnapshot(snapshotData);
        utils.showToast('Snapshot captured from stream!', 'success');

    } catch (error) {
        utils.showToast(`Error: ${error.message}`, 'error');
        console.error('Snapshot error:', error);
    } finally {
        utils.hideLoading();
    }
});

// Display snapshot
function displaySnapshot(data) {
    currentSnapshotData = data;

    document.getElementById('snapshotImage').src = `data:image/jpeg;base64,${data.annotated_image}`;
    document.getElementById('snapshotDetections').textContent = data.total_detections;
    document.getElementById('snapshotTime').textContent = utils.formatTimestamp();

    snapshotSection.classList.remove('hidden');
    snapshotSection.scrollIntoView({ behavior: 'smooth' });
}

// Download snapshot
document.getElementById('downloadSnapshotBtn').addEventListener('click', () => {
    if (currentSnapshotData) {
        utils.downloadImage(currentSnapshotData.annotated_image, `badge_snapshot_${Date.now()}.jpg`);
        utils.showToast('Snapshot downloaded!', 'success');
    }
});

// Close snapshot
document.getElementById('closeSnapshotBtn').addEventListener('click', () => {
    snapshotSection.classList.add('hidden');
    currentSnapshotData = null;
});

// Simulate detection count updates
setInterval(() => {
    if (isStreaming) {
        const randomDetections = Math.floor(Math.random() * 3);
        document.getElementById('currentDetections').textContent = randomDetections;
    }
}, 2000);

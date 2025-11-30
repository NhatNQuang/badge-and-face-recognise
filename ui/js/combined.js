// combined.js - JavaScript for combined detection page

let isStreaming = false;
let frameCount = 0;

const cameraSourceSelect = document.getElementById('cameraSource');
const confidenceSlider = document.getElementById('confidence');
const confidenceValue = document.getElementById('confidenceValue');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const videoStream = document.getElementById('videoStream');
const streamPlaceholder = document.getElementById('streamPlaceholder');

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
    const streamUrl = `${API_BASE}/combined/stream?source=${source}&confidence=${confidence}`;

    videoStream.src = streamUrl;
    videoStream.style.display = 'block';
    streamPlaceholder.style.display = 'none';

    isStreaming = true;
    frameCount = 0;

    startBtn.disabled = true;
    stopBtn.disabled = false;
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

    utils.showToast('Combined detection stream started!', 'success');
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
    cameraSourceSelect.disabled = false;

    document.getElementById('streamStatus').textContent = 'Inactive';
    document.getElementById('streamStatus').style.color = 'var(--danger)';
    document.getElementById('humanCount').textContent = '0';
    document.getElementById('badgeCount').textContent = '0';
    document.getElementById('totalCount').textContent = '0';

    utils.showToast('Stream stopped', 'warning');
}

// Simulate detection count updates (in real scenario, you'd parse from stream metadata)
setInterval(() => {
    if (isStreaming) {
        // Random counts for demo (in production, parse from stream)
        const humanCount = Math.floor(Math.random() * 3);
        const badgeCount = Math.floor(Math.random() * 2);

        document.getElementById('humanCount').textContent = humanCount;
        document.getElementById('badgeCount').textContent = badgeCount;
        document.getElementById('totalCount').textContent = humanCount + badgeCount;
    }
}, 2000);

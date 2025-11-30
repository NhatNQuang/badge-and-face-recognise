// API Configuration
const API_BASE = window.location.origin;

// Utility Functions
const utils = {
    // Show toast notification
    showToast(message, type = 'success') {
        const toast = document.createElement('div');
        toast.className = `toast ${type}`;
        toast.innerHTML = `
            <strong>${type.charAt(0).toUpperCase() + type.slice(1)}</strong>
            <p>${message}</p>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.3s ease reverse';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    // Show loading overlay
    showLoading() {
        const overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.id = 'loadingOverlay';
        overlay.innerHTML = '<div class="loading"></div>';
        document.body.appendChild(overlay);
    },

    // Hide loading overlay
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.remove();
    },

    // Fetch with error handling
    async fetchAPI(url, options = {}) {
        try {
            const response = await fetch(url, options);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            }
            
            return response;
        } catch (error) {
            console.error('API Error:', error);
            this.showToast(`Error: ${error.message}`, 'error');
            throw error;
        }
    },

    // Convert base64 to blob
    base64ToBlob(base64, contentType = 'image/jpeg') {
        const byteCharacters = atob(base64);
        const byteArrays = [];
        
        for (let offset = 0; offset < byteCharacters.length; offset += 512) {
            const slice = byteCharacters.slice(offset, offset + 512);
            const byteNumbers = new Array(slice.length);
            
            for (let i = 0; i < slice.length; i++) {
                byteNumbers[i] = slice.charCodeAt(i);
            }
            
            const byteArray = new Uint8Array(byteNumbers);
            byteArrays.push(byteArray);
        }
        
        return new Blob(byteArrays, { type: contentType });
    },

    // Format confidence score
    formatConfidence(confidence) {
        return (confidence * 100).toFixed(1) + '%';
    },

    // Format bounding box coordinates
    formatBBox(bbox) {
        return bbox.map(coord => Math.round(coord)).join(', ');
    },

    // Validate image file
    validateImageFile(file) {
        const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
        const maxSize = 10 * 1024 * 1024; // 10MB
        
        if (!validTypes.includes(file.type)) {
            throw new Error('Invalid file type. Please upload a JPEG, PNG, or WebP image.');
        }
        
        if (file.size > maxSize) {
            throw new Error('File too large. Maximum size is 10MB.');
        }
        
        return true;
    },

    // Create image element from base64
    createImageFromBase64(base64Data) {
        const img = document.createElement('img');
        img.src = `data:image/jpeg;base64,${base64Data}`;
        img.className = 'image-preview';
        return img;
    },

    // Download image
    downloadImage(base64Data, filename = 'detection_result.jpg') {
        const blob = this.base64ToBlob(base64Data);
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },

    // Animate element
    animateElement(element, animationClass = 'fade-in') {
        element.classList.add(animationClass);
    },

    // Debounce function
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    },

    // Format timestamp
    formatTimestamp(date = new Date()) {
        return date.toLocaleString('vi-VN', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });
    },

    // Calculate average
    average(arr) {
        if (arr.length === 0) return 0;
        return arr.reduce((a, b) => a + b, 0) / arr.length;
    },

    // Get detection class name
    getClassName(classId) {
        const classNames = {
            0: 'Person',
            // Add more class names if needed
        };
        return classNames[classId] || `Class ${classId}`;
    }
};

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = utils;
}

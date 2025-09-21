// Vietnamese AI Dubbing - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Vietnamese AI Dubbing loaded');

    // Progress bar animation
    function updateProgress(percent) {
        const progressBar = document.querySelector('.progress-fill');
        if (progressBar) {
            progressBar.style.width = percent + '%';
        }
    }

    // Status message updates
    function updateStatus(message, type = 'info') {
        const statusDiv = document.querySelector('.status');
        if (statusDiv) {
            statusDiv.className = `status ${type}`;
            statusDiv.textContent = message;
        }
    }

    // File upload validation
    const fileInput = document.querySelector('input[type="file"]');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/mkv', 'video/webm'];
                const maxSize = 500 * 1024 * 1024; // 500MB

                if (!validTypes.includes(file.type)) {
                    alert('Chỉ chấp nhận file video (MP4, AVI, MOV, MKV, WebM)');
                    e.target.value = '';
                    return;
                }

                if (file.size > maxSize) {
                    alert('File quá lớn! Tối đa 500MB');
                    e.target.value = '';
                    return;
                }

                updateStatus(`File được chọn: ${file.name} (${(file.size/1024/1024).toFixed(1)}MB)`, 'info');
            }
        });
    }

    // URL validation
    const urlInput = document.querySelector('input[placeholder*="youtube"]');
    if (urlInput) {
        urlInput.addEventListener('blur', function(e) {
            const url = e.target.value.trim();
            if (url) {
                const youtubeRegex = /^(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)\/.+/;
                const tiktokRegex = /^(https?:\/\/)?(www\.)?tiktok\.com\/.+/;

                if (!youtubeRegex.test(url) && !tiktokRegex.test(url)) {
                    updateStatus('URL không hợp lệ. Chỉ hỗ trợ YouTube và TikTok', 'error');
                } else {
                    updateStatus('URL hợp lệ', 'success');
                }
            }
        });
    }

    // Preview voice function
    window.previewVoice = function(voiceName) {
        updateStatus(`Đang tạo preview cho giọng: ${voiceName}...`, 'info');

        // This would be called from Gradio
        // For now, just show message
        setTimeout(() => {
            updateStatus('Preview hoàn thành!', 'success');
        }, 2000);
    };

    // Copy to clipboard function
    window.copyToClipboard = function(text) {
        navigator.clipboard.writeText(text).then(function() {
            updateStatus('Đã copy vào clipboard!', 'success');
        }).catch(function(err) {
            updateStatus('Không thể copy: ' + err, 'error');
        });
    };

    // Auto-hide status messages
    setInterval(function() {
        const statusMessages = document.querySelectorAll('.status');
        statusMessages.forEach(function(msg) {
            if (msg.classList.contains('success') || msg.classList.contains('error')) {
                setTimeout(() => {
                    msg.style.opacity = '0';
                    setTimeout(() => msg.remove(), 300);
                }, 5000);
            }
        });
    }, 1000);

    // Loading animation for buttons
    const buttons = document.querySelectorAll('button');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.textContent.includes('Bắt đầu') || this.textContent.includes('Preview')) {
                this.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
                this.disabled = true;
            }
        });
    });

    // Smooth scrolling
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey || e.metaKey) {
            switch(e.key) {
                case 'o':
                    e.preventDefault();
                    const fileInput = document.querySelector('input[type="file"]');
                    if (fileInput) fileInput.click();
                    break;
                case 'Enter':
                    const primaryBtn = document.querySelector('button[variant="primary"]');
                    if (primaryBtn && !primaryBtn.disabled) primaryBtn.click();
                    break;
            }
        }
    });

    // Initialize
    updateStatus('Sẵn sàng xử lý video!', 'success');

    // Add loading indicator for long operations
    window.showLoading = function(message = 'Đang xử lý...') {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'loading-overlay';
        loadingDiv.innerHTML = `
            <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%;
                        background: rgba(0,0,0,0.5); z-index: 9999; display: flex;
                        justify-content: center; align-items: center;">
                <div style="background: white; padding: 20px; border-radius: 10px;
                            text-align: center;">
                    <i class="fas fa-spinner fa-spin" style="font-size: 24px;"></i>
                    <p style="margin: 10px 0 0 0;">${message}</p>
                </div>
            </div>
        `;
        document.body.appendChild(loadingDiv);
    };

    window.hideLoading = function() {
        const loadingDiv = document.getElementById('loading-overlay');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    };
});
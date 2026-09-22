/**
 * Video QR Generator - Upload Controller with Real-time Progress
 */

document.addEventListener('DOMContentLoaded', () => {
  const dropzone = document.getElementById('upload-dropzone');
  const fileInput = document.getElementById('video-file-input');
  const form = document.getElementById('video-upload-form');
  const filePreview = document.getElementById('file-preview-card');
  const fileNameDisplay = document.getElementById('file-name-display');
  const fileSizeDisplay = document.getElementById('file-size-display');
  const titleInput = document.getElementById('video-title-input');
  const removeFileBtn = document.getElementById('remove-file-btn');
  const submitBtn = document.getElementById('submit-upload-btn');
  
  const progressContainer = document.getElementById('upload-progress-container');
  const progressBarFill = document.getElementById('progress-bar-fill');
  const progressPercent = document.getElementById('progress-percent');
  const progressSpeed = document.getElementById('progress-speed');
  const progressTime = document.getElementById('progress-time');

  if (!dropzone || !fileInput || !form) return;

  const allowedExtensions = ['mp4', 'webm', 'mov', 'mkv', 'avi', 'm4v'];

  // Trigger file selection on click
  dropzone.addEventListener('click', () => fileInput.click());

  // Drag and Drop Events
  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.add('dragover');
    });
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, (e) => {
      e.preventDefault();
      e.stopPropagation();
      dropzone.classList.remove('dragover');
    });
  });

  dropzone.addEventListener('drop', (e) => {
    const files = e.dataTransfer.files;
    if (files.length > 0) {
      handleFileSelected(files[0]);
    }
  });

  fileInput.addEventListener('change', (e) => {
    if (fileInput.files.length > 0) {
      handleFileSelected(fileInput.files[0]);
    }
  });

  if (removeFileBtn) {
    removeFileBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      resetFileInput();
    });
  }

  function handleFileSelected(file) {
    const ext = file.name.split('.').pop().toLowerCase();
    if (!allowedExtensions.includes(ext)) {
      showToast('Unsupported Format', `Please select a valid video file (.mp4, .webm, .mov, etc.)`, 'warning');
      resetFileInput();
      return;
    }

    // Check Max Size (default 500MB)
    const maxBytes = 500 * 1024 * 1024;
    if (file.size > maxBytes) {
      showToast('File Too Large', `Video size exceeds 500 MB limit.`, 'danger');
      resetFileInput();
      return;
    }

    // Update UI Preview
    dropzone.style.display = 'none';
    filePreview.style.display = 'block';
    fileNameDisplay.textContent = file.name;
    fileSizeDisplay.textContent = formatBytes(file.size);

    // Auto populate title if blank
    if (titleInput && !titleInput.value.trim()) {
      const baseName = file.name.substring(0, file.name.lastIndexOf('.')) || file.name;
      titleInput.value = baseName.replace(/[-_]/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }

    submitBtn.disabled = false;
  }

  function resetFileInput() {
    fileInput.value = '';
    dropzone.style.display = 'block';
    filePreview.style.display = 'none';
    submitBtn.disabled = true;
    progressContainer.style.display = 'none';
    progressBarFill.style.width = '0%';
  }

  // Handle Form Submission with XHR Progress
  form.addEventListener('submit', (e) => {
    e.preventDefault();

    if (!fileInput.files || fileInput.files.length === 0) {
      showToast('No Video Selected', 'Please choose a video file to upload.', 'warning');
      return;
    }

    const formData = new FormData(form);
    formData.append('is_ajax', '1');

    // UI state during upload
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="ri-loader-4-line ri-spin"></i> Uploading Video...';
    progressContainer.style.display = 'block';

    const xhr = new XMLHttpRequest();
    let startTime = Date.now();
    let lastLoaded = 0;

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable) {
        const percent = Math.round((e.loaded / e.total) * 100);
        progressBarFill.style.width = `${percent}%`;
        progressPercent.textContent = `${percent}%`;

        // Calculate transfer speed
        const elapsedSec = (Date.now() - startTime) / 1000;
        if (elapsedSec > 0.5) {
          const speedBps = e.loaded / elapsedSec;
          progressSpeed.textContent = `${(speedBps / (1024 * 1024)).toFixed(2)} MB/s`;

          // Estimate remaining time
          const remainingBytes = e.total - e.loaded;
          const remainingSec = Math.round(remainingBytes / speedBps);
          progressTime.textContent = remainingSec > 0 ? `~${remainingSec}s remaining` : 'Finalizing...';
        }
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const response = JSON.parse(xhr.responseText);
          if (response.success && response.redirect_url) {
            showToast('Success!', 'Video uploaded and QR code ready.', 'success');
            setTimeout(() => {
              window.location.href = response.redirect_url;
            }, 500);
          } else {
            showToast('Upload Failed', response.message || 'An error occurred.', 'danger');
            resetSubmitBtn();
          }
        } catch (err) {
          // If HTML response was returned, redirect to result
          window.location.reload();
        }
      } else {
        let msg = 'Upload failed with server error.';
        try {
          const errRes = JSON.parse(xhr.responseText);
          msg = errRes.message || msg;
        } catch (e) {}
        showToast('Upload Error', msg, 'danger');
        resetSubmitBtn();
      }
    });

    xhr.addEventListener('error', () => {
      showToast('Connection Error', 'Network error during video upload. Please retry.', 'danger');
      resetSubmitBtn();
    });

    xhr.open('POST', form.action, true);
    xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    xhr.send(formData);
  });

  function resetSubmitBtn() {
    submitBtn.disabled = false;
    submitBtn.innerHTML = '<i class="ri-qr-code-line"></i> Upload & Generate QR Code';
  }

  function formatBytes(bytes, decimals = 2) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
  }
});

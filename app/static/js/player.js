/**
 * Video QR Generator - Custom HTML5 Video Player Engine
 */

document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('custom-player-container');
  const wrapper = document.getElementById('custom-player-wrapper');
  const video = document.getElementById('main-video-player');
  
  if (!container || !video) return;

  const centerPlayBtn = document.getElementById('center-play-btn');
  const playPauseBtn = document.getElementById('play-pause-btn');
  const muteBtn = document.getElementById('mute-btn');
  const volumeSlider = document.getElementById('volume-slider');
  const currentTimeEl = document.getElementById('current-time');
  const durationEl = document.getElementById('duration-time');
  const timelineContainer = document.getElementById('timeline-container');
  const timelineProgress = document.getElementById('timeline-progress');
  const timelineBuffered = document.getElementById('timeline-buffered');
  const timelineThumb = document.getElementById('timeline-thumb');
  const fullscreenBtn = document.getElementById('fullscreen-btn');
  const theaterBtn = document.getElementById('theater-btn');
  const speedSelect = document.getElementById('speed-select');
  const pipBtn = document.getElementById('pip-btn');

  let controlsTimeout = null;
  let isDraggingScrubber = false;

  // Initial volume setup
  const savedVolume = localStorage.getItem('vqr_player_volume') || '1';
  video.volume = parseFloat(savedVolume);
  if (volumeSlider) volumeSlider.value = video.volume;
  updateVolumeIcon(video.volume);

  // Play / Pause toggles
  function togglePlay() {
    if (video.paused || video.ended) {
      const playPromise = video.play();
      if (playPromise !== undefined) {
        playPromise.then(() => {
          container.classList.add('playing');
        }).catch(err => {
          console.warn('Direct play error, attempting fallback:', err);
          // Try playing muted if sound policy blocked it
          video.muted = true;
          video.play().then(() => {
            container.classList.add('playing');
            if (typeof showToast === 'function') {
              showToast('Playing Muted', 'Click unmute icon to enable audio', 'info');
            }
          }).catch(e2 => {
            console.error('Video play completely failed:', e2);
          });
        });
      }
    } else {
      video.pause();
    }
  }

  // Handle center play button directly
  if (centerPlayBtn) {
    centerPlayBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      togglePlay();
    });
  }

  container.addEventListener('click', (e) => {
    // If click was inside control bar or buttons, do not trigger play/pause
    if (e.target.closest('.player-controls')) return;
    togglePlay();
  });

  if (playPauseBtn) playPauseBtn.addEventListener('click', (e) => {
    e.stopPropagation();
    togglePlay();
  });

  video.addEventListener('play', () => {
    container.classList.add('playing');
    if (playPauseBtn) playPauseBtn.innerHTML = '<i class="ri-pause-fill"></i>';
    resetControlsTimer();
  });

  video.addEventListener('pause', () => {
    container.classList.remove('playing');
    container.classList.remove('hide-controls');
    if (playPauseBtn) playPauseBtn.innerHTML = '<i class="ri-play-fill"></i>';
    clearTimeout(controlsTimeout);
  });

  video.addEventListener('error', (e) => {
    console.error('Video Element Error:', video.error);
    if (typeof showToast === 'function') {
      showToast('Video Notice', 'Your browser could not stream this codec directly. Please use Download Video.', 'warning');
    }
  });

  // Time formatting (MM:SS or HH:MM:SS)
  function formatTime(seconds) {
    if (isNaN(seconds) || seconds < 0) return '00:00';
    const s = Math.floor(seconds % 60);
    const m = Math.floor((seconds / 60) % 60);
    const h = Math.floor(seconds / 3600);

    const sStr = s < 10 ? `0${s}` : `${s}`;
    const mStr = m < 10 ? `0${m}` : `${m}`;
    if (h > 0) {
      return `${h}:${mStr}:${sStr}`;
    }
    return `${mStr}:${sStr}`;
  }

  // Update Progress & Time Display
  video.addEventListener('loadedmetadata', () => {
    if (durationEl) durationEl.textContent = formatTime(video.duration);
  });

  video.addEventListener('timeupdate', () => {
    if (currentTimeEl) currentTimeEl.textContent = formatTime(video.currentTime);
    if (!isDraggingScrubber && video.duration) {
      const percent = (video.currentTime / video.duration) * 100;
      if (timelineProgress) timelineProgress.style.width = `${percent}%`;
      if (timelineThumb) timelineThumb.style.left = `${percent}%`;
    }
  });

  // Buffer progress
  video.addEventListener('progress', () => {
    if (video.buffered.length > 0 && video.duration) {
      const bufferedEnd = video.buffered.end(video.buffered.length - 1);
      const bufferedPercent = (bufferedEnd / video.duration) * 100;
      if (timelineBuffered) timelineBuffered.style.width = `${bufferedPercent}%`;
    }
  });

  // Scrubber / Timeline Seeking
  if (timelineContainer) {
    function seekTo(e) {
      const rect = timelineContainer.getBoundingClientRect();
      const pos = Math.max(0, Math.min(1, (e.clientX - rect.left) / rect.width));
      if (video.duration) {
        video.currentTime = pos * video.duration;
        const percent = pos * 100;
        if (timelineProgress) timelineProgress.style.width = `${percent}%`;
        if (timelineThumb) timelineThumb.style.left = `${percent}%`;
      }
    }

    timelineContainer.addEventListener('mousedown', (e) => {
      isDraggingScrubber = true;
      seekTo(e);
    });

    window.addEventListener('mousemove', (e) => {
      if (isDraggingScrubber) seekTo(e);
    });

    window.addEventListener('mouseup', () => {
      if (isDraggingScrubber) isDraggingScrubber = false;
    });

    // Touch support for mobile seeking
    timelineContainer.addEventListener('touchstart', (e) => {
      if (e.touches.length > 0) {
        isDraggingScrubber = true;
        seekTo(e.touches[0]);
      }
    });

    window.addEventListener('touchmove', (e) => {
      if (isDraggingScrubber && e.touches.length > 0) {
        seekTo(e.touches[0]);
      }
    });

    window.addEventListener('touchend', () => {
      isDraggingScrubber = false;
    });
  }

  // Volume & Mute Controls
  if (volumeSlider) {
    volumeSlider.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value);
      video.volume = val;
      video.muted = (val === 0);
      localStorage.setItem('vqr_player_volume', val);
      updateVolumeIcon(val);
    });
  }

  if (muteBtn) {
    muteBtn.addEventListener('click', () => {
      video.muted = !video.muted;
      if (video.muted) {
        updateVolumeIcon(0);
        if (volumeSlider) volumeSlider.value = 0;
      } else {
        const val = video.volume || 1;
        updateVolumeIcon(val);
        if (volumeSlider) volumeSlider.value = val;
      }
    });
  }

  function updateVolumeIcon(vol) {
    if (!muteBtn) return;
    if (vol === 0 || video.muted) {
      muteBtn.innerHTML = '<i class="ri-volume-mute-fill"></i>';
    } else if (vol < 0.5) {
      muteBtn.innerHTML = '<i class="ri-volume-down-fill"></i>';
    } else {
      muteBtn.innerHTML = '<i class="ri-volume-up-fill"></i>';
    }
  }

  // Speed Selector
  if (speedSelect) {
    speedSelect.addEventListener('change', (e) => {
      video.playbackRate = parseFloat(e.target.value);
    });
  }

  // Theater Mode
  if (theaterBtn && wrapper) {
    theaterBtn.addEventListener('click', () => {
      wrapper.classList.toggle('theater-mode');
      const isTheater = wrapper.classList.contains('theater-mode');
      theaterBtn.innerHTML = isTheater 
        ? '<i class="ri-layout-right-line"></i>' 
        : '<i class="ri-aspect-ratio-line"></i>';
    });
  }

  // Picture in Picture
  if (pipBtn) {
    if (document.pictureInPictureEnabled) {
      pipBtn.addEventListener('click', async () => {
        try {
          if (document.pictureInPictureElement) {
            await document.exitPictureInPicture();
          } else {
            await video.requestPictureInPicture();
          }
        } catch (err) {
          console.log('PiP Error:', err);
        }
      });
    } else {
      pipBtn.style.display = 'none';
    }
  }

  // Fullscreen
  if (fullscreenBtn) {
    fullscreenBtn.addEventListener('click', toggleFullscreen);
  }

  function toggleFullscreen() {
    if (!document.fullscreenElement) {
      if (wrapper.requestFullscreen) {
        wrapper.requestFullscreen();
      } else if (video.webkitEnterFullscreen) {
        // iOS Safari full screen fallback
        video.webkitEnterFullscreen();
      }
    } else {
      if (document.exitFullscreen) {
        document.exitFullscreen();
      }
    }
  }

  document.addEventListener('fullscreenchange', () => {
    if (fullscreenBtn) {
      fullscreenBtn.innerHTML = document.fullscreenElement 
        ? '<i class="ri-fullscreen-exit-fill"></i>' 
        : '<i class="ri-fullscreen-fill"></i>';
    }
  });

  // Auto Hide Controls on Inactivity
  function resetControlsTimer() {
    container.classList.remove('hide-controls');
    clearTimeout(controlsTimeout);
    if (!video.paused) {
      controlsTimeout = setTimeout(() => {
        if (!video.paused && !isDraggingScrubber) {
          container.classList.add('hide-controls');
        }
      }, 2500);
    }
  }

  container.addEventListener('mousemove', resetControlsTimer);
  container.addEventListener('touchstart', resetControlsTimer);

  // Keyboard Navigation Shortcuts
  window.addEventListener('keydown', (e) => {
    // Avoid triggering if typing in an input
    if (['INPUT', 'TEXTAREA', 'SELECT'].includes(document.activeElement.tagName)) return;

    switch (e.key.toLowerCase()) {
      case ' ':
      case 'k':
        e.preventDefault();
        togglePlay();
        break;
      case 'm':
        e.preventDefault();
        if (muteBtn) muteBtn.click();
        break;
      case 'f':
        e.preventDefault();
        toggleFullscreen();
        break;
      case 't':
        e.preventDefault();
        if (theaterBtn) theaterBtn.click();
        break;
      case 'arrowleft':
        e.preventDefault();
        video.currentTime = Math.max(0, video.currentTime - 5);
        break;
      case 'arrowright':
        e.preventDefault();
        if (video.duration) {
          video.currentTime = Math.min(video.duration, video.currentTime + 5);
        }
        break;
      case 'arrowup':
        e.preventDefault();
        video.volume = Math.min(1, video.volume + 0.1);
        if (volumeSlider) volumeSlider.value = video.volume;
        updateVolumeIcon(video.volume);
        break;
      case 'arrowdown':
        e.preventDefault();
        video.volume = Math.max(0, video.volume - 0.1);
        if (volumeSlider) volumeSlider.value = video.volume;
        updateVolumeIcon(video.volume);
        break;
    }
  });
});

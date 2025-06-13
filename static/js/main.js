// Main JavaScript functionality for Paraulins

// Global variables
let currentAudio = null;
let currentPlayButton = null;

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;

    // Insert at the top of the container
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function setButtonLoading(button, loading = true) {
    if (loading) {
        button.disabled = true;
        button.classList.add('loading');
        button.dataset.originalText = button.innerHTML;
        button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
    } else {
        button.disabled = false;
        button.classList.remove('loading');
        if (button.dataset.originalText) {
            button.innerHTML = button.dataset.originalText;
            delete button.dataset.originalText;
        }
    }
}

// API functions
async function apiRequest(url, options = {}) {
    try {
        const response = await fetch(url, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Request failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
}

// Child management
async function addChild() {
    const nameInput = document.getElementById('childName');
    const name = nameInput.value.trim();

    if (!name) {
        showAlert('Please enter a child\'s name', 'warning');
        return;
    }

    const addButton = document.querySelector('#addChildModal .btn-primary');
    setButtonLoading(addButton);

    try {
        await apiRequest('/api/children', {
            method: 'POST',
            body: JSON.stringify({ name })
        });

        showAlert(`${name} has been added successfully!`, 'success');

        // Close modal and reset form
        bootstrap.Modal.getInstance(document.getElementById('addChildModal')).hide();
        nameInput.value = '';

        // Reload page to show new child
        setTimeout(() => window.location.reload(), 1000);

    } catch (error) {
        showAlert(`Failed to add child: ${error.message}`, 'danger');
    } finally {
        setButtonLoading(addButton, false);
    }
}

// Word management
let isAddingWord = false; // Flag to prevent duplicate submissions

async function addWord(childName) {
    // Prevent duplicate submissions
    if (isAddingWord) {
        return;
    }

    const textInput = document.getElementById('wordText');
    const text = textInput.value.trim();

    if (!text) {
        showAlert('Please enter a word', 'warning');
        return;
    }

    isAddingWord = true; // Set flag to prevent duplicates
    const addButton = document.querySelector('#addWordModal .btn-primary');
    setButtonLoading(addButton);

    try {
        await apiRequest(`/api/children/${encodeURIComponent(childName)}/words`, {
            method: 'POST',
            body: JSON.stringify({ text })
        });

        showAlert(`Word "${text}" has been added successfully!`, 'success');

        // Close modal and reset form
        bootstrap.Modal.getInstance(document.getElementById('addWordModal')).hide();
        textInput.value = '';

        // Reload page to show new word
        setTimeout(() => window.location.reload(), 1000);

    } catch (error) {
        showAlert(`Failed to add word: ${error.message}`, 'danger');
    } finally {
        isAddingWord = false; // Reset flag
        setButtonLoading(addButton, false);
    }
}

// Recording management (legacy function for backward compatibility)
async function addRecording(childName) {
    // This function is now handled by saveRecording
    await saveRecording(childName);
}

// Image management
async function addImage(childName) {
    const fileInput = document.getElementById('imageFile');
    const file = fileInput.files[0];

    if (!file) {
        showAlert('Please select an image file', 'warning');
        return;
    }

    const addButton = document.querySelector('#addImageModal .btn-primary');
    setButtonLoading(addButton);

    try {
        const formData = new FormData();
        formData.append('image', file);

        const response = await fetch(`/api/children/${encodeURIComponent(childName)}/words/${encodeURIComponent(currentWord)}/image`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }

        showAlert(`Image for "${currentWord}" has been uploaded successfully!`, 'success');

        // Close modal and reset form
        bootstrap.Modal.getInstance(document.getElementById('addImageModal')).hide();
        fileInput.value = '';

        // Reload page to show new image
        setTimeout(() => window.location.reload(), 1000);

    } catch (error) {
        showAlert(`Failed to upload image: ${error.message}`, 'danger');
    } finally {
        setButtonLoading(addButton, false);
    }
}

// Audio playback
function playAudio(childName, wordText, year, month, day, filename) {
    const button = event.target.closest('.play-btn');

    // Stop current audio if playing
    if (currentAudio && !currentAudio.paused) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        if (currentPlayButton) {
            currentPlayButton.classList.remove('playing');
            const originalText = currentPlayButton.textContent.trim();
            currentPlayButton.innerHTML = '<i class="fas fa-play me-1"></i>' + originalText.replace('⏸️', '');
        }
    }

    // If clicking the same button that was playing, just stop
    if (currentPlayButton === button && button.classList.contains('playing')) {
        button.classList.remove('playing');
        const originalText = button.textContent.trim();
        button.innerHTML = '<i class="fas fa-play me-1"></i>' + originalText.replace('⏸️', '');
        currentPlayButton = null;
        currentAudio = null;
        return;
    }

    // Set up new audio
    currentAudio = new Audio(`/api/audio/${encodeURIComponent(childName)}/${encodeURIComponent(wordText)}/${encodeURIComponent(filename)}`);
    currentPlayButton = button;

    // Update button state
    button.classList.add('playing');
    const originalText = button.textContent.trim();
    button.innerHTML = '<i class="fas fa-pause me-1"></i>' + originalText.replace('▶️', '');

    // Set up event listeners
    currentAudio.onended = () => {
        button.classList.remove('playing');
        const originalText = button.textContent.trim();
        button.innerHTML = '<i class="fas fa-play me-1"></i>' + originalText.replace('⏸️', '');
        currentPlayButton = null;
        currentAudio = null;
    };

    currentAudio.onerror = () => {
        button.classList.remove('playing');
        const originalText = button.textContent.trim();
        button.innerHTML = '<i class="fas fa-play me-1"></i>' + originalText.replace('⏸️', '');
        showAlert('Failed to play audio file', 'danger');
        currentPlayButton = null;
        currentAudio = null;
    };

    // Play the audio
    currentAudio.play().catch(error => {
        console.error('Audio playback failed:', error);
        showAlert('Failed to play audio file', 'danger');
        button.classList.remove('playing');
        const originalText = button.textContent.trim();
        button.innerHTML = '<i class="fas fa-play me-1"></i>' + originalText.replace('⏸️', '');
        currentPlayButton = null;
        currentAudio = null;
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Initialize recording modal if it exists
    if (document.getElementById('addRecordingModal')) {
        initializeRecordingModal();
    }

    // Add click listeners to play buttons
    document.addEventListener('click', function(event) {
        if (event.target.closest('.play-btn')) {
            const button = event.target.closest('.play-btn');
            const childName = button.dataset.child;
            const wordText = button.dataset.word;
            const year = button.dataset.year;
            const month = button.dataset.month || '1'; // Default to January for legacy data
            const day = button.dataset.day || '1'; // Default to 1st day for legacy data
            const filename = button.dataset.filename;

            playAudio(childName, wordText, year, month, day, filename);
        }
    });

    // Form submission handlers
    document.getElementById('addChildForm')?.addEventListener('submit', function(e) {
        e.preventDefault();
        addChild();
    });

    document.getElementById('addWordForm')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const childName = new URLSearchParams(window.location.search).get('child') ||
                          document.body.getAttribute('data-child-name');
        addWord(childName);
    });

    document.getElementById('addRecordingForm')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const childName = new URLSearchParams(window.location.search).get('child') ||
                          document.body.getAttribute('data-child-name');
        addRecording(childName);
    });

    document.getElementById('addImageForm')?.addEventListener('submit', function(e) {
        e.preventDefault();
        const childName = new URLSearchParams(window.location.search).get('child') ||
                          document.body.getAttribute('data-child-name');
        addImage(childName);
    });

    // Auto-focus on modal inputs
    document.addEventListener('shown.bs.modal', function(event) {
        const modal = event.target;
        const input = modal.querySelector('input[type="text"], input[type="number"]');
        if (input) {
            input.focus();
        }

        // Reset recording modal when shown
        if (modal.id === 'addRecordingModal') {
            resetRecordingModal();
        }
    });

    // Clean up audio recorder when modal is hidden
    document.addEventListener('hidden.bs.modal', function(event) {
        const modal = event.target;
        if (modal.id === 'addRecordingModal' && audioRecorder) {
            audioRecorder.cleanup();
        }
    });
});

// Audio Trimming functionality
class AudioTrimmer {
    constructor(audioElement, canvasId, overlayId, playheadId, startTimeId, endTimeId, selectionInfoId) {
        this.audio = audioElement;
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.overlay = document.getElementById(overlayId);
        this.playhead = document.getElementById(playheadId);
        this.startTimeInput = document.getElementById(startTimeId);
        this.endTimeInput = document.getElementById(endTimeId);
        this.selectionInfo = document.getElementById(selectionInfoId);

        this.audioBuffer = null;
        this.audioContext = null;
        this.startTime = 0;
        this.endTime = 0;
        this.duration = 0;
        this.isSelecting = false;
        this.selectionStart = 0;
        this.selectionEnd = 0;

        this.setupEventListeners();
    }

    async loadAudio(audioSrc) {
        try {
            // Create audio context
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();

            // Load audio data
            let audioData;
            if (audioSrc instanceof Blob) {
                audioData = await audioSrc.arrayBuffer();
            } else {
                const response = await fetch(audioSrc);
                audioData = await response.arrayBuffer();
            }

            // Decode audio data
            this.audioBuffer = await this.audioContext.decodeAudioData(audioData);
            this.duration = this.audioBuffer.duration;

            // Reset selection to full audio
            this.startTime = 0;
            this.endTime = this.duration;
            this.startTimeInput.value = 0;
            this.endTimeInput.value = this.duration.toFixed(1);
            this.startTimeInput.max = this.duration;
            this.endTimeInput.max = this.duration;

            // Draw waveform
            this.drawWaveform();
            this.updateSelectionInfo();

        } catch (error) {
            console.error('Error loading audio for trimming:', error);
            showAlert('Failed to load audio for trimming', 'warning');
        }
    }

    drawWaveform() {
        if (!this.audioBuffer) return;

        const width = this.canvas.width = this.canvas.offsetWidth;
        const height = this.canvas.height = this.canvas.offsetHeight;

        this.ctx.clearRect(0, 0, width, height);

        // Get audio data (use first channel)
        const data = this.audioBuffer.getChannelData(0);
        const step = Math.ceil(data.length / width);
        const amp = height / 2;

        // Draw waveform
        this.ctx.fillStyle = '#007bff';
        this.ctx.globalAlpha = 0.6;

        for (let i = 0; i < width; i++) {
            let min = 1.0;
            let max = -1.0;

            for (let j = 0; j < step; j++) {
                const datum = data[(i * step) + j];
                if (datum < min) min = datum;
                if (datum > max) max = datum;
            }

            const yMin = (1 + min) * amp;
            const yMax = (1 + max) * amp;

            this.ctx.fillRect(i, yMin, 1, yMax - yMin);
        }

        this.ctx.globalAlpha = 1.0;

        // Draw center line
        this.ctx.strokeStyle = '#dee2e6';
        this.ctx.lineWidth = 1;
        this.ctx.beginPath();
        this.ctx.moveTo(0, height / 2);
        this.ctx.lineTo(width, height / 2);
        this.ctx.stroke();

        this.updateSelectionOverlay();
    }

    updateSelectionOverlay() {
        if (!this.duration) return;

        const containerWidth = this.canvas.offsetWidth;
        const startPercent = (this.startTime / this.duration) * 100;
        const endPercent = (this.endTime / this.duration) * 100;
        const widthPercent = endPercent - startPercent;

        this.overlay.style.left = startPercent + '%';
        this.overlay.style.width = widthPercent + '%';
        this.overlay.style.display = 'block';
    }

    setupEventListeners() {
        // Canvas mouse events for selection
        this.canvas.addEventListener('mousedown', (e) => {
            if (!this.duration) return;
            this.isSelecting = true;
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const percent = x / rect.width;
            this.selectionStart = percent * this.duration;
            this.startTime = this.selectionStart;
            this.startTimeInput.value = this.startTime.toFixed(1);
        });

        this.canvas.addEventListener('mousemove', (e) => {
            if (!this.isSelecting || !this.duration) return;
            const rect = this.canvas.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const percent = Math.max(0, Math.min(1, x / rect.width));
            this.selectionEnd = percent * this.duration;

            // Ensure proper order
            this.startTime = Math.min(this.selectionStart, this.selectionEnd);
            this.endTime = Math.max(this.selectionStart, this.selectionEnd);

            this.startTimeInput.value = this.startTime.toFixed(1);
            this.endTimeInput.value = this.endTime.toFixed(1);

            this.updateSelectionOverlay();
            this.updateSelectionInfo();
        });

        this.canvas.addEventListener('mouseup', () => {
            this.isSelecting = false;
        });

        // Time input events
        this.startTimeInput.addEventListener('input', () => {
            this.startTime = Math.max(0, Math.min(parseFloat(this.startTimeInput.value) || 0, this.duration));
            this.endTime = Math.max(this.startTime, this.endTime);
            this.endTimeInput.value = this.endTime.toFixed(1);
            this.updateSelectionOverlay();
            this.updateSelectionInfo();
        });

        this.endTimeInput.addEventListener('input', () => {
            this.endTime = Math.max(0, Math.min(parseFloat(this.endTimeInput.value) || 0, this.duration));
            this.startTime = Math.min(this.startTime, this.endTime);
            this.startTimeInput.value = this.startTime.toFixed(1);
            this.updateSelectionOverlay();
            this.updateSelectionInfo();
        });

        // Audio time update for playhead
        if (this.audio) {
            this.audio.addEventListener('timeupdate', () => {
                this.updatePlayhead();
            });
        }
    }

    updatePlayhead() {
        if (!this.duration || !this.audio) return;

        const currentTime = this.audio.currentTime;
        const percent = (currentTime / this.duration) * 100;

        this.playhead.style.left = percent + '%';
        this.playhead.style.display = currentTime > 0 ? 'block' : 'none';
    }

    updateSelectionInfo() {
        if (!this.duration) {
            this.selectionInfo.textContent = 'No audio loaded';
            return;
        }

        const selectionDuration = this.endTime - this.startTime;
        const isFullAudio = this.startTime === 0 && Math.abs(this.endTime - this.duration) < 0.1;

        if (isFullAudio) {
            this.selectionInfo.textContent = 'Full audio (no trimming)';
        } else {
            this.selectionInfo.textContent = `${this.startTime.toFixed(1)}s - ${this.endTime.toFixed(1)}s (${selectionDuration.toFixed(1)}s)`;
        }
    }

    playSelection() {
        if (!this.audio || !this.duration) return;

        this.audio.currentTime = this.startTime;
        this.audio.play();

        // Stop at end time
        const checkTime = () => {
            if (this.audio.currentTime >= this.endTime) {
                this.audio.pause();
            } else if (!this.audio.paused) {
                requestAnimationFrame(checkTime);
            }
        };

        if (this.endTime < this.duration) {
            requestAnimationFrame(checkTime);
        }
    }

    resetSelection() {
        this.startTime = 0;
        this.endTime = this.duration;
        this.startTimeInput.value = 0;
        this.endTimeInput.value = this.duration.toFixed(1);
        this.updateSelectionOverlay();
        this.updateSelectionInfo();
    }

    getSelection() {
        const isFullAudio = this.startTime === 0 && Math.abs(this.endTime - this.duration) < 0.1;
        return {
            startTime: this.startTime,
            endTime: this.endTime,
            isFullAudio: isFullAudio
        };
    }

    async getTrimmedBlob(originalBlob) {
        const selection = this.getSelection();
        if (selection.isFullAudio) {
            return originalBlob;
        }

        return this.trimAudioBlob(originalBlob, selection.startTime, selection.endTime);
    }

    async trimAudioBlob(blob, startTime, endTime) {
        try {
            // This is a simplified version - for production you might want to use FFmpeg.js
            // For now, we'll return the original blob and handle trimming on the server
            console.log(`Would trim audio from ${startTime}s to ${endTime}s`);
            return blob;
        } catch (error) {
            console.error('Error trimming audio:', error);
            return blob;
        }
    }

    cleanup() {
        if (this.audioContext && this.audioContext.state !== 'closed') {
            this.audioContext.close();
        }
        this.audioBuffer = null;
        this.audioContext = null;
    }
}

// Global audio trimmer instances
let audioTrimmer = null;
let uploadTrimmer = null;

// Audio Recording functionality
class AudioRecorder {
    constructor() {
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.recordedBlob = null;
        this.stream = null;
        this.startTime = null;
        this.timerInterval = null;
        this.maxRecordingTime = 60000; // 60 seconds in milliseconds
        this.autoStopTimeout = null;
    }

    async requestPermission() {
        try {
            // Show permission request message
            const permissionAlert = document.getElementById('permissionAlert');
            const permissionMessage = document.getElementById('permissionMessage');

            if (permissionAlert && permissionMessage) {
                permissionMessage.textContent = 'Requesting microphone access...';
                permissionAlert.classList.remove('d-none');
            }

            this.stream = await navigator.mediaDevices.getUserMedia({
                audio: {
                    echoCancellation: true,
                    noiseSuppression: true,
                    sampleRate: 44100
                }
            });

            // Hide permission alert on success
            if (permissionAlert) {
                permissionAlert.classList.add('d-none');
            }

            return true;
        } catch (error) {
            console.error('Error accessing microphone:', error);

            let message = 'Failed to access microphone. ';
            if (error.name === 'NotAllowedError') {
                message += 'Please allow microphone access and try again.';
            } else if (error.name === 'NotFoundError') {
                message += 'No microphone found. Please connect a microphone and try again.';
            } else {
                message += 'Please check your microphone settings.';
            }

            // Show error in permission alert
            const permissionAlert = document.getElementById('permissionAlert');
            const permissionMessage = document.getElementById('permissionMessage');

            if (permissionAlert && permissionMessage) {
                permissionAlert.classList.remove('alert-warning');
                permissionAlert.classList.add('alert-danger');
                permissionMessage.innerHTML = `<strong>Error:</strong> ${message}`;
                permissionAlert.classList.remove('d-none');
            } else {
                showAlert(message, 'danger');
            }

            return false;
        }
    }

    startRecording() {
        if (!this.stream) return false;

        this.audioChunks = [];
        this.recordedBlob = null;

        try {
            // Try different audio formats in order of preference
            let options = {};

            if (MediaRecorder.isTypeSupported('audio/webm;codecs=opus')) {
                options.mimeType = 'audio/webm;codecs=opus';
            } else if (MediaRecorder.isTypeSupported('audio/webm')) {
                options.mimeType = 'audio/webm';
            } else if (MediaRecorder.isTypeSupported('audio/ogg;codecs=opus')) {
                options.mimeType = 'audio/ogg;codecs=opus';
            } else if (MediaRecorder.isTypeSupported('audio/mp4')) {
                options.mimeType = 'audio/mp4';
            }
            // If none supported, let browser choose default

            this.mediaRecorder = new MediaRecorder(this.stream, options);

            this.mediaRecorder.ondataavailable = (event) => {
                if (event.data.size > 0) {
                    this.audioChunks.push(event.data);
                }
            };

            this.mediaRecorder.onstop = () => {
                this.recordedBlob = new Blob(this.audioChunks, {
                    type: this.mediaRecorder.mimeType || 'audio/webm'
                });
                this.updatePlaybackSection();
            };

            this.mediaRecorder.start(1000); // Collect data every second
            this.startTime = Date.now();
            this.startTimer();

            // Auto-stop after max recording time
            this.autoStopTimeout = setTimeout(() => {
                if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
                    this.stopRecording();
                    showAlert('Recording stopped automatically after 60 seconds', 'info');
                }
            }, this.maxRecordingTime);

            return true;
        } catch (error) {
            console.error('Error starting recording:', error);
            showAlert('Failed to start recording. Please try again.', 'danger');
            return false;
        }
    }

    stopRecording() {
        if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
            this.mediaRecorder.stop();
            this.stopTimer();

            // Clear auto-stop timeout
            if (this.autoStopTimeout) {
                clearTimeout(this.autoStopTimeout);
                this.autoStopTimeout = null;
            }

            return true;
        }
        return false;
    }

    startTimer() {
        this.updateTimer();
        this.timerInterval = setInterval(() => {
            this.updateTimer();
        }, 1000);
    }

    stopTimer() {
        if (this.timerInterval) {
            clearInterval(this.timerInterval);
            this.timerInterval = null;
        }
    }

    updateTimer() {
        if (this.startTime) {
            const elapsed = Math.floor((Date.now() - this.startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const seconds = elapsed % 60;
            const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;

            const statusText = document.getElementById('recordingStatusText');
            if (statusText) {
                statusText.textContent = `Recording... ${timeString}`;
            }

            // Update progress bar
            const progressBar = document.getElementById('recordingProgress');
            if (progressBar) {
                const progressPercent = Math.min((elapsed / 60) * 100, 100);
                progressBar.style.width = `${progressPercent}%`;

                // Change color as it approaches limit
                if (progressPercent > 80) {
                    progressBar.classList.remove('bg-success', 'bg-warning');
                    progressBar.classList.add('bg-danger');
                } else if (progressPercent > 60) {
                    progressBar.classList.remove('bg-success', 'bg-danger');
                    progressBar.classList.add('bg-warning');
                } else {
                    progressBar.classList.remove('bg-warning', 'bg-danger');
                    progressBar.classList.add('bg-success');
                }
            }
        }
    }

    updatePlaybackSection() {
        if (this.recordedBlob) {
            const playbackSection = document.getElementById('playbackSection');
            const recordingPreview = document.getElementById('recordingPreview');
            const durationSpan = document.getElementById('recordingDuration');

            if (playbackSection && recordingPreview) {
                const audioUrl = URL.createObjectURL(this.recordedBlob);
                recordingPreview.src = audioUrl;
                playbackSection.classList.remove('d-none');

                // Update duration when metadata loads
                recordingPreview.addEventListener('loadedmetadata', async () => {
                    const duration = Math.round(recordingPreview.duration);
                    if (durationSpan) {
                        durationSpan.textContent = `${duration}s`;
                    }

                    // Initialize audio trimmer
                    if (!audioTrimmer) {
                        audioTrimmer = new AudioTrimmer(
                            recordingPreview,
                            'waveformCanvas',
                            'selectionOverlay',
                            'playheadIndicator',
                            'startTime',
                            'endTime',
                            'selectionInfo'
                        );
                    }

                    // Load audio for trimming
                    await audioTrimmer.loadAudio(this.recordedBlob);
                }, { once: true });
            }
        }
    }

    getRecordedBlob() {
        return this.recordedBlob;
    }

    cleanup() {
        this.stopTimer();

        // Clear auto-stop timeout
        if (this.autoStopTimeout) {
            clearTimeout(this.autoStopTimeout);
            this.autoStopTimeout = null;
        }

        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.stream = null;
        }
        if (this.recordedBlob) {
            URL.revokeObjectURL(document.getElementById('recordingPreview')?.src);
        }
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.recordedBlob = null;
    }
}

// Global audio recorder instance
let audioRecorder = null;

// Recording management functions
function initializeRecordingModal() {
    // Initialize audio recorder
    audioRecorder = new AudioRecorder();

    // Set up event listeners
    const methodRadios = document.querySelectorAll('input[name="recordingMethod"]');
    const recordingSection = document.getElementById('recordingSection');
    const uploadSection = document.getElementById('uploadSection');
    const startBtn = document.getElementById('startRecordBtn');
    const stopBtn = document.getElementById('stopRecordBtn');
    const playBtn = document.getElementById('playRecordingBtn');
    const reRecordBtn = document.getElementById('reRecordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const playbackSection = document.getElementById('playbackSection');
    const saveBtn = document.getElementById('saveRecordingBtn');
    const saveText = document.getElementById('saveRecordingText');
    const fileInput = document.getElementById('recordingFile');

    // Method selection handler
    methodRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            const isRecord = e.target.value === 'record';

            if (recordingSection && uploadSection) {
                recordingSection.classList.toggle('d-none', !isRecord);
                uploadSection.classList.toggle('d-none', isRecord);
            }

            // Update save button text
            if (saveText) {
                saveText.textContent = isRecord ? 'Save Recording' : 'Upload Recording';
            }

            // Reset recording state when switching methods
            if (isRecord) {
                resetRecordingState();
            } else {
                // Reset upload preview
                const uploadPreviewSection = document.getElementById('uploadPreviewSection');
                if (uploadPreviewSection) {
                    uploadPreviewSection.classList.add('d-none');
                }
            }
        });
    });

    // File input change handler for upload preview
    if (fileInput) {
        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (file) {
                const uploadPreviewSection = document.getElementById('uploadPreviewSection');
                const uploadedPreview = document.getElementById('uploadedPreview');
                const uploadedDuration = document.getElementById('uploadedDuration');

                if (uploadPreviewSection && uploadedPreview) {
                    const audioUrl = URL.createObjectURL(file);
                    uploadedPreview.src = audioUrl;
                    uploadPreviewSection.classList.remove('d-none');

                    // Initialize upload trimmer when metadata loads
                    uploadedPreview.addEventListener('loadedmetadata', async () => {
                        const duration = Math.round(uploadedPreview.duration);
                        if (uploadedDuration) {
                            uploadedDuration.textContent = `${duration}s`;
                        }

                        // Initialize upload audio trimmer
                        if (!uploadTrimmer) {
                            uploadTrimmer = new AudioTrimmer(
                                uploadedPreview,
                                'uploadWaveformCanvas',
                                'uploadSelectionOverlay',
                                'uploadPlayheadIndicator',
                                'uploadStartTime',
                                'uploadEndTime',
                                'uploadSelectionInfo'
                            );
                        }

                        // Load audio for trimming
                        await uploadTrimmer.loadAudio(file);
                    }, { once: true });
                }
            }
        });
    }

    // Start recording
    if (startBtn) {
        startBtn.addEventListener('click', async () => {
            const hasPermission = await audioRecorder.requestPermission();
            if (!hasPermission) return;

            const started = audioRecorder.startRecording();
            if (started) {
                startBtn.style.display = 'none';
                stopBtn.style.display = 'inline-block';

                if (recordingStatus) {
                    recordingStatus.classList.remove('d-none', 'ready');
                    recordingStatus.classList.add('recording');
                }

                if (recordingSection) {
                    recordingSection.classList.add('recording-active');
                }

                if (playbackSection) {
                    playbackSection.classList.add('d-none');
                }
            }
        });
    }

    // Stop recording
    if (stopBtn) {
        stopBtn.addEventListener('click', () => {
            const stopped = audioRecorder.stopRecording();
            if (stopped) {
                stopBtn.style.display = 'none';
                startBtn.style.display = 'inline-block';

                if (recordingStatus) {
                    recordingStatus.classList.remove('recording');
                    recordingStatus.classList.add('ready');
                    document.getElementById('recordingStatusText').textContent = 'Recording completed! You can now preview and save.';
                }

                if (recordingSection) {
                    recordingSection.classList.remove('recording-active');
                }
            }
        });
    }

    // Play recorded audio
    if (playBtn) {
        playBtn.addEventListener('click', () => {
            const preview = document.getElementById('recordingPreview');
            if (preview) {
                if (preview.paused) {
                    preview.play();
                    playBtn.innerHTML = '<i class="fas fa-pause me-1"></i>Pause';
                } else {
                    preview.pause();
                    playBtn.innerHTML = '<i class="fas fa-play me-1"></i>Play';
                }
            }
        });
    }

    // Re-record
    if (reRecordBtn) {
        reRecordBtn.addEventListener('click', () => {
            resetRecordingState();
        });
    }

    // Audio trimming control buttons for recorded audio
    const playSelectionBtn = document.getElementById('playSelectionBtn');
    const resetSelectionBtn = document.getElementById('resetSelectionBtn');
    const useFullAudioBtn = document.getElementById('useFullAudioBtn');

    if (playSelectionBtn) {
        playSelectionBtn.addEventListener('click', () => {
            if (audioTrimmer) {
                audioTrimmer.playSelection();
            }
        });
    }

    if (resetSelectionBtn) {
        resetSelectionBtn.addEventListener('click', () => {
            if (audioTrimmer) {
                audioTrimmer.resetSelection();
            }
        });
    }

    if (useFullAudioBtn) {
        useFullAudioBtn.addEventListener('click', () => {
            if (audioTrimmer) {
                audioTrimmer.resetSelection();
            }
        });
    }

    // Audio trimming control buttons for uploaded audio
    const playUploadSelectionBtn = document.getElementById('playUploadSelectionBtn');
    const resetUploadSelectionBtn = document.getElementById('resetUploadSelectionBtn');
    const useFullUploadBtn = document.getElementById('useFullUploadBtn');

    if (playUploadSelectionBtn) {
        playUploadSelectionBtn.addEventListener('click', () => {
            if (uploadTrimmer) {
                uploadTrimmer.playSelection();
            }
        });
    }

    if (resetUploadSelectionBtn) {
        resetUploadSelectionBtn.addEventListener('click', () => {
            if (uploadTrimmer) {
                uploadTrimmer.resetSelection();
            }
        });
    }

    if (useFullUploadBtn) {
        useFullUploadBtn.addEventListener('click', () => {
            if (uploadTrimmer) {
                uploadTrimmer.resetSelection();
            }
        });
    }

    // Handle audio preview events
    const preview = document.getElementById('recordingPreview');
    if (preview) {
        preview.addEventListener('ended', () => {
            if (playBtn) {
                playBtn.innerHTML = '<i class="fas fa-play me-1"></i>Play';
            }
        });

        preview.addEventListener('pause', () => {
            if (playBtn) {
                playBtn.innerHTML = '<i class="fas fa-play me-1"></i>Play';
            }
        });
    }
}

function resetRecordingState() {
    const startBtn = document.getElementById('startRecordBtn');
    const stopBtn = document.getElementById('stopRecordBtn');
    const recordingStatus = document.getElementById('recordingStatus');
    const playbackSection = document.getElementById('playbackSection');
    const recordingSection = document.getElementById('recordingSection');
    const playBtn = document.getElementById('playRecordingBtn');
    const permissionAlert = document.getElementById('permissionAlert');
    const progressBar = document.getElementById('recordingProgress');

    if (startBtn) startBtn.style.display = 'inline-block';
    if (stopBtn) stopBtn.style.display = 'none';

    if (recordingStatus) {
        recordingStatus.classList.add('d-none');
        recordingStatus.classList.remove('recording', 'ready');
        document.getElementById('recordingStatusText').textContent = 'Ready to record';
    }

    if (progressBar) {
        progressBar.style.width = '0%';
        progressBar.classList.remove('bg-warning', 'bg-danger');
        progressBar.classList.add('bg-success');
    }

    if (playbackSection) {
        playbackSection.classList.add('d-none');
    }

    if (recordingSection) {
        recordingSection.classList.remove('recording-active');
    }

    if (playBtn) {
        playBtn.innerHTML = '<i class="fas fa-play me-1"></i>Play';
    }

    if (permissionAlert) {
        permissionAlert.classList.add('d-none');
        permissionAlert.classList.remove('alert-danger');
        permissionAlert.classList.add('alert-warning');
    }

    // Clean up audio trimmer
    if (audioTrimmer) {
        audioTrimmer.cleanup();
        audioTrimmer = null;
    }

    if (audioRecorder) {
        audioRecorder.cleanup();
        audioRecorder = new AudioRecorder();
    }
}

// Updated save recording function
async function saveRecording(childName) {
    const dateInput = document.getElementById('recordingDate');
    const dateValue = dateInput.value;

    if (!dateValue) {
        showAlert('Please select a recording date', 'warning');
        return;
    }

    // Parse the date (format: YYYY-MM-DD)
    const dateParts = dateValue.split('-');
    const year = parseInt(dateParts[0]);
    const month = parseInt(dateParts[1]);
    const day = parseInt(dateParts[2]);

    if (!year || !month || !day) {
        showAlert('Please select a valid date', 'warning');
        return;
    }

    const method = document.querySelector('input[name="recordingMethod"]:checked')?.value;
    const saveBtn = document.getElementById('saveRecordingBtn');

    setButtonLoading(saveBtn);

    try {
        if (method === 'record') {
            // Handle browser recording
            if (!audioRecorder || !audioRecorder.getRecordedBlob()) {
                showAlert('Please record audio first', 'warning');
                return;
            }

            await saveRecordedAudio(childName, dateValue, audioRecorder.getRecordedBlob());
        } else {
            // Handle file upload (existing functionality)
            await saveUploadedAudio(childName, dateValue);
        }
    } catch (error) {
        showAlert(`Failed to save recording: ${error.message}`, 'danger');
    } finally {
        setButtonLoading(saveBtn, false);
    }
}

async function saveRecordedAudio(childName, dateValue, audioBlob) {
    let finalBlob = audioBlob;
    let selectionInfo = null;

    // Check if trimming is available and get selection
    if (audioTrimmer) {
        const selection = audioTrimmer.getSelection();
        if (!selection.isFullAudio) {
            selectionInfo = selection;
            // For now, we'll pass the selection info to the server
            // In a production app, you might want to trim client-side using Web Audio API
            // or a library like FFmpeg.js
        }
    }

    const formData = new FormData();

    // Determine file extension based on mime type
    let extension = 'webm'; // default
    const mimeType = finalBlob.type.toLowerCase();

    if (mimeType.includes('webm')) {
        extension = 'webm';
    } else if (mimeType.includes('ogg')) {
        extension = 'ogg';
    } else if (mimeType.includes('mp4') || mimeType.includes('m4a')) {
        extension = 'm4a';
    } else if (mimeType.includes('wav')) {
        extension = 'wav';
    }

    const fileName = `recording_${dateValue}.${extension}`;
    const audioFile = new File([finalBlob], fileName, { type: finalBlob.type });

    formData.append('audio', audioFile);
    formData.append('date', dateValue);

    // Add trimming information if available
    if (selectionInfo) {
        formData.append('trimStart', selectionInfo.startTime);
        formData.append('trimEnd', selectionInfo.endTime);
    }

    const response = await fetch(`/api/children/${encodeURIComponent(childName)}/words/${encodeURIComponent(currentWord)}/recordings`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Upload failed');
    }

    // Format date for display
    const date = new Date(dateValue);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    const displayDate = date.toLocaleDateString('en-US', options);

    let message = `Recording for ${displayDate} has been saved successfully!`;
    if (selectionInfo) {
        const duration = selectionInfo.endTime - selectionInfo.startTime;
        message += ` (Trimmed to ${duration.toFixed(1)}s)`;
    }

    showAlert(message, 'success');

    // Close modal and reset
    bootstrap.Modal.getInstance(document.getElementById('addRecordingModal')).hide();
    resetRecordingModal();

    // Reload page to show new recording
    setTimeout(() => window.location.reload(), 1000);
}

async function saveUploadedAudio(childName, dateValue) {
    const fileInput = document.getElementById('recordingFile');
    const file = fileInput.files[0];

    if (!file) {
        showAlert('Please select an audio file', 'warning');
        return;
    }

    let selectionInfo = null;

    // Check if trimming is available and get selection
    if (uploadTrimmer) {
        const selection = uploadTrimmer.getSelection();
        if (!selection.isFullAudio) {
            selectionInfo = selection;
        }
    }

    const formData = new FormData();
    formData.append('audio', file);
    formData.append('date', dateValue);

    // Add trimming information if available
    if (selectionInfo) {
        formData.append('trimStart', selectionInfo.startTime);
        formData.append('trimEnd', selectionInfo.endTime);
    }

    const response = await fetch(`/api/children/${encodeURIComponent(childName)}/words/${encodeURIComponent(currentWord)}/recordings`, {
        method: 'POST',
        body: formData
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Upload failed');
    }

    // Format date for display
    const date = new Date(dateValue);
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    const displayDate = date.toLocaleDateString('en-US', options);

    let message = `Recording for ${displayDate} has been uploaded successfully!`;
    if (selectionInfo) {
        const duration = selectionInfo.endTime - selectionInfo.startTime;
        message += ` (Trimmed to ${duration.toFixed(1)}s)`;
    }

    showAlert(message, 'success');

    // Close modal and reset
    bootstrap.Modal.getInstance(document.getElementById('addRecordingModal')).hide();
    resetRecordingModal();

    // Reload page to show new recording
    setTimeout(() => window.location.reload(), 1000);
}

function resetRecordingModal() {
    // Reset form - set to current date
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('recordingDate').value = today;

    const fileInput = document.getElementById('recordingFile');
    if (fileInput) fileInput.value = '';

    // Reset method selection
    const recordRadio = document.getElementById('methodRecord');
    if (recordRadio) recordRadio.checked = true;

    // Reset sections visibility
    const recordingSection = document.getElementById('recordingSection');
    const uploadSection = document.getElementById('uploadSection');
    const uploadPreviewSection = document.getElementById('uploadPreviewSection');

    if (recordingSection) recordingSection.classList.remove('d-none');
    if (uploadSection) uploadSection.classList.add('d-none');
    if (uploadPreviewSection) uploadPreviewSection.classList.add('d-none');

    // Reset recording state
    resetRecordingState();

    // Clean up upload trimmer
    if (uploadTrimmer) {
        uploadTrimmer.cleanup();
        uploadTrimmer = null;
    }

    // Reset save button text
    const saveText = document.getElementById('saveRecordingText');
    if (saveText) saveText.textContent = 'Save Recording';
}

// Delete functions
async function deleteWord(childName, wordText) {
    if (!confirm(`Are you sure you want to delete the word "${wordText}" and all its recordings?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/children/${encodeURIComponent(childName)}/words/${encodeURIComponent(wordText)}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Delete failed');
        }

        showAlert(`Word "${wordText}" deleted successfully!`, 'success');
        setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
        showAlert(`Failed to delete word: ${error.message}`, 'danger');
    }
}

async function deleteRecording(childName, wordText, year, month, day, displayDate) {
    if (!confirm(`Are you sure you want to delete the recording for "${displayDate}"?`)) {
        return;
    }

    try {
        const response = await fetch(`/api/children/${encodeURIComponent(childName)}/words/${encodeURIComponent(wordText)}/recordings/${year}/${month}/${day}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Delete failed');
        }

        showAlert(`Recording for "${displayDate}" deleted successfully!`, 'success');
        setTimeout(() => window.location.reload(), 1000);
    } catch (error) {
        showAlert(`Failed to delete recording: ${error.message}`, 'danger');
    }
}

// Image search functionality
let selectedImageUrl = '';
let currentSearchQuery = '';

async function searchImages() {
    const query = document.getElementById('imageSearchQuery').value.trim();
    if (!query) {
        showAlert('Please enter search terms', 'warning');
        return;
    }

    currentSearchQuery = query;
    const resultsContainer = document.getElementById('imageSearchResults');
    const loadingIndicator = document.getElementById('searchLoading');
    const noResultsMessage = document.getElementById('noResults');

    // Show loading state
    resultsContainer.style.display = 'none';
    noResultsMessage.classList.add('d-none');
    loadingIndicator.classList.remove('d-none');

    try {
        const response = await fetch(`/api/search/images?q=${encodeURIComponent(query)}&page=1`);

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Search failed');
        }

        const data = await response.json();

        // Check if there's an error in the response data
        if (data.error) {
            throw new Error(data.error);
        }

        displaySearchResults(data.images);

    } catch (error) {
        showAlert(`Image search unavailable: ${error.message}`, 'warning');
        loadingIndicator.classList.add('d-none');

        // Show a helpful message about the image search feature
        noResultsMessage.innerHTML = `
            <i class="fas fa-exclamation-triangle fa-3x mb-3 text-warning"></i>
            <h5>Image Search Unavailable</h5>
            <p class="text-muted">${error.message}</p>
            <p class="text-muted">You can still upload your own images using the "Upload File" tab.</p>
        `;
        noResultsMessage.classList.remove('d-none');
    }
}

function displaySearchResults(images) {
    const resultsContainer = document.getElementById('imageSearchResults');
    const loadingIndicator = document.getElementById('searchLoading');
    const noResultsMessage = document.getElementById('noResults');

    loadingIndicator.classList.add('d-none');

    if (!images || images.length === 0) {
        noResultsMessage.classList.remove('d-none');
        return;
    }

    resultsContainer.innerHTML = '';

    images.forEach(image => {
        const imageCard = document.createElement('div');
        imageCard.className = 'col-6 col-md-4 col-lg-3';
        imageCard.innerHTML = `
            <div class="card h-100 image-search-result" data-image-url="${image.webformatURL}" style="cursor: pointer;">
                <img src="${image.previewURL}" class="card-img-top" alt="${image.tags}" style="height: 120px; object-fit: cover;">
                <div class="card-body p-2">
                    <small class="text-muted d-block" style="font-size: 0.7rem; line-height: 1.2;">
                        ${image.tags.split(',').slice(0, 3).join(', ')}
                    </small>
                    <small class="text-muted">
                        <i class="fas fa-eye me-1"></i>${image.views}
                        <i class="fas fa-download ms-2 me-1"></i>${image.downloads}
                    </small>
                </div>
            </div>
        `;

        // Add click handler
        imageCard.addEventListener('click', () => selectImage(imageCard, image.webformatURL));

        resultsContainer.appendChild(imageCard);
    });

    resultsContainer.style.display = 'flex';
}

function selectImage(cardElement, imageUrl) {
    // Remove previous selection
    document.querySelectorAll('.image-search-result').forEach(card => {
        card.classList.remove('border-primary', 'bg-light');
    });

    // Highlight selected image
    cardElement.classList.add('border-primary', 'bg-light');

    // Store selected image URL
    selectedImageUrl = imageUrl;

    // Show download button
    document.getElementById('uploadImageBtn').classList.add('d-none');
    document.getElementById('downloadImageBtn').classList.remove('d-none');
}

async function downloadSelectedImage() {
    if (!selectedImageUrl) {
        showAlert('Please select an image first', 'warning');
        return;
    }

    const downloadButton = document.getElementById('downloadImageBtn');
    setButtonLoading(downloadButton);

    try {
        const response = await fetch(`/api/children/${encodeURIComponent(currentChildName)}/words/${encodeURIComponent(currentWord)}/image/download`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ imageUrl: selectedImageUrl })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Download failed');
        }

        showAlert(`Image for "${currentWord}" has been added successfully!`, 'success');

        // Close modal and reset
        bootstrap.Modal.getInstance(document.getElementById('addImageModal')).hide();
        resetImageModal();

        // Reload page to show new image
        setTimeout(() => window.location.reload(), 1000);

    } catch (error) {
        showAlert(`Failed to download image: ${error.message}`, 'danger');
    } finally {
        setButtonLoading(downloadButton, false);
    }
}

function resetImageModal() {
    // Reset search
    document.getElementById('imageSearchQuery').value = '';
    document.getElementById('imageSearchResults').style.display = 'none';
    document.getElementById('searchLoading').classList.add('d-none');
    document.getElementById('noResults').classList.add('d-none');

    // Reset selection
    selectedImageUrl = '';
    document.getElementById('uploadImageBtn').classList.remove('d-none');
    document.getElementById('downloadImageBtn').classList.add('d-none');

    // Reset file input
    document.getElementById('imageFile').value = '';

    // Reset to upload tab
    const uploadTab = document.getElementById('upload-tab');
    const searchTab = document.getElementById('search-tab');
    const uploadPanel = document.getElementById('upload-panel');
    const searchPanel = document.getElementById('search-panel');

    uploadTab.classList.add('active');
    searchTab.classList.remove('active');
    uploadPanel.classList.add('show', 'active');
    searchPanel.classList.remove('show', 'active');
}

// Global variables for current context
let currentChildName = '';

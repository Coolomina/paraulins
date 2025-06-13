// Main JavaScript functionality for Family Voices

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
async function addWord(childName) {
    const textInput = document.getElementById('wordText');
    const text = textInput.value.trim();
    
    if (!text) {
        showAlert('Please enter a word', 'warning');
        return;
    }
    
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
        setButtonLoading(addButton, false);
    }
}

// Recording management
async function addRecording(childName) {
    const yearInput = document.getElementById('recordingYear');
    const fileInput = document.getElementById('recordingFile');
    
    const year = parseInt(yearInput.value);
    const file = fileInput.files[0];
    
    if (!year || year < 2000 || year > 2030) {
        showAlert('Please enter a valid year', 'warning');
        return;
    }
    
    if (!file) {
        showAlert('Please select an audio file', 'warning');
        return;
    }
    
    const addButton = document.querySelector('#addRecordingModal .btn-primary');
    setButtonLoading(addButton);
    
    try {
        const formData = new FormData();
        formData.append('audio', file);
        formData.append('year', year.toString());
        
        const response = await fetch(`/api/children/${encodeURIComponent(childName)}/words/${encodeURIComponent(currentWord)}/recordings`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }
        
        showAlert(`Recording for ${year} has been uploaded successfully!`, 'success');
        
        // Close modal and reset form
        bootstrap.Modal.getInstance(document.getElementById('addRecordingModal')).hide();
        yearInput.value = '2025';
        fileInput.value = '';
        
        // Reload page to show new recording
        setTimeout(() => window.location.reload(), 1000);
        
    } catch (error) {
        showAlert(`Failed to upload recording: ${error.message}`, 'danger');
    } finally {
        setButtonLoading(addButton, false);
    }
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
function playAudio(childName, wordText, year, filename) {
    const button = event.target.closest('.play-btn');
    
    // Stop current audio if playing
    if (currentAudio && !currentAudio.paused) {
        currentAudio.pause();
        currentAudio.currentTime = 0;
        if (currentPlayButton) {
            currentPlayButton.classList.remove('playing');
            currentPlayButton.innerHTML = '<i class="fas fa-play me-1"></i>' + currentPlayButton.textContent.trim();
        }
    }
    
    // If clicking the same button that was playing, just stop
    if (currentPlayButton === button && button.classList.contains('playing')) {
        button.classList.remove('playing');
        button.innerHTML = '<i class="fas fa-play me-1"></i>' + year;
        currentPlayButton = null;
        currentAudio = null;
        return;
    }
    
    // Set up new audio
    currentAudio = new Audio(`/api/audio/${encodeURIComponent(childName)}/${encodeURIComponent(wordText)}/${encodeURIComponent(filename)}`);
    currentPlayButton = button;
    
    // Update button state
    button.classList.add('playing');
    button.innerHTML = '<i class="fas fa-pause me-1"></i>' + year;
    
    // Set up event listeners
    currentAudio.onended = () => {
        button.classList.remove('playing');
        button.innerHTML = '<i class="fas fa-play me-1"></i>' + year;
        currentPlayButton = null;
        currentAudio = null;
    };
    
    currentAudio.onerror = () => {
        button.classList.remove('playing');
        button.innerHTML = '<i class="fas fa-play me-1"></i>' + year;
        showAlert('Failed to play audio file', 'danger');
        currentPlayButton = null;
        currentAudio = null;
    };
    
    // Play the audio
    currentAudio.play().catch(error => {
        console.error('Audio playback failed:', error);
        showAlert('Failed to play audio file', 'danger');
        button.classList.remove('playing');
        button.innerHTML = '<i class="fas fa-play me-1"></i>' + year;
        currentPlayButton = null;
        currentAudio = null;
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Add click listeners to play buttons
    document.addEventListener('click', function(event) {
        if (event.target.closest('.play-btn')) {
            const button = event.target.closest('.play-btn');
            const childName = button.dataset.child;
            const wordText = button.dataset.word;
            const year = button.dataset.year;
            const filename = button.dataset.filename;
            
            playAudio(childName, wordText, year, filename);
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
    });
});

// Global variables
let currentUser = null;
let bloodSugarChart = null;
let currentUnits = 'mg/dL';

// DOM Elements
const authSection = document.getElementById('auth-section');
const dashboardSection = document.getElementById('dashboard-section');
const loginForm = document.getElementById('login-form');
const registerForm = document.getElementById('register-form');
const logEntryForm = document.getElementById('log-entry-form');
const logoutBtn = document.getElementById('logout-btn');
const refreshRecommendationBtn = document.getElementById('refresh-recommendation');
const loadingOverlay = document.getElementById('loading-overlay');
const notification = document.getElementById('notification');
const notificationMessage = document.getElementById('notification-message');
const notificationClose = document.getElementById('notification-close');

// Password change elements
const changePasswordBtn = document.getElementById('change-password-btn');
const passwordChangeModal = document.getElementById('password-change-modal');
const passwordChangeForm = document.getElementById('password-change-form');
const closePasswordModal = document.getElementById('close-password-modal');
const cancelPasswordChange = document.getElementById('cancel-password-change');

// Units selector elements
const unitsSelect = document.getElementById('units-select');
const bloodSugarLabel = document.getElementById('blood-sugar-label');
const bloodSugarInput = document.getElementById('blood-sugar');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    setDefaultDate();
});

function initializeApp() {
    // Check if user is already logged in (from localStorage)
    const savedUser = localStorage.getItem('currentUser');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        showDashboard();
        loadUserData();
    }
}

function setupEventListeners() {
    // Auth forms
    loginForm.addEventListener('submit', handleLogin);
    registerForm.addEventListener('submit', handleRegister);
    
    // Dashboard forms
    logEntryForm.addEventListener('submit', handleLogEntry);
    logoutBtn.addEventListener('submit', handleLogout);
    logoutBtn.addEventListener('click', handleLogout);
    refreshRecommendationBtn.addEventListener('click', loadRecommendation);
    
    // Password change functionality
    changePasswordBtn.addEventListener('click', showPasswordChangeModal);
    passwordChangeForm.addEventListener('submit', handlePasswordChange);
    closePasswordModal.addEventListener('click', hidePasswordChangeModal);
    cancelPasswordChange.addEventListener('click', hidePasswordChangeModal);
    
    // AI buttons
    document.getElementById('get-meal-suggestions').addEventListener('click', getMealSuggestions);
    document.getElementById('get-exercise-recommendations').addEventListener('click', getExerciseRecommendations);
    
    // Units selector
    unitsSelect.addEventListener('change', handleUnitsChange);
    
    // Notification
    notificationClose.addEventListener('click', hideNotification);
    
    // Date input default
    const dateInput = document.getElementById('date');
    if (dateInput) {
        dateInput.addEventListener('change', function() {
            // Validate date is not in the future
            const selectedDate = new Date(this.value);
            const today = new Date();
            today.setHours(23, 59, 59, 999);
            
            if (selectedDate > today) {
                showNotification('Please select a valid date (not in the future)', 'error');
                this.value = '';
            }
        });
    }
}

function setDefaultDate() {
    const dateInput = document.getElementById('date');
    const timeInput = document.getElementById('time');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }
    if (timeInput) {
        const now = new Date();
        const timeString = now.toTimeString().split(' ')[0].substring(0, 5); // Get HH:MM format
        timeInput.value = timeString;
    }
}

// Tab functionality
function showTab(tabName) {
    // Hide all tabs
    const tabs = document.querySelectorAll('.auth-tab');
    tabs.forEach(tab => tab.classList.remove('active'));
    
    // Remove active class from all buttons
    const buttons = document.querySelectorAll('.tab-btn');
    buttons.forEach(btn => btn.classList.remove('active'));
    
    // Show selected tab
    document.getElementById(tabName + '-tab').classList.add('active');
    event.target.classList.add('active');
}

// Authentication functions
async function handleLogin(event) {
    event.preventDefault();
    showLoading();
    
    const formData = new FormData(loginForm);
    const username = formData.get('username');
    const password = formData.get('password');
    
    try {
        const response = await fetch('/api/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            currentUser = { username };
            localStorage.setItem('currentUser', JSON.stringify(currentUser));
            showNotification('Login successful!', 'success');
            showDashboard();
            loadUserData();
        } else {
            showNotification(data.error || 'Login failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function handleRegister(event) {
    event.preventDefault();
    showLoading();
    
    const formData = new FormData(registerForm);
    const username = formData.get('username');
    const password = formData.get('password');
    const confirmPassword = formData.get('confirm_password');
    
    if (password !== confirmPassword) {
        showNotification('Passwords do not match', 'error');
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Registration successful! Please login.', 'success');
            showTab('login');
            registerForm.reset();
        } else {
            showNotification(data.error || 'Registration failed', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

function handleLogout() {
    currentUser = null;
    localStorage.removeItem('currentUser');
    showAuth();
    showNotification('Logged out successfully', 'success');
}

// Dashboard functions
function showDashboard() {
    authSection.classList.add('hidden');
    dashboardSection.classList.remove('hidden');
    document.getElementById('user-display').textContent = currentUser.username;
    loadUserPreferences();
}

// Unit conversion functions
function mgDlToMmolL(mgDlValue) {
    return Math.round((mgDlValue / 18.018) * 10) / 10;
}

function mmolLToMgDl(mmolLValue) {
    return Math.round(mmolLValue * 18.018);
}

function convertToUserUnits(value, fromUnits, toUnits) {
    if (fromUnits === toUnits) {
        return value;
    }
    
    if (fromUnits === 'mg/dL' && toUnits === 'mmol/L') {
        return mgDlToMmolL(value);
    } else if (fromUnits === 'mmol/L' && toUnits === 'mg/dL') {
        return mmolLToMgDl(value);
    }
    
    return value;
}

function getValidationRange(units) {
    if (units === 'mg/dL') {
        return { min: 50, max: 500 };
    } else if (units === 'mmol/L') {
        return { min: 2.8, max: 27.8 };
    }
    return { min: 50, max: 500 };
}

function updateBloodSugarInput() {
    const range = getValidationRange(currentUnits);
    bloodSugarInput.min = range.min;
    bloodSugarInput.max = range.max;
    bloodSugarInput.step = currentUnits === 'mmol/L' ? '0.1' : '0.1';
    bloodSugarLabel.textContent = `Blood Sugar (${currentUnits})`;
}

async function loadUserPreferences() {
    // Check localStorage first for instant loading
    const storedUnits = localStorage.getItem('userUnits');
    if (storedUnits && (storedUnits === 'mg/dL' || storedUnits === 'mmol/L')) {
        currentUnits = storedUnits;
        unitsSelect.value = currentUnits;
        updateBloodSugarInput();
    }
    
    // Try to get from server and sync
    try {
        const response = await fetch(`/api/user-preferences/${currentUser.username}`);
        if (response.ok) {
            const data = await response.json();
            const serverUnits = data.preferred_units || 'mg/dL';
            
            // If localStorage is empty or different, update it
            if (!storedUnits || storedUnits !== serverUnits) {
                localStorage.setItem('userUnits', serverUnits);
                currentUnits = serverUnits;
                unitsSelect.value = currentUnits;
                updateBloodSugarInput();
            }
        }
    } catch (error) {
        console.error('Error loading user preferences from server:', error);
        // Use localStorage value if available, otherwise default
        if (!storedUnits) {
            currentUnits = 'mg/dL';
            unitsSelect.value = currentUnits;
            updateBloodSugarInput();
        }
    }
}

async function handleUnitsChange() {
    const newUnits = unitsSelect.value;
    if (newUnits === currentUnits) return;
    
    try {
        showLoading();
        
        // Store in localStorage immediately for instant feedback
        localStorage.setItem('userUnits', newUnits);
        
        // Update user preference on server (but don't fail if it doesn't work)
        try {
            const response = await fetch('/api/update-units', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: currentUser.username,
                    units: newUnits
                })
            });
            
            if (!response.ok) {
                console.warn('Server unit update failed, using localStorage only');
            }
        } catch (serverError) {
            console.warn('Server unit update failed, using localStorage only:', serverError);
        }
        
        // Update UI regardless of server response
        currentUnits = newUnits;
        updateBloodSugarInput();
        
        // Reload all data with new units
        await loadUserData();
        showNotification('Units updated successfully!', 'success');
        
    } catch (error) {
        console.error('Error updating units:', error);
        showNotification('Network error. Please try again.', 'error');
        // Revert the selector
        unitsSelect.value = currentUnits;
    } finally {
        hideLoading();
    }
}

function showAuth() {
    dashboardSection.classList.add('hidden');
    authSection.classList.remove('hidden');
    loginForm.reset();
    registerForm.reset();
}

async function loadUserData() {
    if (!currentUser) return;
    
    try {
        // Load user stats
        await loadUserStats();
        
        // Load history
        await loadHistory();
        
        // Load chart data
        await loadChartData();
        
        // Only load recommendation if there's no current recommendation
        const recommendationContent = document.getElementById('recommendation-content');
        if (!recommendationContent.innerHTML || recommendationContent.innerHTML.includes('Start logging')) {
            await loadRecommendation();
        }
        
    } catch (error) {
        showNotification('Error loading user data', 'error');
    }
}

async function loadUserStats() {
    try {
        const response = await fetch(`/api/user-stats/${currentUser.username}`);
        const data = await response.json();
        
        if (response.ok) {
            const stats = data.stats;
            
            document.getElementById('total-entries').textContent = stats.total_entries;
            document.getElementById('avg-blood-sugar').textContent = `${stats.avg_blood_sugar} ${stats.units}`;
            document.getElementById('entries-this-week').textContent = stats.entries_this_week;
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function calculateStats(history) {
    if (!history || history.length === 0) {
        return {
            totalEntries: 0,
            avgBloodSugar: 0,
            entriesThisWeek: 0
        };
    }
    
    const totalEntries = history.length;
    const avgBloodSugar = Math.round(
        history.reduce((sum, entry) => sum + parseFloat(entry.blood_sugar), 0) / totalEntries
    );
    
    const weekAgo = new Date();
    weekAgo.setDate(weekAgo.getDate() - 7);
    
    const entriesThisWeek = history.filter(entry => {
        const entryDate = new Date(entry.date);
        return entryDate >= weekAgo;
    }).length;
    
    return {
        totalEntries,
        avgBloodSugar,
        entriesThisWeek
    };
}

async function loadHistory() {
    try {
        const response = await fetch(`/api/history/${currentUser.username}`);
        const data = await response.json();
        
        if (response.ok) {
            displayHistory(data.history, data.units);
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayHistory(history, units = 'mg/dL') {
    const historyContent = document.getElementById('history-content');
    
    if (!history || history.length === 0) {
        historyContent.innerHTML = '<p>No entries yet. Start logging to see your history!</p>';
        return;
    }
    
    const historyHTML = history.map(entry => `
        <div class="history-item">
            <h4>Blood Sugar: ${entry.blood_sugar} ${units}</h4>
            <p><strong>Date:</strong> ${formatDate(entry.date)}</p>
            <p><strong>Meal:</strong> ${entry.meal}</p>
            <p><strong>Exercise:</strong> ${entry.exercise}</p>
            <p class="date">Logged: ${formatDateTime(entry.created_at)}</p>
        </div>
    `).join('');
    
    historyContent.innerHTML = historyHTML;
}

async function loadChartData() {
    try {
        const response = await fetch(`/api/chart-data/${currentUser.username}`);
        const data = await response.json();
        
        if (response.ok) {
            createBloodSugarChart(data.chart_data);
        }
    } catch (error) {
        console.error('Error loading chart data:', error);
    }
}

function createBloodSugarChart(chartData) {
    const chartContainer = document.querySelector('.chart-container');
    const chartMessage = document.getElementById('chart-message');
    const canvas = document.getElementById('bloodSugarChart');
    
    // Destroy existing chart if it exists
    if (bloodSugarChart) {
        bloodSugarChart.destroy();
    }
    
    if (!chartData || !chartData.labels || chartData.labels.length === 0) {
        chartContainer.style.display = 'none';
        chartMessage.style.display = 'block';
        return;
    }
    
    // Show chart container and hide message
    chartContainer.style.display = 'block';
    chartMessage.style.display = 'none';
    
    // Create the chart
    const ctx = canvas.getContext('2d');
    bloodSugarChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: `Blood Sugar (${chartData.units || currentUnits})`,
                data: chartData.data,
                borderColor: '#667eea',
                backgroundColor: 'rgba(102, 126, 234, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#667eea',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#667eea',
                    borderWidth: 1,
                    cornerRadius: 8,
                    displayColors: false,
                    callbacks: {
                        title: function(context) {
                            return `Date & Time: ${chartData.dates[context[0].dataIndex]}`;
                        },
                        label: function(context) {
                            return `Blood Sugar: ${context.parsed.y} ${chartData.units || currentUnits}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#666',
                        font: {
                            size: 12
                        }
                    }
                },
                y: {
                    beginAtZero: false,
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#666',
                        font: {
                            size: 12
                        },
                        callback: function(value) {
                            return value + ` ${chartData.units || currentUnits}`;
                        }
                    }
                }
            },
            interaction: {
                intersect: false,
                mode: 'index'
            },
            elements: {
                point: {
                    hoverBackgroundColor: '#764ba2'
                }
            }
        }
    });
}

async function loadRecommendation() {
    try {
        const response = await fetch(`/api/recommendation/${currentUser.username}`);
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('recommendation-content').innerHTML = 
                `<div class="recommendation-text">${formatRecommendationText(data.recommendation)}</div>`;
        }
    } catch (error) {
        console.error('Error loading recommendation:', error);
        document.getElementById('recommendation-content').innerHTML = 
            '<p>Unable to load recommendation. Please try again later.</p>';
    }
}

async function getMealSuggestions() {
    const bloodSugar = document.getElementById('blood-sugar').value;
    if (!bloodSugar) {
        showNotification('Please enter your blood sugar level first', 'error');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch('/api/meal-suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                blood_sugar: parseFloat(bloodSugar),
                preferences: document.getElementById('meal').value || ''
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('recommendation-content').innerHTML = 
                `<h4>🍽️ Meal Suggestions for Blood Sugar: ${bloodSugar} mg/dL</h4>
                <div class="recommendation-text">${formatRecommendationText(data.suggestions)}</div>`;
        } else {
            showNotification(data.error || 'Failed to get meal suggestions', 'error');
        }
    } catch (error) {
        console.error('Error getting meal suggestions:', error);
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

async function getExerciseRecommendations() {
    const bloodSugar = document.getElementById('blood-sugar').value;
    if (!bloodSugar) {
        showNotification('Please enter your blood sugar level first', 'error');
        return;
    }
    
    try {
        showLoading();
        const response = await fetch('/api/exercise-recommendations', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                blood_sugar: parseFloat(bloodSugar),
                current_exercise: document.getElementById('exercise').value || 'None'
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            document.getElementById('recommendation-content').innerHTML = 
                `<h4>🏃‍♂️ Exercise Recommendations for Blood Sugar: ${bloodSugar} mg/dL</h4>
                <div class="recommendation-text">${formatRecommendationText(data.recommendations)}</div>`;
        } else {
            showNotification(data.error || 'Failed to get exercise recommendations', 'error');
        }
    } catch (error) {
        console.error('Error getting exercise recommendations:', error);
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Log entry function
async function handleLogEntry(event) {
    event.preventDefault();
    showLoading();
    
    const formData = new FormData(logEntryForm);
    const bloodSugar = parseFloat(formData.get('blood_sugar'));
    const meal = formData.get('meal');
    const exercise = formData.get('exercise');
    const date = formData.get('date');
    const time = formData.get('time');
    
    // Combine date and time into ISO string
    const dateTime = new Date(`${date}T${time}`).toISOString();
    
    // Validate blood sugar based on current units
    const range = getValidationRange(currentUnits);
    if (bloodSugar < range.min || bloodSugar > range.max) {
        showNotification(`Blood sugar should be between ${range.min} and ${range.max} ${currentUnits}`, 'error');
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/log-entry', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: currentUser.username,
                blood_sugar: bloodSugar,
                meal,
                exercise,
                date: dateTime,
                units: currentUnits
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Entry logged successfully!', 'success');
            logEntryForm.reset();
            setDefaultDate();
            
            // Display AI recommendation if available
            if (data.recommendation) {
                document.getElementById('recommendation-content').innerHTML = 
                    `<div class="recommendation-text">${formatRecommendationText(data.recommendation)}</div>`;
            }
            
            // Reload user data
            await loadUserData();
        } else {
            showNotification(data.error || 'Failed to log entry', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
}

// Utility functions
function showLoading() {
    loadingOverlay.classList.remove('hidden');
}

function hideLoading() {
    loadingOverlay.classList.add('hidden');
}

function showNotification(message, type = 'success') {
    notificationMessage.textContent = message;
    notification.className = `notification ${type}`;
    notification.classList.remove('hidden');
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        hideNotification();
    }, 5000);
}

function hideNotification() {
    notification.classList.add('hidden');
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

function formatDateTime(dateTimeString) {
    const date = new Date(dateTimeString);
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Format recommendation text with proper line breaks
function formatRecommendationText(text) {
    if (!text) return '';
    
    // Replace double newlines with paragraph breaks
    let formatted = text.replace(/\n\n/g, '</p><p>');
    
    // Replace single newlines with line breaks
    formatted = formatted.replace(/\n/g, '<br>');
    
    // Wrap in paragraph tags if not already wrapped
    if (!formatted.startsWith('<p>')) {
        formatted = '<p>' + formatted + '</p>';
    }
    
    return formatted;
}

// Error handling
window.addEventListener('error', function(e) {
    console.error('JavaScript error:', e.error);
    showNotification('An error occurred. Please refresh the page.', 'error');
});

// Handle network errors
window.addEventListener('offline', function() {
    showNotification('You are offline. Please check your connection.', 'error');
});

window.addEventListener('online', function() {
    showNotification('You are back online!', 'success');
});

// Password change functions
function showPasswordChangeModal() {
    passwordChangeModal.classList.remove('hidden');
    // Clear form
    passwordChangeForm.reset();
}

function hidePasswordChangeModal() {
    passwordChangeModal.classList.add('hidden');
    // Clear form
    passwordChangeForm.reset();
}

async function handlePasswordChange(event) {
    event.preventDefault();
    showLoading();
    
    const formData = new FormData(passwordChangeForm);
    const oldPassword = formData.get('old_password');
    const newPassword = formData.get('new_password');
    const confirmNewPassword = formData.get('confirm_new_password');
    
    // Validate passwords match
    if (newPassword !== confirmNewPassword) {
        showNotification('New passwords do not match', 'error');
        hideLoading();
        return;
    }
    
    // Validate password length
    if (newPassword.length < 6) {
        showNotification('New password must be at least 6 characters long', 'error');
        hideLoading();
        return;
    }
    
    // Validate old password is not the same as new password
    if (oldPassword === newPassword) {
        showNotification('New password must be different from current password', 'error');
        hideLoading();
        return;
    }
    
    try {
        const response = await fetch('/api/change-password', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: currentUser.username,
                old_password: oldPassword,
                new_password: newPassword
            })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showNotification('Password changed successfully!', 'success');
            hidePasswordChangeModal();
        } else {
            showNotification(data.error || 'Failed to change password', 'error');
        }
    } catch (error) {
        showNotification('Network error. Please try again.', 'error');
    } finally {
        hideLoading();
    }
} 
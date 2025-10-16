// Global variables
let currentUser = null;
let bloodSugarChart = null;

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
    
    // AI buttons
    document.getElementById('get-meal-suggestions').addEventListener('click', getMealSuggestions);
    document.getElementById('get-exercise-recommendations').addEventListener('click', getExerciseRecommendations);
    
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
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
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
        const response = await fetch(`/api/history/${currentUser.username}`);
        const data = await response.json();
        
        if (response.ok) {
            const history = data.history;
            const stats = calculateStats(history);
            
            document.getElementById('total-entries').textContent = stats.totalEntries;
            document.getElementById('avg-blood-sugar').textContent = stats.avgBloodSugar;
            document.getElementById('entries-this-week').textContent = stats.entriesThisWeek;
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
            displayHistory(data.history);
        }
    } catch (error) {
        console.error('Error loading history:', error);
    }
}

function displayHistory(history) {
    const historyContent = document.getElementById('history-content');
    
    if (!history || history.length === 0) {
        historyContent.innerHTML = '<p>No entries yet. Start logging to see your history!</p>';
        return;
    }
    
    const historyHTML = history.map(entry => `
        <div class="history-item">
            <h4>Blood Sugar: ${entry.blood_sugar} mg/dL</h4>
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
                label: 'Blood Sugar (mg/dL)',
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
                            return `Date: ${chartData.dates[context[0].dataIndex]}`;
                        },
                        label: function(context) {
                            return `Blood Sugar: ${context.parsed.y} mg/dL`;
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
                            return value + ' mg/dL';
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
    
    // Validate blood sugar
    if (bloodSugar < 50 || bloodSugar > 500) {
        showNotification('Blood sugar should be between 50 and 500 mg/dL', 'error');
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
                date
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
// Global variables
let webcamStream = null;
let currentImageFile = null;

// DOM elements
const fileInput = document.getElementById('file-input');
const webcamBtn = document.getElementById('webcam-btn');
const webcamInterface = document.getElementById('webcam-interface');
const webcamVideo = document.getElementById('webcam-video');
const webcamCanvas = document.getElementById('webcam-canvas');
const captureBtn = document.getElementById('capture-btn');
const stopWebcamBtn = document.getElementById('stop-webcam-btn');
const previewSection = document.getElementById('preview-section');
const previewImage = document.getElementById('preview-image');
const analyzeBtn = document.getElementById('analyze-btn');
const clearBtn = document.getElementById('clear-btn');
const loadingSection = document.getElementById('loading-section');
const resultsSection = document.getElementById('results-section');
const osintToggle = document.getElementById('osint-toggle');

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeEventListeners();
    checkApplicationStatus();
});

function initializeEventListeners() {
    // File input change
    fileInput.addEventListener('change', handleFileSelect);
    
    // Webcam controls
    webcamBtn.addEventListener('click', startWebcam);
    captureBtn.addEventListener('click', captureWebcamImage);
    stopWebcamBtn.addEventListener('click', stopWebcam);
    
    // Action buttons
    analyzeBtn.addEventListener('click', analyzeImage);
    clearBtn.addEventListener('click', clearAll);
    
    // Drag and drop functionality
    const uploadMethods = document.querySelector('.upload-methods');
    uploadMethods.addEventListener('dragover', handleDragOver);
    uploadMethods.addEventListener('drop', handleDrop);
}

function handleFileSelect(event) {
    const file = event.target.files[0];
    if (file) {
        displayImagePreview(file);
    }
}

function handleDragOver(event) {
    event.preventDefault();
    event.currentTarget.style.backgroundColor = 'rgba(102, 126, 234, 0.1)';
}

function handleDrop(event) {
    event.preventDefault();
    event.currentTarget.style.backgroundColor = '';
    
    const files = event.dataTransfer.files;
    if (files.length > 0) {
        const file = files[0];
        if (file.type.startsWith('image/')) {
            displayImagePreview(file);
        } else {
            showNotification('Please select an image file', 'error');
        }
    }
}

function displayImagePreview(file) {
    currentImageFile = file;
    const reader = new FileReader();
    
    reader.onload = function(e) {
        previewImage.src = e.target.result;
        previewSection.style.display = 'block';
        previewSection.classList.add('fade-in');
        
        // Hide other sections
        webcamInterface.style.display = 'none';
        resultsSection.style.display = 'none';
    };
    
    reader.readAsDataURL(file);
}

async function startWebcam() {
    try {
        webcamStream = await navigator.mediaDevices.getUserMedia({ 
            video: { 
                width: { ideal: 640 },
                height: { ideal: 480 }
            } 
        });
        
        webcamVideo.srcObject = webcamStream;
        webcamInterface.style.display = 'block';
        webcamInterface.classList.add('fade-in');
        
        // Hide other sections
        previewSection.style.display = 'none';
        resultsSection.style.display = 'none';
        
        webcamBtn.textContent = 'Camera Active';
        webcamBtn.disabled = true;
        
    } catch (error) {
        console.error('Error accessing webcam:', error);
        showNotification('Unable to access webcam. Please check permissions.', 'error');
    }
}

function captureWebcamImage() {
    const canvas = webcamCanvas;
    const video = webcamVideo;
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0);
    
    // Convert to blob and create file-like object
    canvas.toBlob(function(blob) {
        const file = new File([blob], 'webcam-capture.jpg', { type: 'image/jpeg' });
        displayImagePreview(file);
        stopWebcam();
    }, 'image/jpeg', 0.8);
}

function stopWebcam() {
    if (webcamStream) {
        webcamStream.getTracks().forEach(track => track.stop());
        webcamStream = null;
    }
    
    webcamInterface.style.display = 'none';
    webcamBtn.textContent = 'Start Camera';
    webcamBtn.disabled = false;
}

async function analyzeImage() {
    if (!currentImageFile) {
        showNotification('Please select an image first', 'error');
        return;
    }
    
    // Show loading
    loadingSection.style.display = 'block';
    loadingSection.classList.add('fade-in');
    previewSection.style.display = 'none';
    resultsSection.style.display = 'none';
    
    try {
        let response;
        
        if (currentImageFile.name === 'webcam-capture.jpg') {
            // Handle webcam capture
            const canvas = webcamCanvas;
            const imageData = canvas.toDataURL('image/jpeg');
            
            response = await fetch('/api/face/webcam', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    image: imageData,
                    osint_enabled: osintToggle.checked
                })
            });
        } else {
            // Handle file upload
            const formData = new FormData();
            formData.append('file', currentImageFile);
            formData.append('osint_enabled', osintToggle.checked);
            
            response = await fetch('/api/face/upload', {
                method: 'POST',
                body: formData
            });
        }
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result);
        } else {
            showNotification(result.error || 'Analysis failed', 'error');
        }
        
    } catch (error) {
        console.error('Analysis error:', error);
        showNotification('Network error. Please try again.', 'error');
    } finally {
        loadingSection.style.display = 'none';
    }
}

function displayResults(data) {
    // Update threat level
    updateThreatLevel(data.threat_level);
    
    // Display face matches
    displayFaceMatches(data.matches || []);
    
    // Display OSINT results
    displayOSINTResults(data.osint_results || []);
    
    // Display analysis summary
    displayAnalysisSummary(data);
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.classList.add('slide-up');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function updateThreatLevel(level) {
    const threatBar = document.getElementById('threat-bar');
    const threatLabel = document.getElementById('threat-label');
    
    threatBar.className = 'threat-bar ' + level.toLowerCase();
    threatLabel.textContent = level;
    threatLabel.style.color = getThreatColor(level);
}

function getThreatColor(level) {
    switch (level.toLowerCase()) {
        case 'low': return '#56ab2f';
        case 'medium': return '#f7971e';
        case 'high': return '#ff6b6b';
        default: return '#666';
    }
}

function displayFaceMatches(matches) {
    const container = document.getElementById('matches-container');
    
    if (matches.length === 0) {
        container.innerHTML = '<p class="no-results">No matching faces found in database</p>';
        return;
    }
    
    container.innerHTML = matches.map(match => `
        <div class="match-item">
            <div class="match-info">
                <div class="match-filename">${match.filename}</div>
                <div class="match-confidence">Confidence: ${match.confidence}%</div>
            </div>
        </div>
    `).join('');
}

function displayOSINTResults(results) {
    const container = document.getElementById('osint-container');
    
    if (results.length === 0) {
        container.innerHTML = '<p class="no-results">No public data found</p>';
        return;
    }
    
    container.innerHTML = results.map(result => `
        <div class="osint-item">
            <div class="osint-source">${result.source}</div>
            <div class="osint-details">
                ${formatOSINTData(result)}
            </div>
        </div>
    `).join('');
}

function formatOSINTData(result) {
    if (result.source === 'Gravatar') {
        return `
            <p><strong>Email:</strong> ${result.email}</p>
            <p><strong>Profile Found:</strong> Yes</p>
        `;
    } else if (result.source === 'GitHub') {
        const data = result.data;
        return `
            <p><strong>Username:</strong> ${result.username}</p>
            <p><strong>Name:</strong> ${data.name || 'Not provided'}</p>
            <p><strong>Bio:</strong> ${data.bio || 'Not provided'}</p>
            <p><strong>Public Repos:</strong> ${data.public_repos}</p>
            <p><strong>Followers:</strong> ${data.followers}</p>
        `;
    }
    return '<p>Data found</p>';
}

function displayAnalysisSummary(data) {
    const container = document.getElementById('summary-content');
    
    const matchCount = data.matches ? data.matches.length : 0;
    const osintCount = data.osint_results ? data.osint_results.length : 0;
    
    let summary = `
        <div class="summary-stats">
            <div class="stat-item">
                <span class="stat-number">${matchCount}</span>
                <span class="stat-label">Face Matches</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${osintCount}</span>
                <span class="stat-label">Public Profiles</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${data.threat_level}</span>
                <span class="stat-label">Threat Level</span>
            </div>
        </div>
        
        <div class="summary-text">
            <h5>Privacy Risk Assessment:</h5>
    `;
    
    if (data.threat_level === 'HIGH') {
        summary += `
            <p class="risk-high">⚠️ <strong>High Risk:</strong> Your face was successfully matched with existing data and/or public profiles were found. This demonstrates how easily someone could be identified using facial recognition technology combined with public data.</p>
        `;
    } else if (data.threat_level === 'MEDIUM') {
        summary += `
            <p class="risk-medium">⚠️ <strong>Medium Risk:</strong> Some facial matches were found but with lower confidence. While not immediately identifiable, this shows potential privacy vulnerabilities.</p>
        `;
    } else {
        summary += `
            <p class="risk-low">✅ <strong>Low Risk:</strong> No strong matches or public data were found. However, this doesn't guarantee privacy as databases and search capabilities continue to expand.</p>
        `;
    }
    
    summary += `
            <p><strong>Educational Note:</strong> This simulation demonstrates how facial recognition technology can be combined with publicly available data to potentially identify individuals. In real-world scenarios, more sophisticated algorithms and larger databases could pose even greater privacy risks.</p>
        </div>
    `;
    
    container.innerHTML = summary;
}

function clearAll() {
    // Reset all sections
    previewSection.style.display = 'none';
    webcamInterface.style.display = 'none';
    loadingSection.style.display = 'none';
    resultsSection.style.display = 'none';
    
    // Reset form
    fileInput.value = '';
    currentImageFile = null;
    
    // Stop webcam if active
    stopWebcam();
    
    showNotification('Cleared successfully', 'success');
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <i class="fas fa-${getNotificationIcon(type)}"></i>
        <span>${message}</span>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => notification.classList.add('show'), 100);
    
    // Remove after delay
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => document.body.removeChild(notification), 300);
    }, 3000);
}

function getNotificationIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

async function checkApplicationStatus() {
    try {
        const response = await fetch('/api/face/status');
        const status = await response.json();
        
        if (status.status === 'active') {
            console.log('Application status:', status);
        }
    } catch (error) {
        console.error('Failed to check application status:', error);
    }
}

// Modal functions
function showInfo() {
    const modal = document.getElementById('info-modal');
    const modalBody = document.getElementById('modal-body');
    
    modalBody.innerHTML = `
        <h2>How It Works</h2>
        <div class="info-content">
            <h3>Face Detection & Matching</h3>
            <p>The system uses OpenCV's Haar Cascade classifiers to detect faces in uploaded images. It then extracts basic facial features and compares them against a database of known faces using correlation analysis.</p>
            
            <h3>OSINT (Open Source Intelligence) Lookup</h3>
            <p>When enabled, the system attempts to find public information associated with detected faces by:</p>
            <ul>
                <li><strong>Gravatar Search:</strong> Checking for profile pictures associated with common email patterns</li>
                <li><strong>GitHub Lookup:</strong> Searching for user profiles based on filename patterns</li>
                <li><strong>Reverse Image Search:</strong> Simulating searches across public databases</li>
            </ul>
            
            <h3>Threat Level Assessment</h3>
            <p>The system calculates a privacy threat level based on:</p>
            <ul>
                <li>Face matching confidence scores</li>
                <li>Number of public profiles found</li>
                <li>Quality and quantity of available data</li>
            </ul>
            
            <h3>Educational Purpose</h3>
            <p>This tool demonstrates potential privacy risks and is designed to raise awareness about facial recognition technology and data correlation techniques used in OSINT investigations.</p>
        </div>
    `;
    
    modal.style.display = 'block';
}

function showPrivacy() {
    const modal = document.getElementById('info-modal');
    const modalBody = document.getElementById('modal-body');
    
    modalBody.innerHTML = `
        <h2>Privacy Policy</h2>
        <div class="info-content">
            <h3>Data Collection</h3>
            <p>This application processes images locally and temporarily for demonstration purposes. No images or personal data are permanently stored or transmitted to external servers without your explicit consent.</p>
            
            <h3>Image Processing</h3>
            <p>Uploaded images are processed using client-side and server-side algorithms for face detection and analysis. Images are automatically deleted after processing.</p>
            
            <h3>OSINT Lookups</h3>
            <p>When OSINT lookup is enabled, the system may make requests to public APIs (Gravatar, GitHub) using generic search patterns. No personal information is transmitted in these requests.</p>
            
            <h3>No Tracking</h3>
            <p>This application does not use cookies, analytics, or tracking mechanisms. All processing is done locally for educational purposes.</p>
            
            <h3>Disclaimer</h3>
            <p>This tool is for educational and awareness purposes only. Users are responsible for ensuring they have appropriate permissions before analyzing any images containing faces.</p>
        </div>
    `;
    
    modal.style.display = 'block';
}

function showAbout() {
    const modal = document.getElementById('info-modal');
    const modalBody = document.getElementById('modal-body');
    
    modalBody.innerHTML = `
        <h2>About This Project</h2>
        <div class="info-content">
            <h3>Purpose</h3>
            <p>This OSINT Face Recognition Simulator was created to demonstrate the privacy implications of facial recognition technology when combined with publicly available data sources.</p>
            
            <h3>Technology Stack</h3>
            <ul>
                <li><strong>Backend:</strong> Flask (Python)</li>
                <li><strong>Face Detection:</strong> OpenCV</li>
                <li><strong>Frontend:</strong> HTML5, CSS3, JavaScript</li>
                <li><strong>APIs:</strong> Gravatar, GitHub</li>
            </ul>
            
            <h3>Educational Goals</h3>
            <ul>
                <li>Raise awareness about facial recognition privacy risks</li>
                <li>Demonstrate OSINT correlation techniques</li>
                <li>Show how public data can be used for identification</li>
                <li>Encourage better privacy practices</li>
            </ul>
            
            <h3>Ethical Use</h3>
            <p>This tool should only be used for:</p>
            <ul>
                <li>Educational purposes</li>
                <li>Privacy awareness training</li>
                <li>Security research (with proper authorization)</li>
                <li>Personal privacy assessment</li>
            </ul>
            
            <p><strong>Do not use this tool for unauthorized surveillance, stalking, or any illegal activities.</strong></p>
        </div>
    `;
    
    modal.style.display = 'block';
}

function closeModal() {
    document.getElementById('info-modal').style.display = 'none';
}

// Close modal when clicking outside
window.onclick = function(event) {
    const modal = document.getElementById('info-modal');
    if (event.target === modal) {
        modal.style.display = 'none';
    }
}

// Add notification styles dynamically
const notificationStyles = `
    .notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 15px 20px;
        border-radius: 10px;
        color: white;
        font-weight: 600;
        z-index: 1000;
        transform: translateX(400px);
        transition: transform 0.3s ease;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.2);
    }
    
    .notification.show {
        transform: translateX(0);
    }
    
    .notification-success {
        background: linear-gradient(45deg, #56ab2f, #a8e6cf);
    }
    
    .notification-error {
        background: linear-gradient(45deg, #ff6b6b, #ee5a24);
    }
    
    .notification-warning {
        background: linear-gradient(45deg, #f7971e, #ffd200);
    }
    
    .notification-info {
        background: linear-gradient(45deg, #667eea, #764ba2);
    }
    
    .summary-stats {
        display: flex;
        justify-content: space-around;
        margin-bottom: 20px;
        padding: 20px;
        background: rgba(102, 126, 234, 0.05);
        border-radius: 10px;
    }
    
    .stat-item {
        text-align: center;
    }
    
    .stat-number {
        display: block;
        font-size: 2rem;
        font-weight: 700;
        color: #667eea;
    }
    
    .stat-label {
        font-size: 0.9rem;
        color: #666;
    }
    
    .risk-high {
        color: #e53e3e;
        font-weight: 600;
    }
    
    .risk-medium {
        color: #f7971e;
        font-weight: 600;
    }
    
    .risk-low {
        color: #56ab2f;
        font-weight: 600;
    }
    
    .no-results {
        text-align: center;
        color: #666;
        font-style: italic;
        padding: 20px;
    }
    
    .info-content h3 {
        color: #667eea;
        margin-top: 20px;
        margin-bottom: 10px;
    }
    
    .info-content ul {
        margin-left: 20px;
        margin-bottom: 15px;
    }
    
    .info-content li {
        margin-bottom: 5px;
    }
`;

// Add styles to head
const styleSheet = document.createElement('style');
styleSheet.textContent = notificationStyles;
document.head.appendChild(styleSheet);


// Gemini Analysis Functions
function displayGeminiAnalysis(geminiData) {
    const geminiSection = document.getElementById('gemini-analysis');
    
    if (!geminiData || Object.keys(geminiData).length === 0) {
        geminiSection.style.display = 'none';
        return;
    }
    
    // Show Gemini analysis section
    geminiSection.style.display = 'block';
    
    // Populate face analysis tab
    if (geminiData.face_analysis) {
        populateFaceAnalysisTab(geminiData.face_analysis);
    }
    
    // Populate OSINT insights tab
    if (geminiData.osint_analysis) {
        populateOSINTInsightsTab(geminiData.osint_analysis);
    }
    
    // Populate threat assessment tab
    if (geminiData.threat_assessment) {
        populateThreatAssessmentTab(geminiData.threat_assessment);
    }
}

function populateFaceAnalysisTab(faceAnalysis) {
    const facialAttributes = document.getElementById('facial-attributes');
    const imageContext = document.getElementById('image-context');
    
    // Handle both structured and raw analysis
    if (faceAnalysis.structured) {
        facialAttributes.innerHTML = formatAnalysisText(faceAnalysis.structured.facial_attributes || '');
        imageContext.innerHTML = formatAnalysisText(faceAnalysis.structured.contextual_analysis || '');
    } else if (faceAnalysis.raw_analysis) {
        const sections = parseRawAnalysis(faceAnalysis.raw_analysis);
        facialAttributes.innerHTML = formatAnalysisText(sections.facial_attributes || '');
        imageContext.innerHTML = formatAnalysisText(sections.contextual_analysis || '');
    } else {
        facialAttributes.innerHTML = '<p>Face analysis data available but format not recognized.</p>';
        imageContext.innerHTML = '<p>Context analysis data available but format not recognized.</p>';
    }
}

function populateOSINTInsightsTab(osintAnalysis) {
    const searchStrategy = document.getElementById('search-strategy');
    const potentialIndicators = document.getElementById('potential-indicators');
    
    // Handle both structured and raw analysis
    if (osintAnalysis.structured) {
        searchStrategy.innerHTML = formatAnalysisText(osintAnalysis.structured.reverse_image_search || '');
        potentialIndicators.innerHTML = formatAnalysisText(osintAnalysis.structured.social_media_indicators || '');
    } else if (osintAnalysis.raw_analysis) {
        const sections = parseRawAnalysis(osintAnalysis.raw_analysis);
        searchStrategy.innerHTML = formatAnalysisText(sections.reverse_image_search || '');
        potentialIndicators.innerHTML = formatAnalysisText(sections.social_media_indicators || '');
    } else {
        searchStrategy.innerHTML = '<p>OSINT strategy data available but format not recognized.</p>';
        potentialIndicators.innerHTML = '<p>Indicator data available but format not recognized.</p>';
    }
}

function populateThreatAssessmentTab(threatAssessment) {
    const riskFactors = document.getElementById('risk-factors');
    const privacyRecommendations = document.getElementById('privacy-recommendations');
    
    // Handle both structured and raw analysis
    if (threatAssessment.structured) {
        riskFactors.innerHTML = formatAnalysisText(threatAssessment.structured.risk_factors || '');
        privacyRecommendations.innerHTML = formatAnalysisText(threatAssessment.structured.recommendations || '');
    } else if (threatAssessment.raw_assessment) {
        const sections = parseRawAnalysis(threatAssessment.raw_assessment);
        riskFactors.innerHTML = formatAnalysisText(sections.risk_factors || '');
        privacyRecommendations.innerHTML = formatAnalysisText(sections.recommendations || '');
    } else {
        riskFactors.innerHTML = '<p>Risk assessment data available but format not recognized.</p>';
        privacyRecommendations.innerHTML = '<p>Recommendation data available but format not recognized.</p>';
    }
}

function formatAnalysisText(text) {
    if (!text || text.trim() === '') {
        return '<p><em>No specific information available.</em></p>';
    }
    
    // Convert text to HTML with proper formatting
    const lines = text.split('\n').filter(line => line.trim() !== '');
    let html = '';
    
    for (let line of lines) {
        line = line.trim();
        if (line.startsWith('-') || line.startsWith('•')) {
            // List item
            html += `<li>${line.substring(1).trim()}</li>`;
        } else if (line.includes(':') && line.length < 100) {
            // Likely a header or key-value pair
            const [key, ...valueParts] = line.split(':');
            const value = valueParts.join(':').trim();
            if (value) {
                html += `<p><strong>${key.trim()}:</strong> ${value}</p>`;
            } else {
                html += `<h5>${key.trim()}</h5>`;
            }
        } else {
            // Regular paragraph
            html += `<p>${line}</p>`;
        }
    }
    
    // Wrap list items in ul tags
    html = html.replace(/(<li>.*?<\/li>)+/g, '<ul>$&</ul>');
    
    return html || '<p><em>Analysis completed but no detailed information available.</em></p>';
}

function parseRawAnalysis(rawText) {
    const sections = {
        facial_attributes: '',
        contextual_analysis: '',
        reverse_image_search: '',
        social_media_indicators: '',
        risk_factors: '',
        recommendations: ''
    };
    
    const lines = rawText.split('\n');
    let currentSection = null;
    
    for (let line of lines) {
        line = line.trim();
        const upperLine = line.toUpperCase();
        
        if (upperLine.includes('FACIAL ATTRIBUTES') || upperLine.includes('FACE DETECTION')) {
            currentSection = 'facial_attributes';
        } else if (upperLine.includes('CONTEXTUAL') || upperLine.includes('BACKGROUND')) {
            currentSection = 'contextual_analysis';
        } else if (upperLine.includes('REVERSE IMAGE') || upperLine.includes('SEARCH STRATEGY')) {
            currentSection = 'reverse_image_search';
        } else if (upperLine.includes('SOCIAL MEDIA') || upperLine.includes('INDICATORS')) {
            currentSection = 'social_media_indicators';
        } else if (upperLine.includes('RISK') || upperLine.includes('VULNERABILITIES')) {
            currentSection = 'risk_factors';
        } else if (upperLine.includes('RECOMMENDATION') || upperLine.includes('MITIGATION')) {
            currentSection = 'recommendations';
        } else if (currentSection && line) {
            sections[currentSection] += line + '\n';
        }
    }
    
    return sections;
}

function showGeminiTab(tabName) {
    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => {
        content.classList.remove('active');
    });
    
    // Remove active class from all tab buttons
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(btn => {
        btn.classList.remove('active');
    });
    
    // Show selected tab content
    const selectedTab = document.getElementById(tabName + '-tab');
    if (selectedTab) {
        selectedTab.classList.add('active');
    }
    
    // Add active class to clicked button
    event.target.classList.add('active');
}

function updateThreatLevelWithConfidence(level, confidence) {
    updateThreatLevel(level);
    
    // Show confidence score if available
    const confidenceScore = document.getElementById('confidence-score');
    const confidenceValue = document.getElementById('confidence-value');
    
    if (confidence && confidence > 0) {
        confidenceValue.textContent = confidence + '%';
        confidenceScore.style.display = 'block';
    } else {
        confidenceScore.style.display = 'none';
    }
}

// Enhanced displayResults function to handle Gemini data
function displayResultsEnhanced(data) {
    // Update threat level with confidence
    updateThreatLevelWithConfidence(data.threat_level, data.confidence_score);
    
    // Display Gemini analysis if available
    if (data.gemini_analysis) {
        displayGeminiAnalysis(data.gemini_analysis);
    }
    
    // Display traditional face matches
    displayFaceMatches(data.matches || []);
    
    // Display traditional OSINT results (renamed to avoid confusion)
    displayTraditionalOSINT(data.traditional_osint || data.osint_results || []);
    
    // Display enhanced analysis summary
    displayEnhancedAnalysisSummary(data);
    
    // Show results section
    resultsSection.style.display = 'block';
    resultsSection.classList.add('slide-up');
    
    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });
}

function displayTraditionalOSINT(results) {
    const container = document.getElementById('osint-container');
    
    if (results.length === 0) {
        container.innerHTML = '<p class="no-results">No public data found through traditional OSINT methods</p>';
        return;
    }
    
    container.innerHTML = results.map(result => `
        <div class="osint-item">
            <div class="osint-source">${result.source}</div>
            <div class="osint-details">
                ${formatOSINTData(result)}
            </div>
        </div>
    `).join('');
}

function displayEnhancedAnalysisSummary(data) {
    const container = document.getElementById('summary-content');
    
    const matchCount = data.matches ? data.matches.length : 0;
    const osintCount = (data.traditional_osint || data.osint_results || []).length;
    const geminiEnabled = data.gemini_enabled || false;
    
    let summary = `
        <div class="summary-stats">
            <div class="stat-item">
                <span class="stat-number">${matchCount}</span>
                <span class="stat-label">Face Matches</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${osintCount}</span>
                <span class="stat-label">OSINT Hits</span>
            </div>
            <div class="stat-item">
                <span class="stat-number">${data.threat_level}</span>
                <span class="stat-label">Threat Level</span>
            </div>
        </div>
    `;
    
    if (geminiEnabled) {
        summary += `
            <div class="gemini-summary">
                <h5><i class="fas fa-brain"></i> AI-Enhanced Analysis Available</h5>
                <p>Advanced analysis using Google's Gemini AI provides deeper insights into facial attributes, OSINT potential, and privacy risks. Check the "AI-Enhanced Analysis" section above for detailed findings.</p>
            </div>
        `;
    } else {
        summary += `
            <div class="gemini-unavailable">
                <h5><i class="fas fa-info-circle"></i> Enhanced Analysis Unavailable</h5>
                <p>Gemini AI integration is not configured. Results shown are from traditional face recognition and basic OSINT methods only.</p>
            </div>
        `;
    }
    
    container.innerHTML = summary;
}

// Update the main analyzeImage function to use enhanced display
function analyzeImageEnhanced() {
    if (!currentImageFile) {
        alert('Please select an image first');
        return;
    }
    
    // Show loading
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';
    
    const formData = new FormData();
    formData.append('file', currentImageFile);
    
    fetch('/api/face/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        loadingSection.style.display = 'none';
        
        if (data.success) {
            displayResultsEnhanced(data);
        } else {
            alert('Analysis failed: ' + (data.error || 'Unknown error'));
        }
    })
    .catch(error => {
        loadingSection.style.display = 'none';
        console.error('Error:', error);
        alert('Analysis failed: ' + error.message);
    });
}

// Replace the original analyzeImage function
if (typeof analyzeImage !== 'undefined') {
    analyzeImage = analyzeImageEnhanced;
}

// Add loading state for Gemini analysis
function showGeminiLoading() {
    const geminiSection = document.getElementById('gemini-analysis');
    geminiSection.style.display = 'block';
    geminiSection.innerHTML = `
        <div class="analysis-header">
            <h3><i class="fas fa-brain"></i> AI-Enhanced Analysis</h3>
            <span class="gemini-badge">Powered by Gemini</span>
        </div>
        <div class="gemini-loading">
            Analyzing with AI...
        </div>
    `;
}


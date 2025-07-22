from flask import Blueprint, request, jsonify, current_app
import os
import cv2
import numpy as np
from PIL import Image
import base64
import io
from werkzeug.utils import secure_filename
import hashlib
import requests
from src.utils.gemini_integration import get_gemini_analyzer, is_gemini_available

face_bp = Blueprint('face', __name__)

# Configuration
UPLOAD_FOLDER = 'src/face_data/uploads'
KNOWN_FACES_FOLDER = 'src/face_data/known_faces'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def detect_faces_opencv(image_path):
    """Detect faces using OpenCV Haar Cascades"""
    # Load the cascade
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    # Read the image
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Detect faces
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    return faces, img

def extract_face_features(image_path):
    """Extract basic face features for comparison"""
    faces, img = detect_faces_opencv(image_path)
    
    if len(faces) == 0:
        return None
    
    # Get the largest face (assuming it's the main subject)
    largest_face = max(faces, key=lambda x: x[2] * x[3])
    x, y, w, h = largest_face
    
    # Extract face region
    face_roi = img[y:y+h, x:x+w]
    
    # Resize to standard size for comparison
    face_roi = cv2.resize(face_roi, (100, 100))
    
    # Convert to grayscale and flatten for simple comparison
    gray_face = cv2.cvtColor(face_roi, cv2.COLOR_BGR2GRAY)
    
    return {
        'face_region': face_roi,
        'gray_face': gray_face,
        'coordinates': (x, y, w, h),
        'features': gray_face.flatten()
    }

def compare_faces(features1, features2):
    """Simple face comparison using correlation"""
    if features1 is None or features2 is None:
        return 0.0
    
    # Calculate correlation coefficient
    correlation = np.corrcoef(features1['features'], features2['features'])[0, 1]
    
    # Convert to confidence score (0-100)
    confidence = max(0, correlation * 100) if not np.isnan(correlation) else 0
    
    return confidence

def search_gravatar(email_hash):
    """Search for Gravatar profile"""
    try:
        url = f"https://www.gravatar.com/{email_hash}.json"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def search_github_avatar(username):
    """Search for GitHub avatar"""
    try:
        url = f"https://api.github.com/users/{username}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            user_data = response.json()
            return {
                'avatar_url': user_data.get('avatar_url'),
                'name': user_data.get('name'),
                'bio': user_data.get('bio'),
                'public_repos': user_data.get('public_repos'),
                'followers': user_data.get('followers')
            }
    except:
        pass
    return None

@face_bp.route('/upload', methods=['POST'])
def upload_face():
    """Handle face image upload and analysis with Gemini enhancement"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            file.save(filepath)
            
            # Extract features from uploaded image (traditional method)
            uploaded_features = extract_face_features(filepath)
            
            if uploaded_features is None:
                return jsonify({'error': 'No face detected in uploaded image'}), 400
            
            # Compare with known faces (traditional method)
            matches = []
            known_faces_dir = KNOWN_FACES_FOLDER
            
            if os.path.exists(known_faces_dir):
                for known_file in os.listdir(known_faces_dir):
                    if allowed_file(known_file):
                        known_path = os.path.join(known_faces_dir, known_file)
                        known_features = extract_face_features(known_path)
                        
                        if known_features is not None:
                            confidence = compare_faces(uploaded_features, known_features)
                            if confidence > 30:  # Threshold for potential match
                                matches.append({
                                    'filename': known_file,
                                    'confidence': round(confidence, 2),
                                    'path': known_path
                                })
            
            # Sort matches by confidence
            matches.sort(key=lambda x: x['confidence'], reverse=True)
            
            # Enhanced analysis with Gemini API
            gemini_results = {}
            if is_gemini_available():
                analyzer = get_gemini_analyzer()
                
                # Perform Gemini face analysis
                face_analysis = analyzer.analyze_face_image(filepath)
                if face_analysis.get('success'):
                    gemini_results['face_analysis'] = face_analysis['analysis']
                
                # Perform Gemini OSINT analysis
                osint_analysis = analyzer.enhance_osint_search(filepath, {'matches': matches})
                if osint_analysis.get('success'):
                    gemini_results['osint_analysis'] = osint_analysis['osint_analysis']
                
                # Generate enhanced threat assessment
                threat_assessment = analyzer.generate_threat_assessment(
                    face_analysis.get('analysis', {}),
                    osint_analysis.get('osint_analysis', {}),
                    matches
                )
                if threat_assessment.get('success'):
                    gemini_results['threat_assessment'] = threat_assessment['threat_assessment']
            
            # Traditional OSINT lookup (basic implementation)
            traditional_osint = []
            
            # Try some common email patterns for Gravatar
            if matches:
                # Extract name from filename for demo purposes
                name_guess = matches[0]['filename'].split('.')[0].lower()
                common_domains = ['gmail.com', 'yahoo.com', 'hotmail.com']
                
                for domain in common_domains:
                    email = f"{name_guess}@{domain}"
                    email_hash = hashlib.md5(email.encode()).hexdigest()
                    gravatar_data = search_gravatar(email_hash)
                    
                    if gravatar_data:
                        traditional_osint.append({
                            'source': 'Gravatar',
                            'email': email,
                            'data': gravatar_data
                        })
                        break
                
                # Try GitHub lookup
                github_data = search_github_avatar(name_guess)
                if github_data:
                    traditional_osint.append({
                        'source': 'GitHub',
                        'username': name_guess,
                        'data': github_data
                    })
            
            # Calculate enhanced threat level
            threat_level = "LOW"
            confidence_score = 0
            
            # Use Gemini threat assessment if available
            if gemini_results.get('threat_assessment'):
                threat_data = gemini_results['threat_assessment']
                if isinstance(threat_data, dict):
                    if 'structured' in threat_data:
                        threat_level = threat_data['structured'].get('threat_level', 'LOW')
                        confidence_score = threat_data['structured'].get('confidence_score', 0)
                    elif 'threat_level' in threat_data:
                        threat_level = threat_data.get('threat_level', 'LOW')
                        confidence_score = threat_data.get('confidence_score', 0)
            else:
                # Fallback to traditional threat assessment
                if matches and len(matches) > 0:
                    max_confidence = max([m['confidence'] for m in matches])
                    if max_confidence > 70:
                        threat_level = "HIGH"
                        confidence_score = 85
                    elif max_confidence > 50:
                        threat_level = "MEDIUM"
                        confidence_score = 65
                    else:
                        confidence_score = 35
                
                if traditional_osint:
                    threat_level = "HIGH"  # Any OSINT hit increases threat level
                    confidence_score = max(confidence_score, 80)
            
            # Prepare response
            response_data = {
                'success': True,
                'faces_detected': 1,
                'matches': matches[:5],  # Top 5 matches
                'traditional_osint': traditional_osint,
                'threat_level': threat_level,
                'confidence_score': confidence_score,
                'uploaded_file': filename,
                'gemini_enabled': is_gemini_available()
            }
            
            # Add Gemini results if available
            if gemini_results:
                response_data['gemini_analysis'] = gemini_results
            
            return jsonify(response_data)
        
        return jsonify({'error': 'Invalid file type'}), 400
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@face_bp.route('/webcam', methods=['POST'])
def process_webcam():
    """Process webcam snapshot"""
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({'error': 'No image data provided'}), 400
        
        # Decode base64 image
        image_data = data['image'].split(',')[1]  # Remove data:image/jpeg;base64,
        image_bytes = base64.b64decode(image_data)
        
        # Save temporary file
        filename = f"webcam_{hashlib.md5(image_bytes).hexdigest()[:8]}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        
        with open(filepath, 'wb') as f:
            f.write(image_bytes)
        
        # Process same as upload
        uploaded_features = extract_face_features(filepath)
        
        if uploaded_features is None:
            return jsonify({'error': 'No face detected in webcam image'}), 400
        
        # Same matching logic as upload
        matches = []
        known_faces_dir = KNOWN_FACES_FOLDER
        
        if os.path.exists(known_faces_dir):
            for known_file in os.listdir(known_faces_dir):
                if allowed_file(known_file):
                    known_path = os.path.join(known_faces_dir, known_file)
                    known_features = extract_face_features(known_path)
                    
                    if known_features is not None:
                        confidence = compare_faces(uploaded_features, known_features)
                        if confidence > 30:
                            matches.append({
                                'filename': known_file,
                                'confidence': round(confidence, 2),
                                'path': known_path
                            })
        
        matches.sort(key=lambda x: x['confidence'], reverse=True)
        
        # Calculate threat level
        threat_level = "LOW"
        if matches and len(matches) > 0:
            max_confidence = max([m['confidence'] for m in matches])
            if max_confidence > 70:
                threat_level = "HIGH"
            elif max_confidence > 50:
                threat_level = "MEDIUM"
        
        return jsonify({
            'success': True,
            'faces_detected': 1,
            'matches': matches[:5],
            'threat_level': threat_level,
            'webcam_file': filename
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@face_bp.route('/status', methods=['GET'])
def get_status():
    """Get application status and statistics"""
    try:
        known_faces_count = 0
        if os.path.exists(KNOWN_FACES_FOLDER):
            known_faces_count = len([f for f in os.listdir(KNOWN_FACES_FOLDER) 
                                   if allowed_file(f)])
        
        uploads_count = 0
        if os.path.exists(UPLOAD_FOLDER):
            uploads_count = len([f for f in os.listdir(UPLOAD_FOLDER) 
                               if allowed_file(f)])
        
        # Check Gemini availability
        gemini_available = is_gemini_available()
        
        return jsonify({
            'status': 'active',
            'known_faces': known_faces_count,
            'uploads': uploads_count,
            'features': {
                'face_detection': True,
                'face_matching': True,
                'osint_lookup': True,
                'threat_assessment': True,
                'gemini_integration': gemini_available,
                'enhanced_analysis': gemini_available,
                'advanced_osint': gemini_available
            },
            'gemini': {
                'enabled': gemini_available,
                'capabilities': [
                    'Advanced face analysis',
                    'Enhanced OSINT search suggestions',
                    'Intelligent threat assessment',
                    'Contextual image understanding',
                    'Privacy risk evaluation'
                ] if gemini_available else []
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# OSINT Face Recognition Simulator with Gemini AI

A Flask-based web application designed for Red Team OSINT simulation purposes, demonstrating how facial recognition technology combined with public data can identify individuals and raise awareness of privacy risks. **Now enhanced with Google's Gemini AI for advanced analysis capabilities.**

## ⚠️ Important Disclaimer

**This application is designed for educational and awareness purposes only.** It demonstrates potential privacy risks associated with facial recognition technology and public data correlation. 

**DO NOT USE THIS TOOL FOR:**
- Unauthorized surveillance
- Stalking or harassment
- Identifying individuals without their consent
- Any illegal activities

**ONLY USE FOR:**
- Educational purposes
- Privacy awareness training
- Security research (with proper authorization)
- Personal privacy assessment

## 🎯 Purpose

This simulator demonstrates how easily someone could potentially be identified using:
- Facial recognition technology
- Publicly available data sources
- OSINT (Open Source Intelligence) techniques

The goal is to raise awareness about digital privacy and the importance of protecting personal information online.

## 🚀 Features

### Core Functionality
- **Face Detection**: Uses OpenCV Haar Cascades for face detection
- **Face Matching**: Compares uploaded faces against a local database
- **Confidence Scoring**: Provides matching confidence percentages
- **Threat Level Assessment**: Calculates privacy risk levels (LOW/MEDIUM/HIGH/CRITICAL)

### 🧠 AI-Enhanced Analysis (Gemini Integration)
- **Advanced Face Analysis**: Detailed facial attribute analysis using Gemini's vision capabilities
- **Contextual Understanding**: AI-powered analysis of image context, background, and setting
- **Enhanced OSINT Insights**: Intelligent suggestions for reverse image searches and data correlation
- **Smart Threat Assessment**: AI-driven privacy risk evaluation with detailed explanations
- **Natural Language Analysis**: Human-readable insights and recommendations

### Web Interface
- **Responsive Design**: Works on desktop and mobile devices
- **File Upload**: Support for common image formats (PNG, JPG, JPEG, GIF)
- **Webcam Capture**: Real-time photo capture using device camera
- **Interactive Results**: Visual display of matches and threat levels
- **AI Analysis Tabs**: Organized display of Gemini-powered insights

### OSINT Integration
- **Traditional Methods**: Gravatar and GitHub API lookups
- **AI-Enhanced Search**: Gemini-powered search strategy recommendations
- **Reverse Image Analysis**: Intelligent suggestions for image search optimization
- **Social Media Indicators**: AI identification of platform-specific clues
- **Geographic Analysis**: Location and cultural context identification

### Privacy Features
- **Temporary Processing**: Images are processed and automatically deleted
- **No Tracking**: No cookies, analytics, or persistent data storage
- **Local Processing**: Face detection performed locally
- **Graceful Degradation**: Works with or without Gemini API access

## 🛠️ Technology Stack

- **Backend**: Flask (Python)
- **Face Detection**: OpenCV
- **AI Enhancement**: Google Gemini API
- **Frontend**: HTML5, CSS3, JavaScript
- **APIs**: Gravatar, GitHub, Google Gemini
- **Database**: SQLite (for application data, not face storage)
- **Deployment**: Railway/Heroku compatible

## 📋 Requirements

- Python 3.11+
- OpenCV
- Flask
- Pillow (PIL)
- NumPy
- Requests
- Google Generative AI (for Gemini integration)
- Google AI API Key (optional, for enhanced features)

## 🔧 Installation

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd osint-face-app
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python src/main.py
   ```

5. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

### 🧠 Gemini AI Setup (Optional but Recommended)

To enable advanced AI-powered analysis features:

1. **Get a Google AI API Key**
   - Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the generated API key

2. **Configure the API Key**
   ```bash
   # Option 1: Environment variable (recommended)
   export GOOGLE_AI_API_KEY='your-api-key-here'
   
   # Option 2: Add to your shell profile for persistence
   echo 'export GOOGLE_AI_API_KEY="your-api-key-here"' >> ~/.bashrc
   source ~/.bashrc
   ```

3. **Verify Gemini Integration**
   ```bash
   python test_gemini_integration.py
   ```

4. **Restart the application**
   The application will automatically detect the API key and enable enhanced features.

**Note**: The application works perfectly without Gemini API access, but you'll miss out on advanced AI-powered insights and analysis capabilities.

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "src/main.py"]
```

## 🚀 Deployment

### Railway Deployment

1. **Connect your repository to Railway**
2. **Set environment variables** (if needed)
3. **Deploy automatically** - Railway will detect the Procfile

### Heroku Deployment

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Deploy**
   ```bash
   git push heroku main
   ```

### Manual Server Deployment

1. **Install dependencies on server**
2. **Use a production WSGI server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 src.main:app
   ```

## 📖 Usage Guide

### Basic Usage

1. **Upload an Image**
   - Click "Choose File" to select an image from your device
   - Or drag and drop an image onto the upload area

2. **Use Webcam**
   - Click "Start Camera" to activate your webcam
   - Click "Capture" to take a photo
   - Click "Stop" to deactivate the camera

3. **Analyze Face**
   - Click "Analyze Face" after uploading or capturing an image
   - Wait for the analysis to complete

4. **Review Results**
   - Check the threat level indicator
   - Review face matches and confidence scores
   - Examine any public data found through OSINT

### 🧠 Enhanced AI Analysis (When Gemini is Enabled)

1. **AI-Enhanced Analysis Section**
   - Look for the "AI-Enhanced Analysis" section with the Gemini badge
   - Navigate through three tabs: Face Analysis, OSINT Insights, and Threat Assessment

2. **Face Analysis Tab**
   - **Facial Attributes**: Detailed analysis of age, gender, ethnicity, expressions, and accessories
   - **Image Context**: Background analysis, setting description, and photo quality assessment

3. **OSINT Insights Tab**
   - **Search Strategy**: AI-recommended approaches for reverse image searches
   - **Potential Indicators**: Social media clues, professional contexts, and geographic markers

4. **Threat Assessment Tab**
   - **Risk Factors**: Detailed explanation of what makes the person identifiable
   - **Privacy Recommendations**: Specific steps to protect privacy and reduce digital footprint

5. **Enhanced Threat Level**
   - More accurate threat assessment with confidence scores
   - AI-powered reasoning behind the threat level determination

### Settings

- **OSINT Toggle**: Enable/disable external API lookups
- **Offline Mode**: Use only local face matching when OSINT is disabled

## 🔍 How It Works

### Face Detection Process

1. **Image Processing**: Uploaded images are processed using OpenCV
2. **Face Detection**: Haar Cascade classifiers detect faces in the image
3. **Feature Extraction**: Basic facial features are extracted for comparison
4. **Database Matching**: Features are compared against known faces
5. **Confidence Scoring**: Correlation analysis provides matching confidence

### OSINT Lookup Process

1. **Pattern Generation**: Creates common email/username patterns from filenames
2. **Gravatar Search**: Checks for profile pictures using MD5 email hashes
3. **GitHub Lookup**: Searches for user profiles using GitHub API
4. **Data Correlation**: Combines results to assess identification risk

### Threat Level Calculation

- **LOW**: No strong matches or public data found
- **MEDIUM**: Some facial matches with moderate confidence
- **HIGH**: Strong facial matches and/or public profiles discovered

## 🗂️ Project Structure

```
osint-face-app/
├── src/
│   ├── face_data/
│   │   ├── known_faces/     # Sample face database
│   │   └── uploads/         # Temporary upload storage
│   ├── models/              # Database models
│   ├── routes/              # Flask route handlers
│   │   ├── face_recognition.py  # Main face analysis routes (Gemini-enhanced)
│   │   └── user.py          # User management routes
│   ├── static/              # Frontend files
│   │   ├── index.html       # Main interface (with Gemini UI)
│   │   ├── style.css        # Styling (enhanced for Gemini)
│   │   └── script.js        # JavaScript functionality (Gemini integration)
│   ├── utils/               # Utility modules
│   │   └── gemini_integration.py  # Gemini API integration
│   └── main.py              # Flask application entry point
├── venv/                    # Virtual environment
├── requirements.txt         # Python dependencies (includes Gemini)
├── Procfile                 # Deployment configuration
├── runtime.txt              # Python version specification
├── test_gemini_integration.py  # Gemini integration test script
├── README.md               # This file (updated for Gemini)
├── SECURITY.md             # Security guidelines (updated)
└── DEPLOYMENT.md           # Deployment guide (updated)
```

## 🔒 Security Considerations

### Data Privacy
- Images are processed temporarily and automatically deleted
- No persistent storage of uploaded images
- No tracking or analytics implemented

### API Security
- External API calls use public endpoints only
- No authentication tokens or private data transmitted
- Rate limiting should be implemented for production use

### Deployment Security
- Change default Flask secret key for production
- Use HTTPS in production environments
- Implement proper error handling and logging
- Consider implementing user authentication for sensitive deployments

## 🧪 Testing

### Manual Testing
1. Upload various image types and sizes
2. Test webcam functionality across different browsers
3. Verify face detection accuracy
4. Test OSINT lookup functionality
5. Check responsive design on mobile devices

### API Testing
```bash
# Test status endpoint
curl http://localhost:5000/api/face/status

# Test file upload (with actual image file)
curl -X POST -F "file=@test_image.jpg" http://localhost:5000/api/face/upload
```

## 🤝 Contributing

This is an educational project. If you'd like to contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

### Development Guidelines
- Follow PEP 8 for Python code
- Use meaningful commit messages
- Document new features
- Ensure educational value is maintained

## 📚 Educational Resources

### Privacy Protection
- Use privacy-focused browsers and search engines
- Limit social media profile visibility
- Be cautious about sharing photos online
- Understand facial recognition opt-out options

### OSINT Awareness
- Learn about information that's publicly available about you
- Understand how data correlation works
- Practice good operational security (OPSEC)
- Stay informed about privacy laws and regulations

## 🐛 Troubleshooting

### Common Issues

**Face detection not working:**
- Ensure image contains clear, front-facing faces
- Check image quality and lighting
- Verify OpenCV installation

**Webcam not accessible:**
- Check browser permissions
- Ensure HTTPS is used (required for webcam access)
- Try different browsers

**OSINT lookups failing:**
- Check internet connection
- Verify API endpoints are accessible
- Consider rate limiting issues

**Deployment issues:**
- Verify all dependencies are in requirements.txt
- Check Python version compatibility
- Ensure proper file permissions

## 📄 License

This project is released under the MIT License. See LICENSE file for details.

## 🙏 Acknowledgments

- OpenCV community for computer vision tools
- Flask development team
- Privacy advocacy organizations
- Security research community

## 📞 Support

For educational use questions or issues:
- Check the troubleshooting section
- Review the documentation
- Consider the ethical implications of your use case

Remember: This tool is designed to demonstrate privacy risks and promote awareness. Use responsibly and ethically.

---

**Built for educational purposes to promote digital privacy awareness.**


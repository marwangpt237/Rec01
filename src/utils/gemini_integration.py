"""
Gemini API Integration for Enhanced OSINT Face Recognition
Provides advanced image analysis, face analysis, and OSINT capabilities using Google's Gemini API
"""

import os
import base64
import io
from PIL import Image
import google.generativeai as genai
from typing import Dict, List, Optional, Any
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """
    Enhanced face and image analysis using Google's Gemini API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Gemini analyzer
        
        Args:
            api_key: Google AI API key. If None, will try to get from environment
        """
        self.api_key = api_key or os.getenv('GOOGLE_AI_API_KEY')
        if not self.api_key:
            logger.warning("No Gemini API key provided. Gemini features will be disabled.")
            self.enabled = False
            return
            
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-1.5-flash')
            self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
            self.enabled = True
            logger.info("Gemini API initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")
            self.enabled = False
    
    def is_enabled(self) -> bool:
        """Check if Gemini integration is enabled"""
        return self.enabled
    
    def analyze_face_image(self, image_path: str) -> Dict[str, Any]:
        """
        Analyze a face image using Gemini's vision capabilities
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Dictionary containing analysis results
        """
        if not self.enabled:
            return {"error": "Gemini API not available"}
            
        try:
            # Load and prepare image
            image = Image.open(image_path)
            
            # Create detailed prompt for face analysis
            prompt = """
            Analyze this image for facial recognition and OSINT purposes. Provide a detailed analysis including:
            
            1. FACE DETECTION:
            - Number of faces detected
            - Primary face location and size
            - Face quality assessment (lighting, angle, clarity)
            
            2. FACIAL ATTRIBUTES:
            - Estimated age range
            - Gender presentation
            - Ethnicity/appearance
            - Facial hair (if any)
            - Glasses or accessories
            - Emotional expression
            
            3. CONTEXTUAL ANALYSIS:
            - Background/setting description
            - Clothing or uniform details
            - Any visible text, logos, or identifiers
            - Photo quality and likely source (professional, social media, ID photo, etc.)
            
            4. OSINT POTENTIAL:
            - Unique identifying features
            - Potential reverse image search indicators
            - Social media profile likelihood
            - Professional/corporate context clues
            
            5. PRIVACY RISK ASSESSMENT:
            - How easily identifiable is this person?
            - What additional information could be gathered?
            - Potential privacy concerns
            
            Format your response as structured JSON with clear categories.
            Be thorough but respectful in your analysis.
            """
            
            response = self.vision_model.generate_content([prompt, image])
            
            # Parse response
            analysis_text = response.text
            
            # Try to extract JSON if present, otherwise structure the text response
            try:
                # Look for JSON in the response
                if '{' in analysis_text and '}' in analysis_text:
                    json_start = analysis_text.find('{')
                    json_end = analysis_text.rfind('}') + 1
                    json_str = analysis_text[json_start:json_end]
                    analysis_data = json.loads(json_str)
                else:
                    # Structure the text response
                    analysis_data = {
                        "raw_analysis": analysis_text,
                        "structured": self._parse_analysis_text(analysis_text)
                    }
            except json.JSONDecodeError:
                analysis_data = {
                    "raw_analysis": analysis_text,
                    "structured": self._parse_analysis_text(analysis_text)
                }
            
            return {
                "success": True,
                "analysis": analysis_data,
                "model_used": "gemini-1.5-flash"
            }
            
        except Exception as e:
            logger.error(f"Gemini face analysis failed: {e}")
            return {"error": f"Analysis failed: {str(e)}"}
    
    def enhance_osint_search(self, image_path: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Use Gemini to enhance OSINT search capabilities
        
        Args:
            image_path: Path to the image file
            context: Additional context from previous analysis
            
        Returns:
            Enhanced OSINT search suggestions and analysis
        """
        if not self.enabled:
            return {"error": "Gemini API not available"}
            
        try:
            image = Image.open(image_path)
            
            context_info = ""
            if context:
                context_info = f"Previous analysis context: {json.dumps(context, indent=2)}"
            
            prompt = f"""
            As an OSINT (Open Source Intelligence) expert, analyze this image to suggest search strategies and potential data sources for identification purposes. This is for educational/awareness purposes only.
            
            {context_info}
            
            Provide analysis in these categories:
            
            1. REVERSE IMAGE SEARCH STRATEGY:
            - Best search engines to use (Google Images, TinEye, Yandex, etc.)
            - Optimal image cropping suggestions
            - Alternative search approaches
            
            2. SOCIAL MEDIA INDICATORS:
            - Platform-specific clues (Instagram, LinkedIn, Facebook style)
            - Profile picture likelihood
            - Background location clues
            
            3. PROFESSIONAL/INSTITUTIONAL CLUES:
            - Corporate/organizational indicators
            - Uniform or badge analysis
            - Professional setting context
            
            4. GEOGRAPHIC/LOCATION CLUES:
            - Background architecture or landmarks
            - License plates, signs, or text
            - Cultural or regional indicators
            
            5. TEMPORAL CLUES:
            - Photo age estimation
            - Fashion/style dating
            - Technology visible in image
            
            6. SEARCH KEYWORDS:
            - Suggested search terms
            - Boolean search combinations
            - Alternative descriptive terms
            
            7. PRIVACY IMPLICATIONS:
            - How this information could be misused
            - Privacy protection recommendations
            - Ethical considerations
            
            Format as structured JSON. Be educational and emphasize responsible use.
            """
            
            response = self.vision_model.generate_content([prompt, image])
            analysis_text = response.text
            
            # Parse response similar to face analysis
            try:
                if '{' in analysis_text and '}' in analysis_text:
                    json_start = analysis_text.find('{')
                    json_end = analysis_text.rfind('}') + 1
                    json_str = analysis_text[json_start:json_end]
                    osint_data = json.loads(json_str)
                else:
                    osint_data = {
                        "raw_analysis": analysis_text,
                        "structured": self._parse_osint_text(analysis_text)
                    }
            except json.JSONDecodeError:
                osint_data = {
                    "raw_analysis": analysis_text,
                    "structured": self._parse_osint_text(analysis_text)
                }
            
            return {
                "success": True,
                "osint_analysis": osint_data,
                "model_used": "gemini-1.5-flash"
            }
            
        except Exception as e:
            logger.error(f"Gemini OSINT analysis failed: {e}")
            return {"error": f"OSINT analysis failed: {str(e)}"}
    
    def generate_threat_assessment(self, face_analysis: Dict[str, Any], osint_analysis: Dict[str, Any], 
                                 traditional_matches: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate an enhanced threat assessment using Gemini's reasoning capabilities
        
        Args:
            face_analysis: Results from Gemini face analysis
            osint_analysis: Results from Gemini OSINT analysis
            traditional_matches: Results from traditional face matching
            
        Returns:
            Enhanced threat level assessment
        """
        if not self.enabled:
            return {"error": "Gemini API not available"}
            
        try:
            prompt = f"""
            As a privacy and security expert, analyze the following data to provide a comprehensive threat assessment for facial recognition privacy risks.
            
            FACE ANALYSIS DATA:
            {json.dumps(face_analysis, indent=2)}
            
            OSINT ANALYSIS DATA:
            {json.dumps(osint_analysis, indent=2)}
            
            TRADITIONAL MATCHING RESULTS:
            {json.dumps(traditional_matches, indent=2)}
            
            Provide a comprehensive threat assessment including:
            
            1. OVERALL THREAT LEVEL: (LOW/MEDIUM/HIGH/CRITICAL)
            
            2. RISK FACTORS:
            - Image quality and identifiability
            - OSINT potential and data availability
            - Matching confidence levels
            - Context and background information
            
            3. SPECIFIC VULNERABILITIES:
            - What makes this person identifiable
            - Potential attack vectors
            - Data correlation possibilities
            
            4. MITIGATION RECOMMENDATIONS:
            - Privacy protection steps
            - Image sharing best practices
            - Digital footprint reduction
            
            5. EDUCATIONAL INSIGHTS:
            - What this demonstrates about privacy risks
            - How facial recognition technology works
            - Real-world implications
            
            6. CONFIDENCE SCORE: (0-100)
            - How confident are you in this assessment
            - What factors increase/decrease confidence
            
            Format as structured JSON. Be educational and focus on privacy awareness.
            """
            
            response = self.model.generate_content(prompt)
            assessment_text = response.text
            
            # Parse response
            try:
                if '{' in assessment_text and '}' in assessment_text:
                    json_start = assessment_text.find('{')
                    json_end = assessment_text.rfind('}') + 1
                    json_str = assessment_text[json_start:json_end]
                    assessment_data = json.loads(json_str)
                else:
                    assessment_data = {
                        "raw_assessment": assessment_text,
                        "structured": self._parse_threat_text(assessment_text)
                    }
            except json.JSONDecodeError:
                assessment_data = {
                    "raw_assessment": assessment_text,
                    "structured": self._parse_threat_text(assessment_text)
                }
            
            return {
                "success": True,
                "threat_assessment": assessment_data,
                "model_used": "gemini-1.5-flash"
            }
            
        except Exception as e:
            logger.error(f"Gemini threat assessment failed: {e}")
            return {"error": f"Threat assessment failed: {str(e)}"}
    
    def _parse_analysis_text(self, text: str) -> Dict[str, Any]:
        """Parse unstructured analysis text into categories"""
        sections = {
            "face_detection": "",
            "facial_attributes": "",
            "contextual_analysis": "",
            "osint_potential": "",
            "privacy_risk": ""
        }
        
        current_section = None
        for line in text.split('\n'):
            line = line.strip()
            if 'FACE DETECTION' in line.upper():
                current_section = 'face_detection'
            elif 'FACIAL ATTRIBUTES' in line.upper():
                current_section = 'facial_attributes'
            elif 'CONTEXTUAL' in line.upper():
                current_section = 'contextual_analysis'
            elif 'OSINT' in line.upper():
                current_section = 'osint_potential'
            elif 'PRIVACY' in line.upper():
                current_section = 'privacy_risk'
            elif current_section and line:
                sections[current_section] += line + " "
        
        return sections
    
    def _parse_osint_text(self, text: str) -> Dict[str, Any]:
        """Parse unstructured OSINT text into categories"""
        sections = {
            "reverse_image_search": "",
            "social_media_indicators": "",
            "professional_clues": "",
            "geographic_clues": "",
            "search_keywords": "",
            "privacy_implications": ""
        }
        
        current_section = None
        for line in text.split('\n'):
            line = line.strip()
            if 'REVERSE IMAGE' in line.upper():
                current_section = 'reverse_image_search'
            elif 'SOCIAL MEDIA' in line.upper():
                current_section = 'social_media_indicators'
            elif 'PROFESSIONAL' in line.upper():
                current_section = 'professional_clues'
            elif 'GEOGRAPHIC' in line.upper() or 'LOCATION' in line.upper():
                current_section = 'geographic_clues'
            elif 'KEYWORDS' in line.upper():
                current_section = 'search_keywords'
            elif 'PRIVACY' in line.upper():
                current_section = 'privacy_implications'
            elif current_section and line:
                sections[current_section] += line + " "
        
        return sections
    
    def _parse_threat_text(self, text: str) -> Dict[str, Any]:
        """Parse unstructured threat assessment text"""
        sections = {
            "threat_level": "UNKNOWN",
            "risk_factors": "",
            "vulnerabilities": "",
            "recommendations": "",
            "insights": "",
            "confidence_score": 0
        }
        
        # Extract threat level
        for level in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            if level in text.upper():
                sections['threat_level'] = level
                break
        
        # Extract confidence score
        import re
        confidence_match = re.search(r'(\d+)(?:/100|\%)', text)
        if confidence_match:
            sections['confidence_score'] = int(confidence_match.group(1))
        
        # Parse sections
        current_section = None
        for line in text.split('\n'):
            line = line.strip()
            if 'RISK FACTORS' in line.upper():
                current_section = 'risk_factors'
            elif 'VULNERABILITIES' in line.upper():
                current_section = 'vulnerabilities'
            elif 'RECOMMENDATIONS' in line.upper() or 'MITIGATION' in line.upper():
                current_section = 'recommendations'
            elif 'INSIGHTS' in line.upper() or 'EDUCATIONAL' in line.upper():
                current_section = 'insights'
            elif current_section and line:
                sections[current_section] += line + " "
        
        return sections

# Global instance
gemini_analyzer = None

def get_gemini_analyzer() -> GeminiAnalyzer:
    """Get or create global Gemini analyzer instance"""
    global gemini_analyzer
    if gemini_analyzer is None:
        gemini_analyzer = GeminiAnalyzer()
    return gemini_analyzer

def is_gemini_available() -> bool:
    """Check if Gemini API is available and configured"""
    analyzer = get_gemini_analyzer()
    return analyzer.is_enabled()


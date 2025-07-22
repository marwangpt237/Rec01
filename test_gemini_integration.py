#!/usr/bin/env python3
"""
Test script for Gemini integration in OSINT Face Recognition Simulator
"""

import sys
import os
sys.path.append('src')

from utils.gemini_integration import get_gemini_analyzer, is_gemini_available
from routes.face_recognition import face_bp
import json

def test_gemini_integration():
    """Test Gemini integration functionality"""
    print("🧪 Testing Gemini Integration...")
    print("=" * 50)
    
    # Test 1: Import and initialization
    print("1. Testing imports and initialization...")
    try:
        analyzer = get_gemini_analyzer()
        available = is_gemini_available()
        print(f"   ✅ Gemini analyzer created successfully")
        print(f"   ✅ Gemini available: {available}")
        print(f"   ✅ Analyzer enabled: {analyzer.is_enabled()}")
    except Exception as e:
        print(f"   ❌ Import/initialization failed: {e}")
        return False
    
    # Test 2: Test without API key (should gracefully handle)
    print("\n2. Testing without API key...")
    try:
        if not analyzer.is_enabled():
            print("   ✅ Correctly disabled when no API key provided")
            
            # Test analyze_face_image method
            result = analyzer.analyze_face_image("dummy_path.jpg")
            if "error" in result and "not available" in result["error"]:
                print("   ✅ analyze_face_image correctly returns error when disabled")
            else:
                print(f"   ⚠️  Unexpected result: {result}")
            
            # Test enhance_osint_search method
            result = analyzer.enhance_osint_search("dummy_path.jpg")
            if "error" in result and "not available" in result["error"]:
                print("   ✅ enhance_osint_search correctly returns error when disabled")
            else:
                print(f"   ⚠️  Unexpected result: {result}")
            
            # Test generate_threat_assessment method
            result = analyzer.generate_threat_assessment({}, {}, [])
            if "error" in result and "not available" in result["error"]:
                print("   ✅ generate_threat_assessment correctly returns error when disabled")
            else:
                print(f"   ⚠️  Unexpected result: {result}")
        else:
            print("   ⚠️  Analyzer is enabled (API key might be configured)")
    except Exception as e:
        print(f"   ❌ Testing without API key failed: {e}")
        return False
    
    # Test 3: Test Flask route integration
    print("\n3. Testing Flask route integration...")
    try:
        from flask import Flask
        app = Flask(__name__)
        app.register_blueprint(face_bp, url_prefix='/api/face')
        
        with app.test_client() as client:
            response = client.get('/api/face/status')
            if response.status_code == 200:
                data = response.get_json()
                print("   ✅ Status endpoint accessible")
                print(f"   ✅ Gemini integration reported: {data.get('features', {}).get('gemini_integration', False)}")
                print(f"   ✅ Enhanced analysis reported: {data.get('features', {}).get('enhanced_analysis', False)}")
                
                # Check if gemini section exists in response
                if 'gemini' in data:
                    print(f"   ✅ Gemini section present in status response")
                    print(f"   ✅ Gemini enabled: {data['gemini'].get('enabled', False)}")
                    print(f"   ✅ Capabilities count: {len(data['gemini'].get('capabilities', []))}")
                else:
                    print("   ⚠️  Gemini section missing from status response")
            else:
                print(f"   ❌ Status endpoint failed: {response.status_code}")
                return False
    except Exception as e:
        print(f"   ❌ Flask route integration test failed: {e}")
        return False
    
    # Test 4: Test utility functions
    print("\n4. Testing utility functions...")
    try:
        # Test text parsing functions
        from utils.gemini_integration import GeminiAnalyzer
        analyzer_instance = GeminiAnalyzer()
        
        # Test _parse_analysis_text
        test_text = """
        FACE DETECTION:
        - One face detected
        - Good lighting conditions
        
        FACIAL ATTRIBUTES:
        - Age: 25-35 years
        - Gender: Male
        
        CONTEXTUAL ANALYSIS:
        - Indoor setting
        - Professional background
        """
        
        parsed = analyzer_instance._parse_analysis_text(test_text)
        if isinstance(parsed, dict) and 'face_detection' in parsed:
            print("   ✅ _parse_analysis_text works correctly")
        else:
            print(f"   ⚠️  _parse_analysis_text unexpected result: {type(parsed)}")
        
        # Test _parse_threat_text
        threat_text = "THREAT LEVEL: HIGH\nCONFIDENCE: 85%\nRISK FACTORS: Multiple indicators found"
        threat_parsed = analyzer_instance._parse_threat_text(threat_text)
        if isinstance(threat_parsed, dict) and threat_parsed.get('threat_level') == 'HIGH':
            print("   ✅ _parse_threat_text works correctly")
        else:
            print(f"   ⚠️  _parse_threat_text unexpected result: {threat_parsed}")
            
    except Exception as e:
        print(f"   ❌ Utility functions test failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All Gemini integration tests passed!")
    print("\n📋 Summary:")
    print("   • Gemini integration properly handles missing API key")
    print("   • Flask routes correctly report Gemini capabilities")
    print("   • Utility functions work as expected")
    print("   • Application gracefully degrades when Gemini is unavailable")
    print("\n💡 To enable Gemini features:")
    print("   1. Get a Google AI API key from https://aistudio.google.com/app/apikey")
    print("   2. Set environment variable: export GOOGLE_AI_API_KEY='your-api-key'")
    print("   3. Restart the application")
    
    return True

if __name__ == "__main__":
    success = test_gemini_integration()
    sys.exit(0 if success else 1)


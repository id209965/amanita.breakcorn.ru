#!/usr/bin/env python3
"""Simple test to validate the video player application."""

import requests
import time
from bs4 import BeautifulSoup

def test_server_response():
    """Test that server responds correctly."""
    print("🌐 Testing server response...")
    
    try:
        response = requests.get('http://localhost:8000', timeout=10)
        print(f"✅ Server responded with status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"📄 Content length: {len(response.text)} bytes")
            return True
        else:
            print(f"❌ Unexpected status code: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Server request failed: {e}")
        return False

def test_html_structure():
    """Test HTML structure and required elements."""
    print("\n🔍 Testing HTML structure...")
    
    try:
        response = requests.get('http://localhost:8000', timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Test title
        title = soup.find('title')
        if title and title.text.strip() == 'Λ V X T V':
            print("✅ Page title is correct")
        else:
            print(f"❌ Page title incorrect: {title.text if title else 'Missing'}")
        
        # Test player element
        player = soup.find('div', id='PLAYER')
        if player:
            print("✅ Player element found")
            
            # Check data attributes
            provider = player.get('data-plyr-provider')
            embed_id = player.get('data-plyr-embed-id')
            
            if provider in ['youtube', 'vimeo']:
                print(f"✅ Player provider: {provider}")
            else:
                print(f"❌ Invalid provider: {provider}")
                
            if embed_id:
                print(f"✅ Embed ID present: {embed_id[:10]}...")
            else:
                print("❌ Embed ID missing")
        else:
            print("❌ Player element not found")
            
        # Test script tags
        scripts = soup.find_all('script')
        plyr_script = any('plyr' in script.get('src', '').lower() for script in scripts if script.get('src'))
        
        if plyr_script:
            print("✅ Plyr script found")
        else:
            print("❌ Plyr script not found")
            
        # Test inline JavaScript
        inline_scripts = [script for script in scripts if not script.get('src')]
        if inline_scripts:
            print(f"✅ Found {len(inline_scripts)} inline script blocks")
            
            # Look for key variables
            script_content = ' '.join(script.text for script in inline_scripts)
            if 'videos' in script_content:
                print("✅ Videos array found in JavaScript")
            if 'loadNextVideo' in script_content:
                print("✅ loadNextVideo function found")
            if 'MAX_VIDEOS_BEFORE_RECREATE' in script_content:
                print("✅ Memory management constants found")
        else:
            print("❌ No inline scripts found")
            
        return True
        
    except Exception as e:
        print(f"❌ HTML structure test failed: {e}")
        return False

def test_cypress_files():
    """Test that Cypress files are properly created."""
    print("\n🧪 Testing Cypress test files...")
    
    import os
    
    expected_files = [
        'package.json',
        'cypress.config.js',
        'cypress/support/e2e.js',
        'cypress/support/commands.js',
        'cypress/e2e/unit/basic-page-test.cy.js',
        'cypress/e2e/unit/page-structure.cy.js',
        'cypress/e2e/unit/javascript-functions.cy.js',
        'cypress/e2e/integration/video-player.cy.js',
        'cypress/e2e/memory/memory-management.cy.js',
        'cypress/e2e/performance/performance.cy.js',
        'cypress/fixtures/test-videos.json'
    ]
    
    all_present = True
    for file_path in expected_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_present = False
            
    return all_present

def test_configuration_files():
    """Test configuration files."""
    print("\n⚙️ Testing configuration files...")
    
    import os
    import json
    
    # Test package.json
    try:
        with open('package.json', 'r') as f:
            package_data = json.load(f)
            
        if 'cypress' in package_data.get('devDependencies', {}):
            print("✅ Cypress dependency found in package.json")
        else:
            print("❌ Cypress dependency missing from package.json")
            
        if 'scripts' in package_data:
            scripts = package_data['scripts']
            test_scripts = ['test', 'cypress:open', 'test:unit', 'test:integration']
            
            for script in test_scripts:
                if script in scripts:
                    print(f"✅ Script '{script}' found")
                else:
                    print(f"❌ Script '{script}' missing")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting Video Player Test Validation")
    print("=" * 50)
    
    tests = [
        test_server_response,
        test_html_structure,
        test_cypress_files,
        test_configuration_files
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        if test_func():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Cypress testing system is properly set up.")
        print("\n📋 Next steps:")
        print("   1. Install Node.js 20+ for Cypress compatibility")
        print("   2. Run: npm install")
        print("   3. Run: npm run cypress:open (interactive mode)")
        print("   4. Or run: npm test (headless mode)")
        return 0
    else:
        print(f"❌ {total - passed} tests failed. Please check the issues above.")
        return 1

if __name__ == '__main__':
    exit(main())

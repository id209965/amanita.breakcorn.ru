import os
import time
import json
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


class TestEnvironment:
    """Utilities for setting up test environment."""
    
    @staticmethod
    def is_server_running(url, timeout=30):
        """Check if HTTP server is running."""
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        return False
    
    @staticmethod
    def wait_for_server(url, timeout=30):
        """Wait for HTTP server to become available."""
        if not TestEnvironment.is_server_running(url, timeout):
            raise TimeoutError(f"Server at {url} did not start within {timeout} seconds")
    
    @staticmethod
    def get_test_config():
        """Get test configuration from environment variables."""
        return {
            'base_url': os.getenv('BASE_URL', 'http://localhost:8000'),
            'headless': os.getenv('CI', 'false').lower() == 'true',
            'browser': os.getenv('BROWSER', 'chrome').lower(),
            'timeout': int(os.getenv('TEST_TIMEOUT', '30')),
            'slow_timeout': int(os.getenv('SLOW_TEST_TIMEOUT', '120'))
        }


class VideoTestData:
    """Test data and utilities for video testing."""
    
    # Test video IDs that should be stable
    TEST_VIDEOS = [
        {'type': 'yt', 'id': 'dQw4w9WgXcQ', 'title': 'Test Video 1'},  # Rick Roll - stable test video
        {'type': 'yt', 'id': 'tL6ZTcrDPAU', 'title': 'Duke Ellington Caravan'},
        {'type': 'vimeo', 'id': '1234567', 'title': 'Test Vimeo Video'} # Placeholder
    ]
    
    @staticmethod
    def get_youtube_test_video():
        """Get a reliable YouTube test video."""
        return {'type': 'yt', 'id': 'dQw4w9WgXcQ'}
    
    @staticmethod
    def get_vimeo_test_video():
        """Get a reliable Vimeo test video."""
        # Note: Vimeo test videos might need to be updated periodically
        return {'type': 'vimeo', 'id': '1234567'}


class BrowserHelpers:
    """Helper utilities for browser automation."""
    
    @staticmethod
    def wait_for_element_clickable(driver, locator, timeout=10):
        """Wait for element to be clickable."""
        return WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable(locator)
        )
    
    @staticmethod
    def wait_for_javascript_ready(driver, timeout=30):
        """Wait for JavaScript to be ready."""
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Wait for our specific JavaScript to load
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return typeof videos !== 'undefined';")
        )
    
    @staticmethod
    def safe_execute_script(driver, script, default=None):
        """Safely execute JavaScript with error handling."""
        try:
            return driver.execute_script(script)
        except Exception as e:
            print(f"JavaScript execution failed: {e}")
            return default
    
    @staticmethod
    def get_console_errors(driver):
        """Get console errors from browser."""
        try:
            logs = driver.get_log('browser')
            return [log for log in logs if log['level'] == 'SEVERE']
        except Exception:
            return []
    
    @staticmethod
    def get_network_errors(driver):
        """Get network errors from browser."""
        try:
            logs = driver.get_log('performance')
            # Filter for network errors
            network_errors = []
            for log in logs:
                message = json.loads(log['message'])
                if (message.get('message', {}).get('method') == 'Network.loadingFailed'):
                    network_errors.append(message)
            return network_errors
        except Exception:
            return []
    
    @staticmethod
    def take_screenshot_on_failure(driver, test_name, screenshot_dir='screenshots'):
        """Take screenshot on test failure."""
        try:
            if not os.path.exists(screenshot_dir):
                os.makedirs(screenshot_dir)
            
            timestamp = int(time.time())
            filename = f"{test_name}_{timestamp}.png"
            filepath = os.path.join(screenshot_dir, filename)
            
            driver.save_screenshot(filepath)
            print(f"Screenshot saved: {filepath}")
            return filepath
        except Exception as e:
            print(f"Failed to take screenshot: {e}")
            return None


class MemoryTestHelpers:
    """Helpers for memory testing."""
    
    @staticmethod
    def get_memory_info(driver):
        """Get detailed memory information."""
        return BrowserHelpers.safe_execute_script(driver, """
            const memory = window.performance.memory || {};
            const navigation = window.performance.navigation || {};
            const timing = window.performance.timing || {};
            
            return {
                memory: {
                    usedJSHeapSize: memory.usedJSHeapSize || 0,
                    totalJSHeapSize: memory.totalJSHeapSize || 0,
                    jsHeapSizeLimit: memory.jsHeapSizeLimit || 0
                },
                navigation: {
                    type: navigation.type,
                    redirectCount: navigation.redirectCount
                },
                timing: {
                    loadEventEnd: timing.loadEventEnd,
                    loadEventStart: timing.loadEventStart,
                    domContentLoadedEventEnd: timing.domContentLoadedEventEnd
                },
                timestamp: Date.now()
            };
        """, {})
    
    @staticmethod
    def calculate_memory_delta(before, after):
        """Calculate memory usage delta."""
        if not before.get('memory') or not after.get('memory'):
            return {}
        
        before_mem = before['memory']
        after_mem = after['memory']
        
        return {
            'used_heap_delta': after_mem.get('usedJSHeapSize', 0) - before_mem.get('usedJSHeapSize', 0),
            'total_heap_delta': after_mem.get('totalJSHeapSize', 0) - before_mem.get('totalJSHeapSize', 0),
            'used_heap_delta_mb': (after_mem.get('usedJSHeapSize', 0) - before_mem.get('usedJSHeapSize', 0)) / (1024 * 1024),
            'time_delta': after.get('timestamp', 0) - before.get('timestamp', 0)
        }
    
    @staticmethod
    def force_garbage_collection(driver):
        """Force garbage collection if available."""
        BrowserHelpers.safe_execute_script(driver, """
            if (window.gc) {
                window.gc();
            }
            // Try alternative methods
            if (window.CollectGarbage) {
                window.CollectGarbage();
            }
        """)


class ReportHelpers:
    """Helpers for generating test reports."""
    
    @staticmethod
    def create_performance_report(test_results, output_file='performance_report.json'):
        """Create performance test report."""
        report = {
            'timestamp': time.time(),
            'test_results': test_results,
            'summary': {
                'total_tests': len(test_results),
                'passed_tests': len([r for r in test_results if r.get('passed', False)]),
                'failed_tests': len([r for r in test_results if not r.get('passed', True)])
            }
        }
        
        try:
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(report, f, indent=2)
            return output_file
        except Exception as e:
            print(f"Failed to create report: {e}")
            return None
    
    @staticmethod
    def log_test_metrics(test_name, metrics):
        """Log test metrics for monitoring."""
        print(f"=== {test_name} Metrics ===")
        for key, value in metrics.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
        print("" + "=" * (len(test_name) + 12))

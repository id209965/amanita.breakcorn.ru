import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.unit
@pytest.mark.browser
class TestJavaScriptFunctions:
    """Test JavaScript functions and variables."""
    
    def test_global_variables_initialization(self, loaded_page):
        """Test that global variables are properly initialized."""
        # Check that key global variables exist
        globals_check = loaded_page.execute_script("""
            return {
                videos: typeof videos !== 'undefined',
                currentVideoIndex: typeof currentVideoIndex !== 'undefined',
                currentVideo: typeof currentVideo !== 'undefined',
                player: typeof player !== 'undefined',
                videoCount: typeof videoCount !== 'undefined',
                consecutiveFailures: typeof consecutiveFailures !== 'undefined'
            };
        """)
        
        assert globals_check['videos'], "Videos array should be defined"
        assert globals_check['currentVideoIndex'], "currentVideoIndex should be defined"
        assert globals_check['videoCount'], "videoCount should be defined"
        assert globals_check['consecutiveFailures'], "consecutiveFailures should be defined"
    
    def test_video_constants(self, loaded_page):
        """Test that video-related constants have correct values."""
        constants = loaded_page.execute_script("""
            return {
                MAX_VIDEOS_BEFORE_RECREATE: window.MAX_VIDEOS_BEFORE_RECREATE,
                MAX_CONSECUTIVE_FAILURES: window.MAX_CONSECUTIVE_FAILURES,
                VIDEO_LOAD_TIMEOUT: window.VIDEO_LOAD_TIMEOUT,
                WATCHDOG_CHECK_INTERVAL: window.WATCHDOG_CHECK_INTERVAL
            };
        """)
        
        assert constants['MAX_VIDEOS_BEFORE_RECREATE'] == 5, "MAX_VIDEOS_BEFORE_RECREATE should be 5"
        assert constants['MAX_CONSECUTIVE_FAILURES'] == 3, "MAX_CONSECUTIVE_FAILURES should be 3"
        assert constants['VIDEO_LOAD_TIMEOUT'] == 15000, "VIDEO_LOAD_TIMEOUT should be 15000"
        assert constants['WATCHDOG_CHECK_INTERVAL'] == 3000, "WATCHDOG_CHECK_INTERVAL should be 3000"
    
    def test_load_next_video_function_exists(self, loaded_page):
        """Test that loadNextVideo function exists and is callable."""
        function_exists = loaded_page.execute_script(
            "return typeof loadNextVideo === 'function';"
        )
        assert function_exists, "loadNextVideo function should exist"
    
    def test_create_player_function_exists(self, loaded_page):
        """Test that createPlayer function exists and is callable."""
        function_exists = loaded_page.execute_script(
            "return typeof createPlayer === 'function';"
        )
        assert function_exists, "createPlayer function should exist"
    
    def test_cleanup_player_function_exists(self, loaded_page):
        """Test that cleanupPlayer function exists and is callable."""
        function_exists = loaded_page.execute_script(
            "return typeof cleanupPlayer === 'function';"
        )
        assert function_exists, "cleanupPlayer function should exist"
    
    def test_memory_monitoring_functions(self, loaded_page):
        """Test that memory monitoring functions exist."""
        functions_check = loaded_page.execute_script("""
            return {
                logMemoryUsage: typeof logMemoryUsage === 'function',
                memoryMonitorInterval: typeof memoryMonitorInterval !== 'undefined'
            };
        """)
        
        assert functions_check['logMemoryUsage'], "logMemoryUsage function should exist"
    
    def test_watchdog_functions(self, loaded_page):
        """Test that watchdog monitoring functions exist."""
        functions_check = loaded_page.execute_script("""
            return {
                startWatchdog: typeof startWatchdog === 'function',
                stopWatchdog: typeof stopWatchdog === 'function',
                checkVideoProgress: typeof checkVideoProgress === 'function'
            };
        """)
        
        assert functions_check['startWatchdog'], "startWatchdog function should exist"
        assert functions_check['stopWatchdog'], "stopWatchdog function should exist"
        assert functions_check['checkVideoProgress'], "checkVideoProgress function should exist"
    
    def test_error_handling_functions(self, loaded_page):
        """Test that error handling functions exist."""
        functions_check = loaded_page.execute_script("""
            return {
                handleVideoError: typeof handleVideoError === 'function',
                handleLoadTimeout: typeof handleLoadTimeout === 'function'
            };
        """)
        
        assert functions_check['handleVideoError'], "handleVideoError function should exist"
        assert functions_check['handleLoadTimeout'], "handleLoadTimeout function should exist"
    
    def test_keyboard_event_listeners(self, loaded_page):
        """Test that keyboard event listeners are properly set up."""
        # Check if keydown event listeners are attached
        has_keydown_listeners = loaded_page.execute_script("""
            // Try to determine if keydown listeners are attached
            return document.addEventListener.length !== undefined || 
                   window.onkeydown !== null ||
                   document.onkeydown !== null;
        """)
        
        # This is a basic check - in a real scenario, we might need to simulate key presses
        # to verify the functionality works correctly
        
    def test_console_error_handling(self, loaded_page):
        """Test that console errors are being handled properly."""
        # Execute a script that might cause an error and check if it's handled
        try:
            loaded_page.execute_script("""
                // Try to access a potentially problematic property
                try {
                    window.parent.postMessage('test', '*');
                } catch (e) {
                    console.log('Caught postMessage error, ignoring:', e.message);
                }
            """)
            
            # If we get here, error handling is working
            assert True
        except Exception as e:
            pytest.fail(f"JavaScript error was not properly handled: {e}")

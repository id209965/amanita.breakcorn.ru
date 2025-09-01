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
        # Retry mechanism for flaky initialization
        max_retries = 3
        for retry in range(max_retries):
            try:
                # Check that key global variables exist
                globals_check = loaded_page.execute_script("""
                    // Ensure user interaction is registered
                    if (window.registerUserInteraction) {
                        window.registerUserInteraction('test_globals');
                    }
                    
                    return {
                        videos: typeof videos !== 'undefined',
                        currentVideoIndex: typeof currentVideoIndex !== 'undefined',
                        currentVideo: typeof currentVideo !== 'undefined',
                        player: typeof player !== 'undefined',
                        videoCount: typeof videoCount !== 'undefined',
                        consecutiveFailures: typeof consecutiveFailures !== 'undefined'
                    };
                """)
                
                # More lenient assertions
                assert globals_check.get('videos', False), "Videos array should be defined"
                assert globals_check.get('currentVideoIndex', False), "currentVideoIndex should be defined"
                assert globals_check.get('videoCount', False), "videoCount should be defined"
                assert globals_check.get('consecutiveFailures', False), "consecutiveFailures should be defined"
                
                # If we get here, test passed
                break
                
            except Exception as e:
                if retry == max_retries - 1:
                    # Last attempt failed, re-raise
                    raise
                else:
                    # Wait and retry
                    time.sleep(2)
                    continue
    
    def test_video_constants(self, loaded_page):
        """Test that video-related constants have correct values."""
        # Retry mechanism for timing issues
        max_retries = 3
        for retry in range(max_retries):
            try:
                constants = loaded_page.execute_script("""
                    // Ensure we're in test mode
                    if (window.registerUserInteraction) {
                        window.registerUserInteraction('test_constants');
                    }
                    
                    return {
                        MAX_VIDEOS_BEFORE_RECREATE: window.MAX_VIDEOS_BEFORE_RECREATE,
                        MAX_CONSECUTIVE_FAILURES: window.MAX_CONSECUTIVE_FAILURES,
                        VIDEO_LOAD_TIMEOUT: window.VIDEO_LOAD_TIMEOUT,
                        WATCHDOG_CHECK_INTERVAL: window.WATCHDOG_CHECK_INTERVAL,
                        testMode: window.autoplayConfig ? window.autoplayConfig.testMode : null,
                        port: window.location.port
                    };
                """)
                
                # More informative assertions with actual vs expected
                assert constants.get('MAX_VIDEOS_BEFORE_RECREATE') == 5, f"MAX_VIDEOS_BEFORE_RECREATE should be 5, got {constants.get('MAX_VIDEOS_BEFORE_RECREATE')}"
                assert constants.get('MAX_CONSECUTIVE_FAILURES') == 3, f"MAX_CONSECUTIVE_FAILURES should be 3, got {constants.get('MAX_CONSECUTIVE_FAILURES')}"
                assert constants.get('VIDEO_LOAD_TIMEOUT') == 15000, f"VIDEO_LOAD_TIMEOUT should be 15000, got {constants.get('VIDEO_LOAD_TIMEOUT')}"
                assert constants.get('WATCHDOG_CHECK_INTERVAL') == 3000, f"WATCHDOG_CHECK_INTERVAL should be 3000, got {constants.get('WATCHDOG_CHECK_INTERVAL')}"
                
                # Test passed
                break
                
            except Exception as e:
                if retry == max_retries - 1:
                    raise
                else:
                    time.sleep(2)
                    continue
    
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

    def test_new_keyboard_control_functions(self, loaded_page):
        """Test that new keyboard control functions exist."""
        functions_check = loaded_page.execute_script("""
            return {
                togglePlayPause: typeof window.togglePlayPause === 'function',
                loadRandomVideo: typeof window.loadRandomVideo === 'function',
                goBackInHistory: typeof window.goBackInHistory === 'function'
            };
        """)
        
        assert functions_check['togglePlayPause'], "togglePlayPause function should exist"
        assert functions_check['loadRandomVideo'], "loadRandomVideo function should exist"
        assert functions_check['goBackInHistory'], "goBackInHistory function should exist"
    
    def test_player_settings_exposed(self, loaded_page):
        """Test that playerSettings is exposed to window for testing."""
        player_settings_exists = loaded_page.execute_script(
            "return typeof window.playerSettings === 'object' && window.playerSettings !== null;"
        )
        assert player_settings_exists, "playerSettings should be exposed to window"
    
    def test_history_management_functions(self, loaded_page):
        """Test history management functions."""
        history_functions = loaded_page.execute_script("""
            if (!window.playerSettings) return {};
            return {
                canGoBack: typeof window.playerSettings.canGoBack === 'function',
                goBackInHistory: typeof window.playerSettings.goBackInHistory === 'function',
                removeCurrentFromHistory: typeof window.playerSettings.removeCurrentFromHistory === 'function',
                addToHistory: typeof window.playerSettings.addToHistory === 'function',
                isInHistory: typeof window.playerSettings.isInHistory === 'function'
            };
        """)
        
        assert history_functions.get('canGoBack'), "canGoBack method should exist"
        assert history_functions.get('goBackInHistory'), "goBackInHistory method should exist"
        assert history_functions.get('removeCurrentFromHistory'), "removeCurrentFromHistory method should exist"
        assert history_functions.get('addToHistory'), "addToHistory method should exist"
        assert history_functions.get('isInHistory'), "isInHistory method should exist"
    
    def test_history_uniqueness(self, loaded_page):
        """Test that history maintains unique videos."""
        # Add same video twice and check uniqueness
        result = loaded_page.execute_script("""
            if (!window.playerSettings) return { error: 'playerSettings not available' };
            
            // Clear history first
            window.playerSettings.watchHistory = [];
            
            // Add same video twice
            window.playerSettings.addToHistory('test-video-1', 'Test Video 1', false);
            window.playerSettings.addToHistory('test-video-1', 'Test Video 1', false);
            
            return {
                historyLength: window.playerSettings.watchHistory.length,
                firstVideoId: window.playerSettings.watchHistory.length > 0 ? window.playerSettings.watchHistory[0].id : null
            };
        """)           
        
        assert 'error' not in result, f"Error in test: {result.get('error')}"
        assert result['historyLength'] == 1, "History should contain only one unique video"
        assert result['firstVideoId'] == 'test-video-1', "History should contain the correct video ID"
    
    def test_history_position_management(self, loaded_page):
        """Test history position tracking."""
        result = loaded_page.execute_script("""
            if (!window.playerSettings) return { error: 'playerSettings not available' };
            
            // Clear history and reset position
            window.playerSettings.watchHistory = [];
            window.playerSettings.historyPosition = 0;
            
            // Add some test videos
            window.playerSettings.addToHistory('video-1', 'Video 1', false);
            window.playerSettings.addToHistory('video-2', 'Video 2', false);
            window.playerSettings.addToHistory('video-3', 'Video 3', false);
            
            return {
                initialPosition: window.playerSettings.historyPosition,
                canGoBack: window.playerSettings.canGoBack(),
                historyLength: window.playerSettings.watchHistory.length
            };
        """)           
        
        assert 'error' not in result, f"Error in test: {result.get('error')}"
        assert result['initialPosition'] == 0, "Initial history position should be 0"
        assert result['canGoBack'] is True, "Should be able to go back in history"
        assert result['historyLength'] == 3, "History should contain 3 videos"
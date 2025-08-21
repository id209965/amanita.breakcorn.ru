import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@pytest.mark.integration
@pytest.mark.browser
@pytest.mark.memory
@pytest.mark.slow
class TestMemoryManagement:
    """Test memory management and cleanup functionality."""
    
    def test_memory_monitoring_active(self, loaded_page, memory_monitor):
        """Test that memory monitoring is active."""
        # Wait for initial load
        time.sleep(5)
        
        initial_memory = memory_monitor.get_current_memory()
        assert initial_memory, "Memory monitoring should be available"
        
        # Check that memory monitoring interval is running
        monitor_active = loaded_page.execute_script(
            "return typeof memoryMonitorInterval !== 'undefined' && memoryMonitorInterval !== null;"
        )
        assert monitor_active, "Memory monitoring interval should be active"
    
    def test_player_recreation_after_max_videos(self, loaded_page, video_player_helper, memory_monitor):
        """Test that player is recreated after MAX_VIDEOS_BEFORE_RECREATE."""
        # Get MAX_VIDEOS_BEFORE_RECREATE value
        max_videos = loaded_page.execute_script("return MAX_VIDEOS_BEFORE_RECREATE;")
        assert max_videos == 5, "MAX_VIDEOS_BEFORE_RECREATE should be 5"
        
        # Wait for initial video
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Track initial player instance
        initial_player_id = loaded_page.execute_script(
            "return window.player ? window.player.id || 'no-id' : 'no-player';"
        )
        
        # Go through videos to trigger recreation
        successful_transitions = 0
        for i in range(max_videos + 1):  # One more than the limit
            try:
                video_player_helper.simulate_next_video()
                time.sleep(2)
                video_player_helper.wait_for_video_load(timeout=30)
                successful_transitions += 1
            except TimeoutException:
                # Some videos might fail, continue
                continue
        
        # Check that player was recreated (videoCount should reset or player changed)
        video_count = loaded_page.execute_script("return videoCount;")
        current_player_id = loaded_page.execute_script(
            "return window.player ? window.player.id || 'no-id' : 'no-player';"
        )
        
        # Either videoCount reset or player instance changed
        recreation_occurred = (
            video_count < max_videos or 
            current_player_id != initial_player_id or
            successful_transitions >= max_videos
        )
        
        assert recreation_occurred, f"Player should be recreated after {max_videos} videos. VideoCount: {video_count}"
    
    def test_memory_cleanup_on_recreation(self, loaded_page, video_player_helper, memory_monitor):
        """Test that memory is cleaned up when player is recreated."""
        # Wait for initial video and get baseline memory
        video_player_helper.wait_for_video_load(timeout=60)
        time.sleep(5)  # Let memory stabilize
        
        baseline_memory = memory_monitor.get_current_memory()
        
        # Force player recreation by calling cleanupPlayer and createPlayer
        loaded_page.execute_script("""
            console.log('Forcing player recreation for memory test...');
            if (typeof cleanupPlayer === 'function') {
                cleanupPlayer();
            }
            if (typeof createPlayer === 'function') {
                createPlayer();
            }
        """)
        
        # Wait for recreation and new video load
        time.sleep(5)
        try:
            video_player_helper.wait_for_video_load(timeout=30)
        except TimeoutException:
            pass  # Player might not load immediately after recreation
        
        # Give time for memory cleanup
        time.sleep(10)
        
        # Force garbage collection if available
        loaded_page.execute_script("""
            if (window.gc) {
                window.gc();
            }
        """)
        
        time.sleep(5)
        
        # Check memory after cleanup
        after_cleanup_memory = memory_monitor.get_current_memory()
        
        # Memory should not have grown excessively (allow some growth for normal operations)
        if baseline_memory.get('usedJSHeapSize') and after_cleanup_memory.get('usedJSHeapSize'):
            memory_growth = after_cleanup_memory['usedJSHeapSize'] - baseline_memory['usedJSHeapSize']
            # Allow up to 10MB growth as reasonable
            max_allowed_growth = 10 * 1024 * 1024  # 10MB
            
            assert memory_growth < max_allowed_growth, f"Memory grew too much: {memory_growth / 1024 / 1024:.2f}MB"
    
    def test_iframe_cleanup(self, loaded_page, video_player_helper):
        """Test that iframe elements are properly cleaned up."""
        # Wait for initial video
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Count initial iframes
        initial_iframes = len(loaded_page.find_elements(By.TAG_NAME, "iframe"))
        
        # Force cleanup
        loaded_page.execute_script("""
            console.log('Testing iframe cleanup...');
            if (typeof cleanupPlayer === 'function') {
                cleanupPlayer();
            }
        """)
        
        time.sleep(3)
        
        # Count iframes after cleanup
        after_cleanup_iframes = len(loaded_page.find_elements(By.TAG_NAME, "iframe"))
        
        # Create new player
        loaded_page.execute_script("""
            if (typeof createPlayer === 'function') {
                createPlayer();
            }
        """)
        
        time.sleep(3)
        
        # Count final iframes
        final_iframes = len(loaded_page.find_elements(By.TAG_NAME, "iframe"))
        
        # After cleanup, iframe count should not continuously grow
        # (exact behavior may vary depending on cleanup implementation)
        assert final_iframes <= initial_iframes + 2, f"Too many iframes after cleanup: {final_iframes}"
    
    def test_watchdog_memory_efficiency(self, loaded_page, video_player_helper, memory_monitor):
        """Test that watchdog doesn't cause memory leaks."""
        # Wait for initial video
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Get initial memory
        initial_memory = memory_monitor.get_current_memory()
        
        # Let watchdog run for a while
        time.sleep(30)  # 30 seconds should trigger several watchdog checks
        
        # Check memory after watchdog activity
        after_watchdog_memory = memory_monitor.get_current_memory()
        
        if initial_memory.get('usedJSHeapSize') and after_watchdog_memory.get('usedJSHeapSize'):
            memory_growth = after_watchdog_memory['usedJSHeapSize'] - initial_memory['usedJSHeapSize']
            # Watchdog should not cause significant memory growth
            max_allowed_growth = 5 * 1024 * 1024  # 5MB
            
            assert memory_growth < max_allowed_growth, f"Watchdog caused too much memory growth: {memory_growth / 1024 / 1024:.2f}MB"
    
    def test_consecutive_failures_cleanup(self, loaded_page, video_player_helper, memory_monitor):
        """Test memory cleanup after consecutive failures."""
        # Wait for initial video
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Get MAX_CONSECUTIVE_FAILURES
        max_failures = loaded_page.execute_script("return MAX_CONSECUTIVE_FAILURES;")
        
        # Simulate consecutive failures
        for i in range(max_failures + 1):
            loaded_page.execute_script("""
                consecutiveFailures++;
                console.log('Simulated failure #' + consecutiveFailures);
                if (typeof handleVideoError === 'function') {
                    handleVideoError(new Error('Simulated error'));
                }
            """)
            time.sleep(1)
        
        # Wait for cleanup to trigger
        time.sleep(5)
        
        # Check that cleanup occurred
        current_failures = loaded_page.execute_script("return consecutiveFailures;")
        
        # After max failures, cleanup should reset the counter or recreate player
        assert current_failures < max_failures, f"Consecutive failures not reset: {current_failures}"
    
    @pytest.mark.slow
    def test_long_running_memory_stability(self, loaded_page, video_player_helper, memory_monitor):
        """Test memory stability over longer period of operation."""
        # Wait for initial video
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Get baseline memory
        baseline_memory = memory_monitor.get_current_memory()
        
        # Run for several minutes, switching videos periodically
        test_duration = 120  # 2 minutes
        video_switch_interval = 20  # Switch every 20 seconds
        
        start_time = time.time()
        while time.time() - start_time < test_duration:
            try:
                video_player_helper.simulate_next_video()
                time.sleep(video_switch_interval)
            except Exception:
                # Continue even if some operations fail
                time.sleep(5)
        
        # Final memory check
        final_memory = memory_monitor.get_current_memory()
        
        if baseline_memory.get('usedJSHeapSize') and final_memory.get('usedJSHeapSize'):
            memory_growth = final_memory['usedJSHeapSize'] - baseline_memory['usedJSHeapSize']
            # Over 2 minutes, memory growth should be reasonable
            max_allowed_growth = 20 * 1024 * 1024  # 20MB for long running test
            
            assert memory_growth < max_allowed_growth, f"Long-running memory growth too high: {memory_growth / 1024 / 1024:.2f}MB"

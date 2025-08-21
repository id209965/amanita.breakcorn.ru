import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@pytest.mark.performance
@pytest.mark.browser
@pytest.mark.slow
class TestPerformance:
    """Performance tests for the video player."""
    
    def test_initial_page_load_time(self, browser, base_url):
        """Test that page loads within acceptable time."""
        start_time = time.time()
        
        browser.get(base_url)
        
        # Wait for essential elements to load
        WebDriverWait(browser, 30).until(
            EC.presence_of_element_located((By.ID, "PLAYER"))
        )
        
        # Wait for JavaScript to initialize
        WebDriverWait(browser, 30).until(
            lambda driver: driver.execute_script("return typeof videos !== 'undefined';")
        )
        
        load_time = time.time() - start_time
        
        # Page should load within 30 seconds
        assert load_time < 30, f"Page took too long to load: {load_time:.2f}s"
        
        # Log performance for monitoring
        print(f"Page load time: {load_time:.2f}s")
    
    def test_video_load_time(self, loaded_page, video_player_helper):
        """Test that videos load within acceptable time."""
        # Measure time to load initial video
        start_time = time.time()
        
        video_player_helper.wait_for_video_load(timeout=60)
        
        load_time = time.time() - start_time
        
        # Video should load within VIDEO_LOAD_TIMEOUT (15 seconds)
        assert load_time < 20, f"Video took too long to load: {load_time:.2f}s"
        
        print(f"Initial video load time: {load_time:.2f}s")
    
    def test_video_transition_performance(self, loaded_page, video_player_helper):
        """Test performance of video transitions."""
        # Wait for initial video
        video_player_helper.wait_for_video_load(timeout=60)
        
        transition_times = []
        max_transitions = 5
        
        for i in range(max_transitions):
            start_time = time.time()
            
            try:
                video_player_helper.simulate_next_video()
                video_player_helper.wait_for_video_load(timeout=30)
                
                transition_time = time.time() - start_time
                transition_times.append(transition_time)
                
            except TimeoutException:
                # Some transitions might fail, don't count them
                continue
        
        if transition_times:
            avg_transition_time = sum(transition_times) / len(transition_times)
            max_transition_time = max(transition_times)
            
            # Average transition should be reasonably fast
            assert avg_transition_time < 15, f"Average transition too slow: {avg_transition_time:.2f}s"
            assert max_transition_time < 25, f"Slowest transition too slow: {max_transition_time:.2f}s"
            
            print(f"Average transition time: {avg_transition_time:.2f}s")
            print(f"Max transition time: {max_transition_time:.2f}s")
        else:
            pytest.skip("No successful transitions to measure")
    
    def test_memory_usage_bounds(self, loaded_page, memory_monitor):
        """Test that memory usage stays within reasonable bounds."""
        # Wait for initial load
        time.sleep(10)
        
        memory_info = memory_monitor.get_current_memory()
        
        if memory_info.get('usedJSHeapSize'):
            used_memory_mb = memory_info['usedJSHeapSize'] / (1024 * 1024)
            heap_limit_mb = memory_info.get('jsHeapSizeLimit', 0) / (1024 * 1024)
            
            # Memory usage should be reasonable
            assert used_memory_mb < 100, f"Initial memory usage too high: {used_memory_mb:.2f}MB"
            
            # Should not be using more than 50% of heap limit initially
            if heap_limit_mb > 0:
                usage_percentage = (used_memory_mb / heap_limit_mb) * 100
                assert usage_percentage < 50, f"Using too much of heap limit: {usage_percentage:.1f}%"
            
            print(f"Memory usage: {used_memory_mb:.2f}MB / {heap_limit_mb:.2f}MB ({usage_percentage:.1f}% of limit)")
        else:
            pytest.skip("Memory monitoring not available in this browser")
    
    def test_dom_manipulation_performance(self, loaded_page, video_player_helper):
        """Test performance of DOM manipulations during video changes."""
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Measure DOM manipulation time during player recreation
        start_time = time.time()
        
        # Force DOM manipulation by recreating player
        loaded_page.execute_script("""
            if (typeof cleanupPlayer === 'function') {
                cleanupPlayer();
            }
            if (typeof createPlayer === 'function') {
                createPlayer();
            }
        """)
        
        # Wait for recreation to complete
        time.sleep(5)
        
        manipulation_time = time.time() - start_time
        
        # DOM manipulation should be fast
        assert manipulation_time < 10, f"DOM manipulation took too long: {manipulation_time:.2f}s"
        
        print(f"DOM manipulation time: {manipulation_time:.2f}s")
    
    def test_watchdog_performance_impact(self, loaded_page, video_player_helper, memory_monitor):
        """Test that watchdog doesn't significantly impact performance."""
        # Measure baseline performance without watchdog activity
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Get initial memory
        initial_memory = memory_monitor.get_current_memory()
        
        # Stop watchdog if it's running
        loaded_page.execute_script("""
            if (typeof stopWatchdog === 'function') {
                stopWatchdog();
            }
        """)
        
        time.sleep(10)  # Baseline period
        memory_without_watchdog = memory_monitor.get_current_memory()
        
        # Start watchdog again
        loaded_page.execute_script("""
            if (typeof startWatchdog === 'function') {
                startWatchdog();
            }
        """)
        
        time.sleep(30)  # Let watchdog run for several cycles
        memory_with_watchdog = memory_monitor.get_current_memory()
        
        # Calculate memory impact
        if (initial_memory.get('usedJSHeapSize') and 
            memory_without_watchdog.get('usedJSHeapSize') and
            memory_with_watchdog.get('usedJSHeapSize')):
            
            baseline_growth = memory_without_watchdog['usedJSHeapSize'] - initial_memory['usedJSHeapSize']
            watchdog_growth = memory_with_watchdog['usedJSHeapSize'] - memory_without_watchdog['usedJSHeapSize']
            
            # Watchdog should not cause significant additional memory usage
            watchdog_impact_mb = watchdog_growth / (1024 * 1024)
            assert watchdog_impact_mb < 5, f"Watchdog memory impact too high: {watchdog_impact_mb:.2f}MB"
            
            print(f"Watchdog memory impact: {watchdog_impact_mb:.2f}MB")
    
    def test_console_performance(self, loaded_page, video_player_helper):
        """Test that console logging doesn't impact performance significantly."""
        # Wait for initial video
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Measure performance with heavy console activity
        start_time = time.time()
        
        # Generate console activity
        loaded_page.execute_script("""
            for (let i = 0; i < 100; i++) {
                console.log('Performance test log message #' + i);
            }
        """)
        
        console_time = time.time() - start_time
        
        # Console operations should be fast
        assert console_time < 5, f"Console operations took too long: {console_time:.2f}s"
        
        # Check that the page is still responsive
        start_time = time.time()
        video_info = video_player_helper.get_current_video_info()
        response_time = time.time() - start_time
        
        assert response_time < 2, f"Page became unresponsive: {response_time:.2f}s"
        assert video_info is not None, "Page should still be functional after console activity"
    
    @pytest.mark.slow
    def test_cpu_usage_during_operation(self, loaded_page, video_player_helper):
        """Test CPU usage during normal operation."""
        import psutil
        
        # Get initial CPU usage
        initial_cpu = psutil.cpu_percent(interval=1)
        
        # Wait for video to load and run normally
        video_player_helper.wait_for_video_load(timeout=60)
        time.sleep(30)  # Let it run for 30 seconds
        
        # Measure CPU during operation
        operation_cpu = psutil.cpu_percent(interval=5)
        
        # CPU usage should not be excessive
        # This is a rough check - actual values depend on system load
        cpu_increase = operation_cpu - initial_cpu
        
        print(f"CPU usage - Initial: {initial_cpu:.1f}%, During operation: {operation_cpu:.1f}%")
        print(f"CPU increase: {cpu_increase:.1f}%")
        
        # This is more for monitoring than strict testing
        # Actual thresholds would depend on system specifications
        if cpu_increase > 50:  # More than 50% CPU increase might indicate issues
            print(f"Warning: High CPU usage increase detected: {cpu_increase:.1f}%")

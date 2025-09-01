import pytest
import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(scope="session")
def base_url():
    """Base URL for the application."""
    return os.getenv("BASE_URL", "http://localhost:8000")


@pytest.fixture(scope="session")
def chrome_driver_service():
    """Chrome driver service for selenium."""
    service = Service(ChromeDriverManager().install())
    yield service
    service.stop()


@pytest.fixture(scope="function")
def chrome_options():
    """Chrome options for selenium tests."""
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    
    # Enable performance monitoring
    options.add_argument("--enable-logging")
    options.add_argument("--log-level=0")
    
    # For CI environments
    if os.getenv("CI"):
        options.add_argument("--headless")
    
    return options


@pytest.fixture(scope="function")
def browser(chrome_driver_service, chrome_options):
    """Browser instance for tests."""
    driver = webdriver.Chrome(service=chrome_driver_service, options=chrome_options)
    driver.implicitly_wait(10)
    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def loaded_page(browser, base_url):
    """Browser with loaded application page."""
    browser.get(base_url)
    
    # Wait for the page to load
    WebDriverWait(browser, 30).until(
        EC.presence_of_element_located((By.ID, "PLAYER"))
    )
    
    # Wait a bit more for scripts to initialize
    time.sleep(3)
    
    # Activate autoplay permission via user interaction
    try:
        browser.execute_script("""
            if (window.registerUserInteraction) {
                window.registerUserInteraction('pytest_init');
            }
        """)
        time.sleep(1)  # Wait for activation to process
    except Exception:
        # Ignore any errors in activation
        pass
    
    return browser


@pytest.fixture(scope="function")
def memory_monitor(browser):
    """Memory monitoring utilities."""
    class MemoryMonitor:
        def __init__(self, driver):
            self.driver = driver
            self.initial_memory = None
            
        def start_monitoring(self):
            """Start memory monitoring."""
            try:
                # Get initial memory usage
                performance = self.driver.execute_script(
                    "return window.performance.memory || {};"
                )
                self.initial_memory = performance
                return performance
            except Exception:
                return {}
        
        def get_current_memory(self):
            """Get current memory usage."""
            try:
                return self.driver.execute_script(
                    "return window.performance.memory || {};"
                )
            except Exception:
                return {}
        
        def get_memory_diff(self):
            """Get memory difference from start."""
            current = self.get_current_memory()
            if not self.initial_memory or not current:
                return {}
            
            return {
                'used_heap_size_diff': current.get('usedJSHeapSize', 0) - self.initial_memory.get('usedJSHeapSize', 0),
                'total_heap_size_diff': current.get('totalJSHeapSize', 0) - self.initial_memory.get('totalJSHeapSize', 0),
                'heap_size_limit': current.get('jsHeapSizeLimit', 0)
            }
    
    monitor = MemoryMonitor(browser)
    monitor.start_monitoring()
    return monitor


@pytest.fixture(scope="function")
def video_player_helper(browser):
    """Helper utilities for video player testing."""
    class VideoPlayerHelper:
        def __init__(self, driver):
            self.driver = driver
        
        def get_player_element(self):
            """Get the main player element."""
            return self.driver.find_element(By.ID, "PLAYER")
        
        def get_current_video_info(self):
            """Get information about currently playing video."""
            return self.driver.execute_script("""
                return {
                    currentVideo: window.currentVideo || null,
                    currentVideoIndex: window.currentVideoIndex || 0,
                    player: window.player ? {
                        ready: window.player.ready || false,
                        playing: window.player.playing || false,
                        paused: window.player.paused || false,
                        duration: window.player.duration || 0,
                        currentTime: window.player.currentTime || 0
                    } : null
                };
            """)
        
        def wait_for_video_load(self, timeout=30):
            """Wait for video to load."""
            def video_loaded(driver):
                info = self.get_current_video_info()
                return info['player'] and info['player']['ready']
            
            WebDriverWait(self.driver, timeout).until(video_loaded)
        
        def simulate_next_video(self):
            """Simulate going to next video."""
            self.driver.execute_script("loadNextVideo();")
        
        def get_console_logs(self):
            """Get browser console logs."""
            logs = self.driver.get_log('browser')
            return [log for log in logs if log['level'] in ['SEVERE', 'WARNING', 'INFO']]
    
    return VideoPlayerHelper(browser)

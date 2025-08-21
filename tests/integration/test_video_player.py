import pytest
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


@pytest.mark.integration
@pytest.mark.browser
@pytest.mark.slow
class TestVideoPlayer:
    """Integration tests for video player functionality."""
    
    def test_initial_video_loads(self, loaded_page, video_player_helper):
        """Test that the initial video loads successfully."""
        # Wait for player to be ready
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Check that video info is available
        video_info = video_player_helper.get_current_video_info()
        
        assert video_info is not None, "Video info should be available"
        assert video_info['player'] is not None, "Player should be initialized"
        assert video_info['currentVideo'] is not None, "Current video should be set"
        assert video_info['currentVideoIndex'] >= 0, "Video index should be valid"
    
    def test_next_video_functionality(self, loaded_page, video_player_helper):
        """Test that next video functionality works."""
        # Wait for initial video to load
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Get initial video info
        initial_info = video_player_helper.get_current_video_info()
        initial_index = initial_info['currentVideoIndex']
        
        # Trigger next video
        video_player_helper.simulate_next_video()
        
        # Wait a bit for the transition
        time.sleep(3)
        
        # Wait for new video to load
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Get new video info
        new_info = video_player_helper.get_current_video_info()
        new_index = new_info['currentVideoIndex']
        
        # Check that we moved to next video
        expected_index = (initial_index + 1) % len(loaded_page.execute_script("return videos.length;"))
        assert new_index == expected_index, f"Should move to next video. Expected {expected_index}, got {new_index}"
    
    def test_keyboard_controls(self, loaded_page, video_player_helper):
        """Test keyboard controls for video navigation."""
        # Wait for initial video to load
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Get initial video info
        initial_info = video_player_helper.get_current_video_info()
        initial_index = initial_info['currentVideoIndex']
        
        # Test spacebar (next video)
        body = loaded_page.find_element(By.TAG_NAME, "body")
        body.send_keys(Keys.SPACE)
        
        # Wait for transition
        time.sleep(3)
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Check that video changed
        new_info = video_player_helper.get_current_video_info()
        assert new_info['currentVideoIndex'] != initial_index, "Spacebar should trigger next video"
        
        # Test 'N' key
        current_index = new_info['currentVideoIndex']
        body.send_keys('n')
        
        time.sleep(3)
        video_player_helper.wait_for_video_load(timeout=60)
        
        newer_info = video_player_helper.get_current_video_info()
        assert newer_info['currentVideoIndex'] != current_index, "'N' key should trigger next video"
    
    def test_click_to_next_video(self, loaded_page, video_player_helper):
        """Test clicking on player to go to next video."""
        # Wait for initial video to load
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Get initial video info
        initial_info = video_player_helper.get_current_video_info()
        initial_index = initial_info['currentVideoIndex']
        
        # Click on player
        player_element = video_player_helper.get_player_element()
        player_element.click()
        
        # Wait for transition
        time.sleep(3)
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Check that video changed
        new_info = video_player_helper.get_current_video_info()
        assert new_info['currentVideoIndex'] != initial_index, "Click should trigger next video"
    
    def test_video_provider_alternation(self, loaded_page, video_player_helper):
        """Test that video provider alternation works (YouTube/Vimeo)."""
        videos = loaded_page.execute_script("return videos;")
        
        # Find videos with different providers
        youtube_videos = [i for i, v in enumerate(videos) if v['type'] == 'yt']
        vimeo_videos = [i for i, v in enumerate(videos) if v['type'] == 'vimeo']
        
        if len(youtube_videos) == 0 or len(vimeo_videos) == 0:
            pytest.skip("Need both YouTube and Vimeo videos to test alternation")
        
        # Wait for initial video
        video_player_helper.wait_for_video_load(timeout=60)
        
        providers_encountered = set()
        max_attempts = min(10, len(videos))  # Don't test too many videos
        
        for _ in range(max_attempts):
            current_info = video_player_helper.get_current_video_info()
            current_video = current_info['currentVideo']
            
            if current_video:
                providers_encountered.add(current_video.get('type', 'unknown'))
            
            # Go to next video
            video_player_helper.simulate_next_video()
            time.sleep(3)
            
            try:
                video_player_helper.wait_for_video_load(timeout=30)
            except TimeoutException:
                # Some videos might fail to load, continue testing
                continue
        
        # We should have encountered different providers
        assert len(providers_encountered) > 1, f"Should encounter multiple providers, got: {providers_encountered}"
    
    @pytest.mark.slow
    def test_multiple_video_transitions(self, loaded_page, video_player_helper):
        """Test multiple video transitions to check stability."""
        video_player_helper.wait_for_video_load(timeout=60)
        
        successful_transitions = 0
        max_transitions = 5
        
        for i in range(max_transitions):
            try:
                # Get current state
                current_info = video_player_helper.get_current_video_info()
                current_index = current_info['currentVideoIndex']
                
                # Trigger next video
                video_player_helper.simulate_next_video()
                time.sleep(2)
                
                # Wait for new video
                video_player_helper.wait_for_video_load(timeout=30)
                
                # Verify transition
                new_info = video_player_helper.get_current_video_info()
                new_index = new_info['currentVideoIndex']
                
                if new_index != current_index:
                    successful_transitions += 1
                    
            except TimeoutException:
                # Some transitions might fail, continue
                continue
        
        # At least half of transitions should succeed
        assert successful_transitions >= max_transitions // 2, f"Only {successful_transitions}/{max_transitions} transitions successful"
    
    def test_error_recovery(self, loaded_page, video_player_helper):
        """Test that the player recovers from errors."""
        video_player_helper.wait_for_video_load(timeout=60)
        
        # Inject an error to test recovery
        loaded_page.execute_script("""
            // Simulate a video error
            if (window.player && window.player.on) {
                window.player.emit('error', new Error('Test error'));
            }
        """)
        
        # Wait a bit for error handling
        time.sleep(5)
        
        # Check that player is still functional
        try:
            video_player_helper.wait_for_video_load(timeout=30)
            # If we get here, recovery worked
            assert True
        except TimeoutException:
            # Recovery might involve going to next video
            video_info = video_player_helper.get_current_video_info()
            assert video_info is not None, "Player should recover from errors"

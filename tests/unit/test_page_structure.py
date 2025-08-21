import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.mark.unit
@pytest.mark.browser
class TestPageStructure:
    """Test basic page structure and elements."""
    
    def test_page_title(self, loaded_page):
        """Test that page has correct title."""
        assert loaded_page.title == "Λ V X T V"
    
    def test_player_element_exists(self, loaded_page):
        """Test that main player element exists."""
        player = loaded_page.find_element(By.ID, "PLAYER")
        assert player is not None
        assert player.is_displayed()
    
    def test_required_scripts_loaded(self, loaded_page):
        """Test that required JavaScript libraries are loaded."""
        # Check if Plyr library is loaded
        plyr_loaded = loaded_page.execute_script("return typeof Plyr !== 'undefined';")
        assert plyr_loaded, "Plyr library should be loaded"
        
        # Check if our custom scripts are loaded
        videos_array = loaded_page.execute_script("return typeof videos !== 'undefined';")
        assert videos_array, "Videos array should be defined"
    
    def test_videos_array_structure(self, loaded_page):
        """Test that videos array has correct structure."""
        videos = loaded_page.execute_script("return videos;")
        
        assert isinstance(videos, list), "Videos should be an array"
        assert len(videos) > 0, "Videos array should not be empty"
        
        # Check first video structure
        first_video = videos[0]
        assert 'type' in first_video, "Video should have type"
        assert 'id' in first_video, "Video should have id"
        assert first_video['type'] in ['yt', 'vimeo'], "Video type should be yt or vimeo"
    
    def test_css_styles_loaded(self, loaded_page):
        """Test that CSS styles are properly applied."""
        body = loaded_page.find_element(By.TAG_NAME, "body")
        
        # Check that body has full height and width
        body_height = body.value_of_css_property("height")
        body_width = body.value_of_css_property("width")
        
        # These should be set to 100% according to our CSS
        assert body_height != "auto", "Body height should be set"
        assert body_width != "auto", "Body width should be set"
    
    def test_player_data_attributes(self, loaded_page):
        """Test that player has correct data attributes."""
        player = loaded_page.find_element(By.ID, "PLAYER")
        
        provider = player.get_attribute("data-plyr-provider")
        embed_id = player.get_attribute("data-plyr-embed-id")
        
        assert provider in ["youtube", "vimeo"], f"Provider should be youtube or vimeo, got {provider}"
        assert embed_id is not None, "Embed ID should be set"
        assert len(embed_id) > 0, "Embed ID should not be empty"

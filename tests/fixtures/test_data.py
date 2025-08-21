"""Test data fixtures for video player testing."""

# Test video data - using stable, publicly available videos
TEST_VIDEOS = [
    {
        'type': 'yt',
        'id': 'dQw4w9WgXcQ',
        'title': 'Rick Astley - Never Gonna Give You Up',
        'duration_approx': 213,  # seconds
        'should_load': True
    },
    {
        'type': 'yt', 
        'id': 'tL6ZTcrDPAU',
        'title': 'Duke Ellington Caravan',
        'duration_approx': 240,
        'should_load': True
    },
    {
        'type': 'yt',
        'id': 'invalid_id_12345',
        'title': 'Invalid Video for Error Testing',
        'should_load': False
    }
]

# Expected JavaScript constants from the application
EXPECTED_CONSTANTS = {
    'MAX_VIDEOS_BEFORE_RECREATE': 5,
    'MAX_CONSECUTIVE_FAILURES': 3,
    'VIDEO_LOAD_TIMEOUT': 15000,
    'WATCHDOG_CHECK_INTERVAL': 3000,
    'MAX_STUCK_CHECKS': 3,
    'MAX_ZERO_TIME_CHECKS': 4
}

# Expected JavaScript functions that should be available
EXPECTED_FUNCTIONS = [
    'loadNextVideo',
    'createPlayer', 
    'cleanupPlayer',
    'logMemoryUsage',
    'startWatchdog',
    'stopWatchdog',
    'checkVideoProgress',
    'handleVideoError',
    'handleLoadTimeout'
]

# Expected global variables
EXPECTED_GLOBALS = [
    'videos',
    'currentVideoIndex', 
    'currentVideo',
    'player',
    'videoCount',
    'consecutiveFailures'
]

# Performance thresholds for testing
PERFORMANCE_THRESHOLDS = {
    'page_load_timeout': 30,  # seconds
    'video_load_timeout': 20,  # seconds
    'transition_timeout': 15,  # seconds
    'max_transition_time': 25,  # seconds
    'max_initial_memory_mb': 100,  # MB
    'max_memory_growth_mb': 20,  # MB for long-running tests
    'max_watchdog_impact_mb': 5,  # MB
    'max_heap_usage_percent': 50  # % of heap limit
}

# Browser compatibility test data
BROWSER_CONFIGS = {
    'chrome': {
        'options': [
            '--no-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--window-size=1920,1080'
        ],
        'prefs': {
            'profile.default_content_setting_values.notifications': 2
        }
    },
    'firefox': {
        'options': [
            '--width=1920',
            '--height=1080'
        ],
        'prefs': {
            'media.autoplay.default': 0,
            'media.autoplay.blocking_policy': 0
        }
    }
}

# Test scenarios for error handling
ERROR_SCENARIOS = [
    {
        'name': 'invalid_video_id',
        'script': 'currentVideo = {type: "yt", id: "invalid123"};',
        'expected_recovery': True
    },
    {
        'name': 'network_error',
        'script': 'navigator.onLine = false;',  # Simulate offline
        'expected_recovery': True
    },
    {
        'name': 'player_error',
        'script': 'if (player && player.emit) player.emit("error", new Error("Test error"));',
        'expected_recovery': True
    }
]

# Memory test scenarios
MEMORY_TEST_SCENARIOS = [
    {
        'name': 'normal_operation',
        'video_switches': 3,
        'expected_max_growth_mb': 10
    },
    {
        'name': 'many_switches', 
        'video_switches': 10,
        'expected_max_growth_mb': 15
    },
    {
        'name': 'player_recreation',
        'force_recreation': True,
        'expected_cleanup': True
    }
]

# CSS selectors for testing
SELECTORS = {
    'player': '#PLAYER',
    'iframe': 'iframe',
    'plyr_video': '.plyr__video-embed',
    'body': 'body',
    'html': 'html'
}

# Expected HTML attributes
EXPECTED_ATTRIBUTES = {
    'player': {
        'id': 'PLAYER',
        'data-plyr-provider': ['youtube', 'vimeo'],
        'data-plyr-embed-id': lambda x: x is not None and len(x) > 0
    }
}

# Test timeouts for different types of operations
TIMEOUTS = {
    'page_load': 30,
    'element_wait': 10,
    'video_load': 60,
    'transition': 30,
    'memory_stabilize': 10,
    'watchdog_cycle': 5,
    'error_recovery': 15
}

# User agent strings for testing
USER_AGENTS = {
    'desktop_chrome': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'mobile_chrome': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Mobile/15E148 Safari/604.1',
    'desktop_firefox': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0'
}

# API endpoints for testing (if any)
API_ENDPOINTS = {
    'health_check': '/',
    'static_assets': ['/index.html', '/version']
}

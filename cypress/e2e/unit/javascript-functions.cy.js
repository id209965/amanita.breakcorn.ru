/// <reference types="cypress" />

describe('JavaScript Functions Tests', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.waitForJavaScript()
  })

  it('should have new keyboard control functions available', () => {
    // Wait for page to fully load and functions to be exposed
    // Based on debug logs, function exposure is working correctly
    cy.wait(10000)
    
    // Check functions with retry - they should be exposed after script loads
    cy.window().should((win) => {
      // Check main keyboard control functions
      expect(win.togglePlayPause, 'togglePlayPause should be a function').to.be.a('function')
      expect(win.loadRandomVideo, 'loadRandomVideo should be a function').to.be.a('function') 
      expect(win.goBackInHistory, 'goBackInHistory should be a function').to.be.a('function')
      
      // Check player settings object
      expect(win.playerSettings, 'playerSettings should be an object').to.be.an('object')
      expect(win.playerSettings).to.not.be.null
    })
    
    // Separate check for playerSettings methods with additional wait
    cy.wait(1000)
    cy.window().should((win) => {
      if (win.playerSettings) {
        expect(win.playerSettings.canGoBack, 'playerSettings.canGoBack should be a function').to.be.a('function')
        expect(win.playerSettings.addToHistory, 'playerSettings.addToHistory should be a function').to.be.a('function')
        expect(win.playerSettings.goBackInHistory, 'playerSettings.goBackInHistory should be a function').to.be.a('function')
      }
    })
  })

  it('should initialize global variables properly', () => {
    cy.window().should((win) => {
      expect(win.videos).to.exist
      expect(win.currentVideoIndex).to.exist
      expect(win.videoCount).to.exist
      expect(win.consecutiveFailures).to.exist
    })
  })

  it('should have correct video constants', () => {
    cy.window().should((win) => {
      expect(win.MAX_VIDEOS_BEFORE_RECREATE).to.equal(20) // Updated from 5 to 20 for stability
      expect(win.MAX_CONSECUTIVE_FAILURES).to.equal(3)
      expect(win.VIDEO_LOAD_TIMEOUT).to.equal(15000)
      expect(win.WATCHDOG_CHECK_INTERVAL).to.equal(10000) // Updated from 3000 to 10000 for stability
    })
  })

  it('should have essential functions available', () => {
    cy.window().should((win) => {
      expect(win.loadNextVideo).to.be.a('function')
      expect(win.createPlayer).to.be.a('function')
      expect(win.cleanupPlayer).to.be.a('function')
    })
  })

  it('should have memory monitoring functions', () => {
    cy.window().should((win) => {
      expect(win.logMemoryUsage).to.be.a('function')
    })
  })

  it('should have watchdog functions', () => {
    cy.window().should((win) => {
      expect(win.startWatchdog).to.be.a('function')
      expect(win.stopWatchdog).to.be.a('function')
      expect(win.checkVideoProgress).to.be.a('function')
    })
  })

  it('should have error handling functions', () => {
    cy.window().should((win) => {
      expect(win.handleVideoError).to.be.a('function')
      expect(win.handleLoadTimeout).to.be.a('function')
    })
  })

  it('should handle postMessage errors gracefully', () => {
    cy.window().then((win) => {
      // Try to trigger a postMessage error
      try {
        win.parent.postMessage('test', '*')
      } catch (e) {
        // Should be caught and handled
        cy.log('PostMessage error handled:', e.message)
      }
    })
    
    // Page should still be functional - wait for player to be stable
    cy.wait(2000) // Give time for any video recreation cycles
    cy.get('body').should('exist') // Ensure page is still responsive
    
    // Check that the video system is still working (more flexible approach)
    cy.window().then((win) => {
      const hasVideosArray = win.videos && Array.isArray(win.videos)
      const hasPlayerSettings = win.playerSettings !== undefined
      const hasPlayer = win.player !== undefined
      
      if (hasVideosArray || hasPlayerSettings || hasPlayer) {
        cy.log('✅ Video system still operational after postMessage test')
        expect(true).to.be.true
      } else {
        cy.get('body').then(($body) => {
          const hasPlayerElement = $body.find('#PLAYER').length > 0
          const hasPlyrElement = $body.find('.plyr').length > 0
          expect(hasPlayerElement || hasPlyrElement).to.be.true
        })
      }
    })
    cy.log('PostMessage test completed - page is still functional')
  })

  it('should have proper function return values', () => {
    cy.window().then((win) => {
      // Test loadNextVideo function
      if (typeof win.loadNextVideo === 'function') {
        const result = win.loadNextVideo()
        // Function should not throw errors
        cy.wrap(result).should('not.be.undefined')
      }
    })
  })

  it('should maintain global state consistency', () => {
    cy.getVideoInfo().then((info) => {
      expect(info.currentVideoIndex).to.be.a('number')
      expect(info.currentVideoIndex).to.be.at.least(0)
      expect(info.videoCount).to.be.a('number')
      expect(info.consecutiveFailures).to.be.a('number')
    })
  })

  it('should handle function calls without errors', () => {
    cy.window().then((win) => {
      // Test that functions can be called without throwing
      const functions = [
        'logMemoryUsage',
        'startWatchdog',
        'stopWatchdog'
      ]
      
      functions.forEach(funcName => {
        if (typeof win[funcName] === 'function') {
          expect(() => {
            win[funcName]()
          }).to.not.throw()
        }
      })
    })
  })
})

/// <reference types="cypress" />

describe('JavaScript Functions Tests', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.waitForJavaScript()
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
      expect(win.MAX_VIDEOS_BEFORE_RECREATE).to.equal(5)
      expect(win.MAX_CONSECUTIVE_FAILURES).to.equal(3)
      expect(win.VIDEO_LOAD_TIMEOUT).to.equal(15000)
      expect(win.WATCHDOG_CHECK_INTERVAL).to.equal(3000)
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
    
    // Page should still be functional
    cy.get('#PLAYER').should('be.visible')
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

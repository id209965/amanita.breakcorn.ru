/// <reference types="cypress" />

describe('Video Player Integration Tests', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.waitForJavaScript()
  })

  it('should load initial video successfully', () => {
    cy.waitForVideoLoad()
    
    cy.getVideoInfo().should((info) => {
      expect(info.player).to.not.be.null
      expect(info.currentVideo).to.not.be.null
      expect(info.currentVideoIndex).to.be.at.least(0)
    })
  })

  it('should navigate to next video', () => {
    cy.waitForVideoLoad()
    
    cy.getVideoInfo().then((initialInfo) => {
      const initialIndex = initialInfo.currentVideoIndex
      
      cy.triggerNextVideo()
      cy.wait(3000) // Wait for transition
      cy.waitForVideoLoad()
      
      cy.getVideoInfo().should((newInfo) => {
        expect(newInfo.currentVideoIndex).to.not.equal(initialIndex)
      })
    })
  })

  it('should respond to keyboard controls', () => {
    cy.waitForVideoLoad()
    
    cy.getVideoInfo().then((initialInfo) => {
      const initialIndex = initialInfo.currentVideoIndex
      
      // Test spacebar
      cy.simulateKeyPress(' ')
      cy.wait(3000)
      cy.waitForVideoLoad()
      
      cy.getVideoInfo().should((newInfo) => {
        expect(newInfo.currentVideoIndex).to.not.equal(initialIndex)
      })
    })
  })

  it('should respond to N key press', () => {
    cy.waitForVideoLoad()
    
    cy.getVideoInfo().then((initialInfo) => {
      const initialIndex = initialInfo.currentVideoIndex
      
      // Test N key
      cy.simulateKeyPress('n')
      cy.wait(3000)
      cy.waitForVideoLoad()
      
      cy.getVideoInfo().should((newInfo) => {
        expect(newInfo.currentVideoIndex).to.not.equal(initialIndex)
      })
    })
  })

  it('should handle click to next video', () => {
    cy.waitForVideoLoad()
    
    cy.getVideoInfo().then((initialInfo) => {
      const initialIndex = initialInfo.currentVideoIndex
      
      // Click on player
      cy.get('#PLAYER').click()
      cy.wait(3000)
      cy.waitForVideoLoad()
      
      cy.getVideoInfo().should((newInfo) => {
        expect(newInfo.currentVideoIndex).to.not.equal(initialIndex)
      })
    })
  })

  it('should handle video provider alternation', () => {
    cy.window().its('videos').then((videos) => {
      const youtubeVideos = videos.filter(v => v.type === 'yt')
      const vimeoVideos = videos.filter(v => v.type === 'vimeo')
      
      if (youtubeVideos.length === 0 || vimeoVideos.length === 0) {
        cy.log('Skipping provider alternation test - need both YouTube and Vimeo videos')
        return
      }
      
      cy.waitForVideoLoad()
      
      const providersEncountered = new Set()
      const maxAttempts = Math.min(10, videos.length)
      
      const checkProviders = (attempt = 0) => {
        if (attempt >= maxAttempts) {
          expect(providersEncountered.size).to.be.greaterThan(1)
          return
        }
        
        cy.getVideoInfo().then((info) => {
          if (info.currentVideo) {
            providersEncountered.add(info.currentVideo.type)
          }
          
          cy.triggerNextVideo()
          cy.wait(3000)
          cy.waitForVideoLoad().then(() => {
            checkProviders(attempt + 1)
          })
        })
      }
      
      checkProviders()
    })
  })

  it('should handle multiple video transitions', () => {
    cy.waitForVideoLoad()
    
    const maxTransitions = 5
    let successfulTransitions = 0
    
    const performTransition = (count = 0) => {
      if (count >= maxTransitions) {
        expect(successfulTransitions).to.be.at.least(Math.floor(maxTransitions / 2))
        return
      }
      
      cy.getVideoInfo().then((currentInfo) => {
        const currentIndex = currentInfo.currentVideoIndex
        
        cy.triggerNextVideo()
        cy.wait(2000)
        
        cy.waitForVideoLoad().then(() => {
          cy.getVideoInfo().then((newInfo) => {
            if (newInfo.currentVideoIndex !== currentIndex) {
              successfulTransitions++
            }
            performTransition(count + 1)
          })
        }).catch(() => {
          // Some transitions might fail, continue
          performTransition(count + 1)
        })
      })
    }
    
    performTransition()
  })

  it('should recover from errors', () => {
    cy.waitForVideoLoad()
    
    // Inject an error to test recovery
    cy.window().then((win) => {
      if (win.player && win.player.emit) {
        win.player.emit('error', new Error('Test error'))
      }
    })
    
    // Wait for error handling
    cy.wait(5000)
    
    // Check that player is still functional
    cy.getVideoInfo().should((info) => {
      expect(info).to.not.be.null
    })
    
    // Try to continue normal operation
    cy.triggerNextVideo()
    cy.wait(3000)
    
    // Should still be able to get video info
    cy.getVideoInfo().should((info) => {
      expect(info.currentVideoIndex).to.be.a('number')
    })
  })

  it('should handle iframe elements properly', () => {
    cy.waitForVideoLoad()
    
    // Check initial iframe count
    cy.get('iframe').then(($iframes) => {
      const initialCount = $iframes.length
      
      // Trigger several video changes
      cy.triggerNextVideo()
      cy.wait(3000)
      cy.triggerNextVideo()
      cy.wait(3000)
      
      // Check that iframe count hasn't grown excessively
      cy.get('iframe').should(($newIframes) => {
        expect($newIframes.length).to.be.lessThan(initialCount + 5)
      })
    })
  })
})

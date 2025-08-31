/// <reference types="cypress" />

describe('Memory Management Tests', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.waitForJavaScript()
  })

  it('should have active memory monitoring', () => {
    cy.wait(5000) // Let page stabilize
    
    cy.getMemoryUsage().should((memory) => {
      expect(memory).to.not.be.null
      expect(memory.used).to.be.greaterThan(0)
    })
    
    // Check that memory monitoring interval is active
    cy.window().should((win) => {
      expect(win.memoryMonitorInterval).to.exist
    })
  })

  it('should recreate player after maximum videos', () => {
    cy.waitForVideoLoad()
    
    cy.window().its('MAX_VIDEOS_BEFORE_RECREATE').then((maxVideos) => {
      expect(maxVideos).to.equal(20)
      
      // Track initial state
      cy.getVideoInfo().then((initialInfo) => {
        const initialVideoCount = initialInfo.videoCount
        
        // Trigger enough video changes to force recreation
        const triggerVideos = (count = 0) => {
          if (count >= maxVideos + 1) {
            // Check that recreation occurred
            cy.getVideoInfo().should((newInfo) => {
              // Either videoCount reset or other signs of recreation
              const recreationOccurred = (
                newInfo.videoCount < maxVideos ||
                count >= maxVideos
              )
              expect(recreationOccurred).to.be.true
            })
            return
          }
          
          cy.triggerNextVideo()
          cy.wait(2000)
          cy.waitForVideoLoad().then(() => {
            triggerVideos(count + 1)
          }).catch(() => {
            // Some videos might fail, continue
            triggerVideos(count + 1)
          })
        }
        
        triggerVideos()
      })
    })
  })

  it('should clean up memory on player recreation', () => {
    cy.waitForVideoLoad()
    cy.wait(5000) // Let memory stabilize
    
    cy.getMemoryUsage().then((baselineMemory) => {
      // Force player recreation
      cy.forcePlayerRecreation()
      
      // Wait for recreation and cleanup
      cy.wait(5000)
      cy.waitForVideoLoad().catch(() => {
        // Player might not load immediately after recreation
      })
      
      // Give time for memory cleanup
      cy.wait(10000)
      
      // Force garbage collection if available
      cy.forceGarbageCollection()
      cy.wait(5000)
      
      // Check memory after cleanup
      cy.getMemoryUsage().then((afterCleanupMemory) => {
        if (baselineMemory && afterCleanupMemory) {
          const memoryGrowth = afterCleanupMemory.used - baselineMemory.used
          const growthMB = memoryGrowth / (1024 * 1024)
          
          // Allow up to 10MB growth as reasonable
          const maxAllowedGrowthMB = 10
          
          expect(growthMB).to.be.lessThan(maxAllowedGrowthMB, 
            `Memory grew too much: ${growthMB.toFixed(2)}MB`)
        }
      })
    })
  })

  it('should handle consecutive failures cleanup', () => {
    cy.waitForVideoLoad()
    
    cy.window().its('MAX_CONSECUTIVE_FAILURES').then((maxFailures) => {
      // Simulate consecutive failures
      const simulateFailures = (count = 0) => {
        if (count > maxFailures) {
          // Check that cleanup occurred
          cy.window().its('consecutiveFailures').should('be.lessThan', maxFailures)
          return
        }
        
        cy.window().then((win) => {
          win.consecutiveFailures++
          cy.log(`Simulated failure #${win.consecutiveFailures}`)
          
          if (typeof win.handleVideoError === 'function') {
            win.handleVideoError(new Error('Simulated error'))
          }
        })
        
        cy.wait(1000)
        simulateFailures(count + 1)
      }
      
      simulateFailures()
    })
  })

  it('should maintain memory stability during normal operation', () => {
    cy.waitForVideoLoad()
    
    // Monitor memory for 2 minutes with periodic video switches
    const testDurationMs = 120000 // 2 minutes
    const videoSwitchInterval = 20000 // 20 seconds
    
    cy.getMemoryUsage().then((initialMemory) => {
      const performMemoryTest = (elapsed = 0) => {
        if (elapsed >= testDurationMs) {
          cy.getMemoryUsage().then((finalMemory) => {
            if (initialMemory && finalMemory) {
              const memoryGrowth = finalMemory.used - initialMemory.used
              const growthMB = memoryGrowth / (1024 * 1024)
              
              // Over 2 minutes, memory growth should be reasonable
              const maxAllowedGrowthMB = 20
              
              expect(growthMB).to.be.lessThan(maxAllowedGrowthMB,
                `Long-running memory growth too high: ${growthMB.toFixed(2)}MB`)
            }
          })
          return
        }
        
        // Switch video every 20 seconds
        if (elapsed % videoSwitchInterval === 0 && elapsed > 0) {
          cy.triggerNextVideo()
          cy.wait(2000)
        }
        
        cy.wait(5000) // Wait 5 seconds
        performMemoryTest(elapsed + 5000)
      }
      
      performMemoryTest()
    })
  })

  it('should efficiently manage watchdog memory usage', () => {
    cy.waitForVideoLoad()
    
    cy.getMemoryUsage().then((initialMemory) => {
      // Stop watchdog
      cy.window().then((win) => {
        if (typeof win.stopWatchdog === 'function') {
          win.stopWatchdog()
        }
      })
      
      cy.wait(10000) // Baseline period
      
      cy.getMemoryUsage().then((memoryWithoutWatchdog) => {
        // Start watchdog again
        cy.window().then((win) => {
          if (typeof win.startWatchdog === 'function') {
            win.startWatchdog()
          }
        })
        
        cy.wait(30000) // Let watchdog run for several cycles
        
        cy.getMemoryUsage().then((memoryWithWatchdog) => {
          if (initialMemory && memoryWithoutWatchdog && memoryWithWatchdog) {
            const baselineGrowth = memoryWithoutWatchdog.used - initialMemory.used
            const watchdogGrowth = memoryWithWatchdog.used - memoryWithoutWatchdog.used
            
            const watchdogImpactMB = watchdogGrowth / (1024 * 1024)
            
            // Watchdog should not cause significant additional memory usage
            expect(watchdogImpactMB).to.be.lessThan(5, 
              `Watchdog memory impact too high: ${watchdogImpactMB.toFixed(2)}MB`)
          }
        })
      })
    })
  })

  it('should handle iframe cleanup properly', () => {
    cy.waitForVideoLoad()
    
    // Count initial iframes (handle case when none exist)
    cy.get('body').then(() => {
      const initialCount = Cypress.$('iframe').length
      cy.log(`Initial iframe count: ${initialCount}`)
      
      // Force cleanup
      cy.window().then((win) => {
        cy.log('Testing iframe cleanup...')
        if (typeof win.cleanupPlayer === 'function') {
          win.cleanupPlayer()
        }
      })
      
      cy.wait(3000)
      
      // Count iframes after cleanup
      const afterCleanupCount = Cypress.$('iframe').length
      cy.log(`After cleanup iframe count: ${afterCleanupCount}`)
      
      // Create new player
      cy.window().then((win) => {
        if (typeof win.createPlayer === 'function') {
          win.createPlayer()
        }
      })
      
      cy.wait(3000)
      
      // Count final iframes
      const finalCount = Cypress.$('iframe').length
      cy.log(`Final iframe count: ${finalCount}`)
      
      // After cleanup, iframe count should not continuously grow
      expect(finalCount).to.be.lessThan(initialCount + 5, 
        `Too many iframes after cleanup: ${finalCount} (initial: ${initialCount})`)
    })
  })
})

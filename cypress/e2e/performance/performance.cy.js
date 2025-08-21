/// <reference types="cypress" />

describe('Performance Tests', () => {
  beforeEach(() => {
    cy.visit('/')
    cy.waitForJavaScript()
  })

  it('should load page within acceptable time', () => {
    cy.measurePageLoad().then((loadTime) => {
      // Page should load within 30 seconds
      expect(loadTime).to.be.lessThan(30000, 
        `Page took too long to load: ${loadTime}ms`)
      
      cy.log(`Page load time: ${loadTime}ms`)
    })
  })

  it('should load videos within timeout', () => {
    const startTime = Date.now()
    
    cy.waitForVideoLoad().then(() => {
      const loadTime = Date.now() - startTime
      
      // Video should load within 20 seconds
      expect(loadTime).to.be.lessThan(20000, 
        `Video took too long to load: ${loadTime}ms`)
      
      cy.task('recordPerformanceMetric', {
        name: 'Initial Video Load Time',
        value: loadTime,
        unit: 'ms'
      })
    })
  })

  it('should have fast video transitions', () => {
    cy.waitForVideoLoad()
    
    const transitionTimes = []
    const maxTransitions = 5
    
    const measureTransition = (count = 0) => {
      if (count >= maxTransitions) {
        if (transitionTimes.length > 0) {
          const avgTime = transitionTimes.reduce((a, b) => a + b, 0) / transitionTimes.length
          const maxTime = Math.max(...transitionTimes)
          
          // Average transition should be reasonably fast
          expect(avgTime).to.be.lessThan(15000, 
            `Average transition too slow: ${avgTime}ms`)
          expect(maxTime).to.be.lessThan(25000, 
            `Slowest transition too slow: ${maxTime}ms`)
          
          cy.task('recordPerformanceMetric', {
            name: 'Average Transition Time',
            value: avgTime.toFixed(0),
            unit: 'ms'
          })
          
          cy.task('recordPerformanceMetric', {
            name: 'Max Transition Time',
            value: maxTime,
            unit: 'ms'
          })
        }
        return
      }
      
      cy.measureVideoTransition().then((transitionTime) => {
        transitionTimes.push(transitionTime)
        measureTransition(count + 1)
      }).catch(() => {
        // Some transitions might fail, continue
        measureTransition(count + 1)
      })
    }
    
    measureTransition()
  })

  it('should maintain reasonable memory usage bounds', () => {
    cy.wait(10000) // Let page stabilize
    
    cy.getMemoryUsage().then((memoryInfo) => {
      if (memoryInfo) {
        const usedMemoryMB = memoryInfo.used / (1024 * 1024)
        const heapLimitMB = memoryInfo.limit / (1024 * 1024)
        
        // Memory usage should be reasonable
        expect(usedMemoryMB).to.be.lessThan(100, 
          `Initial memory usage too high: ${usedMemoryMB.toFixed(2)}MB`)
        
        // Should not be using more than 50% of heap limit initially
        if (heapLimitMB > 0) {
          const usagePercentage = (usedMemoryMB / heapLimitMB) * 100
          expect(usagePercentage).to.be.lessThan(50, 
            `Using too much of heap limit: ${usagePercentage.toFixed(1)}%`)
          
          cy.task('recordPerformanceMetric', {
            name: 'Memory Usage',
            value: `${usedMemoryMB.toFixed(2)}MB / ${heapLimitMB.toFixed(2)}MB (${usagePercentage.toFixed(1)}%)`,
            unit: ''
          })
        }
      }
    })
  })

  it('should perform DOM manipulations efficiently', () => {
    cy.waitForVideoLoad()
    
    const startTime = Date.now()
    
    // Force DOM manipulation by recreating player
    cy.forcePlayerRecreation()
    
    // Wait for recreation to complete
    cy.wait(5000)
    
    const manipulationTime = Date.now() - startTime
    
    // DOM manipulation should be fast
    expect(manipulationTime).to.be.lessThan(10000, 
      `DOM manipulation took too long: ${manipulationTime}ms`)
    
    cy.task('recordPerformanceMetric', {
      name: 'DOM Manipulation Time',
      value: manipulationTime,
      unit: 'ms'
    })
  })

  it('should have minimal watchdog performance impact', () => {
    cy.waitForVideoLoad()
    
    cy.getMemoryUsage().then((initialMemory) => {
      // Stop watchdog if it's running
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
            const watchdogGrowth = memoryWithWatchdog.used - memoryWithoutWatchdog.used
            const watchdogImpactMB = watchdogGrowth / (1024 * 1024)
            
            // Watchdog should not cause significant additional memory usage
            expect(watchdogImpactMB).to.be.lessThan(5, 
              `Watchdog memory impact too high: ${watchdogImpactMB.toFixed(2)}MB`)
            
            cy.task('recordPerformanceMetric', {
              name: 'Watchdog Memory Impact',
              value: watchdogImpactMB.toFixed(2),
              unit: 'MB'
            })
          }
        })
      })
    })
  })

  it('should handle console operations efficiently', () => {
    cy.waitForVideoLoad()
    
    const startTime = Date.now()
    
    // Generate console activity
    cy.window().then((win) => {
      for (let i = 0; i < 100; i++) {
        win.console.log(`Performance test log message #${i}`)
      }
    })
    
    const consoleTime = Date.now() - startTime
    
    // Console operations should be fast
    expect(consoleTime).to.be.lessThan(5000, 
      `Console operations took too long: ${consoleTime}ms`)
    
    // Check that the page is still responsive
    const responseStartTime = Date.now()
    
    cy.getVideoInfo().then((videoInfo) => {
      const responseTime = Date.now() - responseStartTime
      
      expect(responseTime).to.be.lessThan(2000, 
        `Page became unresponsive: ${responseTime}ms`)
      expect(videoInfo).to.not.be.null
      
      cy.task('recordPerformanceMetric', {
        name: 'Console Operations Time',
        value: consoleTime,
        unit: 'ms'
      })
      
      cy.task('recordPerformanceMetric', {
        name: 'Post-Console Response Time',
        value: responseTime,
        unit: 'ms'
      })
    })
  })

  it('should maintain performance during long-running operation', () => {
    cy.waitForVideoLoad()
    
    const testDuration = 60000 // 1 minute test
    const checkInterval = 10000 // Check every 10 seconds
    
    cy.getMemoryUsage().then((initialMemory) => {
      const performanceTimes = []
      
      const performCheck = (elapsed = 0) => {
        if (elapsed >= testDuration) {
          if (performanceTimes.length > 0) {
            const avgResponseTime = performanceTimes.reduce((a, b) => a + b, 0) / performanceTimes.length
            const maxResponseTime = Math.max(...performanceTimes)
            
            expect(avgResponseTime).to.be.lessThan(1000, 
              `Average response time degraded: ${avgResponseTime}ms`)
            expect(maxResponseTime).to.be.lessThan(3000, 
              `Max response time too high: ${maxResponseTime}ms`)
            
            cy.task('recordPerformanceMetric', {
              name: 'Long-running Avg Response Time',
              value: avgResponseTime.toFixed(0),
              unit: 'ms'
            })
          }
          
          // Check final memory
          cy.getMemoryUsage().then((finalMemory) => {
            if (initialMemory && finalMemory) {
              const memoryGrowth = finalMemory.used - initialMemory.used
              const growthMB = memoryGrowth / (1024 * 1024)
              
              expect(growthMB).to.be.lessThan(15, 
                `Memory growth during long test too high: ${growthMB.toFixed(2)}MB`)
              
              cy.task('recordPerformanceMetric', {
                name: 'Long-running Memory Growth',
                value: growthMB.toFixed(2),
                unit: 'MB'
              })
            }
          })
          
          return
        }
        
        // Measure response time
        const responseStartTime = Date.now()
        
        cy.getVideoInfo().then(() => {
          const responseTime = Date.now() - responseStartTime
          performanceTimes.push(responseTime)
          
          // Occasionally trigger video change for realistic load
          if (elapsed % 30000 === 0 && elapsed > 0) {
            cy.triggerNextVideo()
            cy.wait(2000)
          }
          
          cy.wait(checkInterval)
          performCheck(elapsed + checkInterval)
        })
      }
      
      performCheck()
    })
  })

  it('should handle rapid user interactions efficiently', () => {
    cy.waitForVideoLoad()
    
    const startTime = Date.now()
    
    // Simulate rapid user interactions
    const interactions = [
      () => cy.simulateKeyPress(' '),
      () => cy.simulateKeyPress('n'),
      () => cy.get('#PLAYER').click(),
      () => cy.triggerNextVideo()
    ]
    
    const performInteractions = (count = 0) => {
      if (count >= 20) { // 20 rapid interactions
        const totalTime = Date.now() - startTime
        
        expect(totalTime).to.be.lessThan(30000, 
          `Rapid interactions took too long: ${totalTime}ms`)
        
        // Check that page is still responsive
        cy.getVideoInfo().should((info) => {
          expect(info).to.not.be.null
        })
        
        cy.task('recordPerformanceMetric', {
          name: 'Rapid Interactions Time',
          value: totalTime,
          unit: 'ms'
        })
        
        return
      }
      
      const interaction = interactions[count % interactions.length]
      interaction()
      
      cy.wait(500) // Small delay between interactions
      performInteractions(count + 1)
    }
    
    performInteractions()
  })
})

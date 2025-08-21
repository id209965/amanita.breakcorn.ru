// Custom commands for video player testing

// Memory monitoring commands
Cypress.Commands.add('getMemoryUsage', () => {
  return cy.window().then((win) => {
    if (win.performance && win.performance.memory) {
      const memory = win.performance.memory
      const data = {
        used: memory.usedJSHeapSize,
        total: memory.totalJSHeapSize,
        limit: memory.jsHeapSizeLimit
      }
      
      cy.task('logMemoryUsage', data)
      return data
    }
    return null
  })
})

Cypress.Commands.add('monitorMemoryGrowth', (durationMs = 30000) => {
  let initialMemory = null
  let maxGrowth = 0
  
  return cy.getMemoryUsage().then((initial) => {
    initialMemory = initial
    
    const checkMemory = () => {
      cy.getMemoryUsage().then((current) => {
        if (initialMemory && current) {
          const growth = current.used - initialMemory.used
          maxGrowth = Math.max(maxGrowth, growth)
        }
      })
    }
    
    // Check memory every 5 seconds
    const interval = 5000
    const checks = Math.floor(durationMs / interval)
    
    for (let i = 0; i < checks; i++) {
      cy.wait(interval).then(checkMemory)
    }
    
    cy.then(() => {
      const growthMB = maxGrowth / (1024 * 1024)
      cy.task('recordPerformanceMetric', {
        name: 'Max Memory Growth',
        value: growthMB.toFixed(2),
        unit: 'MB'
      })
      return growthMB
    })
  })
})

// Video player commands
Cypress.Commands.add('waitForVideoLoad', (timeout = 30000) => {
  return cy.window({ timeout }).then((win) => {
    return new Cypress.Promise((resolve, reject) => {
      const startTime = Date.now()
      
      const checkVideo = () => {
        if (Date.now() - startTime > timeout) {
          reject(new Error(`Video did not load within ${timeout}ms`))
          return
        }
        
        if (win.player && win.player.ready) {
          resolve(win.player)
        } else {
          setTimeout(checkVideo, 500)
        }
      }
      
      checkVideo()
    })
  })
})

Cypress.Commands.add('getVideoInfo', () => {
  return cy.window().then((win) => {
    return {
      currentVideo: win.currentVideo || null,
      currentVideoIndex: win.currentVideoIndex || 0,
      player: win.player ? {
        ready: win.player.ready || false,
        playing: win.player.playing || false,
        paused: win.player.paused || false,
        duration: win.player.duration || 0,
        currentTime: win.player.currentTime || 0
      } : null,
      videoCount: win.videoCount || 0,
      consecutiveFailures: win.consecutiveFailures || 0
    }
  })
})

Cypress.Commands.add('triggerNextVideo', () => {
  return cy.window().then((win) => {
    if (typeof win.loadNextVideo === 'function') {
      win.loadNextVideo()
    }
  })
})

Cypress.Commands.add('simulateKeyPress', (key) => {
  return cy.get('body').type(key)
})

Cypress.Commands.add('forcePlayerRecreation', () => {
  return cy.window().then((win) => {
    if (typeof win.cleanupPlayer === 'function') {
      win.cleanupPlayer()
    }
    
    cy.wait(1000)
    
    if (typeof win.createPlayer === 'function') {
      win.createPlayer()
    }
  })
})

// Performance measurement commands
Cypress.Commands.add('measurePageLoad', () => {
  return cy.window().then((win) => {
    const perfData = win.performance.timing
    const loadTime = perfData.loadEventEnd - perfData.navigationStart
    
    cy.task('recordPerformanceMetric', {
      name: 'Page Load Time',
      value: loadTime,
      unit: 'ms'
    })
    
    return loadTime
  })
})

Cypress.Commands.add('measureVideoTransition', () => {
  const startTime = Date.now()
  
  return cy.getVideoInfo().then((initialInfo) => {
    const initialIndex = initialInfo.currentVideoIndex
    
    cy.triggerNextVideo()
    
    cy.waitForVideoLoad().then(() => {
      const transitionTime = Date.now() - startTime
      
      cy.task('recordPerformanceMetric', {
        name: 'Video Transition Time',
        value: transitionTime,
        unit: 'ms'
      })
      
      return cy.getVideoInfo().then((newInfo) => {
        expect(newInfo.currentVideoIndex).to.not.equal(initialIndex)
        return transitionTime
      })
    })
  })
})

// Utility commands
Cypress.Commands.add('waitForJavaScript', () => {
  return cy.window().should('have.property', 'videos')
    .and('have.property', 'loadNextVideo')
    .and('have.property', 'player')
})

Cypress.Commands.add('getConsoleErrors', () => {
  return cy.window().then((win) => {
    // This would need to be implemented with actual console monitoring
    // For now, return empty array
    return []
  })
})

Cypress.Commands.add('forceGarbageCollection', () => {
  return cy.window().then((win) => {
    if (win.gc) {
      win.gc()
    }
    // Alternative methods
    if (win.CollectGarbage) {
      win.CollectGarbage()
    }
  })
})

// Custom assertion for memory growth
Cypress.Commands.add('assertMemoryGrowth', (maxGrowthMB = 20) => {
  return cy.monitorMemoryGrowth(30000).then((growthMB) => {
    expect(growthMB).to.be.lessThan(maxGrowthMB, 
      `Memory growth ${growthMB.toFixed(2)}MB exceeds limit ${maxGrowthMB}MB`)
  })
})

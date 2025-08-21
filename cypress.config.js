const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:8000',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    supportFile: 'cypress/support/e2e.js',
    videosFolder: 'cypress/videos',
    screenshotsFolder: 'cypress/screenshots',
    downloadsFolder: 'cypress/downloads',
    fixturesFolder: 'cypress/fixtures',
    
    // Viewport settings
    viewportWidth: 1920,
    viewportHeight: 1080,
    
    // Test settings - more permissive
    defaultCommandTimeout: 30000,
    requestTimeout: 30000,
    responseTimeout: 30000,
    pageLoadTimeout: 60000,
    
    // Video and screenshot settings
    video: true,
    screenshotOnRunFailure: true,
    
    // Retry settings
    retries: {
      runMode: 1,
      openMode: 0
    },
    
    // Browser settings
    chromeWebSecurity: false,
    
    // Setup node events
    setupNodeEvents(on, config) {
      // Code coverage plugin
      try {
        require('@cypress/code-coverage/task')(on, config)
      } catch (e) {
        console.log('Code coverage plugin not available')
      }
      
      // Mochawesome reporter
      try {
        require('cypress-mochawesome-reporter/plugin')(on)
      } catch (e) {
        console.log('Mochawesome reporter not available')
      }
      
      // Memory monitoring task
      on('task', {
        log(message) {
          console.log(message)
          return null
        },
        
        logMemoryUsage(data) {
          try {
            const { used, total, limit } = data
            const usedMB = (used / (1024 * 1024)).toFixed(2)
            const totalMB = (total / (1024 * 1024)).toFixed(2)
            const limitMB = (limit / (1024 * 1024)).toFixed(2)
            
            console.log(`Memory Usage: ${usedMB}MB / ${totalMB}MB (Limit: ${limitMB}MB)`)
          } catch (e) {
            console.log('Memory logging error:', e.message)
          }
          return null
        },
        
        recordPerformanceMetric({ name, value, unit }) {
          console.log(`Performance: ${name} = ${value}${unit || ''}`)
          return null
        },
        
        // Custom task for saving test data
        saveTestData(data) {
          try {
            const fs = require('fs')
            const path = require('path')
            
            const reportsDir = path.join(__dirname, 'cypress', 'reports')
            if (!fs.existsSync(reportsDir)) {
              fs.mkdirSync(reportsDir, { recursive: true })
            }
            
            const filePath = path.join(reportsDir, `${data.filename}.json`)
            fs.writeFileSync(filePath, JSON.stringify(data, null, 2))
            
            return filePath
          } catch (e) {
            console.log('Save test data error:', e.message)
            return null
          }
        }
      })
      
      return config
    },
    
    // Environment variables
    env: {
      // Test configuration
      VIDEO_LOAD_TIMEOUT: 30000,
      MEMORY_CHECK_INTERVAL: 5000,
      MAX_MEMORY_GROWTH_MB: 50, // More permissive
      PERFORMANCE_THRESHOLD_MS: 10000, // More permissive
      
      // Test data
      TEST_VIDEOS: [
        { type: 'yt', id: 'dQw4w9WgXcQ', title: 'Rick Astley - Never Gonna Give You Up' },
        { type: 'yt', id: 'tL6ZTcrDPAU', title: 'Duke Ellington Caravan' }
      ]
    }
  },
  
  // Reporter configuration
  reporter: 'cypress-mochawesome-reporter',
  reporterOptions: {
    charts: true,
    reportPageTitle: 'Video Player Test Report',
    embeddedScreenshots: true,
    inlineAssets: true,
    saveAllAttempts: false,
    reportDir: 'cypress/reports',
    overwrite: false,
    html: true,
    json: true
  }
})

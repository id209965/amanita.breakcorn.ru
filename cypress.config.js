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
    
    // Test settings
    defaultCommandTimeout: 30000,
    requestTimeout: 30000,
    responseTimeout: 30000,
    pageLoadTimeout: 60000,
    
    // Video and screenshot settings
    video: true,
    videoUploadOnPasses: false,
    screenshotOnRunFailure: true,
    
    // Retry settings
    retries: {
      runMode: 2,
      openMode: 0
    },
    
    // Browser settings
    chromeWebSecurity: false,
    
    // Setup node events
    setupNodeEvents(on, config) {
      // Code coverage plugin
      require('@cypress/code-coverage/task')(on, config)
      
      // Mochawesome reporter
      require('cypress-mochawesome-reporter/plugin')(on)
      
      // Memory monitoring task
      on('task', {
        log(message) {
          console.log(message)
          return null
        },
        
        logMemoryUsage(data) {
          const { used, total, limit } = data
          const usedMB = (used / (1024 * 1024)).toFixed(2)
          const totalMB = (total / (1024 * 1024)).toFixed(2)
          const limitMB = (limit / (1024 * 1024)).toFixed(2)
          
          console.log(`Memory Usage: ${usedMB}MB / ${totalMB}MB (Limit: ${limitMB}MB)`)
          return null
        },
        
        recordPerformanceMetric({ name, value, unit }) {
          console.log(`Performance: ${name} = ${value}${unit || ''}`)
          return null
        },
        
        // Custom task for saving test data
        saveTestData(data) {
          const fs = require('fs')
          const path = require('path')
          
          const reportsDir = path.join(__dirname, 'cypress', 'reports')
          if (!fs.existsSync(reportsDir)) {
            fs.mkdirSync(reportsDir, { recursive: true })
          }
          
          const filePath = path.join(reportsDir, `${data.filename}.json`)
          fs.writeFileSync(filePath, JSON.stringify(data, null, 2))
          
          return filePath
        }
      })
      
      return config
    },
    
    // Environment variables
    env: {
      // Test configuration
      VIDEO_LOAD_TIMEOUT: 30000,
      MEMORY_CHECK_INTERVAL: 5000,
      MAX_MEMORY_GROWTH_MB: 20,
      PERFORMANCE_THRESHOLD_MS: 5000,
      
      // Test data
      TEST_VIDEOS: [
        { type: 'yt', id: 'dQw4w9WgXcQ', title: 'Rick Astley - Never Gonna Give You Up' },
        { type: 'yt', id: 'tL6ZTcrDPAU', title: 'Duke Ellington Caravan' }
      ]
    }
  },
  
  component: {
    devServer: {
      framework: 'create-react-app',
      bundler: 'webpack'
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

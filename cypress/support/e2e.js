// Import commands.js using ES2015 syntax:
import './commands'

// Import additional plugins
import 'cypress-real-events'
import '@cypress/code-coverage/support'
import 'cypress-mochawesome-reporter/register'

// Global before hook
beforeEach(() => {
  // Set up viewport
  cy.viewport(1920, 1080)
  
  // Clear any previous state
  cy.clearCookies()
  cy.clearLocalStorage()
  
  // Visit the page with error handling
  cy.visit('/', {
    failOnStatusCode: false,
    timeout: 60000
  })
  
  // Wait for basic page elements
  cy.get('#PLAYER', { timeout: 30000 }).should('exist')
  
  // Wait for JavaScript to initialize
  cy.window().should('have.property', 'videos')
  cy.window().should('have.property', 'player')
})

// Global after hook for cleanup
afterEach(() => {
  // Take screenshot on failure
  cy.window().then((win) => {
    if (Cypress.currentTest.state === 'failed') {
      cy.screenshot(`failed-${Cypress.currentTest.title.replace(/\s+/g, '-')}`)
    }
  })
})

// Uncaught exception handler
Cy.on('uncaught:exception', (err, runnable) => {
  // Don't fail tests on YouTube/Vimeo embed errors
  if (err.message.includes('postMessage') || 
      err.message.includes('cross-origin') ||
      err.message.includes('YouTube') ||
      err.message.includes('Vimeo')) {
    cy.log('Ignoring expected embed error:', err.message)
    return false
  }
  
  // Log other errors but don't fail the test immediately
  cy.log('Uncaught exception:', err.message)
  return true
})

// Window load handler for performance monitoring
Cy.on('window:before:load', (win) => {
  // Add performance monitoring
  win.performance.mark('test-start')
  
  // Override console methods for better logging
  const originalLog = win.console.log
  win.console.log = function(...args) {
    // Forward to Cypress log
    cy.task('log', args.join(' '), { log: false })
    return originalLog.apply(this, args)
  }
})

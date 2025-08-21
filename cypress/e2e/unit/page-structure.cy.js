/// <reference types="cypress" />

describe('Page Structure Tests', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('should have correct page title', () => {
    cy.title().should('eq', 'Λ V X T V')
  })

  it('should have main player element', () => {
    cy.get('#PLAYER')
      .should('exist')
      .and('be.visible')
  })

  it('should load required JavaScript libraries', () => {
    cy.window().should((win) => {
      expect(win.Plyr).to.exist
      expect(win.videos).to.exist
    })
  })

  it('should have properly structured videos array', () => {
    cy.window().its('videos').should((videos) => {
      expect(videos).to.be.an('array')
      expect(videos).to.have.length.greaterThan(0)
      
      // Check first video structure
      const firstVideo = videos[0]
      expect(firstVideo).to.have.property('type')
      expect(firstVideo).to.have.property('id')
      expect(['yt', 'vimeo']).to.include(firstVideo.type)
    })
  })

  it('should apply CSS styles correctly', () => {
    cy.get('body').should(($body) => {
      const height = $body.css('height')
      const width = $body.css('width')
      
      expect(height).to.not.equal('auto')
      expect(width).to.not.equal('auto')
    })
  })

  it('should have correct player data attributes', () => {
    cy.get('#PLAYER')
      .should('have.attr', 'data-plyr-provider')
      .and('match', /^(youtube|vimeo)$/)
    
    cy.get('#PLAYER')
      .should('have.attr', 'data-plyr-embed-id')
      .and('not.be.empty')
  })

  it('should have responsive design elements', () => {
    // Test different viewport sizes
    const viewports = [
      [1920, 1080],
      [1366, 768],
      [768, 1024],
      [375, 667]
    ]

    viewports.forEach(([width, height]) => {
      cy.viewport(width, height)
      cy.get('#PLAYER').should('be.visible')
    })
  })
})

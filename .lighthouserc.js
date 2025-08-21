module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:8000'],
      numberOfRuns: 3,
      settings: {
        chromeFlags: '--no-sandbox --disable-dev-shm-usage'
      }
    },
    assert: {
      assertions: {
        'categories:performance': ['error', {minScore: 0.7}],
        'categories:accessibility': ['error', {minScore: 0.8}],
        'categories:best-practices': ['error', {minScore: 0.8}],
        'categories:seo': ['error', {minScore: 0.9}],
        'categories:pwa': 'off', // PWA not applicable for this project
        
        // Performance metrics
        'first-contentful-paint': ['error', {maxNumericValue: 3000}],
        'largest-contentful-paint': ['error', {maxNumericValue: 5000}],
        'cumulative-layout-shift': ['error', {maxNumericValue: 0.1}],
        'total-blocking-time': ['error', {maxNumericValue: 500}],
        
        // Resource efficiency
        'unused-javascript': ['warn', {maxNumericValue: 50}],
        'unused-css-rules': ['warn', {maxNumericValue: 50}],
        'render-blocking-resources': ['warn', {maxNumericValue: 1000}],
        
        // Network efficiency
        'server-response-time': ['error', {maxNumericValue: 1000}],
        'uses-text-compression': 'error',
        'uses-optimized-images': 'warn',
        
        // JavaScript specific
        'no-unload-listeners': 'error',
        'no-document-write': 'error',
        'uses-passive-event-listeners': 'error'
      }
    },
    upload: {
      target: 'temporary-public-storage'
    }
  }
}

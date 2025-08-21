#!/bin/bash
# Script to run Cypress tests without Docker

set -e

echo "🚀 Cypress Test Runner (Non-Docker Version)"
echo "=========================================="

# Check if Node.js version is compatible
NODE_VERSION=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
echo "📋 Node.js version: v$NODE_VERSION"

if [ "$NODE_VERSION" -lt 20 ]; then
    echo "⚠️  Warning: Node.js $NODE_VERSION may not be compatible with Cypress 15+"
    echo "   Recommended: Node.js 20+ or use Docker"
fi

# Check if dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Start HTTP server in background
echo "🌐 Starting HTTP server on port 8000..."
python3 -m http.server 8000 > /dev/null 2>&1 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Function to cleanup
cleanup() {
    echo "\n🧹 Cleaning up..."
    if [ ! -z "$SERVER_PID" ]; then
        kill $SERVER_PID 2>/dev/null || true
    fi
}

# Set trap to cleanup on exit
trap cleanup EXIT INT TERM

# Check if server is running
echo "🔍 Checking server status..."
if curl -f http://localhost:8000 > /dev/null 2>&1; then
    echo "✅ HTTP server is running"
else
    echo "❌ HTTP server failed to start"
    exit 1
fi

# Parse command line arguments
TEST_TYPE="${1:-basic}"
MODE="${2:-run}"

echo "🎯 Test type: $TEST_TYPE"
echo "🎬 Mode: $MODE"

# Run tests based on type
case $TEST_TYPE in
    "basic")
        echo "🧪 Running basic page tests..."
        npx cypress run --spec "cypress/e2e/unit/basic-page-test.cy.js" --config baseUrl=http://localhost:8000
        ;;
    "unit")
        echo "🧪 Running unit tests..."
        npx cypress run --spec "cypress/e2e/unit/**/*.cy.js" --config baseUrl=http://localhost:8000
        ;;
    "integration")
        echo "🔗 Running integration tests..."
        npx cypress run --spec "cypress/e2e/integration/**/*.cy.js" --config baseUrl=http://localhost:8000
        ;;
    "all")
        echo "🎯 Running all tests..."
        npx cypress run --config baseUrl=http://localhost:8000
        ;;
    *)
        echo "❌ Unknown test type: $TEST_TYPE"
        echo "Available types: basic, unit, integration, all"
        echo "Usage: $0 [test_type]"
        exit 1
        ;;
esac

echo "\n🎉 Tests completed!"

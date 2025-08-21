#!/usr/bin/env python3
"""Test runner script with convenient options."""

import os
import sys
import subprocess
import argparse
import time
import signal
from pathlib import Path


def start_http_server(port=8000):
    """Start HTTP server for testing."""
    print(f"Starting HTTP server on port {port}...")
    try:
        proc = subprocess.Popen(
            [sys.executable, '-m', 'http.server', str(port)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        
        # Wait for server to start
        time.sleep(2)
        
        # Test if server is running
        try:
            import requests
            response = requests.get(f'http://localhost:{port}', timeout=5)
            if response.status_code == 200:
                print(f"✓ Server started successfully on http://localhost:{port}")
                return proc
        except Exception:
            pass
        
        print("✗ Failed to start HTTP server")
        proc.terminate()
        return None
        
    except Exception as e:
        print(f"✗ Error starting server: {e}")
        return None


def run_tests(test_type='all', verbose=False, coverage=False, html_report=False, 
              parallel=False, base_url=None, browser='chrome', headless=None):
    """Run tests with specified options."""
    
    cmd = ['pytest']
    
    # Test selection
    if test_type == 'unit':
        cmd.append('tests/unit/')
    elif test_type == 'integration':
        cmd.append('tests/integration/')
    elif test_type == 'performance':
        cmd.append('tests/performance/')
    elif test_type == 'fast':
        cmd.extend(['-m', 'not slow'])
    elif test_type == 'slow':
        cmd.extend(['-m', 'slow'])
    elif test_type == 'memory':
        cmd.extend(['-m', 'memory'])
    elif test_type == 'browser':
        cmd.extend(['-m', 'browser'])
    
    # Verbosity
    if verbose:
        cmd.append('-v')
    
    # Coverage
    if coverage:
        cmd.extend([
            '--cov=.',
            '--cov-report=html:reports/coverage',
            '--cov-report=term-missing'
        ])
    
    # HTML report
    if html_report:
        cmd.extend([
            '--html=reports/test-report.html',
            '--self-contained-html'
        ])
    
    # Parallel execution
    if parallel:
        cmd.extend(['-n', 'auto'])
    
    # Environment variables
    env = os.environ.copy()
    
    if base_url:
        env['BASE_URL'] = base_url
    
    if browser:
        env['BROWSER'] = browser
    
    if headless is not None:
        env['CI'] = 'true' if headless else 'false'
    
    # Create reports directory
    Path('reports').mkdir(exist_ok=True)
    
    print(f"Running command: {' '.join(cmd)}")
    print(f"Environment: BASE_URL={env.get('BASE_URL', 'default')}, "
          f"BROWSER={env.get('BROWSER', 'chrome')}, "
          f"CI={env.get('CI', 'false')}")
    
    try:
        result = subprocess.run(cmd, env=env)
        return result.returncode
    except KeyboardInterrupt:
        print("\n✗ Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"✗ Error running tests: {e}")
        return 1


def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Run automated tests for video player',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py                          # Run all tests
  python run_tests.py --type unit -v          # Run unit tests with verbose output
  python run_tests.py --type integration --server  # Run integration tests with local server
  python run_tests.py --type performance --headless  # Run performance tests in headless mode
  python run_tests.py --fast --parallel       # Run fast tests in parallel
  python run_tests.py --coverage --html       # Run with coverage and HTML report
        """
    )
    
    parser.add_argument(
        '--type', '-t',
        choices=['all', 'unit', 'integration', 'performance', 'fast', 'slow', 'memory', 'browser'],
        default='all',
        help='Type of tests to run (default: all)'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Verbose output'
    )
    
    parser.add_argument(
        '--coverage', '-c',
        action='store_true',
        help='Run with coverage analysis'
    )
    
    parser.add_argument(
        '--html', '-h',
        action='store_true',
        help='Generate HTML test report'
    )
    
    parser.add_argument(
        '--parallel', '-p',
        action='store_true',
        help='Run tests in parallel'
    )
    
    parser.add_argument(
        '--server', '-s',
        action='store_true',
        help='Start local HTTP server for testing'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Port for HTTP server (default: 8000)'
    )
    
    parser.add_argument(
        '--url', '-u',
        help='Base URL for testing (overrides --server)'
    )
    
    parser.add_argument(
        '--browser', '-b',
        choices=['chrome', 'firefox'],
        default='chrome',
        help='Browser to use for testing (default: chrome)'
    )
    
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode'
    )
    
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Force browser GUI mode (useful for debugging)'
    )
    
    args = parser.parse_args()
    
    # Determine headless mode
    headless = None
    if args.headless:
        headless = True
    elif args.no_headless:
        headless = False
    
    # Determine base URL
    base_url = args.url
    server_proc = None
    
    if args.server and not base_url:
        server_proc = start_http_server(args.port)
        if server_proc:
            base_url = f'http://localhost:{args.port}'
        else:
            print("✗ Failed to start server, exiting")
            return 1
    
    def cleanup_server(signum=None, frame=None):
        if server_proc:
            print("\nStopping HTTP server...")
            server_proc.terminate()
            try:
                server_proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server_proc.kill()
    
    # Setup signal handlers for graceful shutdown
    if server_proc:
        signal.signal(signal.SIGINT, cleanup_server)
        signal.signal(signal.SIGTERM, cleanup_server)
    
    try:
        # Run tests
        exit_code = run_tests(
            test_type=args.type,
            verbose=args.verbose,
            coverage=args.coverage,
            html_report=args.html,
            parallel=args.parallel,
            base_url=base_url,
            browser=args.browser,
            headless=headless
        )
        
        if exit_code == 0:
            print("\n✓ All tests passed!")
        else:
            print("\n✗ Some tests failed")
        
        return exit_code
        
    finally:
        cleanup_server()


if __name__ == '__main__':
    sys.exit(main())

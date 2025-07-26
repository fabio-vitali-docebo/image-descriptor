#!/usr/bin/env python3
"""
Test runner script for Image Descriptor Bot

This script allows easy execution of the test suite locally.
"""
import subprocess
import sys
import os

def install_test_dependencies():
    """Install test dependencies if not already installed"""
    print("📦 Installing test dependencies...")
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], check=True, capture_output=True)
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print(f"Error output: {e.stderr.decode()}")
        return False
    return True

def run_tests_simple(test_type="all", verbose=False):
    """Run tests using the simple test runner"""
    
    if not install_test_dependencies():
        return False
    
    print(f"🧪 Running {test_type} tests with simple runner...")
    
    # Use our updated test runner
    cmd = [sys.executable, "test_runner.py", "--type", test_type]
    
    # Run tests
    try:
        result = subprocess.run(cmd, cwd=os.getcwd())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return False

def run_tests_pytest(test_type="all", verbose=False):
    """Run tests using pytest"""
    
    if not install_test_dependencies():
        return False
    
    print(f"🧪 Running {test_type} tests with pytest...")
    
    # Build pytest command
    cmd = [sys.executable, "-m", "pytest"]
    
    # Add test paths based on type
    if test_type == "unit":
        cmd.extend(["tests/test_unit.py"])
    elif test_type in ["integration", "e2e"]:
        cmd.extend(["tests/test_e2e.py"])
    elif test_type == "all":
        cmd.extend(["tests/"])
    else:
        cmd.extend(["tests/"])
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-v")  # Always verbose for better output
    
    # Run tests
    try:
        result = subprocess.run(cmd, cwd=os.getcwd())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running pytest: {e}")
        return False

def run_coverage():
    """Run tests with coverage report"""
    print("📊 Running tests with coverage...")
    
    try:
        # Install coverage if not available
        subprocess.run([
            sys.executable, "-m", "pip", "install", "coverage"
        ], check=True, capture_output=True)
        
        # Run tests with coverage
        subprocess.run([
            sys.executable, "-m", "coverage", "run", "-m", "pytest", "tests/"
        ], check=True)
        
        # Generate coverage report
        subprocess.run([
            sys.executable, "-m", "coverage", "report", "-m"
        ], check=True)
        
        print("✅ Coverage report generated")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Coverage failed: {e}")
        return False

def run_specific_test_file(test_file, runner="simple"):
    """Run a specific test file"""
    if not install_test_dependencies():
        return False
    
    print(f"🧪 Running specific test file: {test_file} with {runner} runner...")
    
    if runner == "pytest":
        cmd = [sys.executable, "-m", "pytest", test_file, "-v"]
    else:
        # For simple runner, we need to specify the type based on the file
        if "e2e" in test_file:
            test_type = "e2e"
        else:
            test_type = "unit"
        cmd = [sys.executable, "test_runner.py", "--type", test_type]
    
    try:
        result = subprocess.run(cmd, cwd=os.getcwd())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error running specific test: {e}")
        return False

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run Image Descriptor Bot tests")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "e2e", "all"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--runner",
        choices=["simple", "pytest"],
        default="simple",
        help="Test runner to use"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run with coverage report"
    )
    parser.add_argument(
        "--file",
        help="Run a specific test file"
    )
    
    args = parser.parse_args()
    
    print("🤖 Image Descriptor Bot Test Suite")
    print("=" * 40)
    
    # Handle specific file testing
    if args.file:
        success = run_specific_test_file(args.file, args.runner)
    # Handle coverage testing
    elif args.coverage:
        success = run_coverage()
    # Handle regular testing
    elif args.runner == "pytest":
        success = run_tests_pytest(args.type, args.verbose)
    else:
        success = run_tests_simple(args.type, args.verbose)
    
    if success:
        print("\n🎉 Test run completed successfully!")
        sys.exit(0)
    else:
        print("\n💥 Test run failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 
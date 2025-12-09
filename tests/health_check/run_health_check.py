#!/usr/bin/env python3
"""
Health Check Runner
Runs all health check tests and provides a comprehensive report

Usage:
    python tests/health_check/run_health_check.py
    python tests/health_check/run_health_check.py --quick  # Skip long-running tests
    python tests/health_check/run_health_check.py --verbose  # Show detailed output
"""

import subprocess
import sys
import os
import time
import argparse
from pathlib import Path
from datetime import datetime
import json


class HealthCheckRunner:
    """Runs health checks and generates reports"""
    
    def __init__(self, verbose=False, quick=False):
        self.verbose = verbose
        self.quick = quick
        self.results = {}
        self.start_time = None
        self.end_time = None
        
        # Get project root
        self.project_root = Path(__file__).parent.parent.parent
        self.health_check_dir = Path(__file__).parent
    
    def print_header(self):
        """Print test header"""
        print("\n" + "=" * 80)
        print("AI CODE EDITOR - HEALTH CHECK")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Project Root: {self.project_root}")
        print(f"Quick Mode: {'Yes' if self.quick else 'No'}")
        print(f"Verbose: {'Yes' if self.verbose else 'No'}")
        print("=" * 80 + "\n")
    
    def run_test_module(self, module_name, description):
        """Run a specific test module"""
        print(f"\n{'=' * 80}")
        print(f"🧪 {description}")
        print(f"{'=' * 80}")
        
        test_file = self.health_check_dir / module_name
        
        if not test_file.exists():
            print(f"❌ Test file not found: {test_file}")
            self.results[module_name] = {"status": "NOT_FOUND", "duration": 0}
            return False
        
        # Build pytest command
        cmd = [sys.executable, "-m", "pytest", str(test_file), "-v"]
        
        if self.quick:
            cmd.extend(["-m", "not slow"])
        
        if not self.verbose:
            cmd.append("--tb=short")
        
        # Run test
        start = time.time()
        try:
            result = subprocess.run(
                cmd,
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout per test module
            )
            duration = time.time() - start
            
            # Parse output
            output = result.stdout + result.stderr
            passed = result.returncode == 0
            
            # Store results
            self.results[module_name] = {
                "status": "PASSED" if passed else "FAILED",
                "duration": duration,
                "output": output
            }
            
            # Print summary
            if passed:
                print(f"✅ PASSED ({duration:.2f}s)")
            else:
                print(f"❌ FAILED ({duration:.2f}s)")
                if self.verbose:
                    print("\nOutput:")
                    print(output)
            
            return passed
            
        except subprocess.TimeoutExpired:
            duration = time.time() - start
            print(f"⏰ TIMEOUT ({duration:.2f}s)")
            self.results[module_name] = {
                "status": "TIMEOUT",
                "duration": duration,
                "output": ""
            }
            return False
        except Exception as e:
            duration = time.time() - start
            print(f"💥 ERROR: {e}")
            self.results[module_name] = {
                "status": "ERROR",
                "duration": duration,
                "output": str(e)
            }
            return False
    
    def run_all_tests(self):
        """Run all health check tests"""
        self.start_time = time.time()
        
        # Define test modules
        test_modules = [
            ("test_tool_schemas.py", "Tool Schema Validation"),
            ("test_tool_registry.py", "Tool Registry & Imports"),
            ("test_tool_execution.py", "Tool Execution Tests"),
            ("test_agent_core.py", "Agent Core Functionality"),
            ("test_design_system.py", "Design System Tests"),
            ("test_e2e_design_system.py", "End-to-End Integration Tests"),
        ]
        
        passed_count = 0
        failed_count = 0
        
        for module, description in test_modules:
            if self.run_test_module(module, description):
                passed_count += 1
            else:
                failed_count += 1
        
        self.end_time = time.time()
        
        return passed_count, failed_count
    
    def print_summary(self, passed, failed):
        """Print test summary"""
        total = passed + failed
        duration = self.end_time - self.start_time
        
        print("\n" + "=" * 80)
        print("HEALTH CHECK SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"⏱️  Duration: {duration:.2f}s")
        print(f"Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
        print("=" * 80)
        
        # Detailed results
        print("\nDetailed Results:")
        for module, result in self.results.items():
            status_icon = {
                "PASSED": "✅",
                "FAILED": "❌",
                "TIMEOUT": "⏰",
                "ERROR": "💥",
                "NOT_FOUND": "❓"
            }.get(result["status"], "❓")
            
            print(f"  {status_icon} {module}: {result['status']} ({result['duration']:.2f}s)")
        
        print("\n")
    
    def check_environment(self):
        """Check that environment is properly configured"""
        print("Checking environment...")
        
        issues = []
        
        # Check Python version
        if sys.version_info < (3, 8):
            issues.append("Python 3.8+ required")
        else:
            print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
        
        # Check if pytest is installed
        try:
            import pytest
            print(f"✅ pytest {pytest.__version__}")
        except ImportError:
            issues.append("pytest not installed")
        
        # Check for .env file
        env_file = self.project_root / ".env"
        if env_file.exists():
            print(f"✅ .env file found")
        else:
            print(f"⚠️  .env file not found (optional)")
        
        # Check GROQ_API_KEY
        if os.getenv("GROQ_API_KEY"):
            print(f"✅ GROQ_API_KEY is set")
        else:
            print(f"⚠️  GROQ_API_KEY not set (some tests will be skipped)")
        
        # Check config files
        config_files = [
            "config/tool_dictionary.json",
            "src/tool_schemas.py",
            "src/agent_core.py"
        ]
        
        for config_file in config_files:
            file_path = self.project_root / config_file
            if file_path.exists():
                print(f"✅ {config_file}")
            else:
                issues.append(f"Missing {config_file}")
        
        if issues:
            print("\n❌ Environment Issues:")
            for issue in issues:
                print(f"  - {issue}")
            return False
        
        print("\n✅ Environment OK\n")
        return True
    
    def generate_report(self):
        """Generate JSON report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "duration": self.end_time - self.start_time if self.end_time else 0,
            "results": self.results,
            "summary": {
                "total": len(self.results),
                "passed": sum(1 for r in self.results.values() if r["status"] == "PASSED"),
                "failed": sum(1 for r in self.results.values() if r["status"] == "FAILED"),
                "timeout": sum(1 for r in self.results.values() if r["status"] == "TIMEOUT"),
                "error": sum(1 for r in self.results.values() if r["status"] == "ERROR"),
            }
        }
        
        report_file = self.project_root / "health_check_report.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"📄 Report saved to: {report_file}")
    
    def run(self):
        """Main entry point"""
        self.print_header()
        
        # Check environment
        if not self.check_environment():
            print("\n⚠️  Environment check failed. Some tests may not work correctly.")
            print("Continue anyway? (y/n): ", end="")
            if input().lower() != 'y':
                return 1
        
        # Run tests
        passed, failed = self.run_all_tests()
        
        # Print summary
        self.print_summary(passed, failed)
        
        # Generate report
        self.generate_report()
        
        # Return exit code
        return 0 if failed == 0 else 1


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Run health check tests")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    parser.add_argument("-q", "--quick", action="store_true", help="Skip long-running tests")
    
    args = parser.parse_args()
    
    runner = HealthCheckRunner(verbose=args.verbose, quick=args.quick)
    exit_code = runner.run()
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()

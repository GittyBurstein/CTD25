#!/usr/bin/env python3
"""
🧪 Test Runner - מריץ את כל הטסטים במערכת
"""
import unittest
import sys
import os
from io import StringIO

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def run_all_tests():
"""🧪 Runs all tests and reports results"""
    
    print("🧪" + "="*60)
print("🧪 Runs all tests in the system")
    print("🧪" + "="*60)
    
# List of all test modules - including הטסטים החדשים המקיפים
    test_modules = [
        'test_command',
        'test_game', 
        'test_threaded_input_manager',
        'test_physics',
        'test_graphics',
        'test_state',
        'test_state_comprehensive',  # 🆕 טסטים מקיפים חדשים לState
        'test_state_advanced',       # 🆕 טסטים מתקדמים לState
        'test_moves_correct',        # 🆕 טסטים מקיפים למחלקת Moves - 25 טסטים!
        'test_board',
        'test_piece',
        'test_mock_img'
    ]
    
    total_tests = 0
    total_failures = 0
    total_errors = 0
    
    results = {}
    
    for module_name in test_modules:
print(f"\n🧪 running tests for {module_name}...")
        print("-" * 50)
        
        try:
            # Import the test module
            test_module = __import__(module_name)
            
            # Create test suite
            loader = unittest.TestLoader()
            suite = loader.loadTestsFromModule(test_module)
            
            # Run tests with custom result collector
            stream = StringIO()
            runner = unittest.TextTestRunner(stream=stream, verbosity=2)
            result = runner.run(suite)
            
            # Collect statistics
            tests_run = result.testsRun
            failures = len(result.failures)
            errors = len(result.errors)
            
            total_tests += tests_run
            total_failures += failures
            total_errors += errors
            
            # Store results
            results[module_name] = {
                'tests_run': tests_run,
                'failures': failures,
                'errors': errors,
                'success': failures == 0 and errors == 0
            }
            
            # Print summary for this module
            if failures == 0 and errors == 0:
print(f"✅ {module_name}: {tests_run} tests passed successfully!")
            else:
print(f"❌ {module_name}: {tests_run} tests, {failures} failures, {errors} errors")
                
                # Print failure details
                if result.failures:
print(" failures:")
                    for test, traceback in result.failures:
                        print(f"     - {test}: {traceback.split('AssertionError:')[-1].strip()}")
                
                if result.errors:
print(" errors:")
                    for test, traceback in result.errors:
                        print(f"     - {test}: {traceback.split('Error:')[-1].strip()}")
            
        except ImportError as e:
print(f"❌ no ניתן לטעון the {module_name}: {e}")
            results[module_name] = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'success': False
            }
            total_errors += 1
        
        except Exception as e:
print(f"❌ error בהרצת tests for {module_name}: {e}")
            results[module_name] = {
                'tests_run': 0,
                'failures': 0,
                'errors': 1,
                'success': False
            }
            total_errors += 1
    
    # Print final summary
    print("\n" + "="*60)
print("🧪 summary all הטסטים")
    print("="*60)
    
    successful_modules = 0
    for module_name, result in results.items():
        if result['success']:
print(f"✅ {module_name}: {result['tests_run']} tests")
            successful_modules += 1
        else:
print(f"❌ {module_name}: {result['tests_run']} tests, {result['failures']} failures, {result['errors']} errors")
    
    print("-" * 60)
print(f"📊 סה\"כ: {total_tests} tests")
print(f"✅ מודולים מוצלחים: {successful_modules}/{len(test_modules)}")
print(f"❌ failures: {total_failures}")
print(f"❌ errors: {total_errors}")
    
    success_rate = (total_tests - total_failures - total_errors) / max(total_tests, 1) * 100
print(f"📈 אחוז success: {success_rate:.1f}%")
    
    if total_failures == 0 and total_errors == 0:
print("\n🎉 All tests passed successfully! 🎉")
        return True
    else:
print(f"\n⚠️ there is {total_failures + total_errors} בעיות שצריך לטפל בהן")
        return False


def run_specific_test(test_name):
"""🧪 running test ספציפי"""
print(f"🧪 running test ספציפי: {test_name}")
    print("-" * 50)
    
    try:
        test_module = __import__(f"test_{test_name}")
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromModule(test_module)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        if result.wasSuccessful():
print(f"✅ test {test_name} passed successfully!")
            return True
        else:
print(f"❌ test {test_name} failed")
            return False
            
    except ImportError:
print(f"❌ no ניתן למצוא test: {test_name}")
        return False


if __name__ == '__main__':
    if len(sys.argv) > 1:
        # Run specific test
        test_name = sys.argv[1]
        success = run_specific_test(test_name)
    else:
        # Run all tests
        success = run_all_tests()
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

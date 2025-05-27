import os
import sys
from setup_test_data import setup_test_data
from test_emergency import test_emergency_system

def run_tests():
    """Run emergency system tests with test data setup"""
    print("\n=== Starting Emergency System Tests ===\n")
    
    try:
        # First, set up test data
        print("Setting up test data...")
        setup_test_data()
        
        # Then run the tests
        print("\nRunning emergency system tests...")
        test_emergency_system()
        
        print("\n✅ All tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test run failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    run_tests() 

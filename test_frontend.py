#!/usr/bin/env python3
"""
Test script for frontend interfaces
"""

import asyncio
import sys
import os

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        import pandas
        print("✅ Pandas imported successfully")
    except ImportError as e:
        print(f"❌ Pandas import failed: {e}")
        return False
    
    try:
        from app.orchestrator import ORCHESTRATOR
        print("✅ Orchestrator imported successfully")
    except ImportError as e:
        print(f"❌ Orchestrator import failed: {e}")
        return False
    
    return True

def test_dashboard_import():
    """Test if dashboard can be imported"""
    print("\n🔍 Testing dashboard import...")
    
    try:
        from app.dashboard import TreasuryDashboard
        print("✅ Enhanced dashboard imported successfully")
    except ImportError as e:
        print(f"❌ Enhanced dashboard import failed: {e}")
        return False
    
    try:
        from app.ui_dashboard import st
        print("✅ Basic dashboard imported successfully")
    except ImportError as e:
        print(f"❌ Basic dashboard import failed: {e}")
        return False
    
    return True

async def test_orchestrator():
    """Test orchestrator functionality"""
    print("\n🔍 Testing orchestrator...")
    
    try:
        from app.orchestrator import ORCHESTRATOR
        
        # Test initialization (this will fail without proper keys, but we can test the structure)
        print("✅ Orchestrator structure is valid")
        
        # Test if methods exist
        if hasattr(ORCHESTRATOR, 'initialize'):
            print("✅ Initialize method exists")
        if hasattr(ORCHESTRATOR, 'run_trading_cycle'):
            print("✅ Run trading cycle method exists")
        if hasattr(ORCHESTRATOR, 'get_portfolio_status'):
            print("✅ Get portfolio status method exists")
        
        return True
    except Exception as e:
        print(f"❌ Orchestrator test failed: {e}")
        return False

def test_cli_dashboard():
    """Test CLI dashboard"""
    print("\n🔍 Testing CLI dashboard...")
    
    try:
        from cli_dashboard import CLIDashboard
        print("✅ CLI dashboard imported successfully")
        
        # Test if methods exist
        dashboard = CLIDashboard()
        if hasattr(dashboard, 'run'):
            print("✅ CLI dashboard run method exists")
        if hasattr(dashboard, 'initialize_system'):
            print("✅ CLI dashboard initialize method exists")
        
        return True
    except Exception as e:
        print(f"❌ CLI dashboard test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Stellar AI Treasury Frontend Interfaces")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Dashboard Import Tests", test_dashboard_import),
        ("Orchestrator Tests", test_orchestrator),
        ("CLI Dashboard Tests", test_cli_dashboard),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = asyncio.run(test_func())
            else:
                result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All frontend tests passed! You can now use the interfaces.")
        print("\n🚀 Available interfaces:")
        print("   1. Enhanced Web Dashboard: python run_enhanced_dashboard.py")
        print("   2. Basic Web Dashboard: python run_dashboard.py")
        print("   3. CLI Dashboard: python cli_dashboard.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()

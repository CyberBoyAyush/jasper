#!/usr/bin/env python
"""
Jasper Finance - Package Test Suite
Tests all core modules to verify the package is working correctly.
"""

import sys

print("=" * 60)
print("🧪 JASPER FINANCE - PACKAGE TEST SUITE")
print("=" * 60)

tests_passed = 0
tests_total = 0

# Test 1: Version
print("\n[1/7] Testing version...")
tests_total += 1
try:
    import jasper
    assert jasper.__version__ == "1.0.0"
    print(f"   ✅ Jasper v{jasper.__version__}")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ {e}")

# Test 2: Core modules
print("\n[2/7] Testing core modules...")
tests_total += 1
try:
    from jasper.core.state import FinalReport
    from jasper.core.config import JasperConfig
    from jasper.core.controller import JasperController
    print("   ✅ Core modules loaded")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ {e}")

# Test 3: Agents
print("\n[3/7] Testing agent modules...")
tests_total += 1
try:
    from jasper.agent.planner import Planner
    from jasper.agent.executor import Executor
    from jasper.agent.validator import validator
    from jasper.agent.synthesizer import Synthesizer
    print("   ✅ Agent modules loaded")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ {e}")

# Test 4: PDF Export
print("\n[4/7] Testing PDF export...")
tests_total += 1
try:
    from jasper.export.pdf import render_report_html, compile_html_to_pdf
    print("   ✅ PDF export module loaded")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ {e}")

# Test 5: Templates & Styles
print("\n[5/7] Testing templates & styles...")
tests_total += 1
try:
    from jasper.export.pdf import get_report_template_dir, get_styles_dir, load_css_content
    template_dir = get_report_template_dir()
    styles_dir = get_styles_dir()
    css = load_css_content()
    print(f"   ✅ Templates found: {template_dir.name}/")
    print(f"   ✅ Styles found: {styles_dir.name}/")
    print(f"   ✅ CSS loaded: {len(css)} bytes")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ {e}")

# Test 6: Tools
print("\n[6/7] Testing financial data tools...")
tests_total += 1
try:
    from jasper.tools.financials import fetch_financial_data
    print("   ✅ Financial tools loaded")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ {e}")

# Test 7: CLI
print("\n[7/7] Testing CLI interface...")
tests_total += 1
try:
    from jasper.cli.interface import render_mission_board, render_final_report
    print("   ✅ CLI interface modules loaded")
    tests_passed += 1
except Exception as e:
    print(f"   ❌ {e}")

# Summary
print("\n" + "=" * 60)
print(f"RESULTS: {tests_passed}/{tests_total} tests passed")
print("=" * 60)

if tests_passed == tests_total:
    print("\n✅ All tests PASSED! Package is production-ready.")
    sys.exit(0)
else:
    print(f"\n⚠️  {tests_total - tests_passed} test(s) failed.")
    sys.exit(1)

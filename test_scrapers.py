#!/usr/bin/env python3
"""
Quick test script to verify scrapers work
"""
import sys
sys.path.insert(0, '.')

from china_fuel_scraper import fetch_province_prices
from global_fuel_scraper import fetch_country_prices

print("=== Testing China Scraper ===")
beijing = fetch_province_prices('beijing', '北京')
if beijing:
    print(f"[OK] Beijing: 92# = {beijing['92_gasoline']} CNY/L")
else:
    print("[FAIL] Beijing failed")

print("\n=== Testing Global Scraper ===")
china = fetch_country_prices('China', 'China')
if china:
    print(f"[OK] China: {china['price']} {china['currency']}/L")
else:
    print("[FAIL] China failed")

usa = fetch_country_prices('USA', 'United States')
if usa:
    print(f"[OK] USA: {usa['price']} {usa['currency']}/L")
else:
    print("[FAIL] USA failed")

print("\n=== Test Complete ===")

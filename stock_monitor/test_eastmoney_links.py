#!/usr/bin/env python3
"""Test EastMoney and TradingView URL generation"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from email_notifier import EmailNotifier


def test_eastmoney_urls():
    """Test EastMoney URL generation for different stock codes"""
    notifier = EmailNotifier(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        from_email="test@test.com",
        password="test",
        receivers=["test@test.com"]
    )

    test_cases = [
        ("600846.SH", "http://quote.eastmoney.com/sh600846.html"),
        ("002709.SZ", "http://quote.eastmoney.com/sz002709.html"),
        ("300959.SZ", "http://quote.eastmoney.com/sz300959.html"),
        ("688210.SH", "http://quote.eastmoney.com/sh688210.html"),
    ]

    print("Testing EastMoney URL generation:\n")
    all_passed = True

    for stock_code, expected_url in test_cases:
        actual_url = notifier._get_eastmoney_url(stock_code)
        passed = actual_url == expected_url

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {stock_code}")
        print(f"   Expected: {expected_url}")
        print(f"   Actual:   {actual_url}\n")

        if not passed:
            all_passed = False

    return all_passed


def test_tradingview_urls():
    """Test TradingView URL generation for different stock codes"""
    notifier = EmailNotifier(
        smtp_server="smtp.gmail.com",
        smtp_port=587,
        from_email="test@test.com",
        password="test",
        receivers=["test@test.com"]
    )

    test_cases = [
        ("600846.SH", "https://www.tradingview.com/chart/?symbol=SSE%3A600846"),
        ("002709.SZ", "https://www.tradingview.com/chart/?symbol=SZSE%3A002709"),
        ("300959.SZ", "https://www.tradingview.com/chart/?symbol=SZSE%3A300959"),
        ("688210.SH", "https://www.tradingview.com/chart/?symbol=SSE%3A688210"),
    ]

    print("\nTesting TradingView URL generation:\n")
    all_passed = True

    for stock_code, expected_url in test_cases:
        actual_url = notifier._get_tradingview_url(stock_code)
        passed = actual_url == expected_url

        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {stock_code}")
        print(f"   Expected: {expected_url}")
        print(f"   Actual:   {actual_url}\n")

        if not passed:
            all_passed = False

    return all_passed


if __name__ == "__main__":
    test1 = test_eastmoney_urls()
    test2 = test_tradingview_urls()

    print("=" * 60)
    if test1 and test2:
        print("✅ All URL generation tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 60)

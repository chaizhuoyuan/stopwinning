#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from email_notifier import EmailNotifier
from config_manager import ConfigManager

# Create sample alert data
sample_alerts = [
    {
        'stock_code': '002709.SZ',
        'close_price': 35.50,
        'trade_date': '2025-10-03',
        'breached_mas': [
            {'ma_period': 5, 'ma_value': 36.20, 'difference': -0.70, 'percentage': -1.93},
            {'ma_period': 10, 'ma_value': 37.10, 'difference': -1.60, 'percentage': -4.31}
        ]
    },
    {
        'stock_code': '300959.SZ',
        'close_price': 89.20,
        'trade_date': '2025-10-03',
        'breached_mas': [
            {'ma_period': 5, 'ma_value': 91.50, 'difference': -2.30, 'percentage': -2.51}
        ]
    },
    {
        'stock_code': '688210.SH',
        'close_price': 58.30,
        'trade_date': '2025-10-03',
        'breached_mas': [
            {'ma_period': 5, 'ma_value': 59.10, 'difference': -0.80, 'percentage': -1.35},
            {'ma_period': 10, 'ma_value': 60.20, 'difference': -1.90, 'percentage': -3.16},
            {'ma_period': 20, 'ma_value': 62.50, 'difference': -4.20, 'percentage': -6.72}
        ]
    }
]

# Test the email format
config = ConfigManager()
notifier = EmailNotifier(
    smtp_server=config.smtp_server,
    smtp_port=config.smtp_port,
    from_email=config.from_email,
    password=config.email_password,
    receivers=config.receivers,
    use_tls=config.use_tls
)

print("Sending test alert email with new format...")
success = notifier.send_alert(sample_alerts)

if success:
    print("\nTest alert email sent successfully!")
    print("The email now includes:")
    print("1. A quick summary at the top (e.g., '002709.SZ 突破5、10日均线')")
    print("2. Detailed information table below")
    print("3. Cleaner logs without SMTP debug output")
else:
    print("\nFailed to send test alert email.")
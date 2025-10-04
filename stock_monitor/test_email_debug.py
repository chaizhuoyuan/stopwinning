#!/usr/bin/env python3
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from config_manager import ConfigManager
from email_notifier import EmailNotifier
import logging

logging.basicConfig(level=logging.DEBUG)

# Test email sending with debug info
config = ConfigManager()
notifier = EmailNotifier(
    smtp_server=config.smtp_server,
    smtp_port=config.smtp_port,
    from_email=config.from_email,
    password=config.email_password,
    receivers=config.receivers,
    use_tls=config.use_tls
)

print("Testing email with debug info...")
print(f"From: {config.from_email}")
print(f"To: {config.receivers}")
print(f"SMTP Server: {config.smtp_server}:{config.smtp_port}")

# Send test email
success = notifier.send_test_email()
if success:
    print("\nTest email sent successfully! Please check your inbox and spam folder.")
    print("If you don't see it, check:")
    print("1. Spam/Junk folder")
    print("2. Gmail's 'All Mail' folder")
    print("3. Any email filters you have set up")
else:
    print("\nFailed to send test email. Check the error logs above.")
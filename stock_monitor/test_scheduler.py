#!/usr/bin/env python3
import sys
import os
import time
from datetime import datetime
import schedule

sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from stock_monitor import StockMonitor

def test_scheduler():
    print(f"Testing scheduler at {datetime.now()}")
    
    monitor = StockMonitor()
    
    next_minute = datetime.now().strftime("%H:%M")
    print(f"Scheduling test run at {next_minute}")
    
    schedule.every().minute.do(monitor.run_analysis)
    
    print("Scheduler started. Will run every minute for testing. Press Ctrl+C to stop.")
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except KeyboardInterrupt:
            print("\nScheduler stopped")
            break

if __name__ == "__main__":
    test_scheduler()
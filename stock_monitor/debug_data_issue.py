#!/usr/bin/env python3
"""
Debug script to investigate insufficient data warnings
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tushare_client import TushareClient
from stock_analyzer import StockAnalyzer
from config_manager import ConfigManager
import pandas as pd
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_stock_data():
    """Debug function to check stock data issues"""
    try:
        # Initialize components
        config = ConfigManager()
        client = TushareClient(config.tushare_api_key)
        analyzer = StockAnalyzer()
        
        # Test with a few sample stocks
        test_stocks = ['002709.SZ', '300959.SZ', '688210.SH', '688269.SH', '300153.SZ']
        
        print(f"Fetching data for {len(test_stocks)} test stocks with 30 days...")
        print("=" * 60)
        
        for stock_code in test_stocks:
            print(f"\nTesting stock: {stock_code}")
            print("-" * 40)
            
            # Fetch 30 days of data (current default)
            data_30 = client.get_stock_data(stock_code, days=30)
            
            if data_30 is not None:
                print(f"30-day data: {len(data_30)} records")
                print(f"Date range: {data_30['trade_date'].min()} to {data_30['trade_date'].max()}")
                
                # Check if sufficient for MA calculation
                max_ma_period = max(analyzer.ma_periods)  # Should be 20
                if len(data_30) < max_ma_period:
                    print(f"⚠️  INSUFFICIENT DATA: Need {max_ma_period} records, got {len(data_30)}")
                else:
                    print(f"✅ Sufficient data for MA calculation (need {max_ma_period}, got {len(data_30)})")
                
                # Show latest few records
                print("Latest 3 records:")
                print(data_30[['trade_date', 'close', 'vol']].tail(3).to_string(index=False))
                
            else:
                print("❌ No data returned")
            
            # Try with more days
            print(f"\nTrying with 60 days for {stock_code}:")
            data_60 = client.get_stock_data(stock_code, days=60)
            if data_60 is not None:
                print(f"60-day data: {len(data_60)} records")
                if len(data_60) < max_ma_period:
                    print(f"⚠️  Still insufficient: Need {max_ma_period}, got {len(data_60)}")
                else:
                    print(f"✅ Now sufficient with 60 days")
            else:
                print("❌ No data with 60 days either")
                
        # Check what's happening with weekends and holidays
        print(f"\n\nChecking trading calendar...")
        print("=" * 60)
        latest_trading_day = client.get_latest_trading_day()
        print(f"Latest trading day according to calendar: {latest_trading_day}")
        
        # Get trading calendar for recent period
        import tushare as ts
        cal_df = client.pro.trade_cal(
            exchange='SSE',
            start_date='20240901',
            end_date='20241004'
        )
        
        trading_days = cal_df[cal_df['is_open'] == 1]
        print(f"Trading days in Sep-Oct 2024: {len(trading_days)}")
        print("Recent trading days:")
        print(trading_days[['cal_date', 'is_open']].tail(10).to_string(index=False))
        
    except Exception as e:
        logger.error(f"Error in debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_stock_data()
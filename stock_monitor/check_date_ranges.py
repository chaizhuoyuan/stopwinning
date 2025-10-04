#!/usr/bin/env python3
"""
Check the date ranges being used for data fetching
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tushare_client import TushareClient
from config_manager import ConfigManager
from datetime import datetime, timedelta
import pandas as pd

def check_date_ranges():
    """Check what date ranges are being used"""
    try:
        config = ConfigManager()
        client = TushareClient(config.tushare_api_key)
        
        print("Current date and time:", datetime.now())
        print()
        
        # Check what dates are being calculated for 30 days
        end_date = datetime.now().strftime('%Y%m%d')
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d')
        
        print(f"30-day range being used:")
        print(f"Start date: {start_date}")
        print(f"End date: {end_date}")
        print()
        
        # Check what was used on Oct 3rd
        oct_3_date = datetime(2025, 10, 3)
        oct_3_end = oct_3_date.strftime('%Y%m%d')
        oct_3_start = (oct_3_date - timedelta(days=30)).strftime('%Y%m%d')
        
        print(f"30-day range on Oct 3rd would have been:")
        print(f"Start date: {oct_3_start}")
        print(f"End date: {oct_3_end}")
        print()
        
        # Get trading calendar to see actual trading days
        print("Getting trading calendar...")
        cal_df = client.pro.trade_cal(
            exchange='SSE',
            start_date='20250901',
            end_date='20251010'
        )
        
        trading_days = cal_df[cal_df['is_open'] == 1]
        print(f"Trading days from Sep 1 to Oct 10, 2025:")
        print(trading_days[['cal_date', 'is_open']].to_string(index=False))
        print()
        
        # Count trading days in the range that was used on Oct 3rd
        oct_3_trading_days = cal_df[(cal_df['cal_date'] >= oct_3_start) & 
                                    (cal_df['cal_date'] <= oct_3_end) & 
                                    (cal_df['is_open'] == 1)]
        print(f"Trading days from {oct_3_start} to {oct_3_end}: {len(oct_3_trading_days)}")
        print(oct_3_trading_days[['cal_date', 'is_open']].to_string(index=False))
        print()
        
        # Test with a sample stock using the Oct 3rd date range
        test_stock = '002709.SZ'
        print(f"Testing {test_stock} with Oct 3rd date range...")
        
        # Simulate what would have been fetched on Oct 3rd
        df_oct3 = client.pro.daily(
            ts_code=test_stock,
            start_date=oct_3_start,
            end_date=oct_3_end
        )
        
        if not df_oct3.empty:
            df_oct3['trade_date'] = pd.to_datetime(df_oct3['trade_date'])
            df_oct3 = df_oct3.sort_values('trade_date')
            print(f"Records returned: {len(df_oct3)}")
            print(f"Date range: {df_oct3['trade_date'].min()} to {df_oct3['trade_date'].max()}")
            print("Latest few records:")
            print(df_oct3[['trade_date', 'close']].tail(5).to_string(index=False))
        else:
            print("No data returned")
            
        print()
        
        # Compare with current date range
        print(f"Testing {test_stock} with current date range...")
        df_current = client.get_stock_data(test_stock, days=30)
        if df_current is not None:
            print(f"Records returned: {len(df_current)}")
            print(f"Date range: {df_current['trade_date'].min()} to {df_current['trade_date'].max()}")
        else:
            print("No data returned")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_date_ranges()
#!/usr/bin/env python3
"""
Find the exact stocks causing the warnings by replicating the exact same conditions
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tushare_client import TushareClient
from stock_analyzer import StockAnalyzer
from stock_reader import StockReader
from config_manager import ConfigManager
from datetime import datetime, timedelta
import pandas as pd
import logging

# Set up logging to capture warnings like the real run
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_exact_problem():
    """Replicate the exact conditions from Oct 3rd run"""
    try:
        # Initialize components exactly like the real run
        config = ConfigManager()
        client = TushareClient(config.tushare_api_key)
        analyzer = StockAnalyzer()
        stock_reader = StockReader("/Users/zhuoyuanchai/stopwinning/Targetstocklist.csv")
        
        # Get all stock codes
        stock_codes = stock_reader.read_stock_codes()
        print(f"Total stocks: {len(stock_codes)}")
        
        # Use the exact same method as the real run - get_multiple_stocks_data
        # But do it in smaller batches to identify problematic stocks
        batch_size = 10
        all_problem_stocks = []
        
        for i in range(0, len(stock_codes), batch_size):
            batch = stock_codes[i:i+batch_size]
            print(f"\nTesting batch {i//batch_size + 1}: stocks {i} to {i+len(batch)}")
            print(f"Stocks: {batch}")
            
            # Use the same method as the real application
            stock_data = client.get_multiple_stocks_data(batch, days=30)
            print(f"Retrieved data for {len(stock_data)} out of {len(batch)} stocks")
            
            # Analyze each stock in this batch like the real analyzer does
            for stock_code in batch:
                if stock_code in stock_data:
                    df = stock_data[stock_code]
                    
                    # This is the exact check from the analyzer
                    if df.empty or len(df) < max(analyzer.ma_periods):
                        print(f"❌ {stock_code}: Insufficient data - {len(df) if not df.empty else 0} records (need {max(analyzer.ma_periods)})")
                        all_problem_stocks.append({
                            'code': stock_code,
                            'records': len(df) if not df.empty else 0,
                            'empty': df.empty
                        })
                        
                        # Get more details about this problematic stock
                        if not df.empty:
                            print(f"   Date range: {df['trade_date'].min()} to {df['trade_date'].max()}")
                            print(f"   Sample dates: {df['trade_date'].head(3).tolist()}")
                        
                        # Check if it's newly listed
                        historical = client.get_stock_data(stock_code, days=200)
                        if historical is not None and not historical.empty:
                            print(f"   Historical data: {len(historical)} records over 200 days")
                            print(f"   First trading day: {historical['trade_date'].min()}")
                        else:
                            print(f"   No historical data available")
                    
                else:
                    print(f"❌ {stock_code}: No data returned at all")
                    all_problem_stocks.append({
                        'code': stock_code,
                        'records': 0,
                        'empty': True
                    })
            
            # Only test a few batches to avoid API limits
            if i >= 50:  # Test first ~50 stocks
                print(f"\nStopping after testing {i+len(batch)} stocks to avoid API limits")
                break
                
        print(f"\n\nFINAL SUMMARY:")
        print("=" * 60)
        if all_problem_stocks:
            print(f"Found {len(all_problem_stocks)} problematic stocks:")
            for stock in all_problem_stocks:
                status = "Empty" if stock['empty'] else f"{stock['records']} records"
                print(f"  {stock['code']}: {status}")
        else:
            print("No problematic stocks found in the tested range")
            print("The warnings might be from stocks later in the list")
            
        # Test a few stocks from the end of the list
        print(f"\nTesting last 10 stocks from the full list...")
        last_batch = stock_codes[-10:]
        print(f"Last stocks: {last_batch}")
        
        last_data = client.get_multiple_stocks_data(last_batch, days=30)
        print(f"Retrieved data for {len(last_data)} out of {len(last_batch)} stocks")
        
        for stock_code in last_batch:
            if stock_code in last_data:
                df = last_data[stock_code]
                if df.empty or len(df) < max(analyzer.ma_periods):
                    print(f"❌ {stock_code}: Insufficient data - {len(df) if not df.empty else 0} records")
                else:
                    print(f"✅ {stock_code}: OK - {len(df)} records")
            else:
                print(f"❌ {stock_code}: No data returned")
                
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_exact_problem()
#!/usr/bin/env python3
"""
Find specific stocks causing insufficient data warnings
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from tushare_client import TushareClient
from stock_analyzer import StockAnalyzer
from stock_reader import StockReader
from config_manager import ConfigManager
import pandas as pd
import logging

# Set up minimal logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def find_problem_stocks():
    """Find specific stocks causing insufficient data warnings"""
    try:
        # Initialize components
        config = ConfigManager()
        client = TushareClient(config.tushare_api_key)
        analyzer = StockAnalyzer()
        stock_reader = StockReader("/Users/zhuoyuanchai/stopwinning/Targetstocklist.csv")
        
        # Get the actual stock list being used
        stock_codes = stock_reader.read_stock_codes()
        print(f"Total stocks in list: {len(stock_codes)}")
        
        # Check different ranges of stocks to find the problematic ones
        test_ranges = [
            (0, 20),     # First 20
            (20, 40),    # Next 20
            (40, 60),    # Next 20
            (60, 80),    # Next 20
            (80, 100),   # Next 20
            (100, 120),  # Next 20
            (120, 132),  # Last 12
        ]
        
        problem_stocks = []
        
        for start, end in test_ranges:
            print(f"\nTesting stocks {start} to {end}...")
            sample_codes = stock_codes[start:end]
            
            print(f"Stocks in this range: {sample_codes}")
            
            for stock_code in sample_codes:
                # Test each stock individually to pinpoint issues
                data = client.get_stock_data(stock_code, days=30)
                
                if data is None:
                    print(f"❌ {stock_code}: No data returned")
                    problem_stocks.append({
                        'code': stock_code,
                        'issue': 'no_data',
                        'records': 0
                    })
                elif data.empty:
                    print(f"❌ {stock_code}: Empty data")
                    problem_stocks.append({
                        'code': stock_code,
                        'issue': 'empty_data',
                        'records': 0
                    })
                elif len(data) < max(analyzer.ma_periods):
                    print(f"❌ {stock_code}: Insufficient data - {len(data)} records (need {max(analyzer.ma_periods)})")
                    problem_stocks.append({
                        'code': stock_code,
                        'issue': 'insufficient_data',
                        'records': len(data)
                    })
                    
                    # Show the data we did get
                    print(f"   Date range: {data['trade_date'].min()} to {data['trade_date'].max()}")
                    
                    # Check if it's a newly listed stock
                    extended_data = client.get_stock_data(stock_code, days=365)
                    if extended_data is not None:
                        print(f"   1-year history: {len(extended_data)} records")
                        print(f"   First trading day: {extended_data['trade_date'].min()}")
                    else:
                        print(f"   No data even with 1 year")
                else:
                    print(f"✅ {stock_code}: OK - {len(data)} records")
            
            if end > 40:  # Stop early to avoid too many API calls
                break
                
        print(f"\n\nSUMMARY OF PROBLEM STOCKS:")
        print("=" * 50)
        for stock in problem_stocks:
            print(f"{stock['code']}: {stock['issue']} ({stock['records']} records)")
            
    except Exception as e:
        logger.error(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_problem_stocks()
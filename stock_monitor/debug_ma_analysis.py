#!/usr/bin/env python3
"""
Debug script to investigate MA calculation warnings more precisely
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

# Set up logging to capture warnings
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_ma_warnings():
    """Debug function to identify exactly which stocks cause MA warnings"""
    try:
        # Initialize components
        config = ConfigManager()
        client = TushareClient(config.tushare_api_key)
        analyzer = StockAnalyzer()
        # Use the actual path from the successful run
        stock_reader = StockReader("/Users/zhuoyuanchai/stopwinning/Targetstocklist.csv")
        
        # Get the actual stock list being used
        stock_codes = stock_reader.read_stock_codes()
        print(f"Total stocks to analyze: {len(stock_codes)}")
        
        # Get stock data for first 20 stocks (to avoid API limits during debugging)
        print("Fetching data for first 20 stocks...")
        sample_codes = stock_codes[:20]
        stock_data = client.get_multiple_stocks_data(sample_codes, days=30)
        print(f"Retrieved data for {len(stock_data)} out of {len(sample_codes)} stocks")
        
        # Track problematic stocks
        insufficient_data_stocks = []
        empty_data_stocks = []
        sufficient_stocks = []
        
        print("\nAnalyzing each stock for MA calculation...")
        print("=" * 80)
        
        for stock_code in sample_codes:
            if stock_code not in stock_data:
                empty_data_stocks.append(stock_code)
                continue
                
            df = stock_data[stock_code]
            
            # Check the exact same condition as in check_ma_breach
            if df.empty or len(df) < max(analyzer.ma_periods):
                insufficient_data_stocks.append({
                    'code': stock_code,
                    'records': len(df) if not df.empty else 0,
                    'empty': df.empty,
                    'required': max(analyzer.ma_periods)
                })
                print(f"❌ {stock_code}: {len(df) if not df.empty else 0} records (need {max(analyzer.ma_periods)})")
            else:
                sufficient_stocks.append(stock_code)
                
        print(f"\nSUMMARY:")
        print(f"Stocks with sufficient data: {len(sufficient_stocks)}")
        print(f"Stocks with insufficient data: {len(insufficient_data_stocks)}")
        print(f"Stocks with no data returned: {len(empty_data_stocks)}")
        
        if insufficient_data_stocks:
            print(f"\nStocks with insufficient data:")
            for stock_info in insufficient_data_stocks:
                print(f"  {stock_info['code']}: {stock_info['records']} records (need {stock_info['required']})")
                
        if empty_data_stocks:
            print(f"\nStocks with no data returned:")
            for stock_code in empty_data_stocks[:10]:  # Show first 10
                print(f"  {stock_code}")
            if len(empty_data_stocks) > 10:
                print(f"  ... and {len(empty_data_stocks) - 10} more")
                
        # Test the analyzer with the problematic stocks
        if insufficient_data_stocks:
            print(f"\nTesting analyzer with a problematic stock...")
            problem_stock = insufficient_data_stocks[0]
            print(f"Testing {problem_stock['code']} with {problem_stock['records']} records")
            
            test_df = stock_data[problem_stock['code']]
            print(f"DataFrame info:")
            print(f"  Shape: {test_df.shape}")
            print(f"  Columns: {list(test_df.columns)}")
            print(f"  Date range: {test_df['trade_date'].min()} to {test_df['trade_date'].max()}")
            
            # Try the analysis
            result = analyzer.analyze_stock(problem_stock['code'], test_df)
            print(f"Analysis result: {result}")
                
        # Check if it's a newly listed stock issue
        print(f"\nChecking for newly listed stocks...")
        for stock_info in insufficient_data_stocks[:5]:  # Check first 5
            stock_code = stock_info['code']
            # Try getting more historical data
            extended_data = client.get_stock_data(stock_code, days=180)  # 6 months
            if extended_data is not None:
                print(f"{stock_code}: {len(extended_data)} records in 6 months")
                print(f"  First trading day: {extended_data['trade_date'].min()}")
            else:
                print(f"{stock_code}: No data even with 6 months")
                
    except Exception as e:
        logger.error(f"Error in debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ma_warnings()
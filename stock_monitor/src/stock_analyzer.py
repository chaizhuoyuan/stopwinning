import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class StockAnalyzer:
    def __init__(self):
        self.ma_periods = [5, 10, 20]
    
    def calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        
        for period in self.ma_periods:
            df[f'MA{period}'] = df['close'].rolling(window=period).mean()
        
        return df
    
    def check_ma_breach(self, df: pd.DataFrame) -> Dict[str, bool]:
        if df.empty:
            logger.warning("No data available for MA calculation")
            return {}
        
        min_required = max(self.ma_periods)
        if len(df) < min_required:
            logger.debug(f"Only {len(df)} days of data available, need {min_required} for full MA calculation")
            return {}
        
        df_with_ma = self.calculate_moving_averages(df)
        
        latest_row = df_with_ma.iloc[-1]
        latest_close = latest_row['close']
        
        breaches = {}
        for period in self.ma_periods:
            ma_col = f'MA{period}'
            if pd.notna(latest_row[ma_col]):
                breaches[f'MA{period}'] = latest_close < latest_row[ma_col]
            else:
                breaches[f'MA{period}'] = False
        
        return breaches
    
    def analyze_stock(self, stock_code: str, df: pd.DataFrame) -> Optional[Dict]:
        if df is None or df.empty:
            logger.warning(f"No data available for {stock_code}")
            return None
        
        breaches = self.check_ma_breach(df)
        
        if not any(breaches.values()):
            return None
        
        df_with_ma = self.calculate_moving_averages(df)
        latest_row = df_with_ma.iloc[-1]
        
        analysis = {
            'stock_code': stock_code,
            'close_price': latest_row['close'],
            'trade_date': latest_row['trade_date'].strftime('%Y-%m-%d'),
            'breached_mas': []
        }
        
        for period in self.ma_periods:
            ma_col = f'MA{period}'
            if breaches.get(f'MA{period}', False):
                analysis['breached_mas'].append({
                    'ma_period': period,
                    'ma_value': latest_row[ma_col],
                    'difference': latest_row['close'] - latest_row[ma_col],
                    'percentage': ((latest_row['close'] - latest_row[ma_col]) / latest_row[ma_col]) * 100
                })
        
        return analysis
    
    def analyze_multiple_stocks(self, stock_data: Dict[str, pd.DataFrame]) -> List[Dict]:
        alerts = []
        
        for stock_code, df in stock_data.items():
            analysis = self.analyze_stock(stock_code, df)
            if analysis:
                alerts.append(analysis)
        
        return alerts
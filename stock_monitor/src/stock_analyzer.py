import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StockAnalyzer:
    def __init__(self):
        self.ma_periods = [5, 10, 20]
        self.baseline_date = '2025-09-30'  # 9/30 baseline for 20% drop check
    
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

    def check_baseline_drop(self, df: pd.DataFrame) -> Optional[Dict]:
        """Check if current price dropped 20% from 9/30 baseline"""
        if df.empty:
            return None

        # Find 9/30 price
        df['trade_date_str'] = df['trade_date'].dt.strftime('%Y-%m-%d')
        baseline_row = df[df['trade_date_str'] == self.baseline_date]

        if baseline_row.empty:
            logger.debug(f"No data found for baseline date {self.baseline_date}")
            return None

        baseline_price = baseline_row.iloc[0]['close']
        latest_price = df.iloc[-1]['close']

        drop_pct = ((latest_price - baseline_price) / baseline_price) * 100

        if drop_pct <= -20:
            return {
                'baseline_date': self.baseline_date,
                'baseline_price': baseline_price,
                'current_price': latest_price,
                'drop_percentage': drop_pct
            }

        return None

    def calculate_true_range(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate True Range for each day"""
        df = df.copy()

        # TR = max(high - low, abs(high - prev_close), abs(low - prev_close))
        df['prev_close'] = df['close'].shift(1)
        df['tr1'] = df['high'] - df['low']
        df['tr2'] = abs(df['high'] - df['prev_close'])
        df['tr3'] = abs(df['low'] - df['prev_close'])
        df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

        return df

    def check_mtr_drop(self, df: pd.DataFrame) -> Optional[Dict]:
        """Check if stock above 20-week MA drops by one MTR (4-day TR average)"""
        if df.empty or len(df) < 100:  # Need 100 days for 20-week MA
            return None

        df = df.copy()

        # Calculate 20-week (100-day) MA
        df['MA100'] = df['close'].rolling(window=100).mean()

        # Calculate True Range and MTR
        df = self.calculate_true_range(df)
        df['MTR'] = df['tr'].rolling(window=4).mean()

        latest_row = df.iloc[-1]
        prev_row = df.iloc[-2] if len(df) > 1 else None

        # Check if above 20-week MA
        if pd.isna(latest_row['MA100']) or latest_row['close'] < latest_row['MA100']:
            return None

        # Check if dropped by one MTR or more
        if prev_row is not None and pd.notna(latest_row['MTR']):
            price_drop = prev_row['close'] - latest_row['close']
            if price_drop >= latest_row['MTR']:
                return {
                    'ma100_value': latest_row['MA100'],
                    'current_price': latest_row['close'],
                    'previous_close': prev_row['close'],
                    'price_drop': price_drop,
                    'mtr_value': latest_row['MTR']
                }

        return None

    def calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> pd.DataFrame:
        """Calculate Bollinger Bands"""
        df = df.copy()

        df['BB_Middle'] = df['close'].rolling(window=period).mean()
        df['BB_Std'] = df['close'].rolling(window=period).std()
        df['BB_Upper'] = df['BB_Middle'] + (df['BB_Std'] * std_dev)
        df['BB_Lower'] = df['BB_Middle'] - (df['BB_Std'] * std_dev)

        return df

    def check_boll_drop(self, df: pd.DataFrame) -> Optional[Dict]:
        """Check if price was above Bollinger Band and dropped >5% next day"""
        if df.empty or len(df) < 21:  # Need at least 21 days for 20-day BB
            return None

        df = self.calculate_bollinger_bands(df)

        if len(df) < 2:
            return None

        prev_row = df.iloc[-2]
        latest_row = df.iloc[-1]

        # Check if previous day's close was above upper Bollinger Band
        if pd.isna(prev_row['BB_Upper']) or prev_row['close'] <= prev_row['BB_Upper']:
            return None

        # Check if current day dropped more than 5%
        drop_pct = ((latest_row['close'] - prev_row['close']) / prev_row['close']) * 100

        if drop_pct <= -5:
            return {
                'previous_close': prev_row['close'],
                'previous_bb_upper': prev_row['BB_Upper'],
                'current_close': latest_row['close'],
                'current_bb_upper': latest_row['BB_Upper'],
                'drop_percentage': drop_pct
            }

        return None
    
    def analyze_stock(self, stock_code: str, df: pd.DataFrame) -> Optional[Dict]:
        if df is None or df.empty:
            logger.warning(f"No data available for {stock_code}")
            return None

        # Check only the 3 new alert conditions
        baseline_drop = self.check_baseline_drop(df)
        mtr_drop = self.check_mtr_drop(df)
        boll_drop = self.check_boll_drop(df)

        # If no alerts triggered, return None
        if not baseline_drop and not mtr_drop and not boll_drop:
            return None

        latest_row = df.iloc[-1]

        analysis = {
            'stock_code': stock_code,
            'close_price': latest_row['close'],
            'trade_date': latest_row['trade_date'].strftime('%Y-%m-%d'),
            'baseline_drop_alert': baseline_drop,
            'mtr_drop_alert': mtr_drop,
            'boll_drop_alert': boll_drop
        }

        return analysis
    
    def analyze_multiple_stocks(self, stock_data: Dict[str, pd.DataFrame]) -> List[Dict]:
        alerts = []
        
        for stock_code, df in stock_data.items():
            analysis = self.analyze_stock(stock_code, df)
            if analysis:
                alerts.append(analysis)
        
        return alerts
import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class TushareClient:
    def __init__(self, api_key: str):
        ts.set_token(api_key)
        self.pro = ts.pro_api()
        self.daily_request_count = 0
        
    def get_stock_data(self, stock_code: str, days: int = 30) -> Optional[pd.DataFrame]:
        try:
            self._rate_limit()
            
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (datetime.now() - timedelta(days=days)).strftime('%Y%m%d')
            
            df = self.pro.daily(
                ts_code=stock_code,
                start_date=start_date,
                end_date=end_date
            )
            
            if df.empty:
                logger.warning(f"No data found for stock {stock_code}")
                return None
            
            df['trade_date'] = pd.to_datetime(df['trade_date'])
            df = df.sort_values('trade_date')
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {stock_code}: {e}")
            return None
    
    def get_multiple_stocks_data(self, stock_codes: List[str], days: int = 30) -> Dict[str, pd.DataFrame]:
        stock_data = {}

        for stock_code in stock_codes:
            logger.info(f"Fetching data for {stock_code}")
            data = self.get_stock_data(stock_code, days)
            if data is not None:
                stock_data[stock_code] = data
            # No delay needed - 500 requests/minute quota

        return stock_data
    
    def _rate_limit(self):
        # 500 requests/minute quota - no delay needed for typical usage
        self.daily_request_count += 1

        if self.daily_request_count >= 500:
            logger.warning("Approaching per-minute request limit")
        elif self.daily_request_count >= 2000:
            logger.warning("Approaching daily request limit")
    
    def get_latest_trading_day(self) -> str:
        try:
            self._rate_limit()
            df = self.pro.trade_cal(
                exchange='SSE',
                end_date=datetime.now().strftime('%Y%m%d'),
                limit=10
            )
            
            trading_days = df[df['is_open'] == 1]['cal_date']
            if not trading_days.empty:
                return trading_days.iloc[-1]
            return datetime.now().strftime('%Y%m%d')
            
        except Exception as e:
            logger.error(f"Error getting latest trading day: {e}")
            return datetime.now().strftime('%Y%m%d')
import pandas as pd
import logging
from typing import List

logger = logging.getLogger(__name__)


class StockReader:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path
    
    def read_stock_codes(self) -> List[str]:
        try:
            df = pd.read_csv(self.csv_path, encoding='utf-8-sig')
            
            if 'code' in df.columns:
                stock_codes = df['code'].tolist()
            elif 'stock_code' in df.columns:
                stock_codes = df['stock_code'].tolist()
            elif '股票代码' in df.columns:
                stock_codes = df['股票代码'].tolist()
            elif '代码' in df.columns:
                stock_codes = df['代码'].tolist()
            else:
                stock_codes = df.iloc[:, 1].tolist()
            
            stock_codes = [str(code).strip() for code in stock_codes if pd.notna(code)]
            
            stock_codes = [code.replace('=', '').replace('"', '').strip() for code in stock_codes]
            
            stock_codes = [self._format_stock_code(code) for code in stock_codes]
            
            # Remove duplicates while preserving order
            seen = set()
            unique_codes = []
            for code in stock_codes:
                if code not in seen:
                    seen.add(code)
                    unique_codes.append(code)
            
            if len(unique_codes) < len(stock_codes):
                logger.info(f"Removed {len(stock_codes) - len(unique_codes)} duplicate stock codes")
            
            logger.info(f"Read {len(unique_codes)} unique stock codes from {self.csv_path}")
            return unique_codes
            
        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_path}")
            raise
        except Exception as e:
            logger.error(f"Error reading CSV file: {e}")
            raise
    
    def _format_stock_code(self, code: str) -> str:
        code = str(code).strip()
        
        if '.' in code:
            return code
        
        if len(code) == 6:
            if code.startswith('6'):
                return f"{code}.SH"
            elif code.startswith('0') or code.startswith('3'):
                return f"{code}.SZ"
            elif code.startswith('8') or code.startswith('4'):
                return f"{code}.BJ"
        
        return code
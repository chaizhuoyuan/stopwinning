import json
import os
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    def __init__(self, config_path: str = None):
        if config_path is None:
            config_path = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                'config',
                'secrets.json'
            )
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
    
    @property
    def tushare_api_key(self) -> str:
        return self.config['tushare']['api_key']
    
    @property
    def email_config(self) -> Dict[str, Any]:
        return self.config['email']
    
    @property
    def stock_list_path(self) -> str:
        return self.config['stock_list_path']
    
    @property
    def run_time(self) -> str:
        return self.config['schedule']['run_time']
    
    @property
    def smtp_server(self) -> str:
        return self.email_config['smtp_server']
    
    @property
    def smtp_port(self) -> int:
        return self.email_config['smtp_port']
    
    @property
    def from_email(self) -> str:
        return self.email_config['from_email']
    
    @property
    def email_password(self) -> str:
        return self.email_config['password']
    
    @property
    def receivers(self) -> List[str]:
        return self.email_config['receivers']
    
    @property
    def use_tls(self) -> bool:
        return self.email_config.get('use_tls', True)
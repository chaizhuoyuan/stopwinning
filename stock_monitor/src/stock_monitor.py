import logging
import sys
from datetime import datetime
import schedule
import time
from pathlib import Path

from config_manager import ConfigManager
from stock_reader import StockReader
from tushare_client import TushareClient
from stock_analyzer import StockAnalyzer
from email_notifier import EmailNotifier

log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / f'stock_monitor_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class StockMonitor:
    def __init__(self, config_path: str = None):
        logger.info("Initializing Stock Monitor")
        
        try:
            self.config = ConfigManager(config_path)
            
            self.stock_reader = StockReader(self.config.stock_list_path)
            self.tushare_client = TushareClient(self.config.tushare_api_key)
            self.analyzer = StockAnalyzer()
            self.email_notifier = EmailNotifier(
                smtp_server=self.config.smtp_server,
                smtp_port=self.config.smtp_port,
                from_email=self.config.from_email,
                password=self.config.email_password,
                receivers=self.config.receivers,
                use_tls=self.config.use_tls
            )
            
            logger.info("Stock Monitor initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Stock Monitor: {e}")
            raise
    
    def run_analysis(self):
        logger.info(f"Starting stock analysis at {datetime.now()}")
        
        try:
            stock_codes = self.stock_reader.read_stock_codes()
            logger.info(f"Monitoring {len(stock_codes)} stocks")
            
            stock_data = self.tushare_client.get_multiple_stocks_data(stock_codes, days=45)
            logger.info(f"Retrieved data for {len(stock_data)} stocks")
            
            alerts = self.analyzer.analyze_multiple_stocks(stock_data)
            
            if alerts:
                logger.warning(f"Found {len(alerts)} stocks breaching MA levels")
                success = self.email_notifier.send_alert(alerts)
                if success:
                    logger.info("Alert email sent successfully")
                else:
                    logger.error("Failed to send alert email")
            else:
                logger.info("No MA breaches detected")
            
            logger.info("Analysis completed successfully")
            
        except Exception as e:
            logger.error(f"Error during analysis: {e}")
            raise
    
    def test_email(self):
        logger.info("Sending test email")
        return self.email_notifier.send_test_email()
    
    def schedule_daily_run(self):
        run_time = self.config.run_time
        logger.info(f"Scheduling daily run at {run_time}")
        
        schedule.every().day.at(run_time).do(self.run_analysis)
        
        logger.info("Scheduler started. Press Ctrl+C to stop.")
        
        while True:
            try:
                schedule.run_pending()
                time.sleep(60)
            except KeyboardInterrupt:
                logger.info("Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"Scheduler error: {e}")
                time.sleep(60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Stock Monitor - Monitor Chinese stocks for MA breaches')
    parser.add_argument('--config', type=str, help='Path to config file')
    parser.add_argument('--run-once', action='store_true', help='Run analysis once and exit')
    parser.add_argument('--test-email', action='store_true', help='Send test email')
    parser.add_argument('--schedule', action='store_true', help='Run on schedule')
    
    args = parser.parse_args()
    
    try:
        monitor = StockMonitor(args.config)
        
        if args.test_email:
            success = monitor.test_email()
            if success:
                print("Test email sent successfully")
            else:
                print("Failed to send test email")
        elif args.run_once:
            monitor.run_analysis()
        elif args.schedule:
            monitor.schedule_daily_run()
        else:
            print("Please specify --run-once, --test-email, or --schedule")
            parser.print_help()
    
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
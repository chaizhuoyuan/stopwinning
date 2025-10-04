import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)


class EmailNotifier:
    def __init__(self, smtp_server: str, smtp_port: int, from_email: str, 
                 password: str, receivers: List[str], use_tls: bool = True):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.from_email = from_email
        self.password = password
        self.receivers = receivers
        self.use_tls = use_tls
    
    def send_alert(self, alerts: List[Dict]) -> bool:
        if not alerts:
            logger.info("No alerts to send")
            return True
        
        try:
            subject = f"股票均线突破警报 - {datetime.now().strftime('%Y-%m-%d')}"
            body = self._format_alert_body(alerts)
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.receivers)
            
            html_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                # server.set_debuglevel(1)  # Enable debug output (disabled for cleaner logs)
                if self.use_tls:
                    server.starttls()
                server.login(self.from_email, self.password)
                server.send_message(msg)
            
            logger.info(f"Alert email sent successfully to {', '.join(self.receivers)}")
            logger.info(f"Email subject: {subject}")
            logger.info(f"Number of alerts: {len(alerts)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def _generate_summary(self, alerts: List[Dict]) -> str:
        """Generate a concise summary of breached stocks"""
        summary_lines = []
        
        for alert in alerts:
            stock_code = alert['stock_code']
            breached_periods = [str(ma['ma_period']) for ma in alert['breached_mas']]
            breached_text = '、'.join(breached_periods)
            summary_lines.append(f"{stock_code} 突破{breached_text}日均线")
        
        return '<br>'.join(summary_lines)
    
    def _format_alert_body(self, alerts: List[Dict]) -> str:
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #d32f2f; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .negative {{ color: #d32f2f; }}
                .alert-summary {{ background-color: #fff3e0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
            </style>
        </head>
        <body>
            <h2>股票均线突破警报</h2>
            <div class="alert-summary">
                <p><strong>警报时间:</strong>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>触发警报股票数:</strong>{len(alerts)} 只</p>
            </div>
            
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>快速摘要</h3>
                <p>{self._generate_summary(alerts)}</p>
            </div>
            
            <h3>详细信息</h3>
            <table>
                <tr>
                    <th>股票代码</th>
                    <th>交易日期</th>
                    <th>收盘价</th>
                    <th>突破均线</th>
                    <th>均线价格</th>
                    <th>偏离幅度</th>
                </tr>
        """
        
        for alert in alerts:
            for ma_breach in alert['breached_mas']:
                html += f"""
                <tr>
                    <td><strong>{alert['stock_code']}</strong></td>
                    <td>{alert['trade_date']}</td>
                    <td>¥{alert['close_price']:.2f}</td>
                    <td>MA{ma_breach['ma_period']}</td>
                    <td>¥{ma_breach['ma_value']:.2f}</td>
                    <td class="negative">{ma_breach['percentage']:.2f}%</td>
                </tr>
                """
        
        html += """
            </table>
            <p style="margin-top: 20px; color: #666;">
                <small>此邮件由股票监控系统自动发送,请勿回复。</small>
            </p>
        </body>
        </html>
        """
        
        return html
    
    def send_test_email(self) -> bool:
        try:
            subject = "股票监控系统 - 测试邮件"
            body = f"""
            <html>
            <body>
                <h2>测试邮件</h2>
                <p>这是一封测试邮件,确认邮件配置正确。</p>
                <p>发送时间:{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </body>
            </html>
            """
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = ', '.join(self.receivers)
            
            html_part = MIMEText(body, 'html', 'utf-8')
            msg.attach(html_part)
            
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                if self.use_tls:
                    server.starttls()
                server.login(self.from_email, self.password)
                server.send_message(msg)
            
            logger.info("Test email sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send test email: {e}")
            return False
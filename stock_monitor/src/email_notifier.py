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
            subject = f"股票监控警报 - {datetime.now().strftime('%Y-%m-%d')}"
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
            alert_types = []

            # MA breach alerts
            if alert.get('breached_mas'):
                breached_periods = [str(ma['ma_period']) for ma in alert['breached_mas']]
                breached_text = '、'.join(breached_periods)
                alert_types.append(f"突破{breached_text}日均线")

            # 9/30 baseline drop alert
            if alert.get('baseline_drop_alert'):
                drop_pct = alert['baseline_drop_alert']['drop_percentage']
                alert_types.append(f"较9/30跌{abs(drop_pct):.1f}%")

            # MTR drop alert
            if alert.get('mtr_drop_alert'):
                alert_types.append("20周均线上方跌一个MTR")

            # Bollinger Band drop alert
            if alert.get('boll_drop_alert'):
                drop_pct = alert['boll_drop_alert']['drop_percentage']
                alert_types.append(f"布林线上方跌{abs(drop_pct):.1f}%")

            if alert_types:
                summary_lines.append(f"{stock_code}: {', '.join(alert_types)}")

        return '<br>'.join(summary_lines)
    
    def _format_alert_body(self, alerts: List[Dict]) -> str:
        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; }}
                h2 {{ color: #d32f2f; }}
                h3 {{ color: #424242; margin-top: 30px; }}
                table {{ border-collapse: collapse; width: 100%; margin-top: 20px; }}
                th, td {{ border: 1px solid #ddd; padding: 12px; text-align: left; }}
                th {{ background-color: #f2f2f2; font-weight: bold; }}
                tr:nth-child(even) {{ background-color: #f9f9f9; }}
                .negative {{ color: #d32f2f; }}
                .alert-summary {{ background-color: #fff3e0; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .stock-section {{ margin: 20px 0; padding: 15px; border: 1px solid #e0e0e0; border-radius: 5px; }}
                .alert-type {{ background-color: #e3f2fd; padding: 10px; margin: 10px 0; border-radius: 3px; }}
            </style>
        </head>
        <body>
            <h2>股票监控警报</h2>
            <div class="alert-summary">
                <p><strong>警报时间:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>触发警报股票数:</strong> {len(alerts)} 只</p>
            </div>

            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 5px; margin: 20px 0;">
                <h3>快速摘要</h3>
                <p>{self._generate_summary(alerts)}</p>
            </div>

            <h3>详细信息</h3>
        """

        for alert in alerts:
            html += f"""
            <div class="stock-section">
                <h4>{alert['stock_code']} - {alert['trade_date']} 收盘价: ¥{alert['close_price']:.2f}</h4>
            """

            # MA breach alerts
            if alert.get('breached_mas'):
                html += """
                <div class="alert-type">
                    <strong>均线突破警报:</strong>
                    <table>
                        <tr>
                            <th>突破均线</th>
                            <th>均线价格</th>
                            <th>偏离幅度</th>
                        </tr>
                """
                for ma_breach in alert['breached_mas']:
                    html += f"""
                        <tr>
                            <td>MA{ma_breach['ma_period']}</td>
                            <td>¥{ma_breach['ma_value']:.2f}</td>
                            <td class="negative">{ma_breach['percentage']:.2f}%</td>
                        </tr>
                    """
                html += """
                    </table>
                </div>
                """

            # Baseline drop alert
            if alert.get('baseline_drop_alert'):
                bd = alert['baseline_drop_alert']
                html += f"""
                <div class="alert-type">
                    <strong>基线下跌警报 (相对9/30):</strong>
                    <ul>
                        <li>基线日期: {bd['baseline_date']}</li>
                        <li>基线价格: ¥{bd['baseline_price']:.2f}</li>
                        <li>当前价格: ¥{bd['current_price']:.2f}</li>
                        <li>跌幅: <span class="negative">{bd['drop_percentage']:.2f}%</span></li>
                    </ul>
                </div>
                """

            # MTR drop alert
            if alert.get('mtr_drop_alert'):
                mtr = alert['mtr_drop_alert']
                html += f"""
                <div class="alert-type">
                    <strong>MTR下跌警报 (20周均线上方):</strong>
                    <ul>
                        <li>20周均线: ¥{mtr['ma100_value']:.2f}</li>
                        <li>前收盘价: ¥{mtr['previous_close']:.2f}</li>
                        <li>当前价格: ¥{mtr['current_price']:.2f}</li>
                        <li>价格下跌: ¥{mtr['price_drop']:.2f}</li>
                        <li>MTR值: ¥{mtr['mtr_value']:.2f}</li>
                    </ul>
                </div>
                """

            # Bollinger Band drop alert
            if alert.get('boll_drop_alert'):
                bb = alert['boll_drop_alert']
                html += f"""
                <div class="alert-type">
                    <strong>布林线下跌警报:</strong>
                    <ul>
                        <li>前日收盘: ¥{bb['previous_close']:.2f} (布林上轨: ¥{bb['previous_bb_upper']:.2f})</li>
                        <li>当前收盘: ¥{bb['current_close']:.2f}</li>
                        <li>跌幅: <span class="negative">{bb['drop_percentage']:.2f}%</span></li>
                    </ul>
                </div>
                """

            html += """
            </div>
            """

        html += """
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
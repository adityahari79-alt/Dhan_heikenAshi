import smtplib
from email.mime.text import MIMEText
import requests

class AlertSystem:
    def __init__(self, email_settings=None, telegram_settings=None):
        self.email_settings = email_settings
        self.telegram_settings = telegram_settings

    def send_email(self, subject, body):
        if not self.email_settings:
            return
        msg = MIMEText(body)
        msg['Subject'] = subject
        msg['From'] = self.email_settings['from_email']
        msg['To'] = self.email_settings['to_email']

        try:
            with smtplib.SMTP_SSL(self.email_settings['smtp_server'], self.email_settings['smtp_port']) as smtp:
                smtp.login(self.email_settings['username'], self.email_settings['password'])
                smtp.sendmail(self.email_settings['from_email'], self.email_settings['to_email'], msg.as_string())
        except Exception as e:
            print(f"Email alert failed: {e}")

    def send_telegram(self, message):
        if not self.telegram_settings:
            return
        url = f"https://api.telegram.org/bot{self.telegram_settings['bot_token']}/sendMessage"
        params = {
            'chat_id': self.telegram_settings['chat_id'],
            'text': message
        }
        try:
            requests.get(url, params=params)
        except Exception as e:
            print(f"Telegram alert failed: {e}")

    def alert(self, subject, message):
        self.send_email(subject, message)
        self.send_telegram(message)

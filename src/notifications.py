import logging
import pandas as pd
import smtplib
import pydash
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from src.utils import config_loader

class NotificationHandler:
    def __init__(self, config):
        self.config = config

    def send_notifications(self, data):
        logging.info("Connecting to smtp server")
        server_url = pydash.get(self.config, 'bot_account.smtp.server', None)
        server_port = pydash.get(self.config, 'bot_account.smtp.port', None)
        if server_url is None or server_port is None:
            logging.warning("Exiting notifications: bot_account.smtp.server/port not configured.")
        server = smtplib.SMTP_SSL(server_url, server_port)
        server.ehlo()

        logging.info("Logging into smtp server with bot credentials")
        bot_username = pydash.get(self.config, 'bot_account.username', None)
        bot_password = pydash.get(self.config, 'bot_account.password', None)
        if bot_username is None or bot_password is None:
            logging.warning("Exiting notifications: bot_account.username/password not configured.")
        server.login(bot_username, bot_password)

        for recipient in self.config.get('recipients', []):
            message = self.construct_message(recipient, data)
            if message:
                server.send_message(message)

    def construct_message(self, recipient, data):
        logging.info(f"Sending notification to {recipient['address']}")

        notification = MIMEMultipart()
        notification['To'] = recipient.get('address')            
        notification['From'] = 'CU Bot'
        notification['Subject'] = 'Successfully Registere d'

        text = '<h1>Registration Success</h1>'
        mime_part = MIMEText(text, 'html')
        notification.attach(mime_part)

        mime_part = MIMEText(data.get('registration_success').to_html(index=False, justify='left'), 'html')
        notification.attach(mime_part)

        text = '<h1>Registration Failed</h1>'
        mime_part = MIMEText(text, 'html')
        notification.attach(mime_part)

        mime_part = MIMEText(data.get('registration_failure').to_html(index=False, justify='left'), 'html')
        notification.attach(mime_part)

        return notification
        

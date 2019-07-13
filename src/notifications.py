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

        registered_df = data.get('registration_success')
        failed_df = data.get('registration_failure')

        if not (pydash.get(recipient, 'notify_on.registration_success') and registered_df.shape[0]) \
            and not (pydash.get(recipient, 'notify_on.registration_failure') and failed_df.shape[0]):
            logging.info("No notification data to send.")
            return None

        if registered_df.shape[0]:
            notification['Subject'] = f'WaitList Update: Successfully Registered for: {", ".join(registered_df.values)}'
        else:
            notification['Subject'] = 'WaitList Update: No New Registrations'
        
        if pydash.get(recipient, 'notify_on.registration_success') and registered_df.shape[0]:
            text = '<h1>Successfully Registered</h1>'
            mime_part = MIMEText(text, 'html')
            notification.attach(mime_part)

            mime_part = MIMEText(registered_df.to_html(index=False, justify='left'), 'html')
            notification.attach(mime_part)

        if pydash.get(recipient, 'notify_on.registration_failure') and failed_df.shape[0]:
            text = '<h1>Still Waiting For</h1>'
            mime_part = MIMEText(text, 'html')
            notification.attach(mime_part)

            mime_part = MIMEText(failed_df[['Status', 'CRN', 'Subj', 'Crse', 'Sec', 'Title']].to_html(index=False, justify='left'), 'html')
            notification.attach(mime_part)

        return notification
        

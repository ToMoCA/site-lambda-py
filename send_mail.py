"""
# References
- https://realpython.com/python-send-email/#sending-a-plain-text-email
- https://www.tutorialspoint.com/send-mail-from-your-gmail-account-using-python
"""
from __future__ import print_function
import smtplib
import ssl
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import json


class EmailSender:
    def __init__(
        self,
        smtp_server,
        sender_email,
        receiver_email,
        password,
        port,
        subject,
        content,
    ):
        self.configs = {
            "SMTP_SERVER": smtp_server,
            "SENDER_EMAIL": sender_email,
            "RECEIVER_EMAIL": receiver_email,
            "PASSWORD": password,
            "PORT": port,
            "SUBJECT": subject,
            "CONTENT": content,
        }

    def __get_message(self):
        # Setup the MIME
        message = MIMEMultipart()
        message["From"] = self.configs["SENDER_EMAIL"]
        message["To"] = self.configs["RECEIVER_EMAIL"]
        message["Subject"] = self.configs["SUBJECT"]
        message.attach(MIMEText(self.configs["CONTENT"], "plain"))
        return message.as_string()

    def send_mail(self):
        # Create a secure SSL context
        context = ssl.create_default_context()

        # Try to log in to server and send email
        try:
            server = smtplib.SMTP(self.configs["SMTP_SERVER"], self.configs["PORT"])
            server.ehlo()  # Can be omitted
            server.starttls(context=context)  # Secure the connection
            server.ehlo()  # Can be omitted
            server.login(self.configs["SENDER_EMAIL"], self.configs["PASSWORD"])
            server.sendmail(
                self.configs["SENDER_EMAIL"],
                self.configs["RECEIVER_EMAIL"],
                self.__get_message(),
            )
        except Exception as e:
            # Print any error messages to stdout
            print(e)
        finally:
            server.quit()

def get_email_content(event):
    try:
        msg = f"""
            {event["company"]},
            {event["division"]},
            {event["name"]},
            {event["address"]},
            {event["phone_number"]},
            {event["email"]},
            {event["content"]},
        """
    except Exception as e:
        # Print any error messages to stdout
        print(e)
        msg = "Sorry! Failed to send message."
    return msg

def handler(event, context):
    print(f"event: {json.dumps(event, indent=2)}")
    print(f"context: {json.dumps(context, indent=2)}")

    receiver_emails = [
        os.environ["RECEIVER_EMAIL"],
        event["email"],
        # add receiver emails here
    ]

    EmailSender(
        smtp_server="smtp.gmail.com",
        sender_email=os.environ["SENDER_EMAIL"],
        receiver_email=", ".join(
            receiver_emails
        ),  # https://stackoverflow.com/a/12422921
        password=os.environ["PASSWORD"],
        port=587,
        subject=os.environ["SUBJECT"],
        content=get_email_content(event),
    ).send_mail()


if __name__ == "__main__":
    handler(
        event={
            "company": "テスト株式会社",
            "division": "テスト事業部",
            "name": "テスト太郎",
            "address": "兵庫県",
            "phone_number": "080-0000-0000",
            "email": "example@gmail.com",
            "content": "こんにちは",
        },
        context={},
    )

import smtplib
import os
import sys
from email import encoders
from email.mime.base import MIMEBase
from email.message import EmailMessage

if len(sys.argv) != 4:
    print("Usage: send_mail.py <subject> <from> <to> /path/to/content")

server = os.getenv("SMTP_SERVER", "postfix-mail")
port = int(os.getenv("SMTP_PORT", "587"))

# Set email contents
msg = EmailMessage()
with open(sys.argv[4], 'r') as contentf:
    msg.set_content(contentf.read())

# Set subject/from/to
msg["Subject"] = sys.argv[1]
msg["From"] = sys.argv[2]
msg["To"] = sys.argv[3]

s = smtplib.SMTP(server, port)
s.send_message(msg)
s.quit()
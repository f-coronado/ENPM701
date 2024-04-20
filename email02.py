import os
from datetime import datetime
import smtplib
from smtplib import SMTP
from smtplib import SMTPException
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from libraries.localization import Localization

def main():
	local = Localization()
	local.email()

if __name__ == "__main__":
	main()




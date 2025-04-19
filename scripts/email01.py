import os
from datetime import datetime
import smtplib
from smtplib import SMTP
from smtplib import SMTPException
import email
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

# define timestamp and record a image
pic_time = datetime.now().strftime('%Y%m%d%H%M%S')
command = 'raspistill -w 1280 -h 720 -vf -hf -o ' + pic_time + '.jpg'
os.system(command)

# email info
smtpUser = 'fabrizzio.enpm701@gmail.com'
#smtpPass = 'jaw7-bold-imply'
smtpPass = 'xshy vmsi btcw swvo'

# destination email info
toAdd = ['ENPM809TS19@gmail.com', 'jsuriya@umd.edu']
fromAdd = smtpUser
subject = 'image recorded at ' + pic_time
msg = MIMEMultipart()
msg['Subject'] = subject
msg['From'] = fromAdd
#msg['To'] = toAdd
msg['To'] = ",".join(toAdd)
msg.preamble = 'Image recorded at ' + pic_time

# email text
body = MIMEText("image recorded at " + pic_time)
msg.attach(body)

# attach image
fp = open(pic_time + '.jpg', 'rb')
img = MIMEImage(fp.read())
fp.close()
msg.attach(img)

# send email
s = smtplib.SMTP('smtp.gmail.com', 587)
s.ehlo()
s.starttls()
s.ehlo()

s.login(smtpUser, smtpPass)
s.sendmail(fromAdd, toAdd, msg.as_string())
s.quit()

print("email delivered")

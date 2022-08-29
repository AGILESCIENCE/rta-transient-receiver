import os
import smtplib
from email.message import EmailMessage



class Mail():

    def __init__(self, gmail_user, gmail_password) -> None:

        self.gmail_user = gmail_user
        self.gmail_password = gmail_password

    def send_email(self, to, subject, body):

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = self.gmail_user
        msg['To'] = ', '.join(to)

        try:

            smtp_server = smtplib.SMTP_SSL('smtp.gmail.com', 465)

            smtp_server.ehlo()

            smtp_server.login(self.gmail_user, self.gmail_password)

            #print(msg)

            smtp_server.send_message(msg)

            smtp_server.close()

            print("Email sent successfully!")

        except Exception as ex:

            print("Something went wrong….",ex)

if __name__ == "__main__":

    mail = Mail("alert.agile@inaf.it", os.environ["MAIL_PASS"])

    to = ["antonio.addis@inaf.it", "adaant@gmail.com"]

    subject = 'Lorem ipsum dolor sit amet'

    body = 'consectetur adipiscing elit'
    
    mail.send_email(to, subject, body)
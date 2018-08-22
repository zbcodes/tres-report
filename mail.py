from smtplib import SMTP_SSL
from email.message import EmailMessage
from email.utils import formatdate


class Email:
    """
    Rozsyłanie raportów pocztą e-mail
    """

    def __init__(self, email_box):
        self.__email_box = email_box

    def send(self, address, subject, file):
        """Wysyła e-mail z plikiem w załączniku"""
        for recipient in address:
            msg = EmailMessage()
            msg['Date'] = formatdate(localtime=True)
            msg['From'] = self.__email_box['sender']
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.set_content('Wiadomość wysłana automatycznie, proszę nie odpowiadać...')

            with open(file, 'rb') as fp:
                msg.add_attachment(fp.read(), maintype='application',
                                   subtype='octet-stream', filename=file)

            with SMTP_SSL('smtp.iq.pl', 465) as smtp:
                smtp.ehlo()
                smtp.login(self.__email_box['user'], self.__email_box['pass'])
                smtp.send_message(msg)

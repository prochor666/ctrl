import smtplib, ssl
from core import smtp_config


def send(from, to, subject, body):
    conf = smtp_config()
    if type(conf) is dict:

        # Create a secure SSL context
        context = ssl.create_default_context()

        # Try to log in to server and send email
        try:
            server = smtplib.SMTP(conf['host'], conf['port'])
            server.ehlo()
            server.starttls(context=context) # Secure the connection
            server.ehlo()
            server.login(conf['username'], conf['password'])
            # TODO: Send email here
        except Exception as e:
            # Print any error messages to stdout
            print(e)
        finally:
            server.quit()

    return False


def via():
    return True

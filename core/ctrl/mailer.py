import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from core import config, utils


def send(from, to, subject, body):
    conf = config.smtp_config()
    if type(conf) is dict:
        via(conf, email_compose({
            'from': from,
            'to': to,
            'subject': subject,
            'alt_body': utils.br2nl(utils.strip_tags(subject, '<br>')),
            'body': body
        }))

    return False


def via(conf):

    if conf['cs'] in ['TLS', 'SSL']:
        context = ssl.create_default_context()

        if conf['cs'] == 'SSL':
            try:
                with smtplib.SMTP_SSL(conf['host'], conf['port'], context=context) as server:
                    server.login(conf['username'], conf['password'])
                    return server

            except Exception as e:
                return str(e)

        if conf['cs'] == 'TLS':
            # Try to log in to server and send email
            try:
                server = smtplib.SMTP(conf['host'], conf['port'])
                server.ehlo()
                server.starttls(context=context)  # Secure the connection
                server.ehlo()
                server.login(conf['username'], conf['password'])

                return server

            except Exception as e:
                # Print any error messages to stdout
                return str(e)

            finally:
                server.quit()

    return False


def email_compose(email):

    msg = MIMEMultipart('alternative')
    msg['Subject'] = email['subject']
    msg['From'] = email['from']
    msg['To'] = email['to']

    # Create the body of the message (a plain-text and an HTML version).
    text = email['alt_body']
    html = email['body']

    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)

    return msg

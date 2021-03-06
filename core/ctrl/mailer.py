import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pyisemail import is_email
from core import config, utils, app
from flask import Flask, render_template


def send(to, subject, body, att = None):
    conf = config.smtp_config()
    if type(conf) is dict:
        return via(conf, email_compose({
            'from': conf['from'],
            'to': to,
            'subject': subject,
            'alt_body': utils.br2nl(utils.strip_tags(subject, '<br>')),
            'body': body
        }, att))

    return False


def via(conf, msg):

    if conf['cs'] in ['TLS', 'SSL']:
        context = ssl.create_default_context()

        if conf['cs'] == 'SSL':
            try:
                with smtplib.SMTP_SSL(conf['host'], conf['port'], context=context) as server:
                    server.login(conf['username'], conf['password'])
                    server.sendmail(msg['From'], msg['To'], msg.as_string())
                    return True

            except Exception as e:
                return 'SSL-error: ' + str(e)

        if conf['cs'] == 'TLS':
            # Try to log in to server and send email
            try:
                server = smtplib.SMTP(conf['host'], conf['port'])
                server.ehlo()
                server.starttls(context=context)  # Secure the connection
                server.ehlo()
                server.login(conf['username'], conf['password'])
                server.sendmail(msg['From'], msg['To'], msg.as_string())
                return True

            except Exception as e:
                print(e)
                # Print any error messages to stdout
                return 'TLS-error: ' + str(e)

            finally:
                server.quit()

    return False


def email_compose(email, att=None):

    msg = MIMEMultipart('alternative')
    msg['Subject'] = email['subject']
    msg['From'] = email['from']
    msg['To'] = email['to']

    # Body of the  message (plain-text + HTML version)
    text = email['alt_body']
    html = email['body']

    # Convert the right MIME types (text/plain + text/html)
    part1 = MIMEText(text, 'plain')
    part2 = MIMEText(html, 'html')

    # Attach parts into message
    # RFC2046 - the last part of a multipart message is the best and preferred
    # We choose HTML version
    msg.attach(part1)
    msg.attach(part2)

    if type(att) is str and len(att)>0:
        part3 = MIMEApplication(
            att,
            Name='deploy.log'
        )

        # After the file is closed
        part3['Content-Disposition'] = 'attachment; filename="deploy.log"'
        msg.attach(part3)

    return msg


def check_email(email=None):
    result = is_email(str(email), check_dns=True, diagnose=True)
    return {
        'valid': result.code == 0,
        'code': result.code,
        'validator_message': result.message,
        'description': result.description
    }


def assign_template(template, data):
    return render_template(
        f"email/{template}.html", data=data)

from flask import current_app
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Message
from website import mail

def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender= current_app.config.get('MAIL_DEFAULT_SENDER')
    )
    mail.send(msg)

def generate_confirmation_token(email):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))
    return serializer.dumps(email, salt=current_app.config.get('SECURITY_PASSWORD_SALT'))


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(current_app.config.get('SECRET_KEY'))
    try:
        email = serializer.loads(
            token,
            salt=current_app.config.get('SECURITY_PASSWORD_SALT'),
            max_age=expiration
        )
    except:
        return False
    return email
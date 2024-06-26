import smtplib
from email.message import EmailMessage
from customer_app.config import EMAIL, EMAIL_APP_PASSWORD


def send_verification_email(email, verification_code):
    msg = EmailMessage()
    msg.set_content(f'Your email verification code for saahitt is {verification_code}')
    msg['Subject'] = 'Email Verification'
    msg['From'] = EMAIL
    msg['To'] = email

    with smtplib.SMTP('smtp.zoho.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL, EMAIL_APP_PASSWORD)
        smtp.send_message(msg)


def send_password_reset_email(email, token, reset_url):
    msg = EmailMessage()
    msg.set_content(
        f'To reset your password, visit the following link:\n{reset_url}/create-new-password/{token}')
    msg['Subject'] = 'Password Reset Request'
    msg['From'] = EMAIL
    msg['To'] = email

    with smtplib.SMTP('smtp.zoho.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL, EMAIL_APP_PASSWORD)
        smtp.send_message(msg)

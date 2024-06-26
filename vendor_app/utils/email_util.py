import smtplib
from email.message import EmailMessage

from vendor_app.config import EMAIL, EMAIL_APP_PASSWORD

def send_verification_email(email, verification_code):
    subject = 'Email Verification'
    sender_email = EMAIL
    recipient_email = email

    # Create the plain-text and HTML version of message
    text = f"""\
    Hi,

    Your email verification code for saahitt is {verification_code}.

    Thank you!
    """

    html = f"""\
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; margin: 20px;">
            <h2 style="color: #333;">Email Verification</h2>
            <p>Hi,</p>
            <p>Your email verification code for <strong>saahitt</strong> is:</p>
            <div style="font-size: 24px; font-weight: bold; margin: 20px 0; padding: 10px; border: 2px dashed #4CAF50; display: inline-block;">
                {verification_code}
            </div>
            <p>Thank you!</p>
            <hr>
            <p style="font-size: 12px; color: #888;">If you did not request this verification, please ignore this email.</p>
        </div>
    </body>
    </html>
    """
    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg.set_content(text)
    msg.add_alternative(html, subtype='html')
    with smtplib.SMTP('smtp.zoho.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL, EMAIL_APP_PASSWORD)
        smtp.send_message(msg)


def send_password_reset_email(email, token, reset_url):
    msg = EmailMessage()
    msg.set_content(
        f'To reset your password, visit the following link:\n{reset_url}/consumer-api/reset-password/{token}')
    msg['Subject'] = 'Password Reset Request'
    msg['From'] = EMAIL
    msg['To'] = email

    with smtplib.SMTP('smtp.zoho.com', 587) as smtp:
        smtp.starttls()
        smtp.login(EMAIL, EMAIL_APP_PASSWORD)
        smtp.send_message(msg)

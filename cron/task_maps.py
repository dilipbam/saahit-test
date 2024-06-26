from cron.async_tasks import send_verification_email, send_password_reset_email

plugins = {
    'SEND_VERIFICATION_EMAIL': send_verification_email,
    'SEND_PASSWORD_RESET_LINK': send_password_reset_email
}
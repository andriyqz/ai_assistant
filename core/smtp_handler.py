import asyncio
from email.message import EmailMessage
import aiosmtplib

async def send_mail(smtp_host: str, smtp_port: int, smtp_user: str, smtp_password: str, subject: str, body: str, to_email: str):
    message = EmailMessage()
    message["From"] = smtp_user
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    await aiosmtplib.send(
        message,
        hostname=smtp_host,
        port=smtp_port,
        use_tls=True,
        username=smtp_user,
        password=smtp_password
    )
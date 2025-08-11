import re
import json
from core.utils import get_config
from core.smtp_handler import send_mail

config = get_config()

async def handle_command(command: str):
    commands_to_functions = {
        '/send_email': handle_email_sending,
    }

    command_without_args = re.findall(r'/\w+', command)[0]
    return await commands_to_functions[command_without_args](command)


async def handle_email_sending(command: str):
    json_part_match = re.search(r'/send_email\s+({.*})', command)
    if not json_part_match:
        return

    json_str = json_part_match.group(1)

    data = json.loads(json_str)

    recipient_email = data.get("recipient_email")
    subject = data.get("subject", "")
    email_text = data.get("email_text", "")

    if not recipient_email:
        return

    print(f"Recipient: {recipient_email}, Subject: {subject}, Body: {email_text}")

    await send_mail(
        smtp_host=config["smtp_server"],
        smtp_port=config["smtp_port"],
        smtp_user=config["assistant_email"],
        smtp_password=config["assistant_email_password"],
        to_email=recipient_email,
        subject=subject,
        body=email_text
    )

import asyncio
import email
from email.header import decode_header
from aioimaplib import aioimaplib
from datetime import datetime
import locale

locale.setlocale(locale.LC_TIME, 'C')

def get_email_body(msg):
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition"))

            if content_type == "text/plain" and "attachment" not in content_disposition:
                try:
                    body = part.get_payload(decode=True)
                    charset = part.get_content_charset() or "utf-8"
                    return body.decode(charset, errors="ignore")
                except Exception:
                    continue
        return ""
    else:
        body = msg.get_payload(decode=True)
        charset = msg.get_content_charset() or "utf-8"
        return body.decode(charset, errors="ignore")

class MailMonitor:
    def __init__(
        self,
        email_addr,
        password,
        imap_server,
        folder='INBOX',
        search_criteria='UNSEEN',
        check_interval=60,
    ):
        self.email = email_addr
        self.password = password
        self.imap_server = imap_server
        self.folder = folder
        self.search_criteria = search_criteria
        self.check_interval = check_interval

        self.start_time = datetime.utcnow()

    def format_since_date(self):
        return self.start_time.strftime('%d-%b-%Y')

    async def fetch_new_emails(self):
        try:
            client = aioimaplib.IMAP4_SSL(host=self.imap_server)
            await client.wait_hello_from_server()

            login_resp = await client.login(self.email, self.password)
            if login_resp.result != 'OK':
                print(f"[Error] Login failed: {login_resp.lines}")
                await client.logout()
                return

            select_resp = await client.select(self.folder)
            if select_resp.result != 'OK':
                print(f"[Error] Select folder failed: {select_resp.lines}")
                await client.logout()
                return

            since_date = self.format_since_date()
            criteria = f'UNSEEN SINCE {since_date}'

            search_resp = await client.search(criteria)
            if search_resp.result != 'OK':
                print(f"[Error] Search failed: {search_resp.lines}")
                await client.logout()
                return

            email_ids = search_resp.lines[0].split()
            for num in email_ids:
                email_id_str = num.decode()

                fetch_resp = await client.fetch(email_id_str, '(RFC822)')
                if fetch_resp.result != 'OK':
                    print(f"[Error] Fetch failed for {email_id_str}: {fetch_resp.lines}")
                    continue

                raw_email = fetch_resp.lines[1]
                if isinstance(raw_email, str):
                    raw_email = raw_email.encode('utf-8')

                msg = email.message_from_bytes(raw_email)

                date_tuple = email.utils.parsedate_tz(msg.get('Date'))
                if date_tuple:
                    msg_date = datetime.fromtimestamp(email.utils.mktime_tz(date_tuple))
                    if msg_date < self.start_time:
                        continue

                subject, encoding = decode_header(msg.get('Subject', ''))[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding or 'utf-8', errors='ignore')
                from_ = msg.get('From', '')

                body = get_email_body(msg)

                store_resp = await client.store(email_id_str, '+FLAGS', r'(\Seen)')

                if store_resp.result != 'OK':
                    print(f"[Warning] Failed to mark {email_id_str} as seen: {store_resp.lines}")

                yield {
                    'from': from_,
                    'subject': subject,
                    'body': body,
                    'message': msg,
                }

            await client.logout()

        except Exception as e:
            print(f"[Error] {e}")


import json
import imaplib
import email
from email.header import decode_header
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Message


class MessageConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        data = json.loads(text_data)

        if 'login' in data and 'password' in data:
            login = data['login']
            password = data['password']
            await self.fetch_emails(login, password)

    async def fetch_emails(self, login, password):
        mail = imaplib.IMAP4_SSL('imap.gmail.com', '993')
        try:
            mail.login(login, password)
            mail.select("inbox")
        except imaplib.IMAP4.error as e:
            await self.send(text_data=json.dumps({
                'status': 'error',
                'message': str(e)
            }))
            return

        status, messages = mail.search(None, 'ALL')
        email_ids = messages[0].split()

        for i in range(len(email_ids)):
            res, msg = mail.fetch(email_ids[i], "(RFC822)")
            msg = email.message_from_bytes(msg[0][1])

            subject, encoding = decode_header(msg['Subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding if encoding else 'utf-8')

            sent_date = msg['Date']
            body = self.get_email_body(msg)

            # Сохранение сообщения в БД
            Message.objects.create(
                subject=subject,
                sent_date=sent_date,
                received_date=sent_date,
                body=body,
                description=body[:50]  # Краткое описание
            )

            # Отправляем информацию о каждом сообщении обратно клиенту
            await self.send(text_data=json.dumps({
                'status': 'progress',
                'message': {
                    'subject': subject,
                    'sent_date': sent_date,
                    'body': body[:50]  # Отправляем краткое описание
                },
                'checked': i + 1,
                'total': len(email_ids)
            }))

        await self.send(text_data=json.dumps({
            'status': 'complete'
        }))

    def get_email_body(self, msg):
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                if part.get_content_type() == "text/plain":
                    body = part.get_payload(decode=True).decode()
                    break
        else:
            body = msg.get_payload(decode=True).decode()
        return body

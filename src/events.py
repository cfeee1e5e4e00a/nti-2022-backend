import asyncio

from db import db
from sqlalchemy import Column, Float, String
import aiosmtplib.smtp
from email.message import EmailMessage
from datetime import datetime

receiver = 'ilyamerzlakov@gmail.com'

class EventModel(db.Model):
    __tablename__ = 'events'

    time = Column(Float(), nullable=False)
    tag = Column(String(), nullable=False)
    data = Column(String(), nullable=False)


class EventService:
    async def register_event(self, tag: str, data: str):
        time = datetime.now().timestamp()
        await self.send_mail(f"{tag}: {data}", f"NTI: {tag}")
        asyncio.ensure_future(EventModel.create(time=time, tag=tag, data=data))
        print(f'EVENT:{tag}: {data}')



    async def send_mail(self, txt: str, theme: str):
        sender = 'uchansansan@cfeee1e5e4e00a.ru'
        sender_password = 'lnhvwqldkhovdzxt'
        recipients = [receiver]

        mail = EmailMessage()
        mail.set_content(txt)
        mail["From"] = sender
        mail["To"] = recipients[0]
        mail["Subject"] = theme


        asyncio.ensure_future(aiosmtplib.send(message=mail, sender=sender, recipients=recipients, hostname='smtp.yandex.ru', port=465, username=sender, password=sender_password, use_tls=True))


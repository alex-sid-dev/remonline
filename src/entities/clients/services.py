from typing import Optional
from src.entities.clients.models import Client, ClientID, ClientUUID
from uuid import uuid4

class ClientService:
    def create_client(
        self,
        full_name: str,
        phone: str,
        email: Optional[str] = None,
        telegram_nick: Optional[str] = None,
        comment: Optional[str] = None,
        address: Optional[str] = None,
    ) -> Client:
        return Client(
            id=None,  # type: ignore
            uuid=ClientUUID(uuid4()),
            full_name=full_name,
            phone=phone,
            email=email,
            telegram_nick=telegram_nick,
            comment=comment,
            address=address,
            is_active=True,
        )

    def update_client(
        self,
        client: Client,
        full_name: Optional[str] = None,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        telegram_nick: Optional[str] = None,
        comment: Optional[str] = None,
        address: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> Client:
        if full_name is not None:
            client.full_name = full_name
        if phone is not None:
            client.phone = phone
        if email is not None:
            client.email = email
        if telegram_nick is not None:
            client.telegram_nick = telegram_nick
        if comment is not None:
            client.comment = comment
        if address is not None:
            client.address = address
        if is_active is not None:
            client.is_active = is_active
        return client

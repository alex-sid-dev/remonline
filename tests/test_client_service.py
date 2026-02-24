from src.entities.clients.services import ClientService


class TestClientService:
    def setup_method(self):
        self.service = ClientService()

    def test_create_client_minimal(self):
        client = self.service.create_client(
            full_name="John Doe",
            phone="+79001234567",
        )
        assert client.full_name == "John Doe"
        assert client.phone == "+79001234567"
        assert client.is_active is True
        assert client.uuid is not None
        assert client.email is None
        assert client.telegram_nick is None
        assert client.address is None

    def test_create_client_full(self):
        client = self.service.create_client(
            full_name="Jane Doe",
            phone="+79009876543",
            email="jane@example.com",
            telegram_nick="@jane",
            comment="VIP customer",
            address="ул. Ленина, 1",
        )
        assert client.email == "jane@example.com"
        assert client.telegram_nick == "@jane"
        assert client.comment == "VIP customer"
        assert client.address == "ул. Ленина, 1"

    def test_update_client_partial(self):
        client = self.service.create_client(
            full_name="John Doe",
            phone="+79001234567",
        )
        updated = self.service.update_client(client, full_name="John Smith")
        assert updated.full_name == "John Smith"
        assert updated.phone == "+79001234567"

    def test_update_client_deactivate(self):
        client = self.service.create_client(
            full_name="John Doe",
            phone="+79001234567",
        )
        updated = self.service.update_client(client, is_active=False)
        assert updated.is_active is False

    def test_update_client_address(self):
        client = self.service.create_client(
            full_name="John Doe",
            phone="+79001234567",
        )
        updated = self.service.update_client(client, address="пр. Мира, 10")
        assert updated.address == "пр. Мира, 10"
        assert updated.full_name == "John Doe"

    def test_update_client_none_does_not_overwrite(self):
        client = self.service.create_client(
            full_name="John Doe",
            phone="+79001234567",
            email="john@example.com",
        )
        updated = self.service.update_client(client, full_name="New Name")
        assert updated.email == "john@example.com"

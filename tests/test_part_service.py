from src.entities.parts.services import PartService


class TestPartService:
    def setup_method(self):
        self.service = PartService()

    def test_create_part_minimal(self):
        part = self.service.create_part(name="Resistor 100Ω")
        assert part.name == "Resistor 100Ω"
        assert part.is_active is True
        assert part.uuid is not None
        assert part.sku is None
        assert part.price is None
        assert part.stock_qty is None

    def test_create_part_full(self):
        part = self.service.create_part(
            name="Screen Assembly",
            sku="SCR-001",
            price=1500.0,
            stock_qty=10,
        )
        assert part.sku == "SCR-001"
        assert part.price == 1500.0
        assert part.stock_qty == 10

    def test_update_part_price(self):
        part = self.service.create_part(name="Resistor", price=10.0)
        updated = self.service.update_part(part, price=15.0)
        assert updated.price == 15.0
        assert updated.name == "Resistor"

    def test_update_part_stock(self):
        part = self.service.create_part(name="Resistor", stock_qty=5)
        updated = self.service.update_part(part, stock_qty=3)
        assert updated.stock_qty == 3

    def test_update_part_deactivate(self):
        part = self.service.create_part(name="Resistor")
        updated = self.service.update_part(part, is_active=False)
        assert updated.is_active is False

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.device_reader import DeviceReader
from src.entities.clients.models import ClientID
from src.entities.devices.models import Device, DeviceID, DeviceUUID


class DeviceReaderAdapter(DeviceReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, device_id: DeviceID) -> Device | None:
        stmt = select(Device).where(Device.id == device_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, device_uuid: DeviceUUID) -> Device | None:
        stmt = select(Device).where(Device.uuid == device_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all_active(self) -> list[Device]:
        stmt = select(Device).where(Device.is_active == True)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def read_by_client_id(self, client_id: ClientID) -> list[Device]:
        stmt = select(Device).where(Device.client_id == client_id)
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

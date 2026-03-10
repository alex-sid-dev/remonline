from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.ports.device_type_reader import DeviceTypeReader
from src.entities.device_types.models import DeviceType, DeviceTypeID, DeviceTypeUUID


class DeviceTypeReaderAdapter(DeviceTypeReader):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read_by_id(self, device_type_id: DeviceTypeID) -> DeviceType | None:
        stmt = select(DeviceType).where(DeviceType.id == device_type_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_by_uuid(self, device_type_uuid: DeviceTypeUUID) -> DeviceType | None:
        stmt = select(DeviceType).where(DeviceType.uuid == device_type_uuid)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def read_all_active(self, organization_id: int) -> list[DeviceType]:
        stmt = select(DeviceType).where(
            DeviceType.is_active.is_(True),
            DeviceType.organization_id == organization_id,
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

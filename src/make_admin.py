from keycloak import KeycloakAdmin
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine


async def make_admin():
    engine = create_async_engine(
        str("postgresql+psycopg://alex:postgres@127.0.0.1:5432/remonline"),
        echo=False,
        pool_size=15,
        max_overflow=15,
        pool_timeout=5,
    )
    session_maker = async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    client = KeycloakAdmin(
        server_url="http://127.0.0.1:8080/",
        username="admin",
        password="admin",
        realm_name="master",
        client_id="admin-cli",
        verify=True,
    )
    user_old = await client.a_get_users({"email": "admin@admin.ru"})
    if user_old:
        return None

    new_user = {
        "email": "admin@admin.ru",
        "username": "admin@admin.ru",
        "enabled": True,
        "emailVerified": False,
        "credentials": [{"value": "1!String", "type": "password"}],
    }

    user_uuid = await client.a_create_user(payload=new_user)
    async with session_maker() as session:
        result = await session.execute(text(
            """
            INSERT INTO users (user_uuid, email)
            VALUES (:user_uuid, :email) RETURNING user_id
            """),
            {"user_uuid": str(user_uuid), "email": "admin@admin.ru"},
        )
        user_id = result.scalar()  # Получаем ID
        await session.flush()
        await session.execute(text("""
                                   INSERT INTO employees (user_id, full_name, phone, position, is_active)
                                   VALUES (:user_id, :full_name, :phone, :position, :is_active)
                                   """),
                              {"user_id": int(user_id), "full_name": "Yahve", "phone": "+1 000 000 000",
                               "position": "supervisor", "is_active": True},
                              )
        await session.commit()
    return None



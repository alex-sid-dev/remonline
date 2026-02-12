import uuid
from keycloak import KeycloakAdmin
from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.config.settings import Settings


async def make_admin(settings: Settings):
    engine = create_async_engine(
        settings.database_url,
        echo=settings.database.echo,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        pool_timeout=settings.database.pool_timeout,
    )
    session_maker = async_sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )
    client = KeycloakAdmin(
        server_url=settings.keycloak.keycloak_url,
        username=settings.keycloak.keycloak_username,
        password=settings.keycloak.keycloak_password,
        realm_name=settings.keycloak.keycloak_realm,
        client_id=settings.keycloak.keycloak_client_id,
        verify=True,
    )
    user_old = await client.a_get_users({"email": "admin@admin.ru"})
    if user_old:
        # Проверяем, есть ли пользователь в нашей базе данных
        async with session_maker() as session:
            result = await session.execute(text(
                "SELECT user_id FROM users WHERE email = :email"
            ), {"email": "admin@admin.ru"})
            user_in_db = result.scalar()
            
            if user_in_db:
                # Проверяем, есть ли сотрудник для этого пользователя
                result = await session.execute(text(
                    "SELECT employee_id FROM employees WHERE user_id = :user_id"
                ), {"user_id": user_in_db})
                employee_in_db = result.scalar()
                
                if employee_in_db:
                    return None
                
                # Если пользователя в Keycloak есть, а сотрудника в нашей БД нет - создаем
                await session.execute(text("""
                                           INSERT INTO employees (employee_uuid, user_id, full_name, phone, position, is_active)
                                           VALUES (:employee_uuid, :user_id, :full_name, :phone, :position, :is_active)
                                           """),
                                      {
                                          "employee_uuid": uuid.uuid4(),
                                          "user_id": int(user_in_db),
                                          "full_name": "Yahve",
                                          "phone": "+1 000 000 000",
                                          "position": "supervisor",
                                          "is_active": True
                                      })
                await session.commit()
                return None
            else:
                # Если в Keycloak есть, а в users нет - берем UUID из Keycloak и создаем в обеих таблицах
                user_uuid = user_old[0]['id']
                result = await session.execute(text(
                    """
                    INSERT INTO users (user_uuid, email)
                    VALUES (:user_uuid, :email) RETURNING user_id
                    """),
                    {"user_uuid": str(user_uuid), "email": "admin@admin.ru"},
                )
                user_id = result.scalar()
                await session.flush()
                await session.execute(text("""
                                           INSERT INTO employees (employee_uuid, user_id, full_name, phone, position, is_active)
                                           VALUES (:employee_uuid, :user_id, :full_name, :phone, :position, :is_active)
                                           """),
                                      {
                                          "employee_uuid": uuid.uuid4(),
                                          "user_id": int(user_id),
                                          "full_name": "Yahve",
                                          "phone": "+1 000 000 000",
                                          "position": "supervisor",
                                          "is_active": True
                                      })
                await session.commit()
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
                                   INSERT INTO employees (employee_uuid, user_id, full_name, phone, position, is_active)
                                   VALUES (:employee_uuid, :user_id, :full_name, :phone, :position, :is_active)
                                   """),
                              {
                                  "employee_uuid": uuid.uuid4(),
                                  "user_id": int(user_id),
                                  "full_name": "Yahve",
                                  "phone": "+1 000 000 000",
                                  "position": "supervisor",
                                  "is_active": True
                              },
                              )
        await session.commit()
    return None



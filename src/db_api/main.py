import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from models import (Base, Link, PromoCode, RoleType, TGUser, VKUser,
                    async_session, engine)
from schemas import Admin, LinkCreate, PromocodeCreate, UserCreate, UserGet
from sqlalchemy import delete, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession


async def lifespan_context(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(lifespan=lifespan_context)


async def get_db():
    async with async_session() as session:
        yield session


@app.post('/tg_users/', response_model=UserCreate)
async def create_tg_user(
    tg_user: UserCreate,
    db: AsyncSession = Depends(get_db)
        ):
    if tg_user.role == 'parent':
        role = RoleType.PARENT
    else:
        role = RoleType.SPEECH_THERAPIST
    stmt = insert(TGUser).values(
        user_id=tg_user.user_id, role=role, is_admin=tg_user.is_admin
        ).on_conflict_do_update(
        constraint=TGUser.__table__.primary_key,
        set_={
            TGUser.role: role,
            TGUser.is_admin: tg_user.is_admin
        }
    ).returning(TGUser.user_id, TGUser.role, TGUser.is_admin)
    result = await db.execute(stmt)
    await db.commit()
    new_tg_user = result.fetchone()
    response_user = UserCreate(
        user_id=new_tg_user.user_id,
        role=new_tg_user.role,
        is_admin=new_tg_user.is_admin
    )
    return response_user


@app.post('/vk_users/', response_model=UserCreate)
async def create_vk_user(
    vk_user: UserCreate,
    db: AsyncSession = Depends(get_db)
        ):
    if vk_user.role == 'parent':
        role = RoleType.PARENT
    else:
        role = RoleType.SPEECH_THERAPIST
    stmt = insert(VKUser).values(
        user_id=vk_user.user_id, role=role, is_admin=vk_user.is_admin
        ).on_conflict_do_update(
        constraint=VKUser.__table__.primary_key,
        set_={
            VKUser.role: role,
            VKUser.is_admin: vk_user.is_admin
        }
    ).returning(VKUser.user_id, VKUser.role, VKUser.is_admin)
    result = await db.execute(stmt)
    await db.commit()
    new_vk_user = result.fetchone()
    response_user = UserCreate(
        user_id=new_vk_user.user_id,
        role=new_vk_user.role,
        is_admin=new_vk_user.is_admin
    )
    return response_user


@app.post('/links/', response_model=LinkCreate)
async def create_link(
    link: LinkCreate,
    db: AsyncSession = Depends(get_db)
        ):
    stmt = insert(Link).values(
        link=link.link, link_name=link.link_name,
        link_type=link.link_type, to_role=link.to_role
        ).returning(
            Link.link,
            Link.link_name,
            Link.link_type,
            Link.to_role
        )
    result = await db.execute(stmt)
    await db.commit()
    new_link = result.fetchone()
    if new_link is None:
        raise HTTPException(status_code=500, detail='Ошибка создания ссылки')
    response_link = LinkCreate(
        link=new_link.link,
        link_name=new_link.link_name,
        link_type=new_link.link_type,
        to_role=new_link.to_role
    )
    return response_link


@app.post('/promocodes/', response_model=PromocodeCreate)
async def create_promocode(
    promocode: PromocodeCreate,
    db: AsyncSession = Depends(get_db)
        ):
    stmt = insert(PromoCode).values(
        promocode=promocode.promocode, file_path=promocode.file_path
        ).returning(
            PromoCode.promocode,
            PromoCode.file_path
        )
    result = await db.execute(stmt)
    await db.commit()
    new_promocode = result.fetchone()
    if new_promocode is None:
        raise HTTPException(
            status_code=500,
            detail='Ошибка создания промокода'
        )
    response_promocode = PromocodeCreate(
        promocode=new_promocode.promocode,
        file_path=new_promocode.file_path
    )
    return response_promocode


@app.post('/admins/', response_model=UserCreate)
async def promote_user_to_admin(
    user: Admin,
    db: AsyncSession = Depends(get_db)
        ):
    if user.platform == 'telegram':
        model = TGUser
    else:
        model = VKUser
    stmt = insert(model).values(
        user_id=user.user_id, role=RoleType.SPEECH_THERAPIST, is_admin=1
        ).on_conflict_do_update(
        constraint=model.__table__.primary_key,
        set_={model.is_admin: 1}
    ).returning(model.user_id, model.role, model.is_admin)
    result = await db.execute(stmt)
    await db.commit()
    new_admin = result.fetchone()
    if new_admin is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    response_admin = UserCreate(
        user_id=new_admin.user_id,
        role=new_admin.role,
        is_admin=new_admin.is_admin
    )
    return response_admin


@app.patch('/admins/', response_model=UserCreate)
async def demote_admin_to_user(
    user: Admin,
    db: AsyncSession = Depends(get_db)
        ):
    if user.platform == 'telegram':
        model = TGUser
    else:
        model = VKUser
    stmt = update(model).where(model.user_id == user.user_id).values(
        is_admin=0).returning(model.user_id, model.role, model.is_admin)
    result = await db.execute(stmt)
    await db.commit()
    updated_user = result.fetchone()
    if updated_user is None:
        raise HTTPException(status_code=404, detail='Администратор не найден')
    response_user = UserCreate(
        user_id=updated_user.user_id,
        role=updated_user.role,
        is_admin=updated_user.is_admin
    )
    return response_user


@app.get('/tg_users/admins/{user_id}', response_model=UserGet)
async def get_tg_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db)
        ):
    stmt = select(TGUser).where(
        TGUser.user_id == user_id,
        TGUser.is_admin == 1
    )
    result = await db.execute(stmt)
    admin = result.scalar_one_or_none()
    if admin is None:
        raise HTTPException(status_code=404, detail='Администратор не найден')
    response_user = UserCreate(
        user_id=admin.user_id,
        role=admin.role,
        is_admin=admin.is_admin
    )
    return response_user


@app.get('/tg_users/admins/', response_model=list[UserGet])
async def get_tg_admins(
    is_admin: int,
    db: AsyncSession = Depends(get_db)
        ):
    stmt = select(TGUser).where(
        TGUser.is_admin == is_admin
    )
    result = await db.execute(stmt)
    admins = result.scalars().all()
    return admins


@app.get('/vk_users/admins/{user_id}', response_model=UserGet)
async def get_vk_admin(
    user_id: int,
    db: AsyncSession = Depends(get_db)
        ):
    stmt = select(VKUser).where(
        VKUser.user_id == user_id,
        VKUser.is_admin == 1
    )
    result = await db.execute(stmt)
    admin = result.scalar_one_or_none()
    if admin is None:
        raise HTTPException(status_code=404, detail='Администратор не найден')
    response_user = UserCreate(
        user_id=admin.user_id,
        role=admin.role,
        is_admin=admin.is_admin
    )
    return response_user


@app.get('/links/{file_path}')
async def get_links_from_file_path(
    file_path: str,
    db: AsyncSession = Depends(get_db)
        ):
    result = await db.execute(select(Link).where(Link.file_path == file_path))
    links = result.scalars().all()
    return links


@app.get('/tg_users/{user_id}', response_model=UserGet)
async def get_tg_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TGUser).where(TGUser.user_id == user_id)
    )
    tg_user_data = result.scalar_one_or_none()
    if tg_user_data is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    response_tg_user = UserGet(
        user_id=tg_user_data.user_id,
        role=tg_user_data.role,
        is_admin=tg_user_data.is_admin
    )
    return response_tg_user


@app.get('/vk_users/{user_id}', response_model=UserGet)
async def get_vk_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(VKUser).where(VKUser.user_id == user_id)
    )
    vk_user_data = result.scalar_one_or_none()
    if vk_user_data is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    response_vk_user = UserGet(
        user_id=vk_user_data.user_id,
        role=vk_user_data.role,
        is_admin=vk_user_data.is_admin
    )
    return response_vk_user


@app.get('/links/{link_id}')
async def get_link(link_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Link).where(Link.link_id == link_id))
    link = result.scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=404, detail='Ссылка не найдена')
    return link


@app.get('/promocodes/{promocode}')
async def get_promocode_filepath(
    promocode: str, db: AsyncSession = Depends(get_db)
        ):
    result = await db.execute(select(PromoCode.file_path).where(
        PromoCode.promocode == promocode
        )
    )
    promocode_data = result.scalar_one_or_none()
    if promocode_data is None:
        raise HTTPException(status_code=404, detail='Промокод не найден')
    return promocode_data


@app.delete(
    '/links/{link_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_link(
    link_id: int,
    db: AsyncSession = Depends(get_db)
        ):
    stmt = delete(Link).where(
        Link.link_id == link_id
    )
    try:
        result = await db.execute(stmt)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail='Ссылка не найдена')
    except NoResultFound:
        raise HTTPException(status_code=404, detail='Ссылка не найдена')
    return


@app.delete(
    '/promocodes/{promocode_id}',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete_promocode(
    promocode_id: int,
    db: AsyncSession = Depends(get_db)
        ):
    stmt = delete(PromoCode).where(
        PromoCode.link_id == promocode_id
    )
    try:
        result = await db.execute(stmt)
        await db.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail='Промокод не найдена')
    except NoResultFound:
        raise HTTPException(status_code=404, detail='Промокод не найдена')
    return


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

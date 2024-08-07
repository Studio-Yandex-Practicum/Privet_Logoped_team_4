import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from models import (Base, Link, PromoCode, RoleType, TGUser, VKUser,
                    async_session, engine)
from schemas import (LinkCreate, PromocodeCreate, PromocodeGetFilepath,
                     UserCreate, UserGet)
from sqlalchemy import delete, select
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
        )
    result = await db.execute(stmt)
    await db.commit()
    new_link = result.fetchone()
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
        )
    result = await db.execute(stmt)
    await db.commit()
    new_promocode = result.fetchone()
    response_promocode = PromocodeCreate(
        promocode=new_promocode.promocode,
        file_path=new_promocode.file_path
    )
    return response_promocode


@app.delete('/links/{link_id}')
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


@app.delete('/promocodes/{promocode_id}')
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


@app.get('/tg_users/')
async def get_tg_users(
    skip: int = 0, limit: int = 10,
    db: AsyncSession = Depends(get_db)
        ):
    result = await db.execute(select(TGUser).offset(skip).limit(limit))
    tg_users = result.scalars().all()
    return tg_users


@app.get('/vk_users/')
async def get_vk_users(
    skip: int = 0, limit: int = 10,
    db: AsyncSession = Depends(get_db)
        ):
    result = await db.execute(select(VKUser).offset(skip).limit(limit))
    vk_users = result.scalars().all()
    return vk_users


@app.get('/links/')
async def get_links(
    skip: int = 0, limit: int = 10,
    db: AsyncSession = Depends(get_db)
        ):
    result = await db.execute(select(Link).offset(skip).limit(limit))
    links = result.scalars().all()
    return links


@app.get('/promocodes/')
async def get_promocodes(
    skip: int = 0, limit: int = 10,
    db: AsyncSession = Depends(get_db)
        ):
    result = await db.execute(select(PromoCode).offset(skip).limit(limit))
    promocodes = result.scalars().all()
    return promocodes


@app.get('/tg_users/{user_id}', response_model=UserGet)
async def get_tg_user(tg_user: UserGet, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(TGUser).where(
            TGUser.user_id == tg_user.user_id,
            TGUser.is_admin == tg_user.is_admin
        ).returning(
            TGUser.user_id,
            TGUser.role,
            TGUser.ia_admin
        )
    )
    tg_user_data = result.fetchone()
    if tg_user_data is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    response_tg_user = UserGet(
        user_id=tg_user_data.user_id,
        role=tg_user_data.role,
        ia_admin=tg_user_data.ia_admin
    )
    return response_tg_user


@app.get('/vk_users/{user_id}', response_model=UserGet)
async def get_vk_user(vk_user: UserGet, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(VKUser).where(
            VKUser.user_id == vk_user.user_id,
            VKUser.is_admin == vk_user.is_admin
        ).returning(
            VKUser.user_id,
            VKUser.role,
            VKUser.ia_admin
        )
    )
    vk_user_data = result.fetchone()
    if vk_user_data is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    response_vk_user = UserGet(
        user_id=vk_user_data.user_id,
        role=vk_user_data.role,
        ia_admin=vk_user_data.ia_admin
    )
    return response_vk_user


@app.get('/links/{link_id}')
async def get_link(link_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Link).where(Link.link_id == link_id))
    link = result.scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=404, detail='Ссылка не найден')
    return link


@app.get('/promocodes/{promocode}', response_model=PromocodeGetFilepath)
async def get_promocode_filepath(
    promocode: str, db: AsyncSession = Depends(get_db)
        ):
    result = await db.execute(select(PromoCode.file_path).where(
        PromoCode.promocode == promocode.promocode
        ).returning(
            PromoCode.promocode_id,
            PromoCode.promocode,
            PromoCode.file_path
        )
    )
    promocode_data = result.fetchone()
    if promocode_data is None:
        raise HTTPException(status_code=404, detail='Промокод не найден')
    response_promocode = PromocodeGetFilepath(
        promocode_id=promocode_data.promocode_id,
        promocode=promocode_data.promocode,
        file_path=promocode_data.file_path
    )
    return response_promocode


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

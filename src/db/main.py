import uvicorn
from fastapi import Depends, FastAPI, HTTPException
from models import (Base, Link, PromoCode, RoleType, TGUser, VKUser,
                    async_session, engine)
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
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


@app.post('/tg_users/')
async def create_tg_user(
    user_id: int, role: str, is_admin: int = 0,
    db: AsyncSession = Depends(get_db)
        ):
    if role == 'parent':
        role = RoleType.PARENT
    else:
        role = RoleType.SPEECH_THERAPIST
    new_tg_user = insert(TGUser).values(
        user_id=user_id, role=role, is_admin=is_admin).on_conflict_do_update(
        constraint=TGUser.__table__.primary_key,
        set_={TGUser.role: role}
    )
    await db.execute(new_tg_user)
    await db.commit()
    await db.refresh(new_tg_user)
    return new_tg_user


@app.post('/vk_users/')
async def create_vk_user(
    user_id: int, role: str, is_admin: int = 0,
    db: AsyncSession = Depends(get_db)
        ):
    new_vk_user = insert(VKUser).values(
        user_id=user_id, role=role, is_admin=is_admin).on_conflict_do_update(
        constraint=VKUser.__table__.primary_key,
        set_={VKUser.role: role}
    )
    await db.execute(new_vk_user)
    await db.commit()
    await db.refresh(new_vk_user)
    return new_vk_user


@app.post('/links/')
async def create_link(
    link: str, link_name: str, link_type: str, to_role: str = None,
    db: AsyncSession = Depends(get_db)
        ):
    new_link = Link(
        link=link, link_name=link_name,
        link_type=link_type, to_role=to_role
    )
    db.add(new_link)
    await db.commit()
    await db.refresh(new_link)
    return new_link


@app.post('/promocodes/')
async def create_promocode(
    promocode: str, file_path: str,
    db: AsyncSession = Depends(get_db)
        ):
    new_promocode = PromoCode(promocode=promocode, file_path=file_path)
    db.add(new_promocode)
    await db.commit()
    await db.refresh(new_promocode)
    return new_promocode


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


@app.get('/tg_users/{user_id}')
async def get_tg_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TGUser).where(TGUser.user_id == user_id))
    tg_user = result.scalar_one_or_none()
    if tg_user is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    return tg_user


@app.get('/vk_users/{user_id}')
async def get_vk_user(user_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(VKUser).where(VKUser.user_id == user_id))
    vk_user = result.scalar_one_or_none()
    if vk_user is None:
        raise HTTPException(status_code=404, detail='Пользователь не найден')
    return vk_user


@app.get('/links/{link_id}')
async def get_link(link_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Link).where(Link.link_id == link_id))
    link = result.scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=404, detail='Ссылка не найден')
    return link


@app.get('/promocodes/{promocode}')
async def get_promocode(promocode: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(PromoCode).where(
        PromoCode.promocode == promocode))
    promocode_data = result.scalar_one_or_none()
    if promocode_data is None:
        raise HTTPException(status_code=404, detail='Промокод не найден')
    return promocode_data.file_path


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

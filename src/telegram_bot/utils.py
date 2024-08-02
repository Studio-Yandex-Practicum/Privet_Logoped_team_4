from db.models import Link, LinkType
from db.main import async_session


async def add_file(file_path: str, file_name: str):
    async with async_session() as session:
        new_file = Link(
            link=file_path,
            link_name=file_name,
            link_type=LinkType.FILEPATH
        )
        session.add(new_file)
        await session.commit()

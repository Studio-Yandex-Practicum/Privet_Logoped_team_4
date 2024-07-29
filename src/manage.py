import argparse
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


DATABASE_URL = 'sqlite:///admins.db'
engine = create_engine(DATABASE_URL)
Base = declarative_base()

class Admin(Base):
    __tablename__ = 'admins'

    id = Column(Integer, primary_key=True)
    platform = Column(String, nullable=False)

def init_db():
    Base.metadata.create_all(engine)

def add_admin(platform, user_id):
    Session = sessionmaker(bind=engine)
    session = Session()
    new_admin = Admin(id=user_id, platform=platform)
    session.add(new_admin)
    session.commit()
    session.close()
    print(f'Пользователь с ID {user_id} на платформе {platform} назначен администратором.')

def main():
    init_db()

    parser = argparse.ArgumentParser(description='Командный интерфейс для управления ботом')
    subparsers = parser.add_subparsers(dest='command')

    admin_parser = subparsers.add_parser('admin')
    admin_parser.add_argument('platform', choices=['telegram', 'vk'])
    admin_parser.add_argument('user_id', type=int,)

    args = parser.parse_args()

    if args.command == 'admin':
        add_admin(args.platform, args.user_id)
    else:
        print('Неизвестная команда.')

if __name__ == '__main__':
    main()

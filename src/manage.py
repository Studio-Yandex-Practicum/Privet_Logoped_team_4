import argparse
import sqlite3

def init_db():
    connection = sqlite3.connect('admins.db')
    cursor = connection.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY,
            platform TEXT NOT NULL
        )
    ''')
    connection.commit()
    connection.close()

def add_admin(platform, user_id):
    connection = sqlite3.connect('admins.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO admins (id, platform) VALUES (?, ?)', (user_id, platform))
    connection.commit()
    connection.close()
    print(f"Пользователь с ID {user_id} на платформе {platform} назначен администратором.")

def main():
    init_db()

    parser = argparse.ArgumentParser(description="Командный интерфейс для управления ботом")
    subparsers = parser.add_subparsers(dest="command")

    admin_parser = subparsers.add_parser("admin")
    admin_parser.add_argument("platform", choices=["telegram", "vk"], help="Платформа для назначения администратора")
    admin_parser.add_argument("user_id", type=int, help="ID пользователя, которого нужно назначить администратором")

    args = parser.parse_args()

    if args.command == "admin":
        add_admin(args.platform, args.user_id)
    else:
        print("Неизвестная команда.")

if __name__ == '__main__':
    main()

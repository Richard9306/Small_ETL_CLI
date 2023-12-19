import argparse
from collections import defaultdict
from pathlib import Path

from database_manager import DatabaseManager


class UserCommands(DatabaseManager):
    def __init__(self, login, password):
        super().__init__()
        self.login = login
        self.password = password

    def connect_db(self):
        super().connect_db()

    def login_into_db(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT individual_id, role FROM individuals WHERE ( email = ? OR telephone_number = ?) AND password = ?",
                (self.login, self.login, self.password),
            )
            user_info = cursor.fetchall()
            if user_info:
                user_info = user_info[0]
                return user_info[0], cursor, user_info[1]
            else:
                print("Invalid Login")
                self.close_connection()
                exit(0)
        except Exception as e:
            print(f"An error occured while trying to log in: {e}")
            raise

    def print_children(self):
        try:
            user_id, cursor, _ = self.login_into_db()
            user_id = str(user_id)
            cursor.execute(
                "SELECT name, age FROM children WHERE individual_id = ?", (user_id,)
            )
            children = cursor.fetchall()
            if children:
                print("Your children:")
                print("Name | age")
                children.sort()
                for child in children:
                    print(f"{child[0]}, {child[1]}")
            else:
                print("You don't have children.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def find_similar_children_by_age(self):
        try:
            user_id, cursor, _ = self.login_into_db()
            cursor.execute(
                "SELECT name, age FROM children WHERE individual_id = ?", (user_id,)
            )
            user_children = cursor.fetchall()
            if user_children:
                query = """
                SELECT 
                i.firstname,
                i.telephone_number,
                c.name,
                c.age
                FROM 
                individuals i
                INNER JOIN children c ON i.individual_id = c.individual_id
                WHERE
                i.individual_id != ? AND c.age = ?
                ORDER BY
                c.name
                """
                all_matching_users = []
                for child in user_children:
                    cursor.execute(query, (user_id, child[1]))
                    matching_users = cursor.fetchall()
                    all_matching_users.extend(matching_users)
                if all_matching_users:
                    all_children_of_user = defaultdict(list)
                    for matching_user in all_matching_users:
                        all_children_of_user[
                            (matching_user[0], matching_user[1])
                        ].append((matching_user[2], matching_user[3]))
                    print("Firstname | telephone number | children")
                    for key, value in all_children_of_user.items():
                        value.sort()
                        join_children = "; ".join(
                            [f"{name}, {age}" for name, age in value]
                        )
                        print(f"{key[0]}, {key[1]}: {join_children}")
                else:
                    print("No match.")
            else:
                print("You don't have children.")
        except Exception as e:
            print(f"An error occurred: {e}")

    def close_connection(self):
        super().close_connection()


class AdminCommands(UserCommands):
    def __init__(self, login, password):
        super().__init__(login, password)

    def login_into_db(self):
        return super().login_into_db()

    def print_all_accounts(self):
        try:
            _, cursor, role = self.login_into_db()
            if role == "admin":
                cursor.execute("SELECT COUNT(*) FROM individuals")
                total_accounts = cursor.fetchone()[0]
                print(total_accounts)
            else:
                print("Access denied. You don't have permissions.")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    def print_oldest_account(self):
        try:
            _, cursor, role = self.login_into_db()
            if role == "admin":
                cursor.execute(
                    "SELECT firstname, email, created_at FROM individuals ORDER BY created_at LIMIT 1"
                )
                oldest_account = cursor.fetchall()[0]
                print(f"name: {oldest_account[0]}")
                print(f"email_address: {oldest_account[1]}")
                print(f"created_at: {oldest_account[2]}")
            else:
                print("Access denied. You don't have permissions.")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise

    def group_children_by_age(self):
        try:
            _, cursor, role = self.login_into_db()
            if role == "admin":
                cursor.execute(
                    "SELECT age, COUNT(age) as count FROM children GROUP BY age ORDER BY count"
                )
                amount_children_by_age = cursor.fetchall()
                print(amount_children_by_age)
                for age, count in amount_children_by_age:
                    print(f"age: {age}, count: {count}")
            else:
                print("Access denied. You don't have permissions.")
        except Exception as e:
            print(f"An error occurred: {e}")
            raise


def execute_commands(args, json_path, csv_path, xml_path):
    user = None
    admin = None
    manager = None
    try:
        if args.command == "print-children":
            user = UserCommands(args.login, args.password)
            user.connect_db()
            user.print_children()
        elif args.command == "find-similar-children-by-age":
            user = UserCommands(args.login, args.password)
            user.connect_db()
            user.find_similar_children_by_age()
        elif args.command == "print-all-accounts":
            admin = AdminCommands(args.login, args.password)
            admin.connect_db()
            admin.print_all_accounts()
        elif args.command == "print-oldest-account":
            admin = AdminCommands(args.login, args.password)
            admin.connect_db()
            admin.print_oldest_account()
        elif args.command == "group-by-age":
            admin = AdminCommands(args.login, args.password)
            admin.connect_db()
            admin.group_children_by_age()
        elif args.command == "create_database":
            manager = DatabaseManager()
            manager.connect_db()
            manager.create_database()
            manager.load_data(json_path, csv_path, xml_path)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if user is not None:
            user.close_connection()
        if admin is not None:
            admin.close_connection()
        if manager is not None:
            manager.close_connection()


def parse_args():
    COMMANDS = [
        "print-children",
        "find-similar-children-by-age",
        "print-all-accounts",
        "print-oldest-account",
        "group-by-age",
        "create_database",
    ]
    parser = argparse.ArgumentParser(description="Recruitment Task")
    parser.add_argument("command", choices=COMMANDS, help="Available commands")
    parser.add_argument("--login", help="User login")
    parser.add_argument("--password", help="User password")
    args = parser.parse_args()
    if args.command != "create_database" and (
        args.login is None or args.password is None
    ):
        parser.error("Login and password are required for the specified command")
    return args


if __name__ == "__main__":
    json_path = Path("../files_to_load/test_data_json.json")
    csv_path = Path("../files_to_load/data_csv.csv")
    xml_path = Path("../files_to_load/data_xml.xml")
    execute_commands(parse_args(), json_path, csv_path, xml_path)

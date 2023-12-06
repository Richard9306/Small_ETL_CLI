import argparse
from collections import defaultdict
from database_manager import DatabaseManager
class UserCommands(DatabaseManager):

    def __init__(self, login, password):
        super().__init__()
        self.login = login
        self.password = password

    def connect_db(self):
        super().connect_db()

    def execute_commands(self, args):
        if args.command == "print-children":
            self.print_children()
        elif args.command == "find-similar-children-by-age":
            self.find_similar_children_by_age()
        else:
            print("Unknown command.")

    def login_into_db(self):
        try:
            cursor = self.conn.cursor()
            cursor.execute("SELECT individual_id, role FROM individuals WHERE ( email = ? OR telephone_number = ?) AND password = ?",
                           (self.login, self.login, self.password))
            user_info = cursor.fetchall()
            user_info = user_info[0]
            if user_info:
                return user_info[0], cursor, user_info[1]
            else:
                print("Wrong credentials.")
        except Exception as e:
            print(f"Error was occured while trying to log in: {e}")
            exit(1)

    def print_children(self):
        user_id, cursor, role = self.login_into_db()
        user_id = str(user_id)
        cursor.execute("SELECT name, age FROM children WHERE individual_id = ?", (user_id,))
        children = cursor.fetchall()
        if children:
            print("UserCommands's children:")
            for child in children:
                print(f"{child[0]}, {child[1]}")
        else:
            print("UserCommands doesn't have children.")

    def find_similar_children_by_age(self):
        user_id, cursor, role = self.login_into_db()
        cursor.execute("SELECT name, age FROM children WHERE individual_id = ?", (user_id,))
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
                    all_children_of_user[(matching_user[0], matching_user[1])].append((matching_user[2], matching_user[3]))
                for key, value in all_children_of_user.items():
                    join_children = "; ".join([f"{name}, {age}" for name, age in value])

                    print(f"{key[0]}, {key[1]}: {join_children}")
            else:
                print("No match.")
        else:
            print("You don't have children.")
    def close_connection(self):
        super().close_connection()
class AdminCommands(UserCommands):
    def __init__(self, login, password):
        super().__init__(login, password)




def parse_args():
    pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Recruitment Task")
    parser.add_argument("command", choices=["print-children", "find-similar-children-by-age"], help="Available commands")
    parser.add_argument("--login", required=True, help="UserCommands login")
    parser.add_argument("--password", required=True, help="UserCommands password")
    args = parser.parse_args()
    user = UserCommands(args.login, args.password)
    user.connect_db()
    user.execute_commands(args)
    user.close_connection()
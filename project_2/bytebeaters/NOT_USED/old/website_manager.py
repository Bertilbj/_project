import sqlite3

db_name = "attendance_db.sqlite3"


class LoginOld:

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.user_type = None

    def set_user_type(self, usr):
        self.user_type = usr

    def authenticate(self):
        with sqlite3.connect(db_name) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Credentials WHERE Username=? AND Password=?",
                        (self.username, self.password))
            result = cur.fetchone()
            if result != None:
                return result[0]
            else:
                return None

    def create_user(self):
        with sqlite3.connect(db_name) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Credentials (User_Type, Username, Password) VALUES (?, ?,?)",
                        (self.user_type, self.username, self.password,))
            conn.commit()


# admin_user = Login("admin","admin")
# teacher_user = Login("SKO","Sten")
# student_user = Login("Bertil","nemkode123")
# admin_user.set_user_type("Admin")
# teacher_user.set_user_type("Teacher")
# student_user.set_user_type("Student")

# # # print(admin_user.authenticate())
# # hey = Login("Hey","Kode")
# # hey.set_user_type("Admin")
# # hey.create_user()
# admin_user.create_user()
# teacher_user.create_user()
# student_user.create_user()

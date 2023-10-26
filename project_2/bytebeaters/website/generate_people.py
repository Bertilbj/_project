"""
Program der kan køres for at generere studerende og kort i databasen til test.
"""

import random

import names
from class_manager import Card, Student, Terminal
from connect_to_mysql import open_db

db = 'timelogging'
# ## CARDS ##
# for _ in range(25):
#     Card(random.randint(100000000000,999999999999))

# # STUDENTS ##
# for _ in range(25):
#     Student(names.get_first_name(),names.get_last_name(),1,Card.get_available_cards()[0]).register_student()

with open_db(db) as conn:
    cur = conn.cursor()
    for _ in range(500):
        cur.execute("INSERT INTO Attendances (teacher_id, student_id, team_id, date, time) VALUES (1000, %s, 1, %s, '08:00:00')",
                    (Student.get_all_ids()[random.randint(0, len(Student.get_all_ids())-1)], f"2023/0{random.randint(1,5)}/{random.randint(10,30)}"))
    conn.commit()

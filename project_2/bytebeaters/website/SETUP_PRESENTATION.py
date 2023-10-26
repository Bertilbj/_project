"""
Program til nulstille databasen og oprette tabellerne igen.
Der også Nogle få Students, Teams, Terminals, en Teacher og Admin til test.
Når programmet køres tester også et par funktioner fra 'class_manager.py'
"""
import time

from class_manager import Admin, Student, Teacher, Terminal
from connect_to_mysql import open_db

if __name__ == "__main__":
    # Logger tiden for at se hvor lang tid det tager at køre programmet
    start = time.perf_counter()

    db = 'timelogging'

    with open_db(db) as conn:
        cur = conn.cursor()
        # Sletter alle tabellerne hvis de eksisterer. Dette er for at nulstille databasen.
        cur.execute("DROP TABLE IF EXISTS Attendances")
        cur.execute("DROP TABLE IF EXISTS Terminals")
        cur.execute("DROP TABLE IF EXISTS Cards")
        cur.execute("DROP TABLE IF EXISTS Students")
        cur.execute("DROP TABLE IF EXISTS Teams")
        cur.execute("DROP TABLE IF EXISTS Teachers")
        cur.execute("DROP TABLE IF EXISTS Logins")
        cur.execute("DROP TABLE IF EXISTS Logging")
        # Opretter tabellerne.
        cur.execute(
            "CREATE TABLE Teams (team_id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(48))")
        cur.execute(
            "CREATE TABLE Terminals (terminal_id INT PRIMARY KEY AUTO_INCREMENT, name VARCHAR(128), team_id INT, FOREIGN KEY(team_id) REFERENCES Teams(team_id))")
        cur.execute("CREATE TABLE Students (student_id INT PRIMARY KEY AUTO_INCREMENT, first_name VARCHAR(48), last_name VARCHAR(128), team_id INT, card_id BIGINT, FOREIGN KEY(team_id) REFERENCES Teams(team_id))")
        cur.execute(
            "CREATE TABLE Teachers (teacher_id INT PRIMARY KEY AUTO_INCREMENT, first_name VARCHAR(48), last_name VARCHAR(128), admin BOOLEAN)")
        cur.execute(
            "CREATE TABLE Cards (card_id BIGINT NOT NULL UNIQUE, student_id INT, FOREIGN KEY(student_id) REFERENCES Students(student_id))")
        cur.execute("CREATE TABLE Attendances (attendance_id BIGINT PRIMARY KEY AUTO_INCREMENT, teacher_id INT, terminal_id INT, student_id INT, team_id INT, date VARCHAR(16), time VARCHAR(16), FOREIGN KEY(teacher_id) REFERENCES Teachers(teacher_id), FOREIGN KEY(terminal_id) REFERENCES Terminals(terminal_id), FOREIGN KEY(student_id) REFERENCES Students(student_id), FOREIGN KEY(team_id) REFERENCES Teams(team_id))")
        cur.execute(
            "CREATE TABLE Logins (login_id INT PRIMARY KEY AUTO_INCREMENT, username VARCHAR(32), password VARCHAR(255), type VARCHAR(16), id INT)")
        cur.execute("CREATE TABLE Logging (log_id BIGINT PRIMARY KEY AUTO_INCREMENT, id BIGINT, location VARCHAR(128), who VARCHAR(128), success BOOLEAN, date VARCHAR(16), time VARCHAR(16))")
        # Indsætter en Terminal for at kunne teste funktionerne.
        cur.execute(
            "INSERT INTO Terminals (name, team_id) VALUES ('IT-Lab', NULL)")
        # Opretter nogle Teams med executemany for at prøve denne funktion.
        cur.executemany("INSERT INTO Teams (name) VALUES (%s)",
                        (("ITT22",), ("ITT23",), ("DMA22",), ("DMA23",)))
        # Opretter en test Student, bruges til at sætte student_id start værdi på 2000.
        cur.execute(
            "INSERT INTO Students (first_name, last_name, team_id, card_id) VALUES ('test', 'test', 1, 12345)")
        # Den første Teacher oprettes som en Terminal som workaround til funktioner i projektet.
        cur.execute(
            "INSERT INTO Teachers (first_name, last_name, admin) VALUES ('Terminal', ' ', 1)")
        # ID values på nogle tabeller sættes op så de ikke alle starter på 1.
        cur.execute(
            "UPDATE Students SET student_id = 2000 where first_name = 'test'")
        cur.execute(
            "UPDATE Teachers SET teacher_id = 1000 where first_name = 'Terminal'")
        cur.execute(
            "INSERT INTO Attendances (teacher_id, student_id, team_id, date, time) VALUES (1000, 2000, 1, 'test', 'test')")
        cur.execute(
            "UPDATE Attendances SET attendance_id = 50000 where date = 'test'")
        conn.commit()

    ## Terminals ##
    # Test Terminaler
    Terminal.register_terminal('CSD 3.2.20')
    Terminal.register_terminal('CSD 5.1.42')

    ## Students ##
    # Test Studerende
    Student('Bertil', 'Bertilsen', 1, 275288510832)._register_student()
    # Student('Jeppe', 'Skovlund Petersen', 2, 926357480238)._register_student()
    # Speciel så det er et let test login til website.
    Student('Stu', 'De', 4, 424242424242, "stude")._register_student()

    ## Teacher + Admin ##
    # Test Teacher og Admin, nemme logins til test af website.
    Teacher('Tea', 'Ch', "teach")._register_teacher()
    Admin('Administrator', 'In', "admin")._register_teacher()

    ## Attendance ##
    # Tilføjer nogle for at have data at arbejde med. Bliver også registreret i Logging.
    Teacher.manuel_attendance_register(1001, 2001, 1)
    Teacher.manuel_attendance_register(1001, 2001, 2)
    Teacher.manuel_attendance_register(1002, 2001, 3)
    Teacher.manuel_attendance_register(1002, 2004, 1)
    Teacher.manuel_attendance_register(1001, 2002, 2)
    Teacher.manuel_attendance_register(1002, 2006, 3)
    Teacher.manuel_attendance_register(1001, 2003, 1)
    Teacher.manuel_attendance_register(1002, 2003, 2)
    Teacher.manuel_attendance_register(1002, 2004, 3)

    # Sætter IT-Lab Terminalen til at være tilknyttet ITT23.
    Terminal.set_team(1, 2)
    # Tester om terminalregisterings funktionen virker.
    Terminal.register_attendance(1, 275288510832, 2)
    #Terminal.register_attendance(1, 926357480238, 2)
    with open_db(db) as conn:
        cur = conn.cursor()
        # Sletter test data, var oprettet for at flytte ID værdierne væk fra 1.
        cur.execute("DELETE FROM Attendances WHERE date = 'test'")
        cur.execute("DELETE FROM Students WHERE first_name = 'test'")
        conn.commit()

    # Printer ud hvor lang tid det har taget at oprette databasen.
    print(f"{db.upper()} is now set up!")
    print(f"Time elapsed: {time.perf_counter() - start:.2f}s")

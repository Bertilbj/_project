"""
Program manager der indeholder alle klasser og funktioner til at oprette, ændre og slette data i databasen.
Alle klasser tilhøre også et tabel i databasen.
Alt er skrevet i OOP for at gøre det nemmere at arbejde med uden for dette program.
"""

from datetime import datetime

from connect_to_mysql import hash_password, open_db

db = 'timelogging'


class Student:
    """
    Klassen Student opretter en ny studerende i databasen.
    Denne klasse bruges i forbindelse med mange dele af projektet, da de studerende er opdrejningspunktet for projektet.
    """
    # Hvis der ikke er angivet et kodeord til den studerende, bliver der automatisk genereret et til den studerende.

    def __init__(self, first_name: str, last_name: str, team_id: int, card_id: int, passwd: str = None):

        self.first_name = first_name
        self.last_name = last_name
        self.team_id = team_id
        self.card_id = card_id
        self.passwd = passwd

    def _register_student(self):
        # Opretter en ny studerende i databasen
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO students (first_name, last_name, team_id, card_id) VALUES (%s, %s, %s, %s)",
                        (self.first_name, self.last_name, self.team_id, self.card_id))
            conn.commit()
            cur.execute(
                "SELECT student_id FROM students WHERE card_id = %s", (self.card_id,))
            self._student_id = cur.fetchone()[0]
        # Opretter en ny login til den studerende
        Login(self._student_id, 'student', self.passwd)
        # Opretter eller opdatere kortet i databasen
        Card(self.card_id, student_id=self._student_id)

    def set_name(self, first_name: str, last_name: str):
        # Opdatere navnet på den studerende i databasen
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE Students SET first_name = %s, last_name = %s WHERE student_id = %s", (first_name, last_name, self._student_id,))
            conn.commit()

    @staticmethod
    def get_name(card_id: int):
        # Henter navnet på den studerende ud fra kort ID.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT first_name, last_name FROM Students WHERE card_id = %s", (card_id,))
            # Returnere navnet som en string
            return (" ").join(cur.fetchall()[0])

    @staticmethod
    def get_team(card_id: int):
        # Henter holdet den studerende er på ud fra kort ID.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT Teams.name FROM Students INNER JOIN Teams ON Students.team_id = Teams.team_id WHERE card_id = %s", (card_id,))
            return cur.fetchall()[0][0]

    @staticmethod
    def get_id(card_id: int):
        # Henter student ID ud fra kort ID.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT student_id FROM Students WHERE card_id = %s", (card_id,))
            return cur.fetchall()[0][0]

    @staticmethod
    def my_overview(student_id: int):
        # Henter alle gange en studerende har været til undervisning.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("""
                SELECT students.first_name, students.last_name, students.student_id, attendances.date, attendances.time FROM students
                INNER JOIN attendances ON students.student_id = attendances.student_id WHERE students.student_id= %s
                """,
                        (student_id,))
            # Returnere en liste med alle de gange den studerende har været til undervisning via list comprehension.
            return [student_data for student_data in cur.fetchall()]

    @staticmethod
    def get_all_ids():
        # Henter alle student ID'er fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT student_id FROM Students")
            # Returnere en liste med alle student ID'er via list comprehension.
            return [student_id[0] for student_id in cur.fetchall()]

    @staticmethod
    def get_card_ids():
        # Henter alle kort ID'er fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT card_id FROM Students")
            # Returnere en liste med alle kort ID'er via list comprehension.
            return [card_id[0] for card_id in cur.fetchall()]


class Teacher:
    """
    Klassen Teacher opretter en ny lærer i databasen.
    """
    # Hvis der ikke er angivet et kodeord til læreren, bliver der automatisk genereret et til læreren.

    def __init__(self, first_name: str, last_name: str, passwd: str = None):
        self.first_name = first_name
        self.last_name = last_name
        self.passwd = passwd

    def _register_teacher(self):
        # Opretter en ny lærer i databasen
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Teachers (first_name, last_name, admin) VALUES (%s, %s, %s)",
                        (self.first_name, self.last_name, 0))
            conn.commit()
            cur.execute(
                "SELECT teacher_id FROM Teachers ORDER BY teacher_id DESC LIMIT 1")
            self._teacher_id = cur.fetchone()[0]
        # Opretter et ny login til læreren
        Login(self._teacher_id, "teacher", self.passwd)

    def set_name(self, first_name: str, last_name: str):
        # Opdatere navnet på læreren i databasen
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE Teachers SET first_name = %s, last_name = %s WHERE teacher_id = %s", (first_name, last_name, self._teacher_id,))
            conn.commit()

    @staticmethod
    def view_all_students():
        # Henter alle studerende fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT Students.student_id, Students.first_name, Students.last_name, Teams.name, Students.card_id FROM Students INNER JOIN Teams ON Students.team_id = Teams.team_id")
            info = cur.fetchall()
            # Returnere en liste med alle studerende via list comprehension.
            return [student_data for student_data in info]

    @staticmethod
    def manuel_attendance_register(teacher_id: int, student_id: int, team_id: int, date: str = None, time: str = None):
        # Manuel tilføjelse af en studerende til undervisning via website.
        # Underviseren kan selv vælge dato og tidspunkt, hvis der ikke er angivet nogen, bliver det automatisk sat til nuværende dato og tidspunkt.
        if date == None:
            date = datetime.now().strftime("%d/%m/%Y")
        if time == None:
            time = datetime.now().strftime("%H:%M")
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM Students WHERE student_id = %s", (student_id,))
            exist = cur.fetchone()
            if exist:
                cur.execute("INSERT into Attendances (teacher_id, student_id, team_id, date, time) VALUES (%s, %s, %s, %s, %s)",
                            (teacher_id, student_id, team_id, date, time,))
                conn.commit()
                # Logger tilføjelsen af en studerende til undervisning så man kan se hvilken underviser der har lavet tilføjelsen. Terminal bruges da det er en manuel tilføjelse.
                Logging.success_login_terminal(
                    student_id, "Website", teacher_id)
            else:
                # Logger fejlen så man kan se hvilken underviser der forsøgte at tilføje en studerende der ikke eksisterer. Terminal bruges da det er en manuel tilføjelse.
                Logging.failed_login_terminal(
                    student_id, "Website", teacher_id)

    @staticmethod
    def show_all_attendance():
        # Henter alle studerende der har været til undervisning fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT Attendances.attendance_id, Attendances.student_id, Students.first_name, Students.last_name, Teams.name, Students.card_id, Attendances.date, Attendances.time FROM Attendances INNER JOIN Students ON Attendances.student_id = Students.student_id INNER JOIN Teams ON Attendances.team_id = Teams.team_id")
            info = cur.fetchall()
            # Returnere en liste med alle studerende der har været til undervisning via list comprehension.
            return [attendance_data for attendance_data in info]


class Admin(Teacher):
    """
    Klassen Admin opretter en ny admin i databasen. Den nedarver fra klassen Teacher.
    En administrator i dette projekt er en lærer der har adgang til at oprette, ændre og slette på hjemmesiden.
    Det er både studerende, terminaler og hold.
    Når en Admin oprettes er den eneste forskel fra en lærer at admin BOOLEAN er sat til 1 (True).
    """

    def _register_teacher(self):
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Teachers (first_name, last_name, admin) VALUES (%s, %s, %s)",
                        (self.first_name, self.last_name, 1))
            conn.commit()
            cur.execute(
                "SELECT teacher_id FROM Teachers ORDER BY teacher_id DESC LIMIT 1")
            self.teacher_id = cur.fetchone()[0]
        # Opretter en ny login til administatoren.
        Login(self.teacher_id, "admin", self.passwd)

    @staticmethod
    def _delete_student(student_id):
        # Sletter en studerende fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM Logins WHERE id = %s", (student_id,))
            cur.execute(
                "DELETE FROM Attendances WHERE student_id = %s", (student_id,))
            cur.execute(
                "UPDATE Cards SET student_id = NULL WHERE student_id = %s", (student_id,))
            cur.execute(
                "DELETE FROM Students WHERE student_id = %s", (student_id,))
            conn.commit()


class Terminal:
    """
    Terminaler i dette projektet er de enheder som står ved klasselokalet og registrerer eleverne når de kommer ind i klasselokalet.
    Terminaler kan være en Raspberry Pi, en Arduino eller en anden enhed som kan læse RFID kort.
    Dette er en statisk klasse.
    """
    def register_terminal(name: str, team_id: int = None):
        # Registrerer en terminal i databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            # Hvis navnet ikke eksisterer i databasen, så oprettes terminalen.
            if name not in Terminal.get_all_names():
                cur.execute(
                    "INSERT INTO Terminals (name, team_id) VALUES (%s, %s)", (name, team_id,))
                conn.commit()
            # Hvis navnet findes bliver team updated.
            else:
                cur.execute(
                    "UPDATE Terminals SET team_id = %s WHERE name = %s", (team_id, name,))
                conn.commit()

    def get_id(name: str):
        # Henter terminal_id fra databasen ud fra terminalens navn.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT terminal_id FROM Terminals WHERE name = %s", (name,))
            return cur.fetchone()[0]

    def get_name(terminal_id: int):
        # Henter terminalens navn fra databasen ud fra terminalens terminal_id.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT name FROM Terminals WHERE terminal_id = %s", (terminal_id,))
            return cur.fetchone()[0]

    def set_name(new_name: str, terminal_id: int):
        # Ændrer terminalens navn i databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE Terminals SET name = %s WHERE terminal_id = %s", (new_name, terminal_id,))
            conn.commit()

    def set_team(terminal_id: int, team_id: int = None):
        # Ændrer terminalens team i databasen efter det er blevet registeret.
        with open_db(db) as conn:
            cur = conn.cursor()
            # Hvis intet team er givet, så fjernes team fra terminalen.
            if team_id == None:
                cur.execute(
                    "UPDATE Terminals SET team_id = NULL WHERE terminal_id = %s", (terminal_id,))
                conn.commit()
            # Hvis team er givet, så bliver team opdateret i databasen.
            else:
                cur.execute(
                    "UPDATE Terminals SET team_id = %s WHERE terminal_id = %s", (team_id, terminal_id,))
                conn.commit()
                
    def get_team(terminal_id: int):
        # Henter team_id fra databasen ud fra terminalens terminal_id.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT team_id FROM Terminals WHERE terminal_id = %s", (terminal_id,))
            return cur.fetchone()[0]

    def get_all_names():
        # Henter navnene på alle terminaler fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM Terminals")
            terms = [terminal_data[0] for terminal_data in cur.fetchall()]
        return terms

    def get_all_info():
        # Henter alle terminaler som er tilknyttet et team i databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT Terminals.name, Teams.name FROM Terminals INNER JOIN Teams ON Terminals.team_id = Teams.team_id")
            terms = [terminal_data for terminal_data in cur.fetchall()]
        return terms

    def register_attendance(terminal_id: int, card_id: int, team_id: int):
        # Registrerer en elevs fremmøde i databasen fra en terminal.
        date = datetime.now().strftime("%d/%m/%Y")
        time = datetime.now().strftime("%H:%M")
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT student_id FROM Students WHERE card_id = %s", (card_id,))
            student_id = cur.fetchone()[0]
            cur.execute(
                "INSERT INTO Attendances (terminal_id, student_id, team_id, date, time) VALUES (%s, %s, %s, %s, %s)", (terminal_id, student_id, team_id, date, time,))
            conn.commit()

    def delete_terminal(terminal_id: int):
        # Sletter en terminal fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM Terminals WHERE terminal_id = %s", (terminal_id,))
            conn.commit()


class Team:
    """
    Teams er de hold som eleverne er inddelt i.
    Dette er en statisk klasse. Man gemmer ikke på instanser og genbruger dem i vores projekt.
    """
    def register_team(name: str):
        # Registrerer et hold i databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO Teams (name) VALUES (%s)", (name,))
            conn.commit()

    def set_name(team_id: int, new_name: str):
        # Ændrer navnet på et hold i databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "UPDATE Teams SET name = %s WHERE team_id = %s", (new_name, team_id,))
            conn.commit()

    def get_all_teams():
        # Henter navnene på alle hold fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT name FROM Teams")
            return [team_data[0] for team_data in cur.fetchall()]

    def get_specific_team(student_id: int = None, team_name: str = None):
        # Henter et bestemt hold, skal enten en Students ID eller et holdnavn.
        with open_db(db) as conn:
            cur = conn.cursor()
            if student_id is not None:
                cur.execute(
                    "SELECT teams.team_id FROM students INNER JOIN teams ON students.team_id = teams.team_id WHERE students.student_id = %s",
                    (student_id,))
                return int(cur.fetchone()[0])

            elif team_name is not None:
                cur.execute(
                    "SELECT team_id FROM teams WHERE name = %s",
                    (team_name,))
                return int(cur.fetchone()[0])

    def delete_team(team_id: int):
        # Sletter et hold fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "DELETE FROM Teams WHERE team_id = %s", (team_id,))
            conn.commit()


class Login:
    """
    Denne klasse er til login på på website. Den opretter username og password til brugeren.
    Den tjekker også om et login forsøg er korrekt.
    """

    def __init__(self, id: int, type: str, passwd: str = None):
        self.id = id
        self.type = type
        # Hvis der ikke er angivet et password, så genereres et.
        if passwd == None:
            self._create_passwd()
        else:
            self.passwd = passwd
        self.username = self._create_username()
        # Når en instans af Login oprettes, så bliver den også registreret i databasen.
        self._register_login()

    def _create_passwd(self):
        # Genererer et password til brugeren.
        with open_db(db) as conn:
            # Admins er gemt i Teacher tabellen, og vi skal bruge teacher_id til at finde navn.
            if self.type == "admin":
                type = "teacher"
            else:
                type = self.type
            cur = conn.cursor()
            # Henter fornavn og efternavn fra databasen. fra Students eller Teachers.
            cur.execute(
                f"SELECT first_name, last_name FROM {type}s WHERE {type}_id = %s", (self.id,))
            # i stedet for cur.fetchone()[0] og cur.fetchone()[1] kan skrive begge variabler før '=' adskildt af komma.
            first, last = cur.fetchone()
        # Passwordet bliver sat til de to første bogstaver i fornavn og efternavn, efterfulgt af et 1-tal. Første bogstav gøres stort.
        self.passwd = f"{first[:2]}{last[:2]}1".capitalize()

    def _create_username(self):
        # Genererer et brugernavn til brugeren.
        with open_db(db) as conn:
            # Admins er gemt i Teacher tabellen, og vi skal bruge teacher_id til at finde navn.
            if self.type == "admin":
                type = "teacher"
            else:
                type = self.type
            cur = conn.cursor()
            # Henter fornavn og efternavn fra databasen. fra Students eller Teachers.
            cur.execute(
                f"SELECT first_name, last_name FROM {type}s WHERE {type}_id = %s", (self.id,))
            # i stedet for cur.fetchone()[0] og cur.fetchone()[1] kan skrive begge variabler før '=' adskildt af komma.
            first, last = cur.fetchone()
            # Brugernavnet bliver sat til de tre første bogstaver i fornavn og de to første bogstaver i efternavn. Gemmes i småt.
            username = f"{first[:3]}{last[:2]}".lower()
        if username in self.get_all_usernames():
            for i in range(len(self.get_all_usernames())):
                username = f"{username}{i+1}"
                if username not in self.get_all_usernames():
                    return username
        else:
            return username

    def _register_login(self):
        # Registrerer login i databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            # Passwordet bliver krypteret før det gemmes i databasen.
            cur.execute("INSERT INTO Logins (username, password, type, id) VALUES (%s, %s, %s, %s)",
                        (self.username, hash_password(self.passwd), self.type.capitalize(), self.id,))
            conn.commit()
            cur.execute(
                "SELECT login_id FROM Logins WHERE id = %s", (self.id,))
            self.login_id = cur.fetchone()[0]

    @staticmethod
    def get_all_usernames():
        # Henter alle brugernavne fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT username FROM Logins")
            usernames = [username[0] for username in cur.fetchall()]
        return usernames

    @staticmethod
    def authenticate(username: str, password: str):
        # Tjekker om et login forsøg via website er korrekt.
        # Try og except er til hvis der ikke er nogen bruger med det brugernavn.
        try:
            with open_db(db) as conn:
                cur = conn.cursor()
                """
                (SELECT) Henter brugerens id, type, fornavn og efternavn fra database.
                (CASE) Tjekker hvilken type bruger det er, og henter fornavn og efternavn fra den rigtige tabel.
                (LEFT JOIN) Logins ID matches op mod Teachers ID eller Students ID for få fat i fornavn og efternavn. Primary/Foreign key forhold
                """
                cur.execute("""
                    SELECT Logins.id, Logins.type,
                    CASE
                        WHEN Logins.type = 'Admin' THEN Teachers.first_name
                        WHEN Logins.type = 'Teacher' THEN Teachers.first_name
                        WHEN Logins.type = 'Student' THEN Students.first_name
                    END AS first_name,
                    CASE
                        WHEN Logins.type = 'Admin' THEN Teachers.last_name
                        WHEN Logins.type = 'Teacher' THEN Teachers.last_name
                        WHEN Logins.type = 'Student' THEN Students.last_name
                    END AS last_name
                    FROM Logins
                    LEFT JOIN Teachers ON Logins.id = Teachers.teacher_id
                    LEFT JOIN Students ON Logins.id = Students.student_id
                    WHERE Logins.username = %s AND Logins.password = %s
                    """,
                            # Username skal ikke være case sensitive og sættes derfor til lower.
                            (username.lower(), password,))
                user_info = cur.fetchall()[0]
                return user_info

        # Hvis der ikke er nogen bruger med det brugernavn, returneres False.
        except IndexError:
            return False


class Logging:
    """
    Klasse til at logge login forsøg i databasen. Både fra website og terminal.
    Er en statisk klasse, da den ikke skal instantieres for at kunne bruges.

    id = brugerens id
    location = hvorfra login forsøget er foretaget
    who = hvem der har foretaget login forsøget
    success = BOOLEAN om login forsøget er succesfuldt eller ej

    """
    # date og time er statiske variabler, da de skal være ens for alle login forsøg.
    _date = datetime.now().strftime("%d/%m/%Y")
    _time = datetime.now().strftime("%H:%M:%S")

    def success_login_terminal(user_id: int, location: str, who: str = None):
        # Registrerer et succesfuldt login fra terminal i databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Logging (id, location, who, success, date, time) VALUES (%s, %s, %s, %s, %s, %s)",
                        (user_id, location, who, 1, Logging._date, Logging._time,))
            conn.commit()

    def failed_login_terminal(user_id: int, location: str, who: str = None):
        # Registrerer et mislykket login fra terminal i databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Logging (id, location, who, success, date, time) VALUES (%s, %s, %s, %s, %s, %s)",
                        (user_id, location, who, 0, Logging._date, Logging._time,))
            conn.commit()

    def succes_login_website(user_id: int):
        # Registrerer et succesfuldt login fra website i databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Logging (id, location, who, success, date, time) VALUES (%s,%s, %s, %s, %s, %s)",
                        (user_id, "Website", "Login", 1, Logging._date, Logging._time,))
            conn.commit()

    def failed_login_website(username: str):
        # Registrerer et mislykket login fra website i databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Logging (id, location, who, success, date, time) VALUES (%s,%s, %s, %s, %s, %s)",
                        (0, "Website", username, 0, Logging._date, Logging._time,))
            conn.commit()

    def get_all_logs():
        # Henter alle login forsøg fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM logging")
            log_list = [log_data for log_data in cur.fetchall()]
        return log_list


class Card:
    """
    Card klassen bruges til at registrere og opdatere kort i databasen.
    Kort registeres før de tildeles til en Student.
    """

    def __init__(self, card_id: int, student_id: int = None):
        self.card_id = int(card_id)
        # Tjekker om kortet allerede er registreret i databasen.
        if self.card_id in self.get_all_card_ids():
            # Hvis kortet er registeret men ikke tilknyttet en bruger, opdateres det med den nye bruger.
            if student_id != None:
                self.student_id = student_id
                self._update_student()
            else:
                return False
        # Registere kortet i databasen.
        else:
            # Hvis en Student er angivet
            if student_id != None:
                self.student_id = student_id
                self._register_student()
            # Ellers registreres kortet uden en Student.
            else:
                self._register_card()

    def _register_student(self):
        # Registrerer kortet i databasen og tilknytter det til en Student.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Cards (card_id, student_id) VALUES (%s, %s)",
                        (self.card_id, self.student_id,))
            conn.commit()

    def _register_card(self):
        # Registrerer kortet i databasen uden at tilknytte det til en Student.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO Cards (card_id) VALUES (%s)",
                        (self.card_id,))
            conn.commit()

    def _update_student(self):
        # Opdaterer kortet i databasen med en ny Student.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE Cards SET student_id = %s WHERE card_id = %s",
                        (self.student_id, self.card_id,))
            conn.commit()

    @staticmethod
    def get_all_card_ids():
        # Henter alle kort id'er fra databasen.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT card_id FROM Cards")
            return [card_id[0] for card_id in cur.fetchall()]

    @staticmethod
    def get_student_id(card_id: int):
        # Henter Student id'et tilknyttet et kort.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT student_id FROM Cards WHERE card_id = %s", (card_id,))
            return cur.fetchone()[0]

    @staticmethod
    def get_available_cards():
        # Henter alle kort der ikke er tilknyttet en Student.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT card_id FROM Cards WHERE student_id IS NULL")
            # Returnerer en liste med alle kort id'er. Lavet med list comprehension.
            return [card_id[0] for card_id in cur.fetchall()]

    @staticmethod
    def get_taken_cards():
        # Henter alle kort der er tilknyttet en Student.
        with open_db(db) as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT card_id FROM Cards WHERE student_id IS NOT NULL")
            # Returnerer en liste med alle kort id'er. Lavet med list comprehension.
            return [card_id[0] for card_id in cur.fetchall()]

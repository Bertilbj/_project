from datetime import datetime

from class_manager import Admin, Card, Logging, Login, Student, Team, Terminal
from connect_to_mysql import hash_password, secret_key
from flask import (Flask, flash, redirect, render_template, request, session,
                   url_for)

"""
Før hver funktion benyttes decorator @app.route(). En Url-sti til funktionen angives, samt HTTP metode der skal benyttes.
Eksempelvis vil en decorataror se således ud: @app.route(/"test_sti", methods = ["GET", "POST"]).
Funktionen der skrives til ovenstående besøges på localhost:5000/test_sti og benytter HTTP GET/POST. (Kan både hente og sende data)
Ved login gemmes relevante session variabler. Disse bruges til fremvisning af bruger data, samt forhindring af uautoriseret brugeradgang til admin funktioner.
"""

time_now = datetime.now()
app = Flask(__name__, template_folder="templates")
app.secret_key = secret_key()


@app.route("/", methods=["GET", "POST"])  # localhost:5000/
def login():
    if request.method == "POST":
        # Hvis login knappen trykkes.
        username_input = request.form["username"]
        password_input = hash_password(request.form["password"])
        # Brugernavn og password inputs gemmes.
        authenticated = Login.authenticate(
            username_input,
            password_input)
        # Authenticate metoden fra Login klassen tager inputs som argument og returnerer en tuple.
        # Eksempelvis (2001, 'Student', 'Bertil', 'Bertilsen')
        if authenticated:
            session["user_id"] = authenticated[0]
            session["user_type"] = authenticated[1]
            session["first_name"] = authenticated[2]
            Logging.succes_login_website(authenticated[0])
            # Hvis login forsøget lykkes,så gemmes diverse session variabler, som eksisterer igennem hele webside besøget.
            if session.get("user_type") == "Admin":
                return admin_index()
            elif session.get("user_type") == "Teacher":
                return admin_index()
            elif session.get("user_type") == "Student":
                return student_index()
            # Hvis user_type stemmer overens, så returneres relevante funktion.
        else:
            flash("Fejl: Forkert brugernavn eller adgangskode.", "error")
            Logging.failed_login_website(username_input)
            # Såfremt forsøget fejler, returneres en fejlbesked og forsøget logges.

    return render_template("login.html")
    # funktionen eksekveres indholdet i login.html


@app.route("/logout")
def logout():
    session.clear()
    # Såfremt der logges ud, ryddes alle session variabler.
    # Returnerer den besøgende til login.html
    return redirect(url_for("login"))


## _____Student_____##
@app.route("/student_index")
def student_index():
    user_type = session.get("user_type")
    first_name = session.get("first_name")
    user_id = session.get("user_id")
    # Session variabler hentes for at vise en personlig oversigt for den studerende.
    return render_template("student_index.html", first_name=first_name, user_type=user_type, user_id=user_id)
    # Funktionen eksekverer indholdet i student_index.html og variablerne first_name/user_type og user_id sendes med.


## _____Student_____##
@app.route("/personal_overview")
def personal_overview():
    output = Student.my_overview(session.get("user_id"))
    # Metodekald fra Student klassen. my_overview gives user_id som argument og en liste med tuples returneres.
    # Eksempelvis ('Bertil', 'Bertilsen', 2001, '31/05/2023', '12:54')

    return render_template("student_overview.html", output=output)
    # Funktionen eksekverer indholdt i student_overview.html og output variablen sendes med.


## _____Admin/Teacher_____##
@app.route("/admin_index")
def admin_index():
    if session.get("user_type") == "Admin" or session.get("user_type") == "Teacher":
        user_type = session.get("user_type")
        first_name = session.get("first_name")
        # Hvis user_type == Admin/Teacher er denne side tilgængelig for den besøgende
    else:
        return redirect(url_for("student_index"))
        # Hvis ikke, returneres student_index.

    return render_template("admin_index.html", first_name=first_name, user_type=user_type)
    # Funktionen eksekverer indholdet i admin_index.html og first_name/last_name variablerne sendes med.


## _____Admin/Teacher_____##
@app.route("/admin_overview", methods=["GET", "POST"])
def admin_overview():
    output = Admin.view_all_students()
    # Metodekald fra Admin klassen returner en liste over alle studerende. Gemmes i en variable.
    # Eksempelvis [(2001, 'Bertil', 'Bertilsen', 'ITT22', 275288510832)]

    if session.get("user_type") == "Admin" or session.get("user_type") == "Teacher":
        return render_template("admin_overview.html", output=output)
    else:
        return redirect(url_for("student_index"))
            # Funktionen eksekverer indholdet i admin_overview.html



## ______Admin______##
@app.route("/add_student", methods=["GET", "POST"])
def add_student():
    if session.get("user_type") == "Admin":
        # Hvis Admin udføres det resterende kode.
        teams = Team.get_all_teams()
        cards = Card.get_available_cards()
        # Metodekald fra Team og Card klassen gemmer alle teams/tilgængelig kort i variabler. Vises som drop down på siden.
        if request.method == "POST":
            new_student = Student(
                request.form["first_name"],
                request.form["last_name"],
                Team.get_specific_team(team_name=request.form.get("teams")),
                request.form.get("cards"))
            # Et Student objekt oprettes/gemmes og constructoren fyldes med inputs fra brugeren, samt med valg fra dropdown menuer.
            # Eksempelvis Student("Bertil","Johansen","2",346154876421)
            new_student._register_student()
            # register_student() kaldes på objektet og den nye studernede oprettes.
            flash("Den studerende er tilføjet.", "success")
    elif session.get("user_type") == "Teacher":
        return redirect(url_for("admin_index"))
    else:
        return redirect(url_for("student_index"))
        # Hvis ikke Admin/Teacher returneres student_index

    return render_template("admin_add_student.html", teams=teams, cards=cards)
    # Funktionen eksekverer indholdet i admin_add_student.html og teams/cards variablen sendes med.


## _____Admin/Teacher_____##
@app.route("/attendance_update", methods=["GET", "POST"])
def attendance_update():
    if session.get("user_type") == "Admin" or session.get("user_type") == "Teacher":
        # Hvis Admin/Teacher udføres det resterende kode.
        user_session_id = session.get("user_id")
        # User_id fetches.
        output = Admin.show_all_attendance()
        # Metodekald fra Admin klassen show_attendance() kaldes. Gemmes i variablen output. Returner en liste over fravær for studerende.
        # Eksempelvis [(50001, 2001, 'Bertil', 'Bertilsen', 'ITT22', 275288510832, '31/05/2023', '12:54')]
        if request.method == "POST":
            student_id_input = int(request.form["Student_ID"])
            try:
                Admin.manuel_attendance_register(user_session_id,
                                                 student_id_input,
                                                 Team.get_specific_team(
                                                     student_id=student_id_input),
                                                 time_now.strftime("%d/%m/%Y"),
                                                 time_now.strftime("%H:%M"))
                # Metodekald fra Admin klassen registrerer fremmøde for en studerende.
                flash("Fremmødet er blevet opdateret.", "success")
            except:
                flash("Fejl: Den studerende eksisterer ikke i databasen.", "error")
                # Hvis student_id ikke stemmer overens med en studerende, så returneres en fejlbesked.
    else:
        return redirect(url_for("student_index"))
    # Hvis ikke Admin/teacher returneres student_index

    return render_template("admin_modify_attendance.html", output=output)
# Funktionen eksekverer indholdet i admin_modify_attendance.html og output variablen sendes med.


## _____Admin_____##
@app.route("/show_log")
def show_log():
    if session.get("user_type") == "Admin":
        logs = Logging.get_all_logs()
        # Metode kald fra Loggin klassen. check_logs() returnerer en liste med tuples.
        # Eksempelvis (1, 2001, 'Website', '1001', 1, '31/05/2023', '12:54:03')
    elif session.get("user_type") == "Teacher":
        return redirect(url_for("admin_index"))
    else:
        return redirect(url_for("student_index"))
        # Hvis student eller teacher, sendes de tilbage til relevante index page.
    return render_template("admin_logs.html", logs=logs)
    # Funktionen eksekverer indholdt i admin_logs.html og logs variablen sendes med.


## _____Admin_____##
@app.route("/manage_terminal", methods=["GET", "POST"])
def manage_terminal():
    if session.get("user_type") == "Admin":
        teams = ['None']
        # en liste defineres
        teams += Team.get_all_teams()
        # Metodekald fra Team klassen. Alle en liste med alle hold hentes og den ny definerede liste tilføjes.
        # Eksempel output ['None','ITT22', 'ITT23', 'DMA22', 'DMA23']
        terminals = Terminal.get_all_names()
        # Metodekald fra Terminal klassen. Alle terminal navne hentes i form af en liste.
        # Eksempelvis ['IT-Lab', 'CSD 3.2.20', 'CSD 5.1.42']
        overview = Terminal.get_all_info()
        # Metode kald fra Terminal. get_all_info() Returnerer en liste med Terminal og team navne hvor team_id stemmer overens
        # [('IT-Lab'), ('ITT23')]
        if request.method == "POST" and request.form.get("Add_Terminal"):
            # Hvis knappen "Tilføj Termninal" trykkes, udføres nedenstående kode.
            if request.form.get("teams") == 'None':
                Terminal.register_terminal(name=request.form["new_terminal"])
                return redirect(url_for('manage_terminal'))
            # Hvis hold valg er = "None" oprettes et team uden et team_id.
            else:
                Terminal.register_terminal(name=request.form["new_terminal"], team_id=Team.get_specific_team(
                    team_name=request.form.get("teams")))
                return redirect(url_for('manage_terminal'))
            # Hvis der er valgt et hold, så oprettes registreres terminalen med det indtastede navn samt med team id.

        elif request.method == "POST" and request.form.get("Edit_Terminal"):
            # Hvis knappen " Tilføj team" trykkes, udføres nedenstående kode.
            if request.form.get("edit_teams") == 'None':
                Terminal.set_team(Terminal.get_id(
                    request.form.get("terminals")), None)
                # fetch_id() henter team_id baseret på valgte terminal navn. Hvis None er team_id == Null
                # set_team() tilknytter et holdnavn til det indhentede team_id(Null)
                return redirect(url_for('manage_terminal'))
            else:
                Terminal.register_terminal(name=request.form.get("terminals"), team_id=Team.get_specific_team(
                    team_name=request.form.get("edit_teams")))
                # Hvis hold_navn ikke er = None så tilknyttes den valgte Terminal til valgte Hold.
                return redirect(url_for('manage_terminal'))
        elif request.method == "POST" and request.form.get("Change_Terminal_Name"):
            # Hvis knappen " Ændre hold navn" trykkes, udføres nedenstående kode.
            Terminal.set_name(request.form["new_terminal_name"], Terminal.get_id(
                request.form.get("terminal_edit")))
            # set_name() tager et indtastede holdnavn og bibeholder det eksisterende team_id.
            return redirect(url_for('manage_terminal'))
        elif request.method == "POST" and request.form.get("Delete_Terminal"):
            # Hvis knappen "Slet terminal" trykkes, udføres nedenstående kode.
            Terminal.delete_terminal(Terminal.get_id(
                request.form.get("terminals")))
            # delete_terminal henter team_id baseret på valgte holdnavn.
            # terminalen fjernes derefter fra databasen.
            return redirect(url_for('manage_terminal'))
    elif session.get("user_type") == "Teacher":
        return redirect(url_for("admin_index"))
    else:
        return redirect(url_for("student_index"))
        # Hvis teacher/student returneres de til deres index side.
    return render_template("admin_manage_terminal.html", teams=teams, terminals=terminals, overview=overview)
    # Funktionen eksekverer indholdt i admin_manage_termninal.html og teams/terminals/overview variablerne sendes med.


## _____Admin_____##
@app.route("/manage_team", methods=["GET", "POST"])
def manage_team():
    if session.get("user_type") == "Admin":
        teams = Team.get_all_teams()
        # get_all_teams() henter en liste over alle hold.
        # Eksempelvis ['ITT22', 'ITT23', 'DMA22', 'DMA23']
        if request.method == "POST" and request.form.get("Add_Team"):
            # Hvis knappen "Tilføj Hold", udføres nedenstående kode.
            Team.register_team(request.form["new_team"])
            # Metoden register_team() tilføjer det indtastede holdnavn.
            return redirect(url_for('manage_team'))
            # Siden opdateres
        elif request.method == "POST" and request.form.get("Change_Team_Name"):
            # Hvis knappen "Ændre hold navn" trykkes, udføres nedenstående kode.
            Team.set_name(Team.get_specific_team(
                team_name=request.form.get("team_id")), request.form["edit_team"])
            # Metoden set_team () tager valgte holdnavn fra dropdown, henter team_id og sætter det nye navn.
            return redirect(url_for('manage_team'))
            # Siden opdateres
        elif request.method == "POST" and request.form.get("Delete_Team"):

            # Hvis knappen "Slet hold" trykkes, udføres nedensående kode.
            Team.delete_team(Team.get_specific_team(
                team_name=request.form.get("team_delete")))
            # Metoden delete_team() tager det valgte hold navn fra dropdown. Holdet slettes.
            return redirect(url_for('manage_team'))
            # Siden opdateres
    elif session.get("user_type") == "Teacher":
        return redirect(url_for("admin_index"))
    else:
        return redirect(url_for("student_index"))
    # Teachers/Students sendes tilbage til deres index sider.
    return render_template("admin_manage_team.html", teams=teams)
    # Funktionen eksekverer indholdt i admin_manage_team.html og teams variablen sendes med.


## _____Admin_____##
@app.route("/admin_delete", methods=["GET", "POST"])
def admin_delete():
    output = Admin.view_all_students()
    # Metodekald fra Admin klassen returner en liste over alle studerende. Gemmes i en variable
    # Eksempelvis [(2001, 'Bertil', 'Bertilsen', 'ITT22', 275288510832)]

    if session.get("user_type") == "Admin":
        # Hvis Admin udføres det resterende kode.
        if request.method == "POST":
            Admin._delete_student(int(request.form["Student_ID"]))

            flash("Du har fjernet den studerende", "success")
            # Hvis user_type er Admin kan den besøgende desuden slette en studerende ved indtast af Student_id
    elif session.get("user_type") == "Teacher":
        return redirect(url_for("admin_index"))
    else:
        return redirect(url_for("student_index"))

    return render_template("admin_delete.html", output=output)
    # Funktionen eksekverer indholdet i admin_delete.html og output variablen sendes med.


if __name__ == "__main__":
    app.run(debug=True)

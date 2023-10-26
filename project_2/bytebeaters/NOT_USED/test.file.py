from class_manager import Card, Admin, Terminal, Login, Student, Teacher, Team, Logging
from connect_to_mysql import hash_password
# test = "helloworld"
# print(encrypt_password(test))
# encrypt_test = b'gAAAAABkd8MBl9XdMcl7HCiq_lCkGBskfG-cLYuVihrpCeU-rEOesJ_iaPbS0JS49TqQi68PH_IqZu5WX9AxZHy64B3jyrMRZw=='
# print(decrypt_password(encrypt_test))
# test = Login.authenticate("berbe","Bebe1")

# first_last = test[1],test[2]

# user_type = test [3]
# print(first_last)

# test = Student.my_overview(2001)
# attendance_info = test
# print(attendance_info)
# authenticated = Login.authenticate("berbe","Bebe1")
# print(authenticated)
# user_data = [data for data in authenticated]

# if authenticated:
#     first_name = authenticated[1]
#     last_name = authenticated[2]
#     usertype = authenticated[3]
#     user_id = authenticated[4]
    
# # print(first_name,last_name,usertype,authenticated)
    
# print(user_data)
# new_student = Student("Mike","Hansen",2,175646252515)
# new_student.register_student()
# print(Teacher.view_all_students())
# # print(Team.get_team_id(2001))
# print(Admin.delete_student(2012))
# print(Team.get_all_teams())
# print(Terminal.teamid_from_teamname("ITT22"))

# print(Team.get_team_id("ITT22"))

# print(Student.my_overview(2001))
# print(Teacher.show_attendance())
# print(Logging.check_logs())
# print(Team.get_all_teams())

# print(hash_password("Bebe1"))
# new_card = Card(12434615487,None)
# new_card.register_card
# print(b'hello_world')
first,last = ["TEST","STUDERNDE"]
print(f"{first[:2]}{last[:2]}1".capitalize())
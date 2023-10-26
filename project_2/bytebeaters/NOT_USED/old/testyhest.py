import mysql.connector

conn = mysql.connector.connect(host='bytebeaters.sof60.dk',
                               user='bytebeaters',
                               password='MangoLoco42',
                               )
cur = conn.cursor()
cur.execute("CREATE DATABASE IF NOT EXISTS timelogging")
conn.commit()
cur.execute("SHOW DATABASES")
print(cur.fetchall())
conn.close()
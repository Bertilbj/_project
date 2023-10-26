import sqlite3

db = 'test.sqlite'
conn = sqlite3.connect(db)
cur = conn.cursor()


class Location:
    def __init__(self, name, inside=0, opening_hours="08:00-16:00", active=True, max_inside=30):
        cur.execute('CREATE TABLE IF NOT EXISTS Location (id INTEGER PRIMARY KEY, name TEXT, inside INTEGER, opening_hours TEXT, active INTEGER, max_inside INTEGER)')
        self.name = name
        if not cur.execute('SELECT name FROM Location WHERE name = ?', (self.name,)).fetchone():
            self.inside = inside
            self.opening_hours = opening_hours
            self.active = active
            self.max_inside = max_inside
            cur.execute('INSERT INTO Location (name, inside, opening_hours, active, max_inside) VALUES (?, ?, ?, ?, ?)', (self.name, self.inside, self.opening_hours, self.active, self.max_inside))
        else:
            self.inside = cur.execute('SELECT inside FROM Location WHERE name = ?', (self.name,)).fetchone()[0]
            self.opening_hours = cur.execute('SELECT opening_hours FROM Location WHERE name = ?', (self.name,)).fetchone()[0]
            self.active = cur.execute('SELECT active FROM Location WHERE name = ?', (self.name,)).fetchone()[0]
            self.max_inside = cur.execute('SELECT max_inside FROM Location WHERE name = ?', (self.name,)).fetchone()[0]
        conn.commit()
    
    def add_person(self):
        if self.inside < self.max_inside:
            self.inside += 1
            cur.execute('UPDATE Location SET inside = ? WHERE name = ?', (self.inside, self.name))
            conn.commit()
        else:
            print("The location is full")
            
    def set_max_inside(self, max_inside):
        self.max_inside = max_inside
        cur.execute('UPDATE Location SET max_inside = ? WHERE name = ?', (self.max_inside, self.name))
        conn.commit()
    
    def set_opening_hours(self, opening_hours):
        if opening_hours[2] != ":" and opening_hours[5] != "-" and opening_hours[8] != ":" and len(opening_hours) != 11:
            print("Opening hours must be in the format HH:MM-HH:MM")
            return
        self.opening_hours = opening_hours
        cur.execute('UPDATE Location SET opening_hours = ? WHERE name = ?', (self.opening_hours, self.name))
        conn.commit()
    
    def turn_off(self):
        self.active = False
        cur.execute('UPDATE Location SET active = ? WHERE name = ?', (self.active, self.name))
        conn.commit()
        
    def turn_on(self):
        self.active = True
        cur.execute('UPDATE Location SET active = ? WHERE name = ?', (self.active, self.name))
        conn.commit()

klasse = Location("Klasse", max_inside= 9)
skole = Location("Skole")
for i in range(10):
    klasse.add_person()

conn.close()
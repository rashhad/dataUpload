import sqlite3
import os
import bcrypt



def findActiveUser():
    with sqlite3.connect('readings.db') as conn:
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            '''
                SELECT name, id
                FROM person
                where loginStatus = 1
            '''

        )
        
        return cursor.fetchone()

def sysLogin(id, pin:str):
    with sqlite3.connect('readings.db') as conn:
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor.execute('''
        select id, pin from person where id = ?
        ''',(id,)
        )
        retId, hashedPin = cursor.fetchone()
        if bcrypt.checkpw(pin.encode('utf-8'), hashedPin):
            cursor.execute('''
            update person
            set loginStatus = 1
            where id = ?
            ''',(id,))
            conn.commit()
            return True
        else:
            return False

def sysLogOut(id):
    with sqlite3.connect('readings.db') as conn:
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            "update person set loginStatus = 0 where id = ?",(id,)
        )
        conn.commit()
        os.system('cls')
        print('logout success')

def creatingUser(id, name, passw:str):
    passw_bytes = passw.encode('utf-8')
    hashedpw = bcrypt.hashpw(passw_bytes, bcrypt.gensalt())
    # print(f'hashed password: {hashedpw}')
    with sqlite3.connect('readings.db') as conn:
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            "insert into person (name, id, pin) values (?,?,?)", (name, id, hashedpw)
        )
    pass

def updatePass(id, oldPass, newPass):
    with sqlite3.connect('readings.db') as conn:
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            "select pin from person where id=?", (id,)
        )
        hashedPin = cursor.fetchone()
        try:
            if bcrypt.checkpw(oldPass.encode('utf-8'), hashedPin[0]):
                hasedNewPass=bcrypt.hashpw(newPass.encode('utf-8'), bcrypt.gensalt())
                cursor.execute(
                    "update person set pin = ? where id = ?",(hasedNewPass,id)
                )
                conn.commit()
                return True
            else:
                return False
        except Exception as e:
            print(f'{e}')

    pass

def updateName(id, name):
    with sqlite3.connect('readings.db') as conn:
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            "update person set name = ? where id=?", (name,id)
        )
        conn.commit()
        return True
    pass

def getName(id):
    with sqlite3.connect('readings.db') as conn:
        cursor = conn.cursor()
        cursor.execute(
            "select name from person where id=?", (id,)
        )
        return cursor.fetchone()[0]
    pass

def deleteUser(id, passw):
    with sqlite3.connect('readings.db') as conn:
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor.execute(
            "select pin from person where id=?", (id,)
        )
        hashedPin = cursor.fetchone()
        if bcrypt.checkpw(passw.encode('utf-8'), hashedPin[0]):
            cursor.execute(
                "delete from person where id=?", (id,)
            )
            conn.commit()
            return True
        else:
            return False

def loadEntry(date, time, voltageLevel, bayName, mw, mvar, person):
        with sqlite3.connect('readings.db') as conn:
            cursor = conn.cursor()
            conn.execute("PRAGMA foreign_keys = ON")
            cursor.execute('''
                        insert into loadReadings (date, time, busVoltage, bayName, MW, MVAR, uploadBy) values (?,?,?,?,?,?,?)
            ''',(date, time, voltageLevel, bayName, mw, mvar, person))
            conn.commit()
            cursor.close()

def findLastEntryTime():
        with sqlite3.connect('readings.db') as conn:
            cursor = conn.cursor()
            conn.execute("PRAGMA foreign_keys = ON")
            cursor.execute('''
            select time from loadReadings order by rowid desc LIMIT 1
            ''')
            return cursor.fetchone()[0]
            

if __name__ == "__main__":
    with sqlite3.connect('readings.db') as conn:
        cursor = conn.cursor()
        conn.execute("PRAGMA foreign_keys = ON")
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS person (
                            id TEXT PRIMARY KEY,
                            name TEXT NOT NULL,
                            pin TEXT,
                            oisCookie BLOB,
                            loginStatus BOOLEAN DEFAULT 0
                        )
                    '''
        )
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS dateTime (
                            date TEXT NOT NULL,
                            time TEXT NOT NULL,
                            PRIMARY KEY (date, time)
                        )
                    '''
        )
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS bus (
                            busName TEXT PRIMARY KEY
                        )
                    '''
        )
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS loadReadings (
                            date TEXT NOT NULL,
                            time TEXT NOT NULL,
                            busVoltage TEXT NOT NULL,
                            bayName TEXT NOT NULL,
                            MW REAL NOT NULL,
                            MVAR REAL NOT NULL,
                            upload TEXT DEFAULT "no" NOT NULL,
                            uploadBy TEXT NOT NULL,
                            PRIMARY KEY (date, time, bayName),
                            FOREIGN KEY (uploadBy) REFERENCES person(id) ON UPDATE CASCADE,
                            FOREIGN KEY (date, time) REFERENCES dateTime(date, time)
                        )
                    '''
        )
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS voltageReadings (
                            date TEXT NOT NULL,
                            time TEXT NOT NULL,
                            bus1 REAL NOT NULL,
                            bus2 REAL NOT NULL,
                            upload TEXT DEFAULT "no" NOT NULL,
                            uploadBy INTEGER NOT NULL,
                            PRIMARY KEY (date, time),
                            FOREIGN KEY (uploadBy) REFERENCES person(id) ON UPDATE CASCADE,
                            FOREIGN KEY (date, time) REFERENCES dateTime(date, time)

                        )
                    '''
        )

        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS sysLog (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            reportedAt TEXT DEFAULT CURRENT_TIMESTAMP,
                            message TEXT NOT NULL
                        )
                    '''
        )

        conn.commit()
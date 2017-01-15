import sqlite3
import datetime

commands = {}

def user_interface():
    response = input("New or old: ").strip().lower()
    while response not in ['new', 'old']:
        response = input("New or old: ").strip().lower()
    db = commands[response]() 
    handle_commands(db)
    print('Thank you for using the tutoring database.')

def make_new_database():
    result = input("Name of your new database: ").strip()
    if result[-3:] != '.db':
        result += '.db'
    conn = sqlite3.connect(result)
    try:
        conn.execute(''' CREATE TABLE Tutorees
            (TutoreeID      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            Rate            DECIMAL(2,2)    NOT NULL,
            PaidHours       REAL            NULL,
            OwedHours       REAL            NULL); ''')

        conn.execute(''' CREATE TABLE TutoreeInfo
        (TutoreeID      REFERENCES Tutorees(TutoreeID),
        FirstName       VARCHAR(100)    NOT NULL, 
        LastName        VARCHAR(100)    NOT NULL,
        Birthday        DATE            NOT NULL,
        Gender          VARCHAR(20)     NULL,
        Grade           INT             NOT NULL,
        School          REFERENCES School(SchoolName),
        PhoneNumber     VARCHAR(20)     NOT NULL,     
        Email           VARCHAR(100)    NOT NULL); ''')

        conn.execute(''' CREATE TABLE Records
        (TutoreeID      REFERENCES Tutorees(TutoreeID),
        Date            DATE           NOT NULL,
        StartTime       TIME           NOT NULL,
        EndTime         TIME           NOT NULL,
        HasPaid         BOOL           NOT NULL);''')

        conn.execute(''' CREATE TABLE Schools
        (SchoolID       INTEGER PRIMARY KEY AUTOINCREMENT           NOT NULL, 
        SchoolName      VARCHAR(200)   NOT NULL,
        Street          VARCHAR(200)   NOT NULL,
        City            VARCHAR(50)    NOT NULL,
        PostalCode      VARCHAR(20)    NOT NULL,
        PhoneNumber     VARCHAR(20)    NOT NULL,
        Type            VARCHAR(20)    NOT NULL, 
        District        VARCHAR(20)    NULL);''')

    except sqlite3.OperationalError:
        print('This is already a database. You will work with this one.') 
    
    conn.commit()
    conn.close()
    
    return result

def get_old_database():
    result = input("Name of database: ").strip()
    if result[-3:] != '.db':
        result += '.db'
    conn = sqlite3.connect(result)
    try:
        conn.execute(''' CREATE TABLE Tutorees
            (TutoreeID      INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            Rate            DECIMAL(2,2)    NOT NULL,
            PaidHours       REAL            NULL,
            OwedHours       REAL            NULL); ''')

        conn.execute(''' CREATE TABLE TutoreeInfo
        (TutoreeID      REFERENCES Tutorees(TutoreeID),
        FirstName       VARCHAR(100)    NOT NULL, 
        LastName        VARCHAR(100)    NOT NULL,
        Birthday        DATE            NOT NULL,
        Gender          VARCHAR(20)     NULL,
        Grade           INT             NOT NULL,
        School          REFERENCES School(SchoolName),
        PhoneNumber     VARCHAR(20)     NOT NULL,     
        Email           VARCHAR(100)    NOT NULL); ''')

        conn.execute(''' CREATE TABLE Records
        (TutoreeID      REFERENCES Tutorees(TutoreeID),
        Date            DATE           NOT NULL,
        StartTime       TIME           NOT NULL,
        EndTime         TIME           NOT NULL,
        HasPaid         BOOL           NOT NULL);''')

        conn.execute(''' CREATE TABLE Schools
        (SchoolID       INTEGER PRIMARY KEY AUTOINCREMENT           NOT NULL, 
        SchoolName      VARCHAR(200)   NOT NULL,
        Street          VARCHAR(200)   NOT NULL,
        City            VARCHAR(50)    NOT NULL,
        PostalCode      VARCHAR(20)    NOT NULL,
        PhoneNumber     VARCHAR(20)    NOT NULL,
        Type            VARCHAR(20)    NOT NULL, 
        District        VARCHAR(20)    NULL);''')

        print('This is a new database. You will work with this one.')

    except sqlite3.OperationalError:
        pass
    
    conn.commit()
    conn.close()
    return result

commands.update({'new': make_new_database, 'old': get_old_database})

def handle_commands(db):
    conn = sqlite3.connect(db)
    c = conn.cursor()
    print('Opened database successfully')
    while True:
        response = input(MENU).strip().upper()
        if response in ['PD', 'AT', 'RT', 'PR', 'AR', 'UR', 'RR']:
            commands[response](c)
        elif response == 'QU':
            break
        else:
            print('That is not a valid command.')
        conn.commit()
    conn.close()

MENU = '''
******************************************
 PD:  Print the tutorees
 AT:  Add a tutoree
 RT:  Remove a tutoree
 PR:  Print records for a tutoree
 AR:  Add a record
 UR:  Update a record
 RR:  Remove a record
 QU:  Quit
******************************************
 '''

def print_database(c: sqlite3.Cursor):
    print()
    print('ID:\tName\t\t{:3s}   {:6s}   {:6s}   {:5s}   {}'.format('Age', 'Gender', 'Rate', 'Grade', 'School')) 
    print('-'*62)
    
    for row in c.execute('''SELECT * FROM Tutorees 
                            JOIN TutoreeInfo
                            ON Tutorees.TutoreeID = TutoreeInfo.TutoreeID
                            ORDER BY Tutorees.TutoreeID'''):

        print(tutoree_str(row))

def tutoree_str(row: tuple) -> str:
    ID = row[0]
    Name = '{} {}.'.format(row[5], row[6][0])
    Gender = row[8]
    Rate = row[1]
    Grade = row[9]
    School = row[10]
    PhoneNum = row[11]
    Email = row[12]
    Birthday = str_to_date(row[7])
    Age = abs(Birthday - Birthday.today())/365
        
    result = '{:2d}:\t{:10s}\t{:2d}    {:6s}   ${:5.2f}   {:2d}      {}'.format(ID, Name, Age.days, Gender, Rate, Grade, School)
    result += '\n\tContact Info:\n' + '\t\t{}  ||  {}'.format(PhoneNum, Email) + '\n'
    
    return result

def add_tutoree(c: sqlite3.Cursor):
    print()
    print('You are adding a tutoree. Please enter the relevant information for the fields coming up. Press enter to continue.')
    enter = input()
    
    FirstName = input('{:20s}: '.format('First Name')).strip()
    LastName = input('{:20s}: '.format('Last Name')).strip()
    
    while True:
        try:
            Birthday = str_to_date(input('{:20s}: '.format('Birthday (ISO)')).strip())
            break
        except ValueError:
            print("That is not a valid birthday. Try again.")
    
    Gender = input('{:20s}: '.format('Female/Male/Other')).title()
    while Gender not in ['Female', 'Male', 'Other']:
        print('Please type in one of the three possible choices.')
        Gender = input('{:20s}: '.format('Female/Male/Other')).title()
        
    while True:
        try:
            Rate = float(input('{:20s}: '.format('Rate per Hour')))
            break
        except ValueError:
            print("That isn't a number. Try again.")
    
    PhoneNum = input('{:20s}: '.format('Phone Number')).strip()
    while not check_phonenum(PhoneNum):
        print("That isn't a phone number formatted correctly. Try again.")
        PhoneNum = input('{:20s}: '.format('Phone Number')).strip()

    Email = input('{:20s}: '.format('E-mail')).strip()
    while not check_email(Email):
        print("That isn't a valid email. Try again.")
        Email = input('{:20s}: '.format('E-mail')).strip()

    print("Here are all of the currently registered schools in the database.")
    print('ID:\tSchool')
    print('-'*14)
    for row in c.execute("SELECT * FROM Schools ORDER BY SchoolID"):
        print(school_str(row))
    while True:
        try:                 
            S = int(input('Type the ID corresponding to the school OR type the number 0 for a new school: '))
            if S == 0:
                School = add_school(c)
                break
            else:
                c.execute('SELECT SchoolName,Type FROM Schools WHERE SchoolID = ?', (S,))
                School = c.fetchone()
                if School != None: 
                    break
                print("That isn't a valid index. Try again.")
        except ValueError:
            print("That isn't a number. Try again.")
    
    while True:
        try:
            GRADES = {'HS': [9, 10, 11, 12], 'MS': [6, 7, 8], 'ES': [1, 2, 3, 4, 5, 6]}
            Grade = int(input('{:20s}: '.format('Grade Level')))
            if Grade not in GRADES[School[1]]:
                print("That isn't an appropriate grade level. Try again.")
            else: 
                break
        except ValueError:
            print("That isn't a number. Try again.")

    c.execute("INSERT INTO Tutorees (Rate, PaidHours, OwedHours) VALUES (?, ?, ?)", (Rate, 0, 0,))
    c.execute("SELECT TutoreeID FROM Tutorees ORDER BY TutoreeID DESC")
    ID = c.fetchone()
    
    c.execute('''INSERT INTO TutoreeInfo VALUES
              (?, ?, ?, ?, ?, ?, ?, ?, ?)''', (ID[0], FirstName, LastName, Birthday, Gender, Grade, School[0], PhoneNum, Email))
    print()
    print('Tutoree added successfully.')

def add_school(c: sqlite3.Cursor):
    print()
    print('You are adding a new school. Please enter the relevant information for the fields coming up. Press enter to continue.')
    enter = input()

    Name = input('{:20s}: '.format('Name of School')).strip()
    
    Street = input('{:20s}: '.format('Street Address')).strip()
    
    City = input('{:20s}: '.format('City in CA')).strip()
    
    PostalCode = input('{:20s}: '.format('Postal Code')).strip()
    
    PhoneNum = input('{:20s}: '.format('Phone Number')).strip()
    while not check_phonenum(PhoneNum):
        print("That isn't a phone number formatted correctly. Try again.")
        PhoneNum = input('{:20s}: '.format('Phone Number')).strip()
        
    Type = input('{:20s}: '.format('Type (ES/MS/HS)')).strip().upper()
    while Type not in ['ES', 'MS', 'HS']:
        print("That isn't one of the three options. Try again.")
        Type = input('{:20s}: '.format('Type (ES/MS/HS)')).strip().upper()
        
    District = input('{:20s}: '.format('District (can be omitted)')).strip()
    if District == '':
        District = None

    c.execute('''INSERT INTO Schools
              (SchoolName, Street, City, PostalCode, PhoneNumber, Type, District) VALUES
              (?, ?, ?, ?, ?, ?, ?)''', (Name, Street, City, PostalCode, PhoneNum, Type, District))
    
    c.execute("SELECT SchoolName,Type FROM Schools ORDER BY SchoolID DESC")
    print()
    print('School added successfully.')
    return c.fetchone()

def school_str(row: list) -> str:
    result = '{:2d}:\t{:}'.format(row[0], row[1])
    result += '\n\t   {}\n\t   {}, CA {}\n\t   {}'.format(row[2]
                                                          , row[3], row[4], row[5])

    return result
    
def check_email(m: str) -> bool:
    return '@' in m

def check_phonenum(p: str) -> bool:
    number = '({}) {}-{}'.format(p[1:4], p[6:9], p[10:])
    return number == p
           
def str_to_date(d: str):
    parts = d.split('-')
    return datetime.date(int(parts[0]), int(parts[1]), int(parts[2]))

def remove_tutoree(c: sqlite3.Cursor):
    print()
    print('You are removing a tutoree. Press enter to continue.')
    enter = input()
    print_database(c)
    while True:
        try:
            ID = int(input('Type in the ID of the tutoree you want to remove: '))
            c.execute('''SELECT * FROM Tutorees JOIN TutoreeInfo
                         ON Tutorees.TutoreeID = TutoreeInfo.TutoreeID
                         WHERE Tutorees.TutoreeID = ? ''', (ID,))
            tutoree = c.fetchone()
            if tutoree != None:
                print()
                print(tutoree_str(tutoree))
                response = input("Are you sure you want to delete " + tutoree[5] + '? Yes/No: ').strip().lower()
                while response not in ['yes', 'no']:
                    response = input("That isn't a valid answer. Yes/No: ").strip().lower()
                if response == 'yes':
                    c.execute("DELETE FROM Tutorees WHERE TutoreeID = ?", (ID, ))
                    c.execute("DELETE FROM TutoreeInfo WHERE TutoreeID = ?", (ID, ))
                    c.execute("DELETE FROM Records WHERE TutoreeID = ?", (ID, ))
                    print()
                    print('Tutoree successfully removed.')
                if response == 'no':
                    print()
                    print('Removal cancelled.')
                break
            else:
                print("That isn't a valid ID. Try again.")
        except ValueError:
            print("That isn't a valid ID. Try again.")

def add_record(c: sqlite3.Cursor):
    print()
    print('You are adding a record for a tutoree. Press enter to continue.')
    enter = input()
    print_database(c)
    while True:
        try:
            ID = int(input('Type in the ID of the tutoree: '))
            c.execute('''SELECT * FROM Tutorees 
                         WHERE TutoreeID = ? ''', (ID,))
            tutoree = c.fetchone()
            if tutoree != None:
                print()
                print('Here are the current records of the tutoree.')
                print_record(c, ID)
                print()
                break
            else:
                print("That isn't a valid ID. Try again.")
        except ValueError:
            print("That isn't a valid ID. Try again.")
            
    print('Please enter the relevant information for the fields coming up. Press enter to continue.')
    enter = input()
    
    while True:
        try:
            date = str_to_date(input('{:20s}: '.format('Date of Record (ISO)')).strip())
            break
        except ValueError:
            print("That is not a valid date. Try again.")
            
    while True:
        try:
            start = str_to_time(input('{:20s}: '.format('Starting Time')).strip())
            break
        except ValueError and IndexError:
            print("That is not a valid time. Try again.")
            
    while True:
        try:
            end = str_to_time(input('{:20s}: '.format('Ending Time')).strip())
            if end < start:
                print("That is not a valid time. Try again.")
            else:
                break
        except ValueError and IndexError:
            print("That is not a valid time. Try again.")
            
    p = input('{:20s}: '.format('Have they paid? Yes/No')).strip().lower()
    while p not in ['yes', 'no']:
        p = input("That isn't a valid answer. Yes/No: ").strip().lower()
    paid = True
    if p == 'no':
        paid = False

    hours = hour_diff(start, end)

    c.execute("SELECT PaidHours, OwedHours FROM Tutorees WHERE TutoreeID =?", (ID,))
    h = c.fetchone()
    paidhours = h[0]
    owedhours = h[1]
    if paid:
        paidhours += hours
    else:
        owedhours += hours

    c.execute("INSERT INTO Records VALUES (?, ?, ?, ?, ?)", (ID, date, start.isoformat(), end.isoformat(), paid,))
    c.execute("UPDATE Tutorees SET PaidHours = ?, OwedHours = ? WHERE TutoreeID = ?", (paidhours, owedhours,  ID))

    print('Here are the records of the tutoree now.')
    
    print_record(c, ID)
    
    print()
    print('Record successfully added.')
        
def record_str(row: tuple) -> str:
    yn = 'Yes'
    if not row[4]:
        yn = 'No'
    result = '\t{}\t{}-{}\t{}'.format(row[1], row[2][:-3], row[3][:-3], yn)
    return result

def print_record(c: sqlite3.Cursor, ID: int):
    print()
    print('Record: {:10s}\t{:11s}\tHas paid?'.format('Date', 'Time'))
    print('-' * 49)
    for row in c.execute('''SELECT * FROM Records
                            WHERE TutoreeID = ?
                            ORDER BY Date''', (ID,)):
        print(record_str(row))
    print()
    c.execute("SELECT Rate, PaidHours, OwedHours FROM Tutorees WHERE TutoreeID =?", (ID,))
    h = c.fetchone()
    c.execute("SELECT FirstName, LastName FROM TutoreeInfo WHERE TutoreeID =?", (ID,))
    tutoree = c.fetchone()
    print('{} {} has paid ${:.2f} and owes ${:.2f}.'.format(tutoree[0], tutoree[1], h[0] * h[1], h[0] * h[2]))

def print_records(c: sqlite3.Cursor):
    print_database(c)
    while True:
        try:
            ID = int(input('Type in the ID of the tutoree: '))
            c.execute('''SELECT FirstName, LastName FROM TutoreeInfo 
                         WHERE TutoreeID = ? ''', (ID,))
            tutoree = c.fetchone()
            if tutoree != None:
                break
            else:
                print("That isn't a valid ID. Try again.")
        except ValueError:
            print("That isn't a valid ID. Try again.")
    print()
    print('Record: {:10s}\t{:11s}\tHas paid?'.format('Date', 'Time'))
    print('-' * 49)
    for row in c.execute('''SELECT * FROM Records
                            WHERE TutoreeID = ?
                            ORDER BY Date''', (ID,)):
        print(record_str(row))
    print()
    c.execute("SELECT Rate, PaidHours, OwedHours FROM Tutorees WHERE TutoreeID =?", (ID,))
    h = c.fetchone()
    print('{} {} has paid ${:.2f} and owes ${:.2f}.'.format(tutoree[0], tutoree[1], h[0] * h[1], h[0] * h[2]))

def str_to_time(t: str):
    l = t.split(':')
    return datetime.time(int(l[0]), int(l[1]))

def hour_diff(start, end):
    return ((end.hour * 60 + end.minute) - (start.hour * 60 + start.minute))/60.0

def update_record(c: sqlite3.Cursor):
    print()
    print('You are updating the record of a tutoree. Press enter to continue.')
    enter = input()
    print_database(c)
    while True:
        try:
            ID = int(input('Type in the ID of the tutoree: '))
            c.execute('''SELECT * FROM Tutorees 
                         WHERE TutoreeID = ? ''', (ID,))
            tutoree = c.fetchone()
            if tutoree != None:
                break
            else:
                print("That isn't a valid ID. Try again.")
        except ValueError:
            print("That isn't a valid ID. Try again.")
    print_record(c, ID)
    while True:
        try:
            date = str_to_date(input('Type in the date of the record (as ISO): ').strip())
            break
        except ValueError:
            print("That is not a valid date. Try again.")
            
    c.execute("SELECT * FROM Records WHERE TutoreeID = ? AND Date = ?", (ID, date,))
    r = c.fetchone()
    hours = hour_diff(str_to_time(r[2]), str_to_time(r[3]))
    c.execute("SELECT PaidHours, OwedHours FROM Tutorees WHERE TutoreeID =?", (ID,))
    h = c.fetchone()
    paidhours = h[0]
    owedhours = h[1]

    change = not r[4]
    
    if change:
        paidhours += hours
        owedhours -= hours
    else:
        owedhours += hours
        paidhours -= hours
        
    print()
    print(record_str(r))
    print()
    response = input("Are you sure you want to update this record? Yes/No: ").strip().lower()
    while response not in ['yes', 'no']:
        response = input("That isn't a valid answer. Yes/No: ").strip().lower()
    if response == 'yes':
        c.execute("UPDATE Records SET HasPaid = ? WHERE TutoreeID = ? AND Date = ?", (change, ID, date,))
        c.execute("UPDATE Tutorees SET PaidHours = ?, OwedHours = ? WHERE TutoreeID = ?", (paidhours, owedhours,  ID))
        print()
        print('Record successfully updated.')
    if response == 'no':
        print()
        print('Update cancelled.')

def remove_record(c: sqlite3.Cursor):
    print()
    print('You are removing the record of a tutoree. Press enter to continue.')
    enter = input()
    print_database(c)
    while True:
        try:
            ID = int(input('Type in the ID of the tutoree: '))
            c.execute('''SELECT * FROM Tutorees 
                         WHERE TutoreeID = ? ''', (ID,))
            tutoree = c.fetchone()
            if tutoree != None:
                break
            else:
                print("That isn't a valid ID. Try again.")
        except ValueError:
            print("That isn't a valid ID. Try again.")

    print_record(c, ID)
    while True:
        try:
            date = str_to_date(input('Type in the date of the record (as ISO): ').strip())
            break
        except ValueError:
            print("That is not a valid date. Try again.")
            
    c.execute("SELECT * FROM Records WHERE TutoreeID = ? AND Date = ?", (ID, date,))
    r = c.fetchone()
    hours = hour_diff(str_to_time(r[2]), str_to_time(r[3]))
    c.execute("SELECT PaidHours, OwedHours FROM Tutorees WHERE TutoreeID =?", (ID,))
    h = c.fetchone()
    paidhours = h[0]
    owedhours = h[1]

    if r[4]:
        paidhours -= hours
    else:
        owedhours -= hours
    print()
    print(record_str(r))
    print()
    response = input("Are you sure you want to delete this record? Yes/No: ").strip().lower()
    while response not in ['yes', 'no']:
        response = input("That isn't a valid answer. Yes/No: ").strip().lower()
    if response == 'yes':
        c.execute("DELETE FROM Records WHERE TutoreeID = ? AND Date = ?", (ID, date,))
        c.execute("UPDATE Tutorees SET PaidHours = ?, OwedHours = ? WHERE TutoreeID = ?", (paidhours, owedhours,  ID))
        print()
        print('Record successfully removed.')
    if response == 'no':
        print()
        print('Removal cancelled.')

commands.update({'PD': print_database, 'AT': add_tutoree, 'RT': remove_tutoree, 'PR': print_records, 'AR': add_record, 'UR': update_record, 'RR': remove_record})

if __name__ == '__main__':
    user_interface()

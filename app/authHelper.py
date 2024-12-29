from database import db
from psycopg2 import IntegrityError


def getUser(username):
    db.refreshDatabaseConnection()
    query = f"SELECT * FROM users WHERE username='{username}'"
    user = db.executeQuery(query)

    if len(user) == 0:
        return None
    else: return user[0]

def registerUser(username, password, email, role):
    error = None
    try:
        if db.cur is None or db.cur.closed: db.cur = db.conn.cursor()
        db.cur.execute(
            "INSERT INTO users (username, psw, email, user_role) VALUES (%s, %s, %s, %s)",
            (username, password, email, role),
        )
        db.conn.commit()
    except IntegrityError:
        error = f"User {username} is already registered."

    return error

def deleteUser(id):
    error = None
    try:
        if db.cur is None or db.cur.closed: db.cur = db.conn.cursor()
        db.cur.execute(
            "DELETE FROM users WHERE user_id = %s ",
            (str(id),)
        )
        db.conn.commit()
    except IntegrityError:
        error = f"User {id} does not exist."

    return error
def updateUser(val):
    error = None
    try:
        if db.cur is None or db.cur.closed: db.cur = db.conn.cursor()
        parts = []
        for k in val.keys():
            if k != 'user_id':
                parts.append(f'{k}=%s')
        db.cur.execute(
            "UPDATE users SET " + ', '.join(parts) + " WHERE userid = %s",
            list(val.values())
        )
        db.conn.commit()
        db.refreshDatabaseConnection()

    except IntegrityError:
        error = f"User {id} does not exist."

    return error

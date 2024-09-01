import sqlite3

from contextlib import contextmanager


@contextmanager
def connect(db_filename):
    conn = sqlite3.connect(db_filename)
    try:
        cur = conn.cursor()
        yield cur

    except sqlite3.IntegrityError:
        print('User already in database')

    except Exception as e:
        conn.rollback()
        raise e

    finally:
        conn.commit()
        conn.close()


def verify_user(db, id):
    with connect(db.filename) as cur:
        if cur.execute(f'SELECT EXISTS(SELECT 1 FROM Users WHERE id = {id});').fetchone() == (0,):
            return False
        return True


def add_user(db, id, username):
    with connect(db.filename) as cur:
        cur.execute('INSERT INTO Users (id, username) VALUES (?, ?)', (id, username))


def get_all_users(db):
    with connect(db.filename) as cur:
        res = []
        for user_record in cur.execute('SELECT id FROM Users').fetchall():
            try:
                res.append(user_record[0])
            except Exception as e:
                print(f'Warning {e}')
                continue
    return res

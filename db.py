import sqlite3

class DatabaseConn:
    def __init__(self, db_str):
        self.db_str = db_str
        self.connection = None
        self.cursor = None

    def __enter__(self):
        self.connection = sqlite3.connect(self.db_str)
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON;")
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:
            print(f"Exception type: {exc_type}")
            print(f"Exception value: {exc_value}")
            print(f"Traceback: {traceback}")
            self.connection.rollback()
        else:
            self.connection.commit()
        if self.connection:
            self.connection.close()
        return False
    
    def fetchall(self):
        return self.cursor.fetchall()

    def fetchone(self):
        return self.cursor.fetchone()

    def execute(self, sql, params=None):
        if params:
            return self.cursor.execute(sql, params)
        return self.cursor.execute(sql)
    
    def commit(self):
        if self.connection:
            self.connection.commit()
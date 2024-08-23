import sqlite3
import pandas as pd

class Database:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.tables = {}  # Store references to Table objects

    def __del__(self):
        self.conn.close()

    # Dictionary-like access
    def __getitem__(self, table_name):
        if table_name in self.tables:
            return self.tables[table_name]
        else:
            return self.get_table(table_name)

    def __setitem__(self, table_name, table_obj):
        self.tables[table_name] = table_obj

    def __delitem__(self, table_name):
        if table_name in self.tables:
            del self.tables[table_name]

    def get_table(self, table_name):
        if table_name not in self.tables:
            table = Table(self.conn, self.cursor, table_name)
            self.tables[table_name] = table
        return self.tables[table_name]

    def add_table(self, table_name):
        table = Table(self.conn, self.cursor, table_name)
        self.tables[table_name] = table
        return table

class Table:
    def __init__(self, conn, cursor, table_name):
        self.conn = conn
        self.cursor = cursor
        self.table_name = table_name

        if not self.check_table_exists(self.table_name):
            self.create_table()

    def update_table_from_csv(self, csv_file):
        new_data = pd.read_csv(csv_file)
        new_data.to_sql(self.table_name, self.conn, if_exists='append', index=False)

    def get_data_from_table(self):
        query = f'''
        SELECT * FROM {self.table_name}
        '''
        data = pd.read_sql(query, self.conn)
        return data

    def check_table_exists(self, table_name):
        query = f'''
        SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'
        '''
        self.cursor.execute(query)
        return self.cursor.fetchone() is not None

    def create_table(self):
        query = f'''
        CREATE TABLE {self.table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT,
            incoming BOOLEAN NOT NULL
        )
        '''
        self.cursor.execute(query)
        self.conn.commit()

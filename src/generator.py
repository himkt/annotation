import sqlite3


class SimpleTextGenerator:

    def __init__(self, input_file):
        self.input_file = input_file

    def __next__(self):
        return self.input_file.__next__()


class DBTextGenerator:

    def __init__(self, dbpath, query):
        conn = sqlite3.connect(dbpath)
        cursor = conn.cursor()
        self.res = cursor.execute(query)

    def __next__(self):
        return self.res.__next__()

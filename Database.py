import sqlite3
from queue import Queue
from threading import Thread


class Database:
    instance = None
    MEASUREMENTS_TABLE = 'measurements'

    def __init__(self):
        if Database.instance is not None:
            raise BaseException('Database already exists!')

        self.queue = Queue()
        Thread(target=self.thread_func).start()
        Database.instance = self

    def thread_func(self):
        self.db = sqlite3.connect('data.db')

        c = self.db.cursor()
        c.execute('SELECT count(*) FROM sqlite_master WHERE type = \'table\' AND tbl_name = :name',
                  {'name': Database.MEASUREMENTS_TABLE})
        count = c.fetchone()[0]
        if count == 0:
            c.execute('CREATE TABLE %s (ts real, type integer, value real)' % Database.MEASUREMENTS_TABLE)

        while True:
            item = self.queue.get()
            c = self.db.cursor()
            c.execute('INSERT INTO %s VALUES (?, ?, ?)' % Database.MEASUREMENTS_TABLE, item)
            self.db.commit()

    def insert_measurement(self, timestamp, type_id, value):
        self.queue.put((timestamp, type_id, value))

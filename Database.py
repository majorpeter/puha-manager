import sqlite3
from queue import Queue
from threading import Thread


class Database:
    instance = None
    MEASUREMENTS_TABLE = 'measurements'
    MEASUREMENTS_SORT_FIELD = 'ts'

    def __init__(self):
        if Database.instance is not None:
            raise BaseException('Database already exists!')

        self._queue = Queue()
        self._outqueue = Queue(maxsize=1)

        Thread(target=self.thread_func, daemon=True).start()
        Database.instance = self

    def thread_func(self):
        self.db = sqlite3.connect('data.db')

        c = self.db.cursor()
        c.execute('SELECT count(*) FROM sqlite_master WHERE type = \'table\' AND tbl_name = :name',
                  {'name': Database.MEASUREMENTS_TABLE})
        count = c.fetchone()[0]
        if count == 0:
            c.execute('CREATE TABLE %s (%s real, type integer, value real)' % (Database.MEASUREMENTS_TABLE, Database.MEASUREMENTS_SORT_FIELD))

        while True:
            item = self._queue.get()
            c = self.db.cursor()
            if item['operation'] == 'insert':
                if item['table'] == Database.MEASUREMENTS_TABLE:
                    c.execute('INSERT INTO %s VALUES (?, ?, ?)' % Database.MEASUREMENTS_TABLE, item['data'])
                    self.db.commit()
                else:
                    raise BaseException('What table? %s' % item['table'])
            elif item['operation'] == 'fetch':
                if item['table'] == Database.MEASUREMENTS_TABLE:
                    result = []
                    for row in c.execute('SELECT * FROM (SELECT * FROM %s WHERE type = ? ORDER BY %s DESC LIMIT %d) ORDER BY %s ASC' %
                              (Database.MEASUREMENTS_TABLE, Database.MEASUREMENTS_SORT_FIELD, item['count'],
                               Database.MEASUREMENTS_SORT_FIELD), (item['type_id'],)):
                        result.append({'time': row[0], 'measurement': row[2]})
                    self._outqueue.put(result)
                else:
                    raise BaseException('What table? %s' % item['table'])

    def insert_measurement(self, timestamp, type_id, value):
        self._queue.put({
            'operation': 'insert',
            'table': Database.MEASUREMENTS_TABLE,
            'data': (timestamp, type_id, value)
        })

    def fetch_latest_measurements(self, type_id, count):
        self._queue.put({
            'operation': 'fetch',
            'table': Database.MEASUREMENTS_TABLE,
            'type_id': type_id,
            'count': count
        })
        return self._outqueue.get()

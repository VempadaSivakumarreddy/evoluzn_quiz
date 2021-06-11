import MySQLdb
from MySQLdb.cursors import DictCursor

class Database:
    @staticmethod
    def connect_dbs():
        dbPrefix = 'Quiz'
        econ = MySQLdb.connect(
            user = 'root',
            passwd = 'Siva@0103',
            host = 'localhost',
            db = dbPrefix,
            cursorclass = MySQLdb.cursors.DictCursor
        )
        return econ 
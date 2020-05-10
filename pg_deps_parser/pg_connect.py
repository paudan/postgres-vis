import psycopg2

class PgConnect:

    def __init__(self, dbhost, dbname, dbuser, dbpass):
        self.dbhost = dbhost
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.connection, self.cursor = None, None

    def __enter__(self):
        pass

    def connect(self):
        try:
            self.connection = psycopg2.connect("dbname='%s' user='%s' host='%s' password='%s'"
                                    % (self.dbname, self.dbuser, self.dbhost, self.dbpass))
            self.cursor = self.connection.cursor()
        except psycopg2.OperationalError as e:
            print("Error connecting to database: " + e.pgerror)
            self.cursor = None
        return self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.cursor:
            self.cursor.close()
        if self.connection and not self.connection.closed:
            self.connection.close()

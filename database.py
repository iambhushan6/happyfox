import sqlite3
connection = sqlite3.connect('mail.db')

cursor = connection.cursor()


class DatabaseService:

    def __init__(self) -> None:
        pass

    def get_data(self, ):
        cursor.execute("SELECT * FROM `mail`")
        rows = cursor.fetchall()
        for row in rows:
            print(row)


    def insert_data(self, row_info):
        sql = ''' INSERT INTO `mail` (`FROM`,`Date`,`Subject`,`To`,`Content`,`id`)
                VALUES(?,?,?,?,?,?) '''

        cursor = connection.cursor()
        cursor.execute(sql, row_info)
        connection.commit()
        return True

    def drop_table(self):

        dropTableStatement = "DROP TABLE IF  EXISTS `mail`"

        cursor.execute(dropTableStatement)
        return True


    def create_table(self):

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS `mail` (
                `id` integer PRIMARY KEY,
                `FROM` text NOT NULL,
                `Date` datetime  NOT NULL,
                `Subject` text NOT NULL,
                `To` text NOT NULL,
                `Content` text NOT NULL
            );
        """)

        return True


    def build_and_execute_query(self, field_name: str, operator: str, value: str):

        query = "SELECT * FROM `mail` WHERE `{0}` {1} {2}".format(field_name,operator,value)
        cursor.execute(query)
        return cursor.fetchall()


    def build_and_execute_date_query(self, operator:str ,value:str):
        query="SELECT * FROM  `mail` where Date {0} strftime('%m/%d/%Y %H:%M', datetime('now','localtime'), '{1}');".format(operator,value)
        cursor.execute(query)
        return cursor.fetchall()
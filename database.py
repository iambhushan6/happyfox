import sqlite3
import datetime
connection = sqlite3.connect('mail.db')

cursor = connection.cursor()


def get_data():
    cursor.execute("SELECT * FROM `mail`")

    rows = cursor.fetchall()

    for row in rows:
        print(row)


def insert_data(row_info):
    sql = ''' INSERT INTO `mail` (`FROM`,`Date`,`Subject`,`To`,`Content`,`id`)
              VALUES(?,?,?,?,?,?) '''

    cursor = connection.cursor()
    cursor.execute(sql, row_info)
    connection.commit()
    # print("Inserted")
    return True

def drop_table():

    dropTableStatement = "DROP TABLE IF  EXISTS `mail`"

    cursor.execute(dropTableStatement)
    return True


def create_table():

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


def select_data(field_name,operator,value):
    
        
    query = "SELECT * FROM `mail` WHERE `{0}` {1} {2}".format(field_name,operator,value)
    # print(query)
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


def date_query(operator,value):
    query="SELECT * FROM  `mail` where Date {0} strftime('%m/%d/%Y %H:%M', datetime('now','localtime'), '{1}');".format(operator,value)
    # print(query)
    cursor.execute(query)
    rows = cursor.fetchall()
    return rows


# get_data()
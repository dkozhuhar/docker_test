from datetime import datetime
import redis
import mysql.connector
import time
MYSQL_SERVER = 'mysql'
REDIS_SERVER = 'redis'


def main():
    print("main start " + datetime.now().__str__())
    try:
        r = redis.Redis(host=REDIS_SERVER, port=6379, db=1)
        m = mysql.connector.connect(user='root',
                                    password='secret',
                                    host=MYSQL_SERVER,
                                    database='user_statistics')
        mysql_cursor = m.cursor()
        # Switching active and flushToMysql cache
        if r.dbsize() == 0:
            r.swapdb(0, 1)
        if r.dbsize() != 0:
            print("Starting scanning redis DB at " + datetime.now().__str__())
            cursor = '0'
            while cursor != 0:
                cursor, data = r.scan(cursor=cursor,
                                      count=10000)
                key_values = r.mget(data)
                data = list(zip(data, key_values))
                mysqlstring = "INSERT INTO tag_statistics(tag, tag_count) VALUES "
                for _ in data:
                    mysqlstring += "(\"" + _[0].decode('utf-8') + "\"," + _[1].decode('utf-8') + "),"
                mysqlstring = mysqlstring[:len(mysqlstring)-1] + " AS new(new_tag, new_tag_count) ON DUPLICATE KEY UPDATE tag_count = tag_count + new_tag_count"
                print("Updating MySQL db at " + datetime.now().__str__())
                mysql_cursor.execute(mysqlstring)
                print("Updated Mysql db at " + datetime.now().__str__())

            mysql_cursor.close()
            m.commit()
            print("Committed changes at Mysql db at " + datetime.now().__str__())
            r.flushdb(asynchronous=True)
        r.close()
        m.close()
    except mysql.connector.errors.InterfaceError as err:
        print("Mysql is not accessible: " + err.__str__())
    except mysql.connector.errors.DatabaseError as err:
        print("Mysql is not accessible: " + err.__str__())
    except redis.exceptions.ConnectionError as err:
        print("Redis is not accesible: " + err.__str__())


while True:
    main()
    time.sleep(10)

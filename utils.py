import pymysql.cursors


def run_query(query):
    connection = pymysql.connect(host='52.66.79.237',
                             user='candidate',
                             password='asdfgh123',
                             db='servify_assignment',
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
    cursor = connection.cursor()
    cursor.execute(query, None)
    return cursor.fetchall()

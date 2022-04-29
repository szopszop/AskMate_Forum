import database_common


@database_common.connection_handler
def get_all_questions(cursor):
    query = """
        SELECT *
        FROM question
        ORDER BY submission_time"""
    cursor.execute(query)
    return cursor.fetchall()


@database_common.connection_handler
def get_last_question(cursor):
    query = """
        SELECT id
        FROM question
        ORDER BY submission_time DESC"""
    cursor.execute(query)
    return cursor.fetchone()


@database_common.connection_handler
def add_question_to_database(cursor, question):
    query = """
        INSERT INTO question (submission_time, view_number, vote_number, title, message, image)
        VALUES (current_timestamp, 0, 0, %(title)s, %(message)s, %(image)s)"""
    cursor.execute(query, {'title': question['title'],
                           'message': question['message'],
                           'image': question['image']})
    question = get_last_question()
    return question['id']

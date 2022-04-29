from werkzeug.utils import secure_filename
import os
import database_common


BASEPATH = os.path.dirname(os.path.abspath(__file__)) + '/'
ALLOWED_EXTENSIONS = {'jpg', 'png'}
UPLOAD_FOLDER = 'sample_data/uploads'


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_image(file):
    if file and file.filename != '' and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(BASEPATH + UPLOAD_FOLDER, filename))
        return filename


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


@database_common.connection_handler
def add_answer_to_database(cursor, answer):
    query = """
        INSERT INTO answer (submission_time, vote_number, question_id, message, image)
        VALUES (current_timestamp, 0, %(question_id)s, %(message)s, %(image)s)"""
    cursor.execute(query, {'question_id': answer['question_id'],
                           'message': answer['message'],
                           'image': answer['image']})


@database_common.connection_handler
def get_question(cursor, question_id):
    query = """
        SELECT *
        FROM question
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_answer(cursor, answer_id):
    query = """
        SELECT *
        FROM answer
        WHERE id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id})
    return cursor.fetchone()


@database_common.connection_handler
def get_answers_for_question(cursor, question_id):
    query = """
        SELECT *
        FROM answer
        WHERE question_id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})
    return cursor.fetchall()


@database_common.connection_handler
def update_question_in_database(cursor, question):
    query = """
        UPDATE question
        SET title = %(title)s,
        message = %(message)s,
        view_number = %(view_number)s,
        vote_number = %(vote_number)s,
        image = %(image)s
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'title': question['title'],
                           'message': question['message'],
                           'view_number': question['view_number'],
                           'vote_number': question['vote_number'],
                           'image': question['image'],
                           'question_id': question['id']})


@database_common.connection_handler
def update_answer_in_database(cursor, answer):
    query = """
        UPDATE answer
        SET message = %(message)s,
        vote_number = %(vote_number)s,
        image = %(image)s
        WHERE id = %(answer_id)s"""
    cursor.execute(query, {'message': answer['message'],
                           'vote_number': answer['vote_number'],
                           'image': answer['image'],
                           'answer_id': answer['id']})


@database_common.connection_handler
def delete_question(cursor, question_id):
    query = """
        DELETE
        FROM question
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': question_id})


@database_common.connection_handler
def delete_answer(cursor, answer_id):
    answer = get_answer(answer_id)
    query = """
        SELECT *
        FROM question
        WHERE id = %(question_id)s"""
    cursor.execute(query, {'question_id': answer['question_id']})
    question = cursor.fetchone()

    query = """
        DELETE
        FROM answer
        WHERE id = %(answer_id)s"""
    cursor.execute(query, {'answer_id': answer_id})

    return question['id']

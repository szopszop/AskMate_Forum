import csv
import os
from flask import redirect, url_for
from werkzeug.utils import secure_filename


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


def get_data_from_file(filename):
    with open(BASEPATH + filename) as data_file:
        read_data_file = csv.DictReader(data_file)
        return list(read_data_file)


def build_headers(data_headers):
    headers = []
    for header in data_headers:
        if '_' in header:
            header = ' '.join([header.capitalize() for header in header.split('_')])
            headers.append(header)
        else:
            headers.append(header.capitalize())
    return headers


def append_new_data_to_file(new_data, filename, headers):
    with open(BASEPATH + filename, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writerow(new_data)


def update_data_in_file(data, filename, headers):
    with open(BASEPATH + filename, 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def get_answers_for_question(question_id):
    all_answers = get_all_answers()
    answers = []
    for answer in all_answers:
        if answer['question_id'] == str(question_id):
            answers.append(answer)
    return answers


def get_all_questions():
    return get_data_from_file('sample_data/question.csv')


def get_question(question_id):
    questions = get_all_questions()
    for question in questions:
        if question['id'] == str(question_id):
            return question


def get_all_answers():
    return get_data_from_file('sample_data/answer.csv')

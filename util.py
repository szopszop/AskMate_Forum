import data_handler
import os
from datetime import datetime

import data_manager

QUESTION_HEADERS = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_HEADERS = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']


def sort_by(items, key=None, order=None):
    if key is None:  # default sort by most recent
        key = 'time'
    if order is None:
        order = 'desc'
    order = False if order == 'asc' else True
    match key:
        case 'title':
            return sorted(items, key=lambda x: x['title'], reverse=order)
        case 'time':
            return sorted(items, key=lambda x: x['submission_time'], reverse=order)
        case 'message':
            return sorted(items, key=lambda x: x['message'], reverse=order)
        case 'views':
            return sorted(items, key=lambda x: int(x['view_number']), reverse=order)
        case 'votes':
            return sorted(items, key=lambda x: int(x['vote_number']), reverse=order)


def vote_on(post_type, id_, endpoint):
    post = data_manager.get_answer(id_) if post_type == 'answer' else data_manager.get_question(id_)
    if endpoint.endswith('vote-up'):
        post['vote_number'] = int(post['vote_number']) + 1
    elif endpoint.endswith('vote-down'):
        post['vote_number'] = int(post['vote_number']) - 1
    if post_type == 'answer':
        data_manager.update_answer_in_database(post)
        return post['question_id']
    else:
        data_manager.update_question_in_database(post)


def delete_all_answers(question_id):
    answers = []
    all_answers = data_handler.get_all_answers()
    for answer in all_answers:
        if answer['question_id'] != str(question_id):
            answers.append(answer)
        else:
            if os.path.isfile(data_handler.BASEPATH + answer['image']):
                os.unlink(data_handler.BASEPATH + answer['image'])
    data_handler.update_data_in_file(answers, 'sample_data/answer.csv', ANSWER_HEADERS)


def delete_question(question_id):
    questions = []
    all_questions = data_handler.get_all_questions()
    for question in all_questions:
        if question['id'] != str(question_id):
            questions.append(question)
        else:
            if os.path.isfile(data_handler.BASEPATH + question['image']):
                os.unlink(data_handler.BASEPATH + question['image'])
    delete_all_answers(question_id)
    data_handler.update_data_in_file(questions, 'sample_data/question.csv', QUESTION_HEADERS)


def delete_answer(answer_id):
    answers = []
    all_answers = data_handler.get_all_answers()
    for answer in all_answers:
        if answer['id'] != str(answer_id):
            answers.append(answer)
        else:
            if os.path.isfile(data_handler.BASEPATH + answer['image']):
                os.unlink(data_handler.BASEPATH + answer['image'])
            question_id_to_redirect = answer['question_id']
    data_handler.update_data_in_file(answers, 'sample_data/answer.csv', ANSWER_HEADERS)
    return question_id_to_redirect


def create_answer(question_id, message, filename=None):
    answer = {
        'question_id': question_id,
        'message': message
    }
    if filename:
        answer['image'] = f'{data_handler.UPLOAD_FOLDER}/{filename}'
    else:
        answer['image'] = "NULL"
    data_manager.add_answer_to_database(answer)


def create_question(title, message, filename=None):
    question = {
        'title': title,
        'message': message
    }
    if filename:
        question['image'] = f'{data_handler.UPLOAD_FOLDER}/{filename}'
    else:
        question['image'] = "NULL"
    question_id = data_manager.add_question_to_database(question)
    return question_id


def update_question(question_id, title, message, filename=None):
    question = data_manager.get_question(question_id)
    question['title'] = title
    question['message'] = message
    if filename:
        if os.path.isfile(data_handler.BASEPATH + question['image']):
            os.unlink(data_handler.BASEPATH + question['image'])
        question['image'] = f'{data_handler.UPLOAD_FOLDER}/{filename}'
    data_manager.update_question_in_database(question)

import os
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


def create_answer(question_id, message, filename=None):
    answer = {
        'question_id': question_id,
        'message': message
    }
    if filename:
        answer['image'] = f'{data_manager.UPLOAD_FOLDER}/{filename}'
    else:
        answer['image'] = None
    data_manager.add_answer_to_database(answer)


def create_question(title, message, filename=None):
    question = {
        'title': title,
        'message': message
    }
    if filename:
        question['image'] = f'{data_manager.UPLOAD_FOLDER}/{filename}'
    else:
        question['image'] = None
    question_id = data_manager.add_question_to_database(question)
    return question_id


def update_question(question_id, title, message, filename=None):
    question = data_manager.get_question(question_id)
    question['title'] = title
    question['message'] = message
    if filename:
        if question['image']:
            os.unlink(data_manager.BASEPATH + question['image'])
        question['image'] = f'{data_manager.UPLOAD_FOLDER}/{filename}'
    data_manager.update_question_in_database(question)

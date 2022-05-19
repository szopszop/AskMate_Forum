import os
import data_manager
from flask import session
from bleach import clean
from markupsafe import Markup

QUESTION_HEADERS = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image', 'user_id']
ANSWER_HEADERS = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image', 'user_id']
POINTS_FOR_ANSWER = 10
POINTS_FOR_QUESTION = 5
MINUS_POINTS = -2


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


def vote_on(post_type, post_id, endpoint, voting_user):
    post = data_manager.get_answer(post_id) if post_type == 'answer' else data_manager.get_question(post_id)
    post_author = data_manager.get_post_author_by_post_id(post_id, post_type) if post['user_id'] else None
    if voting_user == post_author:
        return f'You cannot vote on your {post_type}', 'error'
    if endpoint.endswith('vote-up'):
        post['vote_number'] = int(post['vote_number']) + 1
        reputation_change = POINTS_FOR_ANSWER if post_type == 'answer' else POINTS_FOR_QUESTION
    elif endpoint.endswith('vote-down'):
        post['vote_number'] = int(post['vote_number']) - 1
        reputation_change = MINUS_POINTS
    data_manager.change_reputation(post['user_id'], reputation_change)
    update_post(post_type, post)
    return f'Your vote is added and {post_author} got {reputation_change} reputation points', 'success'


def create_answer(question_id, message, user_id, filename=None):
    answer = {
        'question_id': question_id,
        'message': message,
        'user_id': user_id
    }
    if filename:
        answer['image'] = f'{data_manager.UPLOAD_FOLDER}/{filename}'
    else:
        answer['image'] = None
    data_manager.add_answer_to_database(answer)


def create_question(title, message, user_id, filename=None):
    question = {
        'title': title,
        'message': message,
        'user_id': user_id
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
        delete_file(question)
        question['image'] = f'{data_manager.UPLOAD_FOLDER}/{filename}'
    else:
        delete_file(question)
    data_manager.update_question_in_database(question)


def update_comment(comment_id, message):
    comment = data_manager.get_comment_by_comment_id(comment_id)
    comment['message'] = message
    comment['edited_count'] = 1
    data_manager.update_comment_in_database(comment)


def update_answer(answer_id, message, filename=None):
    answer = data_manager.get_answer(answer_id)
    answer['message'] = message
    if filename:
        delete_file(answer)
        answer['image'] = f'{data_manager.UPLOAD_FOLDER}/{filename}'
    else:
        delete_file(answer)
    data_manager.update_answer_in_database(answer)


def delete_file(post_type):
    if post_type is None:
        pass
    elif post_type['image']:
        try:
            os.unlink(data_manager.BASEPATH + post_type['image'])
        except FileNotFoundError:
            print('File not found, skipping...')
        finally:
            post_type['image'] = None


def increase_views(question):
    question['view_number'] += 1
    data_manager.update_question_in_database(question)


def create_comment(question_id, answer_id, message, user_id):
    comment = {
        'question_id': question_id,
        'answer_id': answer_id,
        'message': message,
        'user_id': user_id
    }
    data_manager.add_comment_to_database(comment)


def highlight_question_search_results(question, phrase):
    question['title'] = question['title'].replace(phrase, f'<mark>{phrase}</mark>')
    question['message'] = question['message'].replace(phrase, f'<mark>{phrase}</mark>')
    return question


def highlight_answer_search_results(answer, phrase):
    answer['message'] = answer['message'].replace(phrase, f'<mark>{phrase}</mark>')
    return answer


def highlight_results(posts, phrase, added_questions_id, search_results):
    for post in posts:
        if len(post) == len(ANSWER_HEADERS):
            post = data_manager.get_question(post['question_id'])
        print('len post', len(post))
        print('len answers headers', len(ANSWER_HEADERS))
        print('post', post)
        post = highlight_question_search_results(post, phrase)
        post['answers'] = []
        question_answers = data_manager.get_answers_for_question(post['id'])
        for question_answer in question_answers:
            question_answer = highlight_answer_search_results(question_answer, phrase)
            post['answers'].append(question_answer)
        if post['id'] not in added_questions_id:
            search_results.append(post)
            added_questions_id.append(post['id'])


def current_user():
    return session.get('username')


def user_logged_in():
    return 'username' in session


def get_question_id_from_answer(answer_id):
    answer = data_manager.get_answer(answer_id)
    return answer['question_id']


def update_post(post_type, post):
    if post_type == 'answer':
        data_manager.update_answer_in_database(post)
    else:
        data_manager.update_question_in_database(post)





def do_clean(text, **kw):
    """Perform clean and return a Markup object to mark the string as safe.
    This prevents Jinja from re-escaping the result."""
    return Markup(clean(text, **kw))

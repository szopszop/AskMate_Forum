import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory
import data_handler
import util
from datetime import datetime
from werkzeug.utils import secure_filename

QUESTION_HEADER = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_HEADER = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/list', methods=['GET', 'POST'])
def list():
    questions = data_handler.get_data_from_file('sample_data/question.csv')
    key, order = None, None
    query_params = request.args
    if 'order_by' in query_params:
        key = query_params.get('order_by')
    if 'order_direction' in query_params:
        order = query_params.get('order_direction')
    questions = util.sort_by(questions, key, order)
    return render_template('list.html', questions=questions)


@app.route('/add-question', methods=['GET', 'POST'])
def ask_a_question():
    questions = data_handler.get_data_from_file('sample_data/question.csv')
    if request.method == 'POST':
        timestamp = datetime.now().timestamp()
        question = {
            'id': len(questions) + 1,
            'submission_time': round(timestamp),
            'view_number': 0,
            'vote_number': 0
        }
        question = question | request.form.to_dict()
        file = request.files['image']
        filename = data_handler.save_image(file)
        if filename:
            question['image'] = f'{data_handler.UPLOAD_FOLDER}/{filename}'
        data_handler.append_new_data_to_file(question, 'sample_data/question.csv', QUESTION_HEADER)
        return redirect(f'/question/{question["id"]}')
    return render_template("add-edit-question.html")


@app.route('/question/<int:question_id>/new-answer', methods=["GET", "POST"])
def answer(question_id):
    all_answers = data_handler.get_data_from_file('sample_data/answer.csv')
    if request.method == 'POST':
        timestamp = datetime.now().timestamp()
        answer = {
            'id': int(all_answers[-1]['id']) + 1,
            'submission_time': round(timestamp),
            'vote_number': 0,
            'question_id': question_id,
            'message': request.form.get("message")
        }
        file = request.files['image']
        filename = data_handler.save_image(file)
        if filename:
            answer['image'] = f'{data_handler.UPLOAD_FOLDER}/{filename}'
        data_handler.append_new_data_to_file(answer, 'sample_data/answer.csv', ANSWER_HEADER)
        return redirect(f'/question/{question_id}')
    return render_template("answer.html", id=question_id)


@app.route('/upload/<filename>')
def send_image(filename):
    return send_from_directory(data_handler.UPLOAD_FOLDER, filename)


@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def questions(question_id):
    questions = data_handler.get_data_from_file('sample_data/question.csv')
    all_answers = data_handler.get_data_from_file('sample_data/answer.csv')
    for question in questions:
        if question['id'] == str(question_id):
            the_question = question
    answers = []
    for answer in all_answers:
        if answer['question_id'] == str(question_id):
            answers.append(answer)
    return render_template('questions.html', question=the_question, answers=answers)


@app.route('/question/<int:question_id>/vote-up', methods=["POST"])
@app.route('/question/<int:question_id>/vote-down', methods=["POST"])
@app.route('/answer/<int:answer_id>/vote-up', methods=["POST"])
@app.route('/answer/<int:answer_id>/vote-down', methods=["POST"])
def vote(question_id=None, answer_id=None):
    endpoint = str(request.url_rule)
    if endpoint.startswith('/question'):
        return util.vote_on('question', question_id, QUESTION_HEADER, endpoint)
    elif endpoint.startswith('/answer'):
        return util.vote_on('answer', answer_id, ANSWER_HEADER, endpoint)


@app.route('/question/<int:question_id>/edit', methods=["GET", "POST"])
def edit_question(question_id):
    questions = data_handler.get_data_from_file('sample_data/question.csv')
    for question in questions:
        if question['id'] == str(question_id):
            break
    if request.method == 'POST':
        question['title'] = request.form.get('title')
        question['message'] = request.form.get('message')
        file = request.files['image']
        filename = data_handler.save_image(file)
        if filename:
            if os.path.isfile(data_handler.BASEPATH+question['image']):
                os.unlink(data_handler.BASEPATH+question['image'])
            question['image'] = f'{data_handler.UPLOAD_FOLDER}/{filename}'
        data_handler.update_data_in_file(questions, 'sample_data/question.csv', QUESTION_HEADER)
        return redirect(f'/question/{question_id}')
    return render_template('add-edit-question.html', question=question)


@app.route('/question/<int:question_id>/delete', methods=["POST"])
def delete_question(question_id):
    questions = []
    all_questions = data_handler.get_data_from_file('sample_data/question.csv')
    for question in all_questions:
        if question['id'] != str(question_id):
            questions.append(question)
        else:
            if os.path.isfile(data_handler.BASEPATH + question['image']):
                os.unlink(data_handler.BASEPATH + question['image'])

    data_handler.update_data_in_file(questions, 'sample_data/question.csv', QUESTION_HEADER)
    return redirect(url_for('list'))


@app.route('/answer/<int:answer_id>/delete', methods=["POST"])
def delete_answer(answer_id):
    answers = []
    all_answers = data_handler.get_data_from_file('sample_data/answer.csv')
    for answer in all_answers:
        if answer['id'] != str(answer_id):
            answers.append(answer)
        else:
            if os.path.isfile(data_handler.BASEPATH + answer['image']):
                os.unlink(data_handler.BASEPATH + answer['image'])
            question_id_to_delete = answer['question_id']
    data_handler.update_data_in_file(answers, 'sample_data/answer.csv', ANSWER_HEADER)
    return redirect(f'/question/{question_id_to_delete}')


if __name__ == "__main__":
    app.run(
        debug=True
    )

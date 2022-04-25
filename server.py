import os
from flask import Flask, request, render_template, redirect, send_from_directory, url_for
import data_handler
import util


QUESTION_HEADERS = ['id', 'submission_time', 'view_number', 'vote_number', 'title', 'message', 'image']
ANSWER_HEADERS = ['id', 'submission_time', 'vote_number', 'question_id', 'message', 'image']

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/list')
def list_questions():
    questions = data_handler.get_all_questions()
    key = request.args.get('order_by')
    order = request.args.get('order_direction')
    questions = util.sort_by(questions, key, order)
    return render_template('list.html', questions=questions)


@app.route('/add-question')
def write_a_question():
    return render_template("add-edit-question.html")


@app.route('/add-question', methods=['POST'])
def ask_a_question():
    title = request.form.get('title')
    message = request.form.get("message")
    file = request.files['image']
    filename = data_handler.save_image(file)
    image_path = f'{data_handler.UPLOAD_FOLDER}/{filename}' if filename else None
    question = util.create_question(title, message, image_path)
    data_handler.append_new_data_to_file(question, 'sample_data/question.csv', QUESTION_HEADERS)
    return redirect(f'/question/{question["id"]}')


@app.route('/question/<int:question_id>/new-answer')
def write_an_answer(question_id):
    return render_template("add-answer.html", id=question_id)


@app.route('/question/<int:question_id>/new-answer', methods=["POST"])
def post_an_answer(question_id):
    message = request.form.get("message")
    file = request.files['image']
    filename = data_handler.save_image(file)
    image_path = f'{data_handler.UPLOAD_FOLDER}/{filename}' if filename else None
    answer = util.create_answer(question_id, message, image_path)
    data_handler.append_new_data_to_file(answer, 'sample_data/answer.csv', ANSWER_HEADERS)
    return redirect(f'/question/{question_id}')


@app.route('/question/<question_id>/image')
def send_question_image(question_id):
    question = data_handler.get_question(question_id)
    return send_from_directory(data_handler.UPLOAD_FOLDER, question['image'].rsplit('/', 1)[1])


@app.route('/answer/<answer_id>/image')
def send_answer_image(answer_id):
    answer = data_handler.get_answer(answer_id)
    return send_from_directory(data_handler.UPLOAD_FOLDER, answer['image'].rsplit('/', 1)[1])


@app.route('/question/<int:question_id>')
def questions(question_id):
    question = data_handler.get_question(question_id)
    answers = data_handler.get_answers_for_question(question_id)
    return render_template('question.html', question=question, answers=answers)


@app.route('/question/<int:question_id>/vote-up', methods=["POST"])
@app.route('/question/<int:question_id>/vote-down', methods=["POST"])
def vote_on_question(question_id):
    endpoint = str(request.url_rule)
    util.vote_on('question', question_id, QUESTION_HEADERS, endpoint)
    return redirect(url_for('list_questions'))


@app.route('/answer/<int:answer_id>/vote-up', methods=["POST"])
@app.route('/answer/<int:answer_id>/vote-down', methods=["POST"])
def vote_on_answer(answer_id):
    endpoint = str(request.url_rule)
    question_id = util.vote_on('answer', answer_id, ANSWER_HEADERS, endpoint)
    return redirect(f"/question/{question_id}")


@app.route('/question/<int:question_id>/edit')
def edit_question(question_id):
    question = data_handler.get_question(question_id)
    return render_template('add-edit-question.html', question=question)


@app.route('/question/<int:question_id>/edit', methods=["POST"])
def update_question(question_id):
    questions = data_handler.get_all_questions()
    for question in questions:
        if question['id'] == str(question_id):
            break
    question['title'] = request.form.get('title')
    question['message'] = request.form.get('message')
    file = request.files['image']
    filename = data_handler.save_image(file)
    if filename:
        if os.path.isfile(data_handler.BASEPATH + question['image']):
            os.unlink(data_handler.BASEPATH + question['image'])
        question['image'] = f'{data_handler.UPLOAD_FOLDER}/{filename}'
    data_handler.update_data_in_file(questions, 'sample_data/question.csv', QUESTION_HEADERS)
    return redirect(f'/question/{question_id}')


@app.route('/question/<int:question_id>/delete', methods=["POST"])
def question_delete(question_id):
    util.delete_question(question_id, QUESTION_HEADERS, ANSWER_HEADERS)
    return redirect(url_for('list_questions'))


@app.route('/answer/<int:answer_id>/delete', methods=["POST"])
def answer_delete(answer_id):
    question_id = util.delete_answer(answer_id, ANSWER_HEADERS)
    return redirect(f'/question/{question_id}')


if __name__ == "__main__":
    app.run(
        debug=True
    )

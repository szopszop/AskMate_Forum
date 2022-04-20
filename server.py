from flask import Flask, request, render_template, redirect, url_for
import data_handler
from datetime import datetime, timezone

import util

app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/list', methods=['GET', 'POST'])
def list():
    questions = data_handler.get_data_file('sample_data/question.csv')
    table_headers = data_handler.build_headers()

    if request.method == 'POST':  # sorting
        key = request.form.get('sort')
        order = request.form.get('order')
        questions = util.sort_by(questions, key, order)
    else:
        key, order = None, None
        query_params = request.args
        if 'order_by' in query_params:
            key = query_params.get('order_by')
        if 'order_direction' in query_params:
            order = query_params.get('order_direction')
        questions = util.sort_by(questions, key, order)

    return render_template('list.html', questions=questions, table_headers=table_headers)


@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def questions(question_id):
    questions = data_handler.get_data_file('sample_data/question.csv')
    all_answers = data_handler.get_data_file('sample_data/answer.csv')

    for question in questions:
        if question['id'] == str(question_id):
            the_question = question
    answers = []
    for answer in all_answers:
        if answer['question_id'] == str(question_id):
            answers.append(answer)

    return render_template('questions.html', question=the_question, answers=answers)


@app.route('/question/<int:question_id>/new-answer', methods=["GET", "POST"])
def answer(question_id):
    all_answers = data_handler.get_data_file('sample_data/answer.csv')
    if request.method == 'POST':
        timestamp = datetime.now().timestamp()
        answer = {'id': len(all_answers) + 1, 'submission_time': timestamp}
        answer = answer | request.form.to_dict()
        data_handler.append_new_data_to_file(answer, 'sample_data/answer.csv')
        redirect(f'/question/{question_id}')
    return render_template("new-answer.html", id=question_id, answer_url=f'/question/{question_id}/new-answer')


if __name__ == "__main__":
    app.run(
        debug=True
    )

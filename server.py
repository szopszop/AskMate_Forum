import answers as answers
from flask import Flask, request, render_template, redirect, url_for
import data_handler


app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/list')
def list():
    questions = data_handler.get_data_file('sample_data/question.csv')
    table_headers = data_handler.build_headers()
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


if __name__ == "__main__":
    app.run(
        debug=True
    )

from flask import Flask, request, render_template, redirect, send_from_directory, url_for
import data_manager
import util


app = Flask(__name__)


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/list')
def list_questions():
    questions = data_manager.get_all_questions()
    key = request.args.get('order_by')
    order = request.args.get('order_direction')
    questions = util.sort_by(questions, key, order)
    return render_template('list.html', questions=questions)


@app.route('/add-question')
def write_a_question():
    return render_template("add-edit-question.html", question=None)


@app.route('/add-question', methods=['POST'])
def ask_a_question():
    title = request.form.get('title')
    message = request.form.get("message")
    file = request.files['image']
    filename = data_manager.save_image(file)
    question_id = util.create_question(title, message, filename)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/question/<int:question_id>/new-answer')
def write_an_answer(question_id):
    return render_template("add-answer.html", id=question_id)


@app.route('/question/<int:question_id>/new-answer', methods=["POST"])
def post_an_answer(question_id):
    message = request.form.get("message")
    file = request.files['image']
    filename = data_manager.save_image(file)
    util.create_answer(question_id, message, filename)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/question/<question_id>/image')
def send_question_image(question_id):
    question = data_manager.get_question(question_id)
    return send_from_directory(data_manager.UPLOAD_FOLDER, question['image'].rsplit('/', 1)[1])


@app.route('/answer/<answer_id>/image')
def send_answer_image(answer_id):
    answer = data_manager.get_answer(answer_id)
    return send_from_directory(data_manager.UPLOAD_FOLDER, answer['image'].rsplit('/', 1)[1])


@app.route('/question/<int:question_id>')
def questions(question_id):
    question = data_manager.get_question(question_id)
    answers = data_manager.get_answers_for_question(question_id)
    return render_template('question.html', question=question, answers=answers)


@app.route('/question/<int:question_id>/vote-up', methods=["POST"], endpoint='question_vote_up')
@app.route('/question/<int:question_id>/vote-down', methods=["POST"], endpoint='question_vote_down')
def vote_on_question(question_id):
    endpoint = str(request.url_rule)
    util.vote_on('question', question_id, endpoint)
    return redirect(url_for('list_questions'))


@app.route('/answer/<int:answer_id>/vote-up', methods=["POST"], endpoint='answer_vote_up')
@app.route('/answer/<int:answer_id>/vote-down', methods=["POST"], endpoint='answer_vote_down')
def vote_on_answer(answer_id):
    endpoint = str(request.url_rule)
    question_id = util.vote_on('answer', answer_id, endpoint)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/question/<int:question_id>/edit')
def edit_question(question_id):
    question = data_manager.get_question(question_id)
    return render_template('add-edit-question.html', question=question)


@app.route('/question/<int:question_id>/edit', methods=["POST"])
def update_question(question_id):
    title = request.form.get('title')
    message = request.form.get("message")
    file = request.files['image']
    filename = data_manager.save_image(file)
    util.update_question(question_id, title, message, filename)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/question/<int:question_id>/delete', methods=["POST"])
def question_delete(question_id):
    data_manager.delete_question(question_id)
    return redirect(url_for('list_questions'))


@app.route('/answer/<int:answer_id>/delete', methods=["POST"])
def answer_delete(answer_id):
    question_id = data_manager.delete_answer(answer_id)
    return redirect(url_for('questions', question_id=question_id))


if __name__ == "__main__":
    app.run(
        debug=True
    )

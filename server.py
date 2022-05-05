from flask import Flask, request, render_template, redirect, send_from_directory, url_for
import data_manager
import util


app = Flask(__name__)


@app.route('/')
def hello():
    question = data_manager.display_latest_question()
    return render_template("index.html", questions=question)


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
    util.increase_views(question)
    answers = data_manager.get_answers_for_question(question_id)
    tags = data_manager.get_tags_for_question(question_id)
    tags_with_ids = data_manager.get_tags_with_ids()
    comments = data_manager.get_comments_for_question(question_id)
    return render_template('question.html', question=question, answers=answers,
                           tags=tags, all_tags=tags_with_ids, comments=comments)


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
    remove = request.form.get("remove-image")
    if remove:
        util.delete_file(data_manager.get_question(question_id))
        filename = None
    else:
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


@app.route('/question/<int:question_id>/new-tag')
def add_tag_to_question(question_id):
    question = data_manager.get_question(question_id)
    question_tags = data_manager.get_tags_for_question(question_id)
    all_tags = data_manager.get_all_tags()
    return render_template('add-tag-question.html', question=question, question_tags=question_tags, all_tags=all_tags)


@app.route('/question/<int:question_id>/new-tag', methods=['POST'])
def update_tags_in_question(question_id):
    new_tag = request.form.get('new-tag')
    if new_tag:
        data_manager.add_new_tag(new_tag)
        return redirect(url_for('add_tag_to_question', question_id=question_id))

    tags = [tag for tag in request.form.values()]
    data_manager.update_tags_for_question(question_id, tags)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/question/<int:question_id>/tag/<int:tag_id>/delete')
def delete_tag_from_question(question_id, tag_id):
    data_manager.remove_tag_from_question(question_id, tag_id)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/answer/<answer_id>/new-comment')
def add_comment_to_answer_get(answer_id):
    return render_template('add-comment.html')


@app.route('/answer/<answer_id>/new-comment', methods=['POST'])
def add_comment_to_answer_post(answer_id):
    answer = data_manager.get_answer(answer_id)
    question_id = answer['question_id']
    message = request.form.get("message")
    util.create_comment(question_id, answer_id, message)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/question/<question_id>/new-comment')
def add_comment_to_question_get(question_id):
    return render_template('add-comment.html')


@app.route('/question/<question_id>/new-comment', methods=['POST'])
def add_comment_to_question_post(question_id):
    question = data_manager.get_question(question_id)
    question_id = question['id']
    message = request.form.get("message")
    util.create_comment(question_id, None,  message)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/search')
def search_questions():
    phrase = request.args.get("q")
    questions = data_manager.search_questions_and_answers_in_db(phrase)
    return render_template('search-results.html', questions=questions, search=True)


@app.route('/comments/<comment_id>/delete')
def comment_delete(comment_id):
    comment = data_manager.get_comment_by_comment_id(comment_id)
    data_manager.remove_comment_from_answer(comment_id)
    return redirect(url_for('questions', question_id=comment['question_id']))


if __name__ == "__main__":
    app.run(
        debug=True
    )

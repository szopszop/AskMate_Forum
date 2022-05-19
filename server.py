from flask import Flask, request, render_template, redirect, send_from_directory, url_for, session, flash, make_response
import data_manager
import util
from bonus_questions import SAMPLE_QUESTIONS
from datetime import timedelta

POINTS_FOR_ANSWER = 15

app = Flask(__name__)
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
app.secret_key = '9f6fe7662c44275ec091ea2b4fcdacc2e8935ab85ed429f9'
app.jinja_env.filters['clean'] = util.do_clean


@app.route("/bonus-questions")
def main():
    return render_template('bonus_questions.html', questions=SAMPLE_QUESTIONS, user=data_manager.get_user_details(),
                           logged_in=util.user_logged_in())


@app.route('/')
def index():
    latest_questions = data_manager.get_latest_questions()
    return render_template("index.html", questions=latest_questions, user=data_manager.get_user_details(),
                           logged_in=util.user_logged_in())


@app.route('/list')
def list_questions():
    questions = data_manager.get_all_questions()
    key = request.args.get('order_by')
    order = request.args.get('order_direction')
    questions = util.sort_by(questions, key, order)
    return render_template('list.html', questions=questions, user=data_manager.get_user_details(),
                           logged_in=util.user_logged_in(), get_user=data_manager.get_user_details_by_id)


@app.route('/add-question')
def write_a_question():
    if not util.user_logged_in():
        return redirect(url_for('show_login_form'))
    return render_template("add-edit-question.html", question=None, user=data_manager.get_user_details(),
                           logged_in=util.user_logged_in())


@app.route('/add-question', methods=['POST'])
def ask_a_question():
    title = request.form.get('title')
    message = request.form.get("message")
    file = request.files['image']
    author_id = data_manager.get_user_details(util.current_user())['id']
    filename = data_manager.save_image(file)
    question_id = util.create_question(title, message, author_id, filename)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/question/<int:question_id>/new-answer')
def write_an_answer(question_id):
    if not util.user_logged_in():
        return redirect(url_for('show_login_form'))
    question = data_manager.get_question(question_id)
    return render_template("add-answer.html", id=question_id, question=question, user=data_manager.get_user_details(),
                           logged_in=util.user_logged_in())


@app.route('/question/<int:question_id>/new-answer', methods=['POST'])
def post_an_answer(question_id):
    message = request.form.get("message")
    file = request.files['image']
    filename = data_manager.save_image(file)
    author_id = data_manager.get_user_details()['id']
    util.create_answer(question_id, message, author_id, filename)
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
                           tags=tags, all_tags=tags_with_ids, comments=comments, user=data_manager.get_user_details(),
                           logged_in=util.user_logged_in(), get_user=data_manager.get_user_details_by_id)


@app.route('/question/<int:question_id>/vote-up', methods=["POST"], endpoint='question_vote_up')
@app.route('/question/<int:question_id>/vote-down', methods=["POST"], endpoint='question_vote_down')
def vote_on_question(question_id):
    if not util.user_logged_in():
        return redirect(url_for('show_login_form'))
    endpoint = str(request.url_rule)
    vote_info = util.vote_on('question', question_id, endpoint, util.current_user())
    flash(vote_info[0], vote_info[1])
    return redirect(request.referrer)


@app.route('/answer/<int:answer_id>/vote-up', methods=["POST"], endpoint='answer_vote_up')
@app.route('/answer/<int:answer_id>/vote-down', methods=["POST"], endpoint='answer_vote_down')
def vote_on_answer(answer_id):
    question_id = util.get_question_id_from_answer(answer_id)
    if not util.user_logged_in():
        return redirect(url_for('show_login_form'))
    endpoint = str(request.url_rule)
    vote_info = util.vote_on('answer', answer_id, endpoint, util.current_user())
    flash(vote_info[0], vote_info[1])
    return redirect(request.referrer)


@app.route('/question/<int:question_id>/edit')
def edit_question(question_id):
    question = data_manager.get_question(question_id)
    return render_template('add-edit-question.html', question=question, user=data_manager.get_user_details(),
                           logged_in=util.user_logged_in())


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
    comments = data_manager.get_comments_by_answer_id(question_id)
    for comment in comments:
        data_manager.remove_comment(comment['id'])
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
    return render_template('add-tag-question.html', question=question, question_tags=question_tags, all_tags=all_tags,
                           user=data_manager.get_user_details(), logged_in=util.user_logged_in())


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
    if not util.user_logged_in():
        return redirect(url_for('show_login_form'))
    answer = data_manager.get_answer(answer_id)
    return render_template('add-comment.html', answer=answer, user=data_manager.get_user_details(),
                           logged_in=util.user_logged_in())


@app.route('/answer/<answer_id>/new-comment', methods=['POST'])
def add_comment_to_answer_post(answer_id):
    answer = data_manager.get_answer(answer_id)
    question_id = answer['question_id']
    message = request.form.get("message")
    author_id = data_manager.get_user_details(util.current_user())['id']
    util.create_comment(question_id, answer_id, message, author_id)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/question/<question_id>/new-comment')
def add_comment_to_question_get(question_id):
    if not util.user_logged_in():
        return redirect(url_for('show_login_form'))
    question = data_manager.get_question(question_id)
    return render_template('add-comment.html', question=question, user=data_manager.get_user_details(),
                           logged_in=util.user_logged_in())


@app.route('/question/<question_id>/new-comment', methods=['POST'])
def add_comment_to_question_post(question_id):
    question = data_manager.get_question(question_id)
    question_id = question['id']
    message = request.form.get("message")
    author_id = data_manager.get_user_details(util.current_user())['id']
    util.create_comment(question_id, None, message, author_id)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/search')
def search_questions():
    phrase = request.args.get("q")
    questions = data_manager.search_questions_in_db(phrase)
    answers = data_manager.search_answers_in_db(phrase)
    added_questions_id = []
    search_results = []
    util.highlight_results(answers, phrase, added_questions_id, search_results)
    util.highlight_results(questions, phrase, added_questions_id, search_results)
    return render_template('search-results.html', questions=search_results, search=True, phrase=phrase,
                           user=data_manager.get_user_details(), logged_in=util.user_logged_in())


@app.route('/comments/<comment_id>/delete')
def comment_delete(comment_id):
    comment = data_manager.get_comment_by_comment_id(comment_id)
    data_manager.remove_comment(comment_id)
    return redirect(url_for('questions', question_id=comment['question_id']))


@app.route('/comment/<comment_id>/edit')
def update_comments(comment_id):
    comment = data_manager.get_comment_by_comment_id(comment_id)
    question = data_manager.get_question(comment['question_id'])
    answer = data_manager.get_answer(comment['answer_id'])
    return render_template('add-comment.html', comment=comment, answer=answer, question=question,
                           user=data_manager.get_user_details(), logged_in=util.user_logged_in())


@app.route('/comment/<comment_id>/edit', methods=["POST"])
def edit_comments(comment_id):
    comment = data_manager.get_comment_by_comment_id(comment_id)
    message = request.form.get("message")
    comment['edited_count'] += 1
    util.update_comment(comment_id, message)
    return redirect(url_for('questions', question_id=comment['question_id']))


@app.route('/answer/<int:answer_id>/edit')
def update_answer(answer_id):
    answer = data_manager.get_answer(answer_id)
    question = data_manager.get_question(answer['question_id'])
    return render_template('add-answer.html', answer=answer, id=answer['question_id'], question=question,
                           user=data_manager.get_user_details(), logged_in=util.user_logged_in())


@app.route('/answer/<int:answer_id>/edit', methods=['POST'])
def edit_answer(answer_id):
    answer = data_manager.get_answer(answer_id)
    message = request.form.get("message")
    file = request.files['image']
    remove = request.form.get("remove-image")
    if remove:
        util.delete_file(data_manager.get_answer(answer_id))
        filename = None
    else:
        filename = data_manager.save_image(file)
    util.update_answer(answer_id, message, filename)
    return redirect(url_for('questions', question_id=answer['question_id']))


@app.route('/registration')
def register_page():
    if util.user_logged_in():
        return redirect(url_for('index'))
    return render_template('registration.html')


@app.route('/registration', methods=['POST'])
def register():
    user_email = request.form.get('email')
    password_1 = request.form.get('password')
    password_2 = request.form.get('repeat_password')
    if not data_manager.check_if_user_exists(user_email):
        if password_1 == password_2:
            new_user = {'username': user_email,
                        'password': data_manager.hash_password(password_1)}
            data_manager.add_user(new_user)
    return redirect(url_for('index'))


@app.route('/login')
def show_login_form():
    if util.user_logged_in():
        return redirect(url_for('index'))
    session['url'] = request.referrer
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    user_email = request.form.get("email")
    password = request.form.get("password")
    if data_manager.check_if_user_exists(user_email) and \
            data_manager.verify_password(password, data_manager.get_user_password(user_email)):
        flash('You were successfully logged in', category='success')
        session["username"] = user_email
        return redirect(session.pop('url', None))
    else:
        flash('Invalid credentials', category='error')
        return redirect(url_for('show_login_form'))


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/users')
def list_users():
    if not util.user_logged_in():
        return redirect(url_for('show_login_form'))
    users = data_manager.get_users()
    for user in users:
        user['number_of_questions'] = data_manager.get_number_of_data(user['id'], data='question')
        user['number_of_answers'] = data_manager.get_number_of_data(user['id'], data='answer')
        user['number_of_comments'] = data_manager.get_number_of_data(user['id'], data='comment')
    return render_template('users-list.html', users=users, user=data_manager.get_user_details(),
                           logged_in=util.user_logged_in())


@app.route('/user/<int:user_id>')
def user_page(user_id):
    user = data_manager.get_user_details_by_id(user_id)
    questions = data_manager.get_questions_from_user(user['username'])
    answers = data_manager.get_answers_and_question_titles_from_user(user['username'])
    comments = data_manager.get_comments_and_question_ids_from_user(user['username'])
    return render_template('user_page.html', questions=questions, answers=answers, comments=comments,
                           user=user, logged_in=util.user_logged_in())


@app.route('/question/<int:question_id>/answer/<int:answer_id>/accept', methods=['POST'])
def accept_answer(question_id, answer_id):
    data_manager.accept_answer(question_id, answer_id)
    answer = data_manager.get_answer(answer_id)
    data_manager.change_reputation(answer['user_id'], POINTS_FOR_ANSWER)
    return redirect(url_for('questions', question_id=question_id))


@app.route('/tags')
def tags_page():
    tags = data_manager.get_tag()
    for tag in tags:
        tag['number_of_tagged_question'] = data_manager.get_number_of_questions_assign_to_tag(tag['id'])
    return render_template('tags-page.html', tags=tags)


@app.route("/set")
@app.route("/set/<theme>")
def set_theme(theme="light"):
    res = make_response(redirect(request.referrer))
    res.set_cookie("theme", theme)
    return res


if __name__ == "__main__":
    app.run(
        debug=True
    )

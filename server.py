from flask import Flask, request, render_template, redirect, url_for
import data_handler


app = Flask(__name__)
def add_question(id_ ,questions ):


@app.route("/")
def hello():
    return "Hello World!"


@app.route('/list')
def list():
    questions = data_handler.get_data_file('sample_data/question.csv')
    table_headers = data_handler.build_headers()
    return render_template('list.html', questions=questions, table_headers=table_headers)

@app.route('/add-question', methods=['GET', 'POST'])
def ask_a_question():
    if request.method == 'POST':
        questions = data_handler.get_data_file('sample_data/question.csv')

        for question in questions:
            question['title'] = request.form['title']
            question['message'] = request.form['message']
            table_headers = data_handler.build_headers()
            return redirect('/')
    return render_template('add-question')


if __name__ == "__main__":
    app.run()

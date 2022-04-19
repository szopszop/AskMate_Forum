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


if __name__ == "__main__":
    app.run()

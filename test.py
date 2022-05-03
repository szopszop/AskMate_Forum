import io

from server import app
from data_manager import get_last_answer, get_last_question, delete_question, delete_answer, add_tag_to_question
from util import create_answer, create_question, update_question
import unittest


class AskMateTestCase(unittest.TestCase):

    # Ensure that route '/list' was set up correctly
    def test_list_page_status(self):
        tester = app.test_client(self)
        response = tester.get('/list', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # Checks response status code

    # Ensure that question list page loads correctly
    def test_list_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/list', content_type='html/text')
        self.assertTrue(b'Questions' in response.data)  # Looks for "Questions" text in rendered html template

    # Ensure that route '/add-question' was set up correctly
    def test_add_question_page_status(self):
        tester = app.test_client(self)
        response = tester.get('/add-question', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # Checks response status code

    # Ensure that add question page loads correctly
    def test_add_question_page_loads(self):
        tester = app.test_client(self)
        response = tester.get('/list', content_type='html/text')
        self.assertTrue(b'Add Question' in response.data)  # Looks for "Add Question" text in rendered html template

    # Ensure that questions are posted correctly
    def test_add_question(self):
        tester = app.test_client(self)
        response = tester.post(
            '/add-question',
            data=dict(
                title="test title",
                message="test message",
                image=(io.BytesIO(b"abcdef"), "test.jpg")
            ),
            follow_redirects=True,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        self.assertIn(b'test title', response.data)  # Checks for correct title
        self.assertIn(b'test message', response.data)  # Checks for correct message
        question = get_last_question()  # Get last added question
        self.assertIsNotNone(question['image'])  # Checks for correct image upload
        delete_question(question['id'])  # Delete that question

    # Ensure that route '/question/<int:question_id>/new_answer' was set up correctly
    def test_post_an_answer_page_status(self):
        tester = app.test_client(self)
        question = get_last_question()
        response = tester.get(f'/question/{question["id"]}/new-answer', content_type='html/text')
        self.assertEqual(response.status_code, 200)  # Checks response status code

    # Ensure that route '/question/<int:question_id>/new_answer' loads correctly
    def test_post_an_answer_page_loads(self):
        tester = app.test_client(self)
        question = get_last_question()
        response = tester.get(f'/question/{question["id"]}/new-answer', content_type='html/text')
        self.assertTrue(b"Add Answer" in response.data)  # Checks response status code

    # Ensure that answers are posted correctly
    def test_post_an_answer(self):
        tester = app.test_client(self)
        question = get_last_question()
        response = tester.post(
            f'/question/{question["id"]}/new-answer',
            data=dict(
                message="test message",
                image=(io.BytesIO(b"abcdef"), "test.jpg")
            ),
            follow_redirects=True,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        self.assertIn(b'test message', response.data)  # Checks for correct message
        answer = get_last_answer()  # Get last added answer
        self.assertIsNotNone(answer['image'])  # Checks for correct image upload
        delete_answer(answer['id'])  # Delete that answer

    # Ensure that vote on questions is working
    def test_vote_on_question(self):
        tester = app.test_client(self)
        create_question('test', 'test')  # Create test question
        question = get_last_question()  # Get last added question
        response = tester.post(
            f'/question/{question["id"]}/vote-up',
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        question = get_last_question()  # Get updated last added question
        self.assertEqual(question['vote_number'], 1)  # Check if vote-up is working
        response = tester.post(
            f'/question/{question["id"]}/vote-down',
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        question = get_last_question()  # Get updated last added question
        self.assertEqual(question['vote_number'], 0)  # Check if vote-down is working
        delete_question(question["id"])  # Delete that question

    # Ensure that vote on answers is working
    def test_vote_on_answer(self):
        tester = app.test_client(self)
        create_question('test', 'test')  # Create test question
        question = get_last_question()  # Get last added question
        create_answer(question["id"], 'test')  # Create test answer
        answer = get_last_answer()  # Get last added answer
        response = tester.post(
            f'/answer/{answer["id"]}/vote-up',
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        answer = get_last_answer()  # Get updated last added answer
        self.assertEqual(answer["vote_number"], 1)  # Check if vote-up is working
        response = tester.post(
            f'/answer/{answer["id"]}/vote-down',
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        answer = get_last_answer()  # Get updated last added answer
        self.assertEqual(answer["vote_number"], 0)  # Check if vote-up is working
        delete_question(question["id"])  # Delete test question and answer

    # Ensure that edit question route was set up correctly
    def test_edit_question_page_status(self):
        tester = app.test_client(self)
        create_question('test title', 'test message')  # Create test question
        question = get_last_question()  # Get last added question
        response = tester.get(
            f'/question/{question["id"]}/edit',
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        delete_question(question["id"])  # Delete test question

    # Ensure that edit question page is loading correctly
    def test_edit_question_page_loads(self):
        tester = app.test_client(self)
        create_question('test title', 'test message')  # Create test question
        question = get_last_question()  # Get last added question
        response = tester.get(
            f'/question/{question["id"]}/edit',
            content_type="html/text"
        )
        self.assertTrue(b'Edit' in response.data)  # Checks for correct page header
        self.assertTrue(b'Save' in response.data)  # Checks for correct page button
        delete_question(question["id"])  # Delete test question

    # Ensure that update question is working
    def test_update_question(self):
        tester = app.test_client(self)
        create_question('test title', 'test message')  # Create test question
        question = get_last_question()  # Get last added question
        update_question(question["id"], "new test title", "new test message")
        response = tester.get(
            f'/question/{question["id"]}',
            content_type="html/text"
        )
        self.assertIn(b"new test title", response.data)  # Check for correct title
        self.assertIn(b"new test message", response.data)  # Check for correct message
        delete_question(question["id"])  # Delete test question

    # Ensure that delete question route was set up correctly
    def test_delete_question_redirect_status(self):
        tester = app.test_client(self)
        create_question('test title', 'test message')  # Create test question
        question = get_last_question()  # Get last added question
        response = tester.post(
            f'/question/{question["id"]}/delete',
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)

    # Ensure that delete question route was set up correctly
    def test_delete_question(self):
        tester = app.test_client(self)
        create_question('test title', 'test message')  # Create test question
        question = get_last_question()  # Get last added question
        self.assertEqual(question['title'], 'test title')  # Checks for correct question title
        self.assertEqual(question['message'], 'test message')  # Checks for correct question message
        response = tester.post(
            f'/question/{question["id"]}/delete',
            follow_redirects=True,
            content_type="html/text"
        )  # Delete last added test question
        question = get_last_question()  # Get last added question
        self.assertNotEqual(question['title'], 'test title')  # Checks if last question have other title
        self.assertNotEqual(question['message'], 'test message')  # Checks if last question have other message

    # Ensure that delete answer route was set up correctly
    def test_delete_answer_redirect_status(self):
        tester = app.test_client(self)
        create_question('test title', 'test message')  # Create test question
        question = get_last_question()  # Get last added question
        create_answer(question["id"], 'test message')  # Create test answer
        answer = get_last_answer()  # Get last added answer
        response = tester.post(
            f'/answer/{answer["id"]}/delete',
            follow_redirects=True,
            content_type="html/text"
        )  # Delete test answer
        self.assertEqual(response.status_code, 200)  # Checks response status code
        delete_question(question["id"])  # Delete test question

    # Ensure that delete question route was set up correctly
    def test_delete_answer(self):
        tester = app.test_client(self)
        create_question('test title', 'test message')  # Create test question
        question = get_last_question()  # Get last added question
        create_answer(question["id"], 'test message')  # Create test answer
        answer = get_last_answer()  # Get last added answer
        self.assertEqual(answer['message'], 'test message')  # Checks for correct answer message
        response = tester.post(
            f'/answer/{answer["id"]}/delete',
            follow_redirects=True,
            content_type="html/text"
        )  # Delete test answer
        answer = get_last_answer()  # Get last added answer
        self.assertNotEqual(answer['message'], 'test message')  # Checks if last answer have other message
        delete_question(question["id"])  # Delete test question

    # Ensure that add_tag_to_question route was set up correctly
    def test_add_tag_to_question_page_status(self):
        tester = app.test_client(self)
        create_question('test title', 'test message')  # Create test question
        question = get_last_question()  # Get last added question
        response = tester.get(
            f'/question/{question["id"]}/new-tag',
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        delete_question(question["id"])  # Delete test question

    # Ensure that add_tag_to_question route loads correctly
    def test_add_tag_to_question_page_loads(self):
        tester = app.test_client(self)
        create_question('test title', 'test message')  # Create test question
        question = get_last_question()  # Get last added question
        response = tester.get(
            f'/question/{question["id"]}/new-tag',
            content_type="html/text"
        )
        self.assertTrue(b'Add tags to Question:' in response.data)  # Checks for correct page header
        delete_question(question["id"])  # Delete test question

    # Ensure that adding tags is working
    def test_add_tag_to_question(self):
        tester = app.test_client(self)
        create_question('test title', 'test message')  # Create test question
        question = get_last_question()  # Get last added question
        add_tag_to_question(question['id'], 1)  # Insert tag "python" into question
        response = tester.get(
            f'/question/{question["id"]}',
            content_type="html/text"
        )
        self.assertTrue(b'python' in response.data)  # Checks for correct tag
        delete_question(question["id"])  # Delete test question

    # Ensure that removing tags is working
    def test_remove_tag_from_question(self):
        tester = app.test_client(self)
        create_question('test title', 'test message')  # Create test question
        question = get_last_question()  # Get last added question
        add_tag_to_question(question['id'], 1)  # Insert tag "python" into question
        response = tester.get(
            f'/question/{question["id"]}/tag/1/delete',
            content_type="html/text"
        )
        self.assertTrue(b'python' not in response.data)  # Checks if tag was removed
        delete_question(question["id"])  # Delete test question


if __name__ == '__main__':
    unittest.main()

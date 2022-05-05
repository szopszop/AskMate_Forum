import io
from time import sleep

from server import app
from data_manager import (
    get_last_answer,
    get_answer,
    get_last_question,
    get_question,
    delete_question,
    delete_answer,
    add_tag_to_question,
    remove_comment,
    get_last_added_comment
)
from util import (
    create_answer,
    create_question,
    update_question,
    create_comment
)

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
                title="test add question title",
                message="test add question message",
                image=(io.BytesIO(b"abcdef"), "test.jpg")
            ),
            follow_redirects=True,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        self.assertIn(b'test add question title', response.data)  # Checks for correct title
        self.assertIn(b'test add question message', response.data)  # Checks for correct message
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
                message="test post an answer",
                image=(io.BytesIO(b"abcdef"), "test.jpg")
            ),
            follow_redirects=True,
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        self.assertIn(b'test post an answer', response.data)  # Checks for correct message
        answer = get_last_answer()  # Get last added answer
        self.assertIsNotNone(answer['image'])  # Checks for correct image upload
        delete_answer(answer['id'])  # Delete that answer

    # Ensure that vote on questions is working
    def test_vote_on_question(self):
        tester = app.test_client(self)
        question_id = create_question('test vote', 'test vote')  # Create test question
        response = tester.post(
            f'/question/{question_id}/vote-up',
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        question = get_question(question_id)  # Get updated last added question
        self.assertEqual(question['vote_number'], 1)  # Check if vote-up is working
        response = tester.post(
            f'/question/{question["id"]}/vote-down',
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        question = get_question(question_id)  # Get updated last added question
        self.assertEqual(question['vote_number'], 0)  # Check if vote-down is working
        delete_question(question_id)  # Delete that question

    # Ensure that vote on answers is working
    def test_vote_on_answer(self):
        tester = app.test_client(self)
        question_id = create_question('test vote', 'test vote')  # Create test question
        answer_id = create_answer(question_id, 'test answer vote')  # Create test answer
        response = tester.post(
            f'/answer/{answer_id}/vote-up',
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        answer = get_answer(answer_id)  # Get updated last added answer
        self.assertEqual(answer["vote_number"], 1)  # Check if vote-up is working
        response = tester.post(
            f'/answer/{answer["id"]}/vote-down',
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        answer = get_answer(answer_id)  # Get updated last added answer
        self.assertEqual(answer["vote_number"], 0)  # Check if vote-up is working
        delete_question(question_id)  # Delete test question and answer

    # Ensure that edit question route was set up correctly
    def test_edit_question_page_status(self):
        tester = app.test_client(self)
        question_id = create_question('test title', 'test message')  # Create test question
        response = tester.get(
            f'/question/{question_id}/edit',
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        delete_question(question_id)  # Delete test question

    # Ensure that edit question page is loading correctly
    def test_edit_question_page_loads(self):
        tester = app.test_client(self)
        question_id = create_question('test title', 'test message')  # Create test question
        response = tester.get(
            f'/question/{question_id}/edit',
            content_type="html/text"
        )
        self.assertTrue(b'Edit' in response.data)  # Checks for correct page header
        self.assertTrue(b'Save' in response.data)  # Checks for correct page button
        delete_question(question_id)  # Delete test question

    # Ensure that update question is working
    def test_update_question(self):
        tester = app.test_client(self)
        question_id = create_question('test title', 'test message')  # Create test question
        update_question(question_id, "new test title", "new test message")
        response = tester.get(
            f'/question/{question_id}',
            content_type="html/text"
        )
        self.assertIn(b"new test title", response.data)  # Check for correct title
        self.assertIn(b"new test message", response.data)  # Check for correct message
        delete_question(question_id)  # Delete test question

    # Ensure that delete question route was set up correctly
    def test_delete_question_redirect_status(self):
        tester = app.test_client(self)
        question_id = create_question('test delete question title', 'test delete question message')  # Create test question
        response = tester.post(
            f'/question/{question_id}/delete',
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        delete_question(question_id)  # Delete test question

    # Ensure that delete question route was set up correctly
    def test_delete_question(self):
        tester = app.test_client(self)
        question_id = create_question('test delete question title', 'test delete question message')  # Create test question
        question = get_question(question_id)  # Get last added question
        self.assertEqual(question['title'], 'test delete question title')  # Checks for correct question title
        self.assertEqual(question['message'], 'test delete question message')  # Checks for correct question message
        delete_question(question_id)  # Delete test question
        question = get_last_question()  # Get last added question
        self.assertNotEqual(question['title'], 'test delete question title')  # Checks if last question have other title
        self.assertNotEqual(question['message'], 'test delete question message')  # Checks if last question have other message

    # Ensure that delete answer route was set up correctly
    def test_delete_answer_redirect_status(self):
        tester = app.test_client(self)
        question_id = create_question('test delete answer redirect title', 'test delete answer redirect message')  # Create test question
        answer_id = create_answer(question_id, 'test delete answer redirect message')  # Create test answer
        response = tester.post(
            f'/answer/{answer_id}/delete',
            follow_redirects=True,
            content_type="html/text"
        )  # Delete test answer
        self.assertEqual(response.status_code, 200)  # Checks response status code
        delete_question(question_id)  # Delete test question

    # Ensure that delete answer is working
    def test_delete_answer(self):
        question_id = create_question('test delete answer title', 'test delete answer message')  # Create test question
        answer_id = create_answer(question_id, 'test delete answer message')  # Create test answer
        answer = get_answer(answer_id)  # Get last added answer
        self.assertEqual(answer['message'], 'test delete answer message')  # Checks for correct answer message
        delete_answer(answer['id'])  # Delete test answer
        answer = get_last_answer()  # Get last added answer
        self.assertNotEqual(answer['message'], 'test delete answer message')  # Checks if last answer have other message
        delete_question(question_id)  # Delete test question

    # Ensure that add_tag_to_question route was set up correctly
    def test_add_tag_to_question_page_status(self):
        tester = app.test_client(self)
        question_id = create_question('test add tag page status title', 'test add tag page status message')  # Create test question
        response = tester.get(
            f'/question/{question_id}/new-tag',
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        delete_question(question_id)  # Delete test question

    # Ensure that add_tag_to_question route loads correctly
    def test_add_tag_to_question_page_loads(self):
        tester = app.test_client(self)
        question_id = create_question('test add tag page load title', 'test add tag page load message')  # Create test question
        response = tester.get(
            f'/question/{question_id}/new-tag',
            content_type="html/text"
        )
        self.assertTrue(b'Add tags to Question:' in response.data)  # Checks for correct page header
        delete_question(question_id)  # Delete test question

    # Ensure that adding tags is working
    def test_add_tag_to_question(self):
        tester = app.test_client(self)
        question_id = create_question('test add tag title', 'test add tag message')  # Create test question
        add_tag_to_question(question_id, 1)  # Insert tag "python" into question
        response = tester.get(
            f'/question/{question_id}',
            content_type="html/text"
        )
        self.assertTrue(b'python' in response.data)  # Checks for correct tag
        delete_question(question_id)  # Delete test question

    # Ensure that removing tags is working
    def test_remove_tag_from_question(self):
        tester = app.test_client(self)
        question_id = create_question('test remove tag title', 'test remove tag message')  # Create test question
        add_tag_to_question(question_id, 1)  # Insert tag "python" into question
        response = tester.get(
            f'/question/{question_id}/tag/1/delete',
            content_type="html/text"
        )
        self.assertTrue(b'python' not in response.data)  # Checks if tag was removed
        delete_question(question_id)  # Delete test question

    # Ensure that adding comments to answer route was set up correctly
    def test_add_comment_to_answer_page_status(self):
        tester = app.test_client(self)
        question_id = create_question('test add comment to answer title', 'test add comment to answer message')  # Create test question
        answer_id = create_answer(question_id, 'test add comment to answer message')  # Create test answer
        response = tester.post(
            f'/answer/{answer_id}/new-comment',
            data=dict(
                message="test add comment to question message"
            ),
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        comment = get_last_added_comment()  # Get latest added test comment
        remove_comment(comment['id'])  # Remove that test comment
        delete_question(question_id)  # Remove test question

    # Ensure that adding comments to answer page loads correctly
    def test_add_comment_to_answer_page_loads(self):
        tester = app.test_client(self)
        question_id = create_question('test add comment to answer title', 'test add comment to answer message')  # Create test question
        answer_id = create_answer(question_id, 'test add comment to answer message')  # Create test answer
        response = tester.get(
            f'/answer/{answer_id}/new-comment',
            content_type="html/text"
        )
        self.assertTrue(b'Your comment:' in response.data)  # Checks if page loads correctly
        delete_question(question_id)  # Remove test question

    # Ensure that on question page button for adding comments to question is visible
    def test_add_comment_to_question_button_visibility(self):
        tester = app.test_client(self)
        question_id = create_question('test add comment to question button visibility',
                        'test add comment to question button visibility')  # Create test question
        response = tester.get(
            f'/question/{question_id}',
            content_type="html/text"
        )
        self.assertTrue(b"Comment on this question" in response.data)
        delete_question(question_id)

    # Ensure that on question page button for adding comments to question is visible
    def test_add_comment_to_answer_button_visibility(self):
        tester = app.test_client(self)
        question_id = create_question('test add comment to answer button visibility',
                        'test add comment to answer button visibility')  # Create test question
        create_answer(question_id, 'test add comment to answer button visibility')
        response = tester.get(
            f'/question/{question_id}',
            content_type="html/text"
        )
        self.assertTrue(b"Comment on this answer" in response.data)
        delete_question(question_id)

    # Ensure that on adding comments to answer page is form with "post" method
    def test_add_comment_to_answer_form(self):
        tester = app.test_client(self)
        question_id = create_question('test add comment to answer form title', 'test add comment to answer form message')  # Create test question
        answer_id = create_answer(question_id, 'test add comment to answer message')  # Create test answer
        response = tester.get(
            f'/answer/{answer_id}/new-comment',
            content_type="html/text"
        )
        self.assertTrue(b'form' in response.data)  # Checks if page loads correctly
        self.assertTrue(b'post' in response.data)
        delete_question(question_id)  # Remove test question

    # Ensure that adding comments to answer function is working
    def test_add_comment_to_answer(self):
        tester = app.test_client(self)
        question_id = create_question('test add comment to question title', 'test add comment to answer message')  # Create test question
        answer_id = create_answer(question_id, 'test add comment to answer message')  # Create test answer
        create_comment(question_id, answer_id, 'test add comment to answer')  # Create test comment
        response = tester.get(
            f'/question/{question_id}',
            content_type="html/text"
        )
        self.assertTrue(b'test add comment to answer' in response.data)
        comment = get_last_added_comment()
        remove_comment(comment['id'])  # Remove test comment
        delete_question(question_id)  # Remove test question

    # Ensure that adding comments to question route was set up correctly
    def test_add_comment_to_question_page_status(self):
        tester = app.test_client(self)
        question_id = create_question('test add comment to question page status title', 'test add comment to question page status message')  # Create test question
        response = tester.post(
            f'/question/{question_id}/new-comment',
            data=dict(
                message="test add comment to question page status message"
            ),
            follow_redirects=True,
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)  # Checks response status code
        comment = get_last_added_comment()  # Get latest added test comment
        remove_comment(comment['id'])  # Remove that test comment
        delete_question(question_id)  # Remove test question

    # Ensure that adding comments to question page loads correctly
    def test_add_comment_to_question_page_loads(self):
        tester = app.test_client(self)
        question_id = create_question('test add comment to question page loads title', 'test add comment to question page loads message')  # Create test question
        response = tester.get(
            f'/question/{question_id}/new-comment',
            content_type="html/text"
        )
        self.assertTrue(b'Your comment:' in response.data)  # Checks if page loads correctly
        delete_question(question_id)  # Remove test question

    # Ensure that adding comments to question function is working
    def test_add_comment_to_question(self):
        tester = app.test_client(self)
        question_id = create_question('test add comment to question title', 'test add comment to question message')  # Create test question
        create_comment(question_id, None, 'test add comment to question')  # Create test comment
        response = tester.get(
            f'/question/{question_id}',
            content_type="html/text"
        )
        self.assertTrue(b'test add comment to question' in response.data)
        comment = get_last_added_comment()
        remove_comment(comment['id'])  # Remove test comment
        delete_question(question_id)  # Remove test question

    # Ensure that main page route was set up correctly
    def test_main_page_status(self):
        tester = app.test_client(self)
        response = tester.get(
            '/',
            content_type="html/text"
        )
        self.assertEqual(response.status_code, 200)

    # Ensure that main page loads correctly
    def test_main_page_loads(self):
        tester = app.test_client(self)
        response = tester.get(
            '/',
            content_type="html/text"
        )
        self.assertTrue(b'Main page' in response.data)

    # Ensure that on main page is search button
    def test_main_page_have_search_button(self):
        tester = app.test_client(self)
        response = tester.get(
            '/',
            content_type="html/text"
        )
        self.assertTrue(b'Search' in response.data)

    # Ensure that searching is working
    def test_search(self):
        tester = app.test_client(self)
        question_id = create_question('590gjaiwrITRti', 'jGHOWAHgjowau52525')
        response = tester.get(
            f'/search?q=590gjaiwrITRti',
            content_type="html/text"
        )
        self.assertTrue(b'jGHOWAHgjowau52525' in response.data)
        delete_question(question_id)

    # Ensure that removing comments route was set up correctly
    def test_remove_comments_page_status(self):
        tester = app.test_client(self)
        question_id = create_question('test remove comment title', 'test remove comment message')
        create_comment(question_id, None, "test remove comment message")
        comment = get_last_added_comment()
        response = tester.get(
            f'/comments/{comment["id"]}/delete',
            content_type="html/text",
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)
        remove_comment(comment['id'])
        delete_question(question_id)

    # Ensure that removing comments is working
    def test_remove_comments(self):
        tester = app.test_client(self)
        question_id = create_question('test remove comment title', 'test remove comment message')
        create_comment(question_id, None, "test remove comment message")
        comment = get_last_added_comment()
        self.assertIn('test remove comment message', comment['message'])
        remove_comment(comment['id'])
        comment = get_last_added_comment()
        self.assertNotIn('test remove comment message', comment['message'])
        delete_question(question_id)


if __name__ == '__main__':
    unittest.main()

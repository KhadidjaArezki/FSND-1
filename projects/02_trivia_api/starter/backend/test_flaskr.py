import os
from config import environ
from sys import platform
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from app import create_app
from models import setup_db, Question, Category, Games, User

database_name = environ['test_database_name']


class TestTrivia(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = database_name
        self.database_path = '{}/{}'.format(environ['database_path'],
                                            self.database_name)
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question': 'What is a question',
            'answer': 'This could be an answer',
            'difficulty': 1,
            'category': 1,
            'rating': 1
        }

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful
    operation and for expected errors.
    """

    def test_get_categories_200(self):
        """ Response must return 200 - a set of categories"""
        response = self.client().get('/categories')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)
        self.assertTrue(len(response_data['categories']) > 0)

    def test_get_questions_200(self):
        """ Response must return 200 - a set of questions"""
        response = self.client().get('/questions?page=2')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertTrue(len(response_data['questions']) > 0)
        self.assertTrue(response_data['total_questions'])

    def test_create_question_200(self):
        """ Response must return 200 - a new question created"""
        response = self.client().post('/questions', json=self.new_question)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['success'], True)

    def test_create_question_400(self):
        """ Response must return a Bad Request"""
        response = self.client().post('/questions')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Bad Request')

    def test_create_question_422(self):
        """ Response must return an  Unprocessible error"""
        response = self.client().post('/questions', json={
            'question': 'Is this good', 'answer': 'NO'
        })
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Unprocessable')

    def test_delete_question_200(self):
        """ Must return 200 - question successfully deleted"""
        response = self.client().delete('/questions/23')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response_data['deleted'], 23)
        self.assertEqual(response_data['success'], True)

    def test_delete_question_404(self):
        """ Response must return a Not Found error """
        response = self.client().delete('/questions/99')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Not Found')

    def test_search_questions_200(self):
        """ Response must return 200 - a new question created"""
        search = {'searchTerm': 'title'}
        response = self.client().post('/questions/search', json=search)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['questions'])
        self.assertTrue(response_data['total_questions'])
        self.assertTrue(response_data['current_category'])

    def test_search_questions_400(self):
        """ Response must return a Bad Request"""
        response = self.client().post('/questions/search')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Bad Request')

    def test_search_questions_422(self):
        """ Response must return an Unprocessable error"""
        search = {'search': 'title'}
        response = self.client().post('/questions/search', json=search)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Unprocessable')

    def test_get_category_questions_200(self):
        """ Response must return 200 - a set of questions
        of the specified category"""
        response = self.client().get('/categories/1/questions')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['questions'])
        self.assertTrue(response_data['total_questions'])
        self.assertTrue(response_data['current_category'])

    def test_get_category_questions_404(self):
        """ Response must return a Not Found error."""
        response = self.client().get('/categories/99/questions')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 404)
        self.assertFalse(response_data['success'])
        self.assertEqual(response_data['message'], 'Not Found')

    def test_create_category_200(self):
        """Response must return 200 - a successfully created category."""
        request_json = {
            'type': 'Tech'
        }
        response = self.client().post('/categories', json=request_json)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])

    def test_create_category_400(self):
        """Response must return 400 - a Bad Request"""
        response = self.client().post('/categories')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Bad Request')

    def test_create_category_422(self):
        """Response must return 422 - an Unprocessable error"""
        request_json = {
            'type': ''
        }
        response = self.client().post('/categories', json=request_json)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Unprocessable')

    def test_play_quiz_200(self):
        """ Response must return 200 - a randomly chosen question"""
        request_json = {
            'previous_questions': [2, 4, 5, 9, 6],
            'quiz_category': {'type': 'Science', 'id': 1}
        }
        response = self.client().post('/quizzes', json=request_json)

        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])
        self.assertTrue(response_data['question'])

    def test_play_quiz_400(self):
        """ Response must return a Bad Request"""
        response = self.client().post('/quizzes')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Bad Request')

    def test_play_quiz_422(self):
        """ Response must return an Unprocessable error"""
        request_json = {
            'previous_questions': [2, 4, 5, 9, 6],
            'category': {'type': 'Science', 'id': 1}
        }
        response = self.client().post('/quizzes', json=request_json)
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Unprocessable')

    def test_save_game_200(self):
        """ Response must return 200 - game successfully saved."""
        request_json = {
            'name': 'tester999',
            'category_id': 2,
            'score': 1,
            'timestamp': '11/06/2021, 01:16:55'
        }
        response = self.client().post('/games', json=request_json)

        response_data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response_data['success'])

    def test_save_game_400(self):
        """ Response must return a Bad Request"""
        response = self.client().post('/games')
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Bad Request')

    def test_save_game_422(self):
        """ Response must return an  Unprocessible error"""
        response = self.client().post('/games', json={
            'score': 10, 'name': 'best_player'
        })
        response_data = json.loads(response.data)

        self.assertEqual(response.status_code, 422)
        self.assertEqual(response_data['success'], False)
        self.assertEqual(response_data['message'], 'Unprocessable')

        # def test_get_categories_404(self):
    #     """ Response must return a Not Found error """
    #     response = self.client().get('/categories')
    #     response_data = json.loads(response.data)

    #     self.assertEqual(response.status_code, 404)
    #     self.assertEqual(response_data['success'], False)
    #     self.assertEqual(response_data['message'], 'Not Found')

    # def test_get_questions_404(self):
    #     """ Response must return a Not Found error"""
    #     response = self.client().get('/questions')
    #     response_data = json.loads(response.data)

    #     self.assertEqual(response.status_code, 404)
    #     self.assertEqual(response_data['success'], False)
    #     self.assertEqual(response_data['message'], 'Not Found')


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
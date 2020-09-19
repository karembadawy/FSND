import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

DB_HOST = os.getenv('DB_HOST', '127.0.0.1:5432')
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'postgres')
DB_NAME = os.getenv('DB_NAME', 'trivia_test')

class TriviaTestCase(unittest.TestCase):
  """This class represents the trivia test case"""

  def setUp(self):
    """Define test variables and initialize app."""
    self.app = create_app()
    self.client = self.app.test_client
    self.database_path = 'postgresql+psycopg2://{}:{}@{}/{}'.format(
        DB_USER, DB_PASSWORD, DB_HOST, DB_NAME
    )
    setup_db(self.app, self.database_path)

    # binds the app to the current context
    with self.app.app_context():
      self.db = SQLAlchemy()
      self.db.init_app(self.app)
      # create all tables
      self.db.create_all()

  def tearDown(self):
    """Executed after reach test"""
    pass

  # test Categories list
  def test_categories(self):
    # make request
    request = self.client().get('/categories')
    data = json.loads(request.data)

    # test results
    self.assertEqual(data['success'], True)
    self.assertTrue(len(data['categories']))

  # test Questions list based on category
  def test_questions_category(self):
    # make request
    request = self.client().get('/categories/1/questions')
    data = json.loads(request.data)

    # test results
    self.assertEqual(data['success'], True)
    self.assertTrue(len(data['questions']))
    self.assertTrue(data['total_questions'])
    self.assertTrue(data['current_category'])

  # test Questions list
  def test_categories(self):
    # make request
    request = self.client().get('/questions')
    data = json.loads(request.data)

    # test results
    self.assertEqual(data['success'], True)
    self.assertTrue(data['questions'])
    self.assertTrue(len(data['total_questions']))

  # test Create Question
  def test_add_question(self):
    # prepare question object
    question = {
      'question': 'new question',
      'answer': 'new answer',
      'difficulty': 1,
      'category': 1
    }
    # store questions count before insert
    questions_count = len(Question.query.all())
    # make request
    request = self.client().post('/questions', json=question)
    data = json.loads(request.data)
    # store questions count after insert
    questions_count_after = len(Question.query.all())

    # test results
    self.assertEqual(data["success"], True)
    self.assertEqual(questions_count_after, questions_count + 1)

  def test_search_question(self):
    # prepare search object
    search = {'searchTerm': 'test'}
    # make request
    request = self.client().post('/questions', json=search)
    data = json.loads(request.data)

    # test results
    self.assertEqual(data['success'], True)
    self.assertIsNotNone(data['questions'])
    self.assertIsNotNone(data['total_questions'])

# Make the tests conveniently executable
if __name__ == "__main__":
  unittest.main()

import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
  """This class represents the trivia test case"""

  def setUp(self):
    """Define test variables and initialize app."""
    self.app = create_app()
    self.client = self.app.test_client
    self.database_path = "postgresql://postgres:postgres@localhost:5432/trivia_test"
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

# Make the tests conveniently executable
if __name__ == "__main__":
  unittest.main()

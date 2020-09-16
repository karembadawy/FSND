#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

#----------------------------------------------------------------------------#
# Pagination
#----------------------------------------------------------------------------#

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in selection]
  current_questions = questions[start:end]

  return current_questions

# create the app
def create_app(test_config=None):
  #----------------------------------------------------------------------------#
  # App Config.
  #----------------------------------------------------------------------------#

  app = Flask(__name__)
  CORS(app)
  setup_db(app)

  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                         'Content-Type,Authorization,true')
    response.headers.add('Access-Control-Allow-Methods',
                         'GET,PATCH,POST,DELETE,OPTIONS')
    return response

  #----------------------------------------------------------------------------#
  # Controllers.
  #----------------------------------------------------------------------------#

  #  ----------------------------------------------------------------
  #  Categories
  #  ----------------------------------------------------------------

  #  Categories list
  #  ----------------------------------------------------------------

  @app.route('/categories')
  def categories():
    # query to retreive all the categories in the system
    selection = Category.query.order_by(Category.id).all()

    # raise 404 error code if there is no categories found
    if len(selection) == 0:
      abort(404)

    # return results in json form
    return jsonify({
      'success': True,
      'categories': { cat.id: cat.type for cat in selection },
      'total_categories': len(selection)
    })

  #  Questions list based on category
  #  ----------------------------------------------------------------

  @app.route('/categories/<int:category_id>/questions')
  def questions_category(category_id):
    # query to retreive all the questions in the system based on category
    selection = Question.query.filter(
      Question.category == str(category_id)).all()

    # raise 404 error code if there is no categories found
    if len(selection) == 0:
      abort(404)

    # return results in json form
    return jsonify({
      'success': True,
      'questions': [q.format() for q in selection],
      'total_questions': len(selection),
      'current_category': category_id
    })

  #  ----------------------------------------------------------------
  #  Questions
  #  ----------------------------------------------------------------

  #  Questions list
  #  ----------------------------------------------------------------

  @app.route('/questions')
  def list_questions():
    # query to retreive all the questions in the system
    selection = Question.query.order_by(Question.id).all()
    # handle pagination
    current_questions = paginate_questions(request, selection)
    # query to retreive all the categories in the system
    categories = Category.query.order_by(Category.id).all()

    # raise 404 error code if there is no questions found
    if len(current_questions) == 0:
      abort(404)

    # return results in json form
    return jsonify({
      'success': True,
      'questions': current_questions,
      'total_questions': len(selection),
      'categories': {cat.id: cat.type for cat in categories},
      'current_category': None
    })

  #  Create and Search Question
  #  ----------------------------------------------------------------

  @app.route("/questions", methods=['POST'])
  def add_search_question():
    # get values from form
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_category = body.get('category', None)
    new_difficulty = body.get('difficulty', None)
    search = body.get('searchTerm', None)

    try:
      if search:
        # query to retreive searched questions in the system
        selection = Question.query.order_by(Question.id).filter(
            Question.question.ilike('%{}%'.format(search)))
        # handle pagination
        current_questions = paginate_questions(request, selection)

        # raise 404 error code if there is no search found
        if len(selection) == 0:
          abort(404)

        # return results in json form
        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection)
        })
      else:
        # create and insert record on db
        question = Question(
          question = new_question,
          answer = new_answer,
          category = new_category,
          difficulty = new_difficulty
        )

        question.insert()
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        # return results in json form
        return jsonify({
          'success': True,
          'created': question.id,
          'questions': current_questions,
          'total_questions': len(selection)
        })
    except:
      # raise 422 error code if any error happend while create question
      abort(422)

  #  Delete Question
  #  ----------------------------------------------------------------

  @app.route("/questions/<int:question_id>", methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(
          Question.id == question_id).one_or_none()

      # raise 404 error code if there is no questions found
      if question is None:
        abort(404)

      # delete question
      question.delete()
      selection = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, selection)

      # return results in json form
      return jsonify({
        'success': True,
        'deleted': question_id,
        'questions': current_questions,
        'total_questions': len(selection)
      })
    except:
      # raise 422 error code if any error happend while delete question
      abort(422)

  #  ----------------------------------------------------------------
  #  Quizzes
  #  ----------------------------------------------------------------

  #  Quiz play
  #  ----------------------------------------------------------------

  @app.route('/quizzes', methods=['POST'])
  def play_quiz():
    try:
      # get values from form
      body = request.get_json()

      category = body.get('quiz_category', None)
      questions = body.get('previous_questions', None)

      # prepare list of questions based on selected category
      if category['type'] == 'click':
        available_questions = Question.query.filter(
          Question.id.notin_(questions)
        ).all()
      else:
        available_questions = Question.query.filter_by(
          category=category['id']
        ).filter(Question.id.notin_(questions)).all()

      # prepare new question for the next round
      question = available_questions[random.randrange(
        0, len(available_questions)
      )].format() if len(available_questions) > 0 else None

      # return results in json form
      return jsonify({
        'success': True,
        'question': question
      })
    except:
      abort(422)

  #----------------------------------------------------------------------------#
  # Errors Handler.
  #----------------------------------------------------------------------------#

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "unprocessable"
    }), 422

  return app

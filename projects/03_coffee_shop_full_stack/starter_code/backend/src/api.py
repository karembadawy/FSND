#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
setup_db(app)
CORS(app)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

#  ----------------------------------------------------------------
#  Drinks
#  ----------------------------------------------------------------

#  Drinks list
#  ----------------------------------------------------------------

@app.route('/drinks')
def drinks():
  try:
    # query to retreive all the drinks in the system
    selection = Drink.query.all()
    drinks = [drink.short() for drink in selection]

    # return results in json form
    return jsonify({
      'success': True,
      'drinks': drinks
    })
  except:
    # raise 404 error code if there is no drinks found
    abort(404)

#  Drinks detail
#  ----------------------------------------------------------------

@app.route("/drinks-detail")
@requires_auth('get:drinks-detail')
def drink_detail(jwt):
  try:
    # query to retreive all the drinks in the system
    selection = Drink.query.all()
    drink_detail = [drink.long() for drink in selection]

    # return results in json form
    return jsonify({
      'success': True,
      'drinks': drink_detail
    })
  except:
    # raise 404 error code if there is no drinks found
    abort(404)

#  Create Drink
#  ----------------------------------------------------------------

@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
  # get values from form
  body = request.get_json()

  new_title = body.get('title', None)
  new_recipe = body.get('recipe', None)

  try:
    # create and insert record on db
    drink = Drink(
      title=new_title,
      recipe=json.dumps(new_recipe)
    )

    drink.insert()
    new_drink = [drink.long()]

    # return results in json form
    return jsonify({
      'success': True,
      'drinks': new_drink
    })
  except:
    # raise 422 error code if any error happend while create drink
    abort(422)

#  Edit Drink
#  ----------------------------------------------------------------

@app.route("/drinks/<int:drink_id>", methods=['PATCH'])
@requires_auth('patch:drinks')
def edit_drink(jwt, drink_id):
  # query to get specific drink
  drink = Drink.query.get(drink_id)

  if drink:
    try:
      # get values from form
      body = request.get_json()

      new_title = body.get('title', None)
      new_recipe = body.get('recipe', None)

      # update record on db
      drink.title = new_recipe
      drink.recipe = new_recipe

      drink.update()
      new_drink = [drink.long()]

      # return results in json form
      return jsonify({
        'success': True,
        'drinks': new_drink
      })
    except:
      # raise 422 error code if any error happend while update drink
      abort(422)
  else:
    # raise 404 error code if the drink not found
    abort(404)

#  Delete Drink
#  ----------------------------------------------------------------

@app.route("/drinks/<int:drink_id>", methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(jwt, drink_id):
  # query to get specific drink
  drink = Drink.query.get(drink_id)

  if drink:
    try:
      # delete record on db
      drink.delete()

      # return results in json form
      return jsonify({
        'success': True,
        'delete': drink_id
      })
    except:
      # raise 422 error code if any error happend while delete drink
      abort(422)
  else:
    # raise 404 error code if the drink not found
    abort(404)

#----------------------------------------------------------------------------#
# Errors Handler.
#----------------------------------------------------------------------------#

@app.errorhandler(422)
def unprocessable(error):
  return jsonify({
    "success": False,
    "error": 422,
    "message": "unprocessable"
  }), 422

@app.errorhandler(404)
def not_found(error):
  return jsonify({
    "success": False,
    "error": 404,
    "message": "resource not found"
  }), 404


@app.errorhandler(AuthError)
def auth_error(ex):
  return jsonify({
    "success": False,
    "error": ex.status_code,
    'message': ex.error
  }), 401

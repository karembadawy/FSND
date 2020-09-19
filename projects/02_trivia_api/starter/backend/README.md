# Full Stack Trivia API Backend

## Getting Started

### Installing Dependencies

#### Python 3.7

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### Virtual Enviornment

We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

#### PIP Dependencies

Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

This will install all of the required packages we selected within the `requirements.txt` file.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server.

## Database Setup

With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:

```bash
psql trivia < trivia.psql
```

## Running the server

From within the `backend` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
export FLASK_APP=flaskr
export FLASK_ENV=development
flask run
```

Setting the `FLASK_ENV` variable to `development` will detect file changes and restart the server automatically.

Setting the `FLASK_APP` variable to `flaskr` directs flask to use the `flaskr` directory and the `__init__.py` file to find the application.

## Tasks

One note before you delve into your tasks: for each endpoint you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior.

1. Use Flask-CORS to enable cross-domain requests and set response headers.
2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories.
3. Create an endpoint to handle GET requests for all available categories.
4. Create an endpoint to DELETE question using a question ID.
5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score.
6. Create a POST endpoint to get questions based on category.
7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question.
8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions.
9. Create error handlers for all expected errors including 400, 404, 422 and 500.

## API Documentation

1. GET `/categories` :

    - Description: fetch all categories data
    - Request Arguments: None
    - Returns:

      ```json
      {
        'success': True,
        'categories': {
          '1' : "Science",
          '2' : "Art",
          '3' : "Geography",
          '4' : "History",
          '5' : "Entertainment",
          '6' : "Sports"
        },
        'total_categories': 6
      }
      ```

2. GET `/categories/<int:category_id>/questions` :

    - Description: fetch Questions list based on category
    - Request Arguments: category_id
    - Returns:

      ```json
      {
        'success': True,
        'questions': [{
          'id': 1,
          'question': "Question 1?",
          'answer': "Answer 1",
          'difficulty': 1,
          'category': 6
        },{
          'id': 2,
          'question': "Question 2?",
          'answer': "Answer 2",
          'difficulty': 2,
          'category': 6
        }],
        'total_questions': 2,
        'current_category': 6
      }
      ```

3. GET `/questions` :

    - Description: fetch all questions data
    - Request Arguments: None
    - Returns:

      ```json
      {
        'success': True,
        'questions': [{
          'id': 1,
          'question': "Question 1?",
          'answer': "Answer 1",
          'difficulty': 1,
          'category': 1
        },{
          'id': 2,
          'question': "Question 2?",
          'answer': "Answer 2",
          'difficulty': 2,
          'category': 2
        }],
        'total_questions': 2,
        'current_category': None
      }
      ```

4. POST `/questions` :

    - Description: create new question
    - Request Body:

      ```json
      {
        'question': "Question 3?",
        'answer': "Answer 3",
        'difficulty': 3,
        'category': 3
      }
      ```

    - Returns:

      ```json
      {
        'success': True,
        'created': 3,
        'questions': [{
          'id': 1,
          'question': "Question 1?",
          'answer': "Answer 1",
          'difficulty': 1,
          'category': 1
        },{
          'id': 2,
          'question': "Question 2?",
          'answer': "Answer 2",
          'difficulty': 2,
          'category': 2
        },{
          'id': 3,
          'question': "Question 3?",
          'answer': "Answer 3",
          'difficulty': 3,
          'category': 3
        }],
        'total_questions': 3
      }
      ```

5. POST `/questions/search` :

    - Description: search for question
    - Request Body:

      ```json
      {
        'searchTerm': "3"
      }
      ```

    - Returns:

      ```json
      {
        'success': True,
        'questions': [{
          'id': 3,
          'question': "Question 3?",
          'answer': "Answer 3",
          'difficulty': 3,
          'category': 3
        }],
        'total_questions': 1
      }
      ```

6. DELETE `/questions/<int:question_id>` :

    - Description: deletes a question given id
    - Request Arguments: question_id
    - Returns:

      ```json
      {
        'success': True,
        'deleted': 2,
        'questions': [{
          'id': 1,
          'question': "Question 1?",
          'answer': "Answer 1",
          'difficulty': 1,
          'category': 1
        },{
          'id': 3,
          'question': "Question 3?",
          'answer': "Answer 3",
          'difficulty': 3,
          'category': 3
        }],
        'total_questions': 2
      }
      ```

7. POST `/quizzes` :

    - Description: get random question
    - Request Body:

        ```json
        {
          'quiz_category': {
            'id': 1,
            type: 'click'
          },
          'previous_questions': []
        }
        ```

    - Returns:

      ```json
      {
        'success': True,
        'question': {
          'id': 1,
          'question': "Question 1?",
          'answer': "Answer 1",
          'difficulty': 1,
          'category': 1
        }
      }
      ```

8. In case of any error will happen like 404, 422, .. etc
    - Returns:

        ```json
        {
          'success': False,
          'error': 422,
          'message': "unprocessable"
        }
        ```

## Testing

To run the tests, run

```BASH
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```

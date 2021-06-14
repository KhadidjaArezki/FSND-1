# Backend - Full Stack Trivia API 

### Installing Dependencies for the Backend

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)


2. **Virtual Enviornment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organaized. Instructions for setting up a virual enviornment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)


3. **PIP Dependencies** - Once you have your virtual environment setup and running, install dependencies by naviging to the `/backend` directory and running:
```bash
pip install -r requirements.txt
```
This will install all of the required packages we selected within the `requirements.txt` file.


4. **Key Dependencies**
 - [Flask](http://flask.pocoo.org/)  is a lightweight backend microservices framework. Flask is required to handle requests and responses.

 - [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py. 

 - [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server. 

### Database Setup
With Postgres running, restore a database using the trivia.psql file provided. From the backend folder in terminal run:
```bash
psql trivia < trivia.psql
```
For Windows run:
'''
psql -d trivia -a -f "trivia.psql"
'''

### Configuration
Configure your database connection in `config.py`.
Inside this file, setup environment variables to connect to your database server.

### Running the server

From within the `./src` directory first ensure you are working using your created virtual environment.

To run the server, execute:

```bash
flask run --reload
```

The `--reload` flag will detect file changes and restart the server automatically.

## ToDo Tasks
These are the files you'd want to edit in the backend:

1. *./backend/app.py
2. *./backend/test_flaskr.py*


One note before you delve into your tasks: for each endpoint, you are expected to define the endpoint and response data. The frontend will be a plentiful resource because it is set up to expect certain endpoints and response data formats already. You should feel free to specify endpoints in your own way; if you do so, make sure to update the frontend or you will get some unexpected behavior. 

1. Use Flask-CORS to enable cross-domain requests and set response headers. 


2. Create an endpoint to handle GET requests for questions, including pagination (every 10 questions). This endpoint should return a list of questions, number of total questions, current category, categories. 


3. Create an endpoint to handle GET requests for all available categories. 


4. Create an endpoint to DELETE question using a question ID. 


5. Create an endpoint to POST a new question, which will require the question and answer text, category, and difficulty score. 


6. Create a POST endpoint to get questions based on category. 


7. Create a POST endpoint to get questions based on a search term. It should return any questions for whom the search term is a substring of the question. 


8. Create a POST endpoint to get questions to play the quiz. This endpoint should take category and previous question parameters and return a random questions within the given category, if provided, and that is not one of the previous questions. 


9. Create error handlers for all expected errors including 400, 404, 422 and 500. 

### Error Handling
Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 404: Resource Not Found
- 422: Not Processable 

## Review Comment to the Students
```
This README is missing documentation of your endpoints. Below is an example for your endpoint to get all categories. Please use it as a reference for creating your documentation and resubmit your code. 

## Endpoints
GET '/categories'
GET '/questions'
GET '/categories/<int:category_id>/questions'
POST '/questions'
POST '/categories'
POST '/questions/search'
POST '/quizzes'
POST '/games'
DELETE '/questions/<int:question_id>'


## GET '/categories'
- Fetches a dictionary of categories in which the keys are the ids and the value is the corresponding string of the category
- Request Arguments: None
- Returns: An object with a single key, categories, that contains a object of id: category_string key:value pairs. 
'''
{'1' : "Science",
'2' : "Art",
'3' : "Geography",
'4' : "History",
'5' : "Entertainment",
'6' : "Sports"}
'''

## GET '/questions'
- Fetches a list of paginated questions: a question has five fields - question, answer, difficulty, category, and rating.
- Request arguments: none
- Returns: An object with four keys - questions: a list of questions, total_questions: an integer representing the total 
    number of questions in the database , categories: an object that maps a category id to its type , current_category: a string
    that represents a category name.
- Sample Resonse:
'''
{
  "categories": {
    "1": "Science",
    "2": "Art",
    "3": "Geography",
    "4": "History",
    "5": "Entertainment",
    "6": "Sports",
    "7": "Tech"
  },
  "current_category": "History",
  "questions": [
    {
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2,
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
      "rating": 3
    },
    {
      "answer": "Muhammad Ali",
      "category": 4,
      "difficulty": 1,
      "id": 9,
      "question": "What boxer's original name is Cassius Clay?",
      "rating": 3
    },
    {
      "answer": "Apollo 13",
      "category": 5,
      "difficulty": 4,
      "id": 2,
      "question": "What movie earned Tom Hanks his third straight Oscar nomination, in 1996?",
      "rating": 3
    }
  ],
  "success": true,
  "total_questions": 3
}
'''

## GET '/categories/<int:category_id>/questions'
- Fetches a list of paginated questions filtered by the provided category id.
- Request arguments : category_id.
- Returns: An object with three keys - questions: a list of questions, total_questions: an integer representing the total 
    number of questions in this category, current_category: a string that represents a category name.
- Sample Response:
'''
{
  "current_category": "Sports",
  "questions": [
    {
      "answer": "Brazil",
      "category": 6,
      "difficulty": 3,
      "id": 10,
      "question": "Which is the only team to play in every soccer World Cup tournament?",
      "rating": 3
    },
    {
      "answer": "Uruguay",
      "category": 6,
      "difficulty": 4,
      "id": 11,
      "question": "Which country won the first ever soccer World Cup in 1930?",
      "rating": 3
    }
  ],
  "success": true,
  "total_questions": 2
}
'''

## POST '/questions'
- Creates a new question using the submitted question, answer, difficulty, category, and rating.
- Sample request: curl "http://127.0.0.1:5000/questions" -X POST -H "Content-Type: application/json" -d '{"question":"When did life begin?", "answer":"You tell me",
    "difficulty":"5", "category":"1", "rating":"3"}'
- Returns: Nothing

## POST '/categories'
- Creates a new category using the submitted type.
- Sample Request: curl "http://127.0.0.1:5000/categories" -X POST -H "Content-Type: application/json" -d '{"type":"Literature"}'
- Returns: Nothing.

## POST '/questions/search'
- Fetches a list of questions filtered by the submitted search term.
- Sample Request: curl "http://127.0.0.1:5000/questions/search" -X POST -H "Content-Type: application/json" -d '{"searchTerm":"title"}'
- Returns: An object with three keys - questions: a list of questions for whom the search term is a substring of the question,
    total_questions: the number of questions matched by the search, current_category: a string that represents a category name.
- Sample Response:
''' 
{
  "current_category": "History",
  "questions": [
    {
      "answer": "Maya Angelou",
      "category": 4,
      "difficulty": 2,
      "id": 5,
      "question": "Whose autobiography is entitled 'I Know Why the Caged Bird Sings'?",
      "rating": 3
    },
    {
      "answer": "Edward Scissorhands",
      "category": 5,
      "difficulty": 3,
      "id": 6,
      "question": "What was the title of the 1990 fantasy directed by Tim Burton about a young man with multi-bladed appendages?",
      "rating": 3
    }
  ],
  "success": true,
  "total_questions": 2
}
'''

## POST '/quizzes'
- Fetches a question to play the quiz. It take category and previous question parameters.
- Sample Request: 
    curl "http://127.0.0.1:5000/quizzes" -X POST -H "Content-Type: application/json" -d '{"previous_questions":"[1,2]", 
    "quiz_category":"{'id':1, 'type': 'Science'}"}'
- Returns: a random questions within the given category, if provided, and that is not one of the previous questions. 
- Sample Response:
'''
{ 
    'question': {
        'id': 1, 
        'question': 'This is a question', 
        'answer': 'This is an answer', 
        'difficulty': 5, 
        'category': 4 
    } 
}
'''

## POST '/games'
- Saves a player's game: A game has a category - if provided - a score and a timestamp.
    If the player is new, it stores the new player's username.
- Sample Request:
    curl "http://127.0.0.1:5000/quizzes" -X POST -H "Content-Type: application/json" -d '{"name": "tester999", "category_id": "1", "timestamp": "11/06/2021, 14:01:40", "score": "0"}'
- Returns: Nothing

## DELETE '/questions/<int:question_id>'
- Deletes a question using a question ID.
- Request arguments: question_id.
- Returns: deleted question id
'''
{
    'deleted': 1
}
'''

## Testing
To run the tests, run
```
dropdb trivia_test
createdb trivia_test
psql trivia_test < trivia.psql
python test_flaskr.py
```
For Windows run:
```
psql -U <owner> -c "drop database trivia_test;"
psql -U <owner> -c "create database trivia_test;"
psql -U <owner> -d trivia_test -a -f "trivia.psql"
python test_flaskr.py

```

## Authors: the API and the test suite were developed by Khadidja Arezki
## Acknowledgements: Special thanks for the Udacity team for providing the frontend, the models, and database, 
    as well as taking care of dependencies and configuration.
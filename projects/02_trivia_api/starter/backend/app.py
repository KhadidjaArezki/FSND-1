import os
import sys
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug import exceptions
from flask_cors import CORS
import random

from models import db, setup_db, Question, Category, User, Games

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
    @DONE: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    '''
    CORS(app, resources={r"/*": {"origins": "*"}})
    '''
    @DONE: Use the after_request decorator to set Access-Control-Allow
    '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, true')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, PATCH, DELETE, OPTIONS')
        return response
    
    ######################################################
    # Helper Method for get_questions

    def paginate_questions(request, questions):
        '''
        Returns question objects paginated by 
        a number (QUESTIONS_PER_PAGE)
        '''
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * QUESTIONS_PER_PAGE
        end = start + QUESTIONS_PER_PAGE
        formatted_questions = [question.format() for question in questions]
        return formatted_questions[start:end]

    #######################################################
    # Helper Method for create_question

    def validate_question(request_json):
        question = request_json['question']
        answer = request_json['answer']
        if question == '' or answer == '':
            raise exceptions.UnprocessableEntity()

        else:
            difficulty = request_json['difficulty']
            rating = request_json['rating']
            category_id = int(request_json['category'])

            category = Category.query.get(category_id)                
            if category is None:
                raise exceptions.UnprocessableEntity()
            
            else:
                new_question = Question(question=question, answer=answer, 
                    difficulty=difficulty, category=category_id, rating=rating)
                return new_question

    #######################################################
    # Helper Methods For play_quiz

    def get_question_objects(request_object):
        '''
        Get question objects by category if provided
        otherwise, returm them all  
        '''
        if request_object['quiz_category'].get('id') == 0:
            question_objects = Question.query.all()
        else:
            quiz_category = request_object['quiz_category']
            category_id = quiz_category.get('id')
            category = Category.query.get(category_id)
            if category is None:
                raise exceptions.UnprocessableEntity() 
            else:
                question_objects = Question.query.filter_by(category=category_id).all()
        
        return question_objects

    def get_unasked_questions(previous_questions, all_questions):
        if len(previous_questions) >= len(all_questions):
            previous_questions = []

        unasked_questions = [
            id for id in all_questions 
                if id not in previous_questions
            ]
        return unasked_questions

    def get_random_question(unasked_questions, question_objects):
        '''
        Get a random question id and return the 
        corresponding question object
        '''
        random_question_id = random.choice(unasked_questions)
        for question in question_objects:
            if question.id == random_question_id:
                return question 
        raise exceptions.InternalServerError()
    
    '''
    @DONE: 
    Create an endpoint to handle GET requests 
    for all available categories.
    '''
    @app.route('/categories')
    def get_categories():

        categories = {}
        try:
            category_objects = Category.query.all()
            if len(category_objects) == 0:
                raise exceptions.NotFound()

            else:
                for category in category_objects:
                    categories[category.id] = category.type
                return jsonify({
                    'success' : True,
                    'categories' : categories, 
                    })
        
        except exceptions.NotFound:
            abort(404)
        except exceptions.BadRequest:
            abort(400)
        except exceptions.MethodNotAllowed:
            abort(405)
        except exceptions.InternalServerError:
            abort(500)
        except:
            print(sys.exc_info())



    '''
    @DONE: 
    Create an endpoint to handle GET requests for questions, 
    including pagination (every 10 questions). 
    This endpoint should return a list of questions, 
    number of total questions, current category, categories. 

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions. 

    '''
    @app.route('/questions')
    def get_questions():
        try:
            questions = Question.query.all()
            formatted_questions = paginate_questions(request, questions)

            if len(formatted_questions) == 0:
                raise exceptions.NotFound()
            else:
                categories = {}
                category_objects = Category.query.all()
                for category in category_objects:
                    categories[category.id] = category.type

                current_category = 'History'
                return jsonify({
                    'success' : True,
                    'questions' : formatted_questions,
                    'total_questions' : len(questions),
                    'categories' : categories,
                    'current_category' : current_category
                })

        except exceptions.NotFound:
            abort(404)
        except exceptions.BadRequest:
            abort(400)
        except exceptions.MethodNotAllowed:
            abort(405)
        except exceptions.InternalServerError:
            abort(500)
        except:
            print(sys.exc_info())

    '''
    @DONE: 
    Create an endpoint to DELETE question using a question ID. 

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page. 
    '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            if question is None:
                raise exceptions.NotFound()
            else:
                question.delete()
                return jsonify({
                    'success' : True,
                    'deleted' : question_id,
                })

        except exceptions.NotFound:
            abort(404)
        except exceptions.BadRequest:
            abort(400)
        except exceptions.MethodNotAllowed:
            abort(405)
        except exceptions.InternalServerError:
            db.session.rollback()
            abort(500)
        except:
            print(sys.exc_info())

        finally:
                db.session.close()

    '''
    @DONE: 
    Create an endpoint to POST a new question, 
    which will require the question and answer text, 
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab, 
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.  
    '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        try:
            request_json = request.get_json()
            if request_json is None:
                raise exceptions.BadRequest()

            else:
                new_question = validate_question(request_json)
                new_question.insert()
                return jsonify({
                    'success' : True
                })

        except exceptions.BadRequest:
            abort(400)
        except exceptions.MethodNotAllowed:
            abort(405)
        except KeyError:
            print(sys.exc_info())
            abort(422)
        except exceptions.UnprocessableEntity:
            print(sys.exc_info())
            abort(422)
        except exceptions.InternalServerError:
            db.session.rollback()
            abort(500)
        except:
            print(sys.exc_info())

        finally:
            db.session.close()


    @app.route('/categories', methods=['POST'])
    def create_category():
        try:
            request_json = request.get_json()
            if request_json is None:
                raise exceptions.BadRequest()

            else:
                category_type = request_json['type']
                if category_type == '':
                    raise exceptions.UnprocessableEntity()
                else:
                    category = Category(type=category_type, games=[])
                    category.insert()

                    return jsonify({
                            'success' : True
                        })
                         
        except exceptions.BadRequest:
            abort(400)
        except exceptions.MethodNotAllowed:
            abort(405)
        except KeyError:
            print(sys.exc_info())
            abort(422)
        except exceptions.UnprocessableEntity:
            print(sys.exc_info())
            abort(422)
        except exceptions.InternalServerError:
            db.session.rollback()
            abort(500)
        except:
            print(sys.exc_info())

        finally:
            db.session.close()

    '''
    @DONE: 
    Create a POST endpoint to get questions based on a search term. 
    It should return any questions for whom the search term 
    is a substring of the question. 

    TEST: Search by any phrase. The questions list will update to include 
    only question that include that string within their question. 
    Try using the word "title" to start. 
    '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        try:
            request_object =  request.get_json()
            if request_object is None:
                raise exceptions.BadRequest()
            else:
                search_term = request_object['searchTerm']
                search = '%{}%'.format(search_term)
                question_objects = Question.query.filter(
                    Question.question.ilike(search)).all()
                questions = [question.format() for question in question_objects]
                category_str = 'History'

                return jsonify({
                    'success' : True,
                    'questions' : questions,
                    'total_questions' : len(questions),
                    'current_category' : category_str
                })

        except exceptions.BadRequest:
            abort(400)
        except exceptions.MethodNotAllowed:
            abort(405)
        except KeyError:
            print(sys.exc_info())    
            abort(422)
        except exceptions.InternalServerError:
            abort(500)
        except:
            print(sys.exc_info())    



    '''
    @DONE: 
    Create a GET endpoint to get questions based on category. 

    TEST: In the "List" tab / main screen, clicking on one of the 
    categories in the left column will cause only questions of that 
    category to be shown. 
    '''
    @app.route('/categories/<int:category_id>/questions')
    def get_category_questions(category_id):
        try:
            category_object = Category.query.get(category_id)
            if category_object is None:
                raise exceptions.NotFound()
            else:
                question_objects = Question.query.filter_by(category=category_id).all()
                questions = [question.format() for question in question_objects]
                category_str = category_object.type
                
                return jsonify({
                    'success' : True,
                    'questions' : questions,
                    'total_questions' : len(questions),
                    'current_category' : category_str
                })

        except exceptions.NotFound:
            abort(404)
        except exceptions.BadRequest:
            abort(400)
        except exceptions.MethodNotAllowed:
            abort(405)
        except exceptions.InternalServerError:
            abort(500)
        except:
            print(sys.exc_info())      
        

    '''
    @DONE: 
    Create a POST endpoint to get questions to play the quiz. 
    This endpoint should take category and previous question parameters 
    and return a random questions within the given category, 
    if provided, and that is not one of the previous questions. 

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not. 
    '''
    @app.route('/quizzes', methods=['POST'])
    def play_quiz():
        try:
            request_object = request.get_json()
            if request_object is None:
                raise exceptions.BadRequest()
            else:
                previous_questions = request_object['previous_questions']

                question_objects = get_question_objects(request_object)
                all_questions = [question.id for question in question_objects]

                unasked_questions = get_unasked_questions(previous_questions, all_questions)
                random_question = get_random_question(unasked_questions, question_objects)

                return jsonify({
                    'success' : True,
                    'question' : random_question.format()
                })

        except exceptions.BadRequest:
            abort(400)
        except exceptions.MethodNotAllowed:
            abort(405)
        except KeyError:
            print('A json key error occured')
            abort(422)
        except exceptions.UnprocessableEntity:
            print('Category is probably non existent')
            abort(422)
        except exceptions.InternalServerError:
            abort(500)
        except:
            print('Unexpected error', sys.exc_info())
            abort(500)


    @app.route('/games', methods=['POST'])
    def save_game():
        '''
        Stores a player's game:
        A game has a category - if provided - a score and a timestamp
        if the player is new, it stores the new player's username
        '''
        try:
            request_object = request.get_json()
            if request_object is None:
                raise exceptions.BadRequest()
            else:
                name = request_object['name']
                category_id = request_object['category_id']
                score = request_object['score']
                time = request_object['timestamp']

                user = User.query.filter_by(name=name).one_or_none()
                if user is None:
                    user = User(name=name, games=[])
                    db.session.add(user)
                    db.session.flush()
                    user_id = user.id
                else:
                    user_id = user.id

                game = Games(user_id=user_id, score=score, category_id=category_id, 
                    time=time, player=user, category=Category.query.get(category_id))
                user.games.append(game)
                db.session.add(game)
                db.session.commit()

                return jsonify({
                    'success': True
                })
        
        except exceptions.BadRequest:
            abort(400)
        except exceptions.MethodNotAllowed:
            abort(405)
        except KeyError:
            print(sys.exc_info())
            abort(422)
        except exceptions.UnprocessableEntity:
            print(sys.exc_info())
            abort(422)
        except exceptions.InternalServerError:
            db.session.rollback()
            abort(500)
        except:
            print(sys.exc_info())

        finally:
            db.session.close()


    '''
    @DONE: 
    Create error handlers for all expected errors 
    including 404 and 422. 
    '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success" : False,
            "error" : 400,
            "message" : "Bad Request",
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False, 
            "error": 404,
            "message": "Not Found",
            }), 404
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success" : False,
            "error" : 405,
            "message" : "Method Not Allowed"
        }), 405
    
    @app.errorhandler(422)
    def uprocessable(error):
        return jsonify({
            "success" : False,
            "error" : 422,
            "message" : "Unprocessable",
        }), 422

    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
            "success" : False,
            "error" : 500,
            "message" : "Internal Server Error"
        }), 500

    
    

    return app

    
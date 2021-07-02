import os
import sys
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
import logging
from werkzeug import exceptions

from .database.models import db, db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

logging.basicConfig(filename='error.log',
                    level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

app = Flask(__name__)
setup_db(app)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                            'Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods',
                            'GET, POST, PUT, PATCH, DELETE, OPTIONS')
    return response

'''
@DONE uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
db_drop_and_create_all()

# ROUTES
'''
@DONE implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks}
        where drinks is the list of drinks or appropriate status
        code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    try:
        drinks_objects = Drink.query.all()
        if len(drinks_objects) == 0:
            raise exceptions.NotFound()

        else:
            drinks = [drink.short() for drink in drinks_objects]
            return jsonify({
                "success": True,
                "drinks": drinks
            })
    except exceptions.NotFound:
            abort(404)
    except exceptions.InternalServerError:
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())

'''
@DONE implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} 
        where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details():
    try:
        drinks_objects = Drink.query.all()
        if len(drinks_objects) == 0:
            raise exceptions.NotFound()
        
        else:
            drinks = [drink.long() for drink in drinks_objects]
            return jsonify({
                'success': True,
                'drinks': drinks
            })
    except exceptions.NotFound:
            abort(404)
    except AuthError as auth_error:
        abort(auth_error)
    except exceptions.InternalServerError:
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())

'''
@DONE implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink():
    try:
        # Retrieve submitted drink
        drink_json = request.get_json('drink')
        if drink_json is None:
            raise exceptions.BadRequest()

        title = drink_json['title']
        recipe_dict = drink_json['recipe']
        for ingredient in recipe_dict:
            if not ingredient['name']:
                raise exceptions.UnprocessableEntity()
        recipe = json.dumps(recipe_dict)

        # Create and add new drink
        new_drink  = Drink(title=title, recipe=recipe)
        db.session.add(new_drink)
        db.session.flush()
        db.session.commit()

        return jsonify({
            "success": True,
            "drinks": [{
                'id': new_drink.id,
                'title': new_drink.title,
                'recipe': json.loads(new_drink.recipe)
            }]
        })

    except exceptions.BadRequest:
        abort(400)
    except AuthError as auth_error:
        abort(auth_error)
    except KeyError:
        print(sys.exc_info())
        abort(422)
    except exceptions.UnprocessableEntity:
        print(sys.exc_info())
        abort(422)
    except exceptions.InternalServerError:
        db.session.rollback()
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())

    finally:
        db.session.close()

'''
@DONE implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink}
        where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(id):
    drink = Drink.query.get(id)
    if drink is None:
        raise exceptions.NotFound()
    try:
        # Retrieve and update submitted drink
        drink_json = request.get_json('drink')
        if drink_json is None:
            raise exceptions.BadRequest()

        drink.title = drink_json['title']
        recipe_object = drink_json['recipe']
        for ingredient in recipe_object:
            if not ingredient['name']:
                raise exceptions.UnprocessableEntity()
        recipe = json.dumps(recipe_object)
        drink.recipe = recipe        

        # Add updated drink
        db.session.add(drink)
        db.session.flush()
        drink.update()

        return jsonify({
            "success": True,
            "drinks": [{
                'id': drink.id,
                'title': drink.title,
                'recipe': json.loads(drink.recipe)
            }]
        })

    except exceptions.BadRequest:
        abort(400)
    except AuthError as auth_error:
        abort(auth_error)
    except KeyError:
        print(sys.exc_info())
        abort(422)
    except exceptions.UnprocessableEntity:
        print(sys.exc_info())
        abort(422)
    except exceptions.InternalServerError:
        db.session.rollback()
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())
    finally:
        db.session.close()

'''
@DONE implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id}
        where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(id):
    try:
        drink = Drink.query.get(id)
        if drink is None:
            raise exceptions.NotFound()
        drink.delete()
        return jsonify({
            "success": True,
            "delete": id
        })
        
    except exceptions.NotFound:
        abort(404)
    except AuthError as auth_error:
        abort(auth_error)
    except exceptions.InternalServerError:
        db.session.rollback()
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())
    finally:
        db.session.close()

# Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    logging.error(error)
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
@DONE implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False,
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''
'''
@DONE implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def unprocessable(error):
    logging.error(error)
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
@DONE implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def unauthorized(error):
    logging.error(error)
    return jsonify({
        "success": False,
        "error": error.status_code,
        "message": error.error,
    }), error.status_code

@app.errorhandler(400)
def bad_request(error):
    logging.error(error)
    return jsonify({
        "success": False,
        "error": 400,
        "message": "Bad Request",
    }), 400

@app.errorhandler(500)
def internal_server_error(error):
    logging.error(error)
    return jsonify({
        "success": False,
        "error": 500,
        "message": "Internal Server Error"
    }), 500
#!./env/Scripts/python
import os
import sys
from flask import Flask, render_template, request, redirect, url_for, jsonify, abort, send_file
from sqlalchemy import exc
from sqlalchemy import and_
from datetime import datetime 
import json
from flask_cors import CORS
import logging
from werkzeug import exceptions
from auth.auth import AuthError, requires_auth
from request_ebay import search_ebay, search_product
import re

from models import db, db_drop_and_create_all, setup_db, Deal, Product, Alert, User, Filter

logging.basicConfig(filename='error.log',
                    level=logging.DEBUG, 
                    format='%(asctime)s %(levelname)s %(name)s %(message)s')

app = Flask(__name__)
setup_db(app)
app.jinja_env.globals.update(len=len)

# setup_db(app)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers',
                            'Origin, Accept, Content-Type, Authorization, true')
    response.headers.add('Access-Control-Allow-Methods',
                            'GET, POST, PUT, PATCH, DELETE, OPTIONS')
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Credentials', 'true')
    return response

'''
uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this funciton will add one
'''
# db_drop_and_create_all()

ITEMS_PER_PAGE = 5

# HELPERS
'''
@TODO: Add helpers docstrings
'''
def paginate_alerts(user_id, page):
    '''
    Returns alert objects paginated by
    a number (QUESTIONS_PER_PAGE)
    '''
    # page = request.args.get('page', 1, type=int)
    alert_objects = Alert.query.filter_by(user_id=user_id).paginate(
                    page=page,
                    per_page=ITEMS_PER_PAGE,
                    max_per_page=5).items

    return alert_objects

def format_alerts(alert_objects):
    alerts = []
    for alert_object in alert_objects:
        alert = {}
        product = alert_object.product

        # Check last time the product price was updated
        last_updated = product.last_updated
        time_diff = datetime.now() - last_updated
        hours_diff = time_diff.total_seconds() / 3600
        # if 12 hours or more have elapsed send request
        #  to ebay to get current price and price diff
        if hours_diff >= 12:
            print(hours_diff, ' update product')
            product = update_product(product) or product
            print(product)
            # product.update()
        alert['alert_id'] = alert_object.id
        alert['desired_price'] = alert_object.desired_price
        alert['product_name'] = product.name
        alert['product_link'] = product.link
        alert['product_image'] = product.image
        alert['price_difference'] = product.price_difference
        alert['product_price'] = product.current_price
        alert['product_currency'] = product.currency
        alert['product_store'] = product.store

        # alert['alert_product'] = formatted_product
        alerts.append(alert)
    return alerts

def paginate_results(search_results, page_number):
    start_page = (page_number - 1) * ITEMS_PER_PAGE
    end_page = start_page + ITEMS_PER_PAGE
    print(start_page, end_page)
    return search_results[start_page: end_page]
    
def get_deals():
    '''
    docstring
    '''
    deals = Deal.query.all()
    if deals:
        return [deal.format() for deal in deals]
    else:
        return []

def add_product(request_json, product_id):
    product_name = request_json['product_name']
    product_link = request_json['product_link']
    product_image = request_json['product_image']
    product_price_str = request_json['product_price']
    product_currency, product_price = product_price_str.split(' ')
    product_initial_price = float(product_price)
    product_store = request_json['product_store']
    last_updated = datetime.now()

    # Add product
    product = Product(product_id=product_id, name=product_name, last_updated=last_updated,
                    link=product_link, image=product_image, store=product_store,
                    initial_price=product_initial_price, current_price=product_initial_price,
                    currency=product_currency, price_difference=0.00)
    db.session.add(product)
    db.session.flush()
    return (product)   

def update_product(product):
    current_price = search_product(product.product_id)
    if current_price != 'not found':
        product.current_price = current_price
        print('Update product success, new price = ', current_price)
        product.price_difference = product.initial_price - product.current_price
        product_object = product
        product.update()
        return product_object
    else: 
        return None

def check_user(request_json):
    if request_json is None:
        raise exceptions.BadRequest()
    user_id = request_json['user_id']
    user = User.query.filter_by(user_id=user_id).one_or_none()
    if user is None:
        raise exceptions.NotFound()
    return user

# ROUTES
'''
@TODO: Add routes docstring
'''
@app.route('/auth_config')
def get_auth_config():
    return send_file('auth/auth_config.json')

@app.route('/')
def index():
    deals = get_deals()
    return render_template('index.html', deals=deals)

@app.route('/user', methods=['POST'])
def add_user():
    '''
    Sent upon login to check if user is stored
    and stores user if not
    '''
    try:
        request_json = request.get_json()
        if request_json is None:
                raise exceptions.BadRequest()
        user_id = request_json['user_id']
        # search user in database and store if not there 
        user = User.query.filter_by(user_id=user_id).one_or_none()
        if user is None:
            user_name = request_json['user_name']
            email = request_json['email']
            user = User(user_id=user_id, user_name=user_name, email=email)
            user.insert()

        return jsonify({
            "success": True
        })
    except exceptions.BadRequest:
        abort(400)
    except KeyError:
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

@app.route('/recent_alerts', methods=['POST'])
def get_recent_alerts():
    '''
    Fetch logged user's recent alerts
    '''
    try:
        request_json = request.get_json()
        user = check_user(request_json)
        # retrieve user's 5 most recent alerts from database
        alert_objects = Alert.query.filter_by(
                                    user_id=user.id
                                ).order_by(
                                    Alert.created.desc()
                                ).limit(5).all()
        recent_alerts = format_alerts(alert_objects)
        # recent_alerts = [
        #     {
        #         'product_name': '2021 Newest Dell Inspiron 3000 Laptop, 15.6 HD Display, Intel N4020 Processor, 16GB RAM, 512GB PCIe SSD, Online Meeting Ready, Webcam, WiFi, HDMI, Bluetooth, Win10 Home, Black',
        #         'product_link': 'https://www.dell.com/en-us/shop/gaming-laptops/g15-gaming-laptop/spd/g-series-15-5510-laptop/gn5510eyrns',
        #         'product_image': 'https://i.dell.com/is/image/DellContent//content/dam/global-site-design/product_images/dell_client_products/notebooks/g_series/15_5510/cn,hk,tw/media_gallery/cs2003g0063_370697_cs_co_media_gallery_g15_5510_dark-shadow-grey_coral-kb_notebook_ff1.psd?fmt=pjpg&pscan=auto&scl=1&hei=402&wid=402&qlt=85,0&resMode=sharp2&op_usm=1.75,0.3,2,0&size=402,402',
        #         'price': 1099.99,
        #         'currency': 'USD',
        #         'price_difference': 0.00,
        #         'store': 'dell',
        #         'alert_id': 0,
        #     }
        # ]
        return jsonify({
            "success": True,
            "recent-alerts": recent_alerts,
            "total_items": len(recent_alerts)
        })

    except exceptions.NotFound:
            abort(404)
    except exceptions.InternalServerError:
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())

@app.route('/alerts', methods=['POST'])
def get_alerts():
    try:
        request_json = request.get_json()
        user = check_user(request_json)
        page_number = request_json['page_number']
        try:
            page_number = int(request.get_json()['page_number'])
        except Exception:
            page_number = 1
        alert_objects = paginate_alerts(user.id, page_number)
        alerts = format_alerts(alert_objects)
        
        return jsonify({
            "success": True,
            "user-alerts": alerts,
            "total_items": len(alerts)
        })
        
    except exceptions.NotFound:
            abort(404)
    except exceptions.InternalServerError:
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())
    finally:
        db.session.close()

@app.route('/alerts/add', methods=['POST'])
def add_alert():
    try:
        request_json = request.get_json()
        user = check_user(request_json)
        product_id = request_json['product_id']
        # Check if product is stored
        product = Product.query.filter_by(product_id=product_id).one_or_none()

        if product is None:
            product = add_product(request_json, product_id)
            # product_object = Product.query.filter_by(product_id=product_id).one_or_none()
        
        # Check if user hasn't made an alert for that product
        if product not in user.products:
            user.products.append(product)
            # Create Alert
            desired_price = request_json['desired_price']
            alert = Alert(desired_price=desired_price, created=datetime.now(),
                        user_id=user.id, product_id=product.id)
            # product.alerts.append(alert)
            # user.alerts.append(alert)
            db.session.add(alert)
            db.session.commit()
        
        return jsonify({
            "success": True,
        })

    except exceptions.BadRequest:
        abort(400)
    except KeyError:
        print(sys.exc_info())
        abort(422)
    except exceptions.NotFound:
        abort(404)
    except exceptions.InternalServerError:
        db.session.rollback()
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())

    finally:
        db.session.close()

@app.route('/alerts', methods=['PATCH'])
def edit_alert():
    try:
        request_json = request.get_json()
        user = check_user(request_json)
        alert_id = request_json['alert_id']
        if alert_id is None:
            raise exceptions.NotFound()
        new_desired_price = request_json['new_desired_price']
        # edit desired price in alert table
        alert = Alert.query.get(alert_id)
        alert.desired_price = new_desired_price
        alert.created = datetime.now()
        alert.update()
        return jsonify({
            "success": True,
        })
    except exceptions.BadRequest:
        abort(400)
    except KeyError:
        print(sys.exc_info())
        abort(422)
    except exceptions.NotFound:
        abort(404)
    except exceptions.InternalServerError:
        db.session.rollback()
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())
    finally:
        db.session.close()

@app.route('/alerts', methods=['DELETE'])
def delete_alert():
    try:
        request_json = request.get_json()
        user = check_user(request_json)
        alert_id = request_json['alert_id']
        # delete alert form alerts table
        alert = Alert.query.get(alert_id)
        if alert is None:
            raise exceptions.NotFound()
        alert.delete()
        return jsonify({
            "success": True,
        })

    except exceptions.NotFound:
        abort(404)
    except exceptions.InternalServerError:
        db.session.rollback()
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())
    finally:
        db.session.close()

@app.route('/search', methods=['POST'])
def search_stores():
    try:
        request_json = request.get_json()
        if request_json is None:
            raise exceptions.BadRequest()
        # user_id = request_json['user_id']
        page_number = request_json['page_number']
        keywords = request_json['keywords']
        filters = request_json['filters']

        # if user is not None: store search keywords
        # store = filters['store']
        # if store == 'ebay':
        search_results, total_items = search_ebay(keywords ,filters, page_number)    
        paginated_results = paginate_results(search_results, page_number)

        return jsonify({
            "success": True,
            "search-results": paginated_results,
            "total_items": total_items
        })
    except exceptions.BadRequest:
        abort(400)
    except KeyError:
        print(sys.exc_info())
        abort(422)
    except exceptions.InternalServerError:
        db.session.rollback()
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())

@app.route('/filters', methods=['GET'])
def get_search_filters():
    """
    docstring
    """
    try:
        # Search filters in filters table
        filter_objects = Filter.query.all()
        if filter_objects:
            filters = [filter_.name for filter_ in filter_objects]
        else:
            filters = []
        return jsonify({
            "success": True,
            "filters": filters
        })

    except exceptions.InternalServerError:
        abort(500)
    except Exception as e:
        logging.error(e)
        print(sys.exc_info())


@app.route('/filters', methods=['POST'])
@requires_auth('post:filters')
def add_search_filter():
    try:
        request_json = request.get_json()
        if request_json is None:
            raise exceptions.BadRequest()
        filter_ = request_json['filter']
        # add filter to filters table
        new_filter =  Filter(name=filter_)
        new_filter.insert()
        return jsonify({
            "success": True,
        })

    except AuthError as auth_error:
        abort(auth_error)
    except exceptions.BadRequest:
        abort(400)
    except KeyError:
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

        
@app.route('/deals', methods=['POST'])
@requires_auth('post:deals')
def add_deal():
    """
    docstring
    """
    try:
        request_json = request.get_json()
        if request_json is None:
            raise exceptions.BadRequest()
        deal_name = request_json['deal_name']
        deal_link = request_json['deal_link']
        deal_image = request_json['deal_image']
        deal_price = request_json['deal_price']
        deal_currency = request_json['deal_currency']
        deal_store = request_json['deal_store']
        # Add deal to deals table
        deal = Deal(name=deal_name, link=deal_link, image=deal_image,
                    price=deal_price, currency=deal_currency, store=deal_store)
        deal.insert()

        return jsonify({
            "success": True
        })
    except AuthError as auth_error:
        abort(auth_error)
    except exceptions.BadRequest:
        abort(400)
    except KeyError:
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
@DONE implement error handler for 404
    error handler should conform to general task above
'''
@app.errorhandler(404)
def notfound(error):
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

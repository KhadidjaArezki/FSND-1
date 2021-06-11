import os
from sqlalchemy import Column, String, Integer, create_engine
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

database_name = "trivia"
database_path = "postgresql://{}@{}/{}".format('postgres:12345', 'localhost:5432', database_name)

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''
def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    migrate = Migrate(app, db)
    # db.create_all()
    

'''
Question

'''
class Question(db.Model):  
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(Integer, db.ForeignKey('categories.id'))
    difficulty = Column(Integer)
    rating = Column(Integer)

    def __init__(self, question, answer, category, difficulty, rating):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty
        self.rating = rating

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def flush(self):
        db.session.add(self)
        db.session.flush()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty,
            'rating': self.rating
        }

'''
Category

'''
class Category(db.Model):  
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String, unique=True)
    games =  db.relationship('Games', back_populates='category')

    def __init__(self, type, games):
        self.type = type
        self.games = games
    
    def insert(self):
        db.session.add(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'type': self.type
        }


'''
User
'''
class User(db.Model):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    games = db.relationship('Games', back_populates='player')

    def __init__(self, name, games):
        self.games = games
        self.name = name


'''
Game
'''
class Games(db.Model):
    ___tablename__ = 'games'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, db.ForeignKey('users.id'), nullable=False)
    score = Column(Integer,nullable=False)
    category_id = Column(Integer, db.ForeignKey('categories.id'), nullable=True)
    time = db.Column(db.DateTime(), nullable=True)
    player = db.relationship('User', back_populates='games')
    category = db.relationship('Category', back_populates='games')

    def __init__(self, user_id, score, category_id, time, player, category):
        self.user_id = user_id
        self.score = score
        self.player = player
        self.category_id = category_id
        self.time = time
        self.category = category
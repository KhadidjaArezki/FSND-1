from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from sqlalchemy.dialects.postgresql import TIME

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)

# DONE: connect to a local postgresql database
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

# Association table between Venue and Genre
#----------------------------------------------------------------------------#

venue_genres = db.Table('venue_genres', 
    db.Column('venue_id', db.INTEGER, db.ForeignKey('Venue.id'), primary_key=True),
    db.Column('genre_id', db.INTEGER, db.ForeignKey('Genre.id'), primary_key=True)
    )

# Association table between Artist and Genre
#----------------------------------------------------------------------------#
artist_genres = db.Table('artist_genres',
    db.Column('artist_id', db.INTEGER, db.ForeignKey('Artist.id'), primary_key=True),
    db.Column('genre_id', db.INTEGER, db.ForeignKey('Genre.id'), primary_key=True)
    )

# Additional tables to avoid redundant data storing
#----------------------------------------------------------------------------#

class Genre(db.Model):
    __tablename__ = 'Genre'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f'<Genre {self.id}: {self.name}>'
        

class City(db.Model):
    __tablename__ = 'City'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String, nullable=False)
    state_id = db.Column(db.INTEGER, db.ForeignKey('State.id'), nullable=False)

    def __repr__(self):
        state = State.query.filter_by(id=self.state_id).one()
        return f'<City: {self.name}, State {state.id}: {state.name}>'


class State(db.Model):
    __tablename__ = 'State'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    def __repr__(self):
        return f'<State {self.id}: {self.name}>'

#----------------------------------------------------------------------------#
# Association Object between Venues and Artists

class Show(db.Model):
    __tablename__ = 'Show'

    id = db.Column(db.INTEGER, primary_key=True)
    venue_id = db.Column(db.INTEGER, db.ForeignKey('Venue.id'), nullable=False)
    artist_id = db.Column(db.INTEGER, db.ForeignKey('Artist.id'), nullable=False)
    start_time = db.Column(db.DateTime(), nullable=False)
    end_time = db.Column(db.DateTime(), nullable=False)
    artist = db.relationship('Artist', back_populates='shows')
    venue = db.relationship('Venue', back_populates='shows')

    def __repr__(self):
        return f'<Show preformed at {self.venue} by {self.artist} on {self.start_time}>'

#----------------------------------------------------------------------------#
# Main Models

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city_id = db.Column(db.INTEGER, db.ForeignKey('City.id'), nullable=False)
    state_id = db.Column(db.INTEGER, db.ForeignKey('State.id'), nullable=False)
    address = db.Column(db.String(120), nullable=False, unique=True)
    phone = db.Column(db.String(120), unique=True)
    image_link = db.Column(db.String(500), unique=True)
    facebook_link = db.Column(db.String(120), unique=True, nullable=True)
    website = db.Column(db.String(120), unique=True, nullable=True)
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    genres = db.relationship('Genre', secondary=venue_genres, backref=db.backref('venues', lazy=True))
    shows = db.relationship('Show', back_populates='venue')

    def __repr__(self):
        return f'<Venue: {self.name}, address: {self.address}>'

    # DONE: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.INTEGER, primary_key=True)
    name = db.Column(db.String, nullable=False)
    city_id = db.Column(db.INTEGER, db.ForeignKey('City.id'), nullable=False)
    state_id = db.Column(db.INTEGER, db.ForeignKey('State.id'), nullable=False)
    phone = db.Column(db.String(120), unique=True)
    image_link = db.Column(db.String(500), unique=True)
    facebook_link = db.Column(db.String(120), unique=True, nullable=True)
    website = db.Column(db.String(120), unique=True, nullable=True)
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    availability_start = db.Column(db.Time())
    availability_end = db.Column(db.Time())
    genres = db.relationship('Genre', secondary=artist_genres, backref=db.backref('artists', lazy=True))
    shows = db.relationship('Show', back_populates='artist')

    def __repr__(self):
        genres = ' and '.join([genre.name for genre in self.genres])
        return f'<Artist {self.name} plays {genres}>'


    # DONE: implement any missing fields, as a database migration using Flask-Migrate

# DONE Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

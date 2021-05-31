#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
from datetime import datetime 
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from sqlalchemy import exc
from sqlalchemy import and_
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *

moment = Moment(app)
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
    return babel.dates.format_datetime(date, format, locale='en')

def format_time(value):
    time = dateutil.parser.parse(value)
    format = 'H:mma'
    return babel.dates.format_time(time, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime
app.jinja_env.filters['time'] = format_time
app.jinja_env.globals.update(len=len)

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
    '''
        The home page displays recently listed venues and artists:
        * artists stores data of recently listed artists.
        * areas stores data of recently listed venues sorted by city .
        * venues is a dictionary - a temporary data structure that 
          will not be returned - venues maps a (city, state) tuple to 
          a list of venues situated in that city.
    '''
    artists = []
    areas = []
    areas_temp = {}
    try:
        venues_rows = Venue.query.order_by(Venue.id.desc()).limit(10).all()
        for venue in venues_rows:
            city = City.query.get(venue.city_id).name
            state = State.query.get(venue.state_id).name

            # Group venues by city in areas_temp
            if not (city, state) in areas_temp: 
                areas_temp[(city, state)] = [(venue.id, venue.name)]
            else:
                areas_temp[(city, state)].append((venue.id, venue.name))

        for area in areas_temp.keys():
            venue_obj = {}
            venue_obj['city'] = area[0]
            venue_obj['state'] = area[1]
            venue_obj['venues'] = []
            for venue in areas_temp[area]:
                venue_obj['venues'].append({'id':venue[0], 'name':venue[1]})
            areas.append(venue_obj)

        artists_rows = Artist.query.order_by(Artist.id.desc()).limit(10).all()
        for artist in artists_rows:
            artist_obj = {}
            artist_obj['name'] = artist.name
            artist_obj['id'] = artist.id
            artists.append(artist_obj)

    except:
        print(sys.exc_info())

    finally:
        return render_template('pages/home.html', areas=areas, artists=artists)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
    # DONE: replace with real venues data.

    # data will store venues data grouped by city 
    data = []
    try:
        cities = City.query.all()
        for city in cities:
            venues = Venue.query.filter_by(city_id=city.id).all()

            if len(venues) > 0:
                city_obj = {}
                city_obj['city'] = city.name
                state = State.query.filter_by(id=city.state_id).one()
                city_obj['state'] = state.name
            
                city_venues = []
                for venue in venues:
                    city_venue = {}
                    city_venue['id'] = venue.id
                    city_venue['name'] = venue.name
                    city_venues.append(city_venue)
                city_obj['venues'] = city_venues
                data.append(city_obj)

    except:
        print(sys.exc_info())
        abort(500)
    else:
        return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # DONE: implement search on venues with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    ''' 
        Search Method:
        If the search term is a comma-separated string, 
        we search cities by name and return all venues of the matching city
        else we search venues by name and return matching venues
    '''
    # response will store the venue data returned by the search
    response = {}
 
    search_list = request.form.get('search_term').split(',')
    try:
        if len(search_list) > 1:
            city = '%' + search_list[0].strip() + '%'
            state = '%' + search_list[1].strip() +'%'

            state_id = State.query.filter(State.name.ilike(state)).one().id
            city_id = City.query.filter_by(state_id=state_id)\
                .filter(City.name.ilike(city)).first().id

            venues = Venue.query.filter_by(city_id=city_id).all()        

        else:
            search_term = '%' + request.form.get('search_term') + '%'
            venues = Venue.query.filter(Venue.name.ilike(search_term)).all()

        response['count'] = len(venues)
        response['data'] = []
        for venue in venues:
            venue_obj = {}
            venue_obj['id'] = venue.id
            venue_obj['name'] = venue.name
            response['data'].append(venue_obj)

    except:
        print(sys.exc_info())
        abort(500)
    else:
        return render_template('pages/search_venues.html', results=response,
            search_term=request.form.get('search_term', ''))


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # DONE: replace with real venue data from the venues table, using venue_id

    # Set up the error flags
    not_found_error = False
    internal_error = False

    # data will store venue data and shows performed there
    data = {}
    try:
        venue = Venue.query.get(venue_id)

        # If the requested row doesn't exist, we will skip further processing
        if venue is None:
            not_found_error = True

        else:
            data['id'] = venue.id
            data['name'] = venue.name
            data['phone'] = venue.phone
            data['address'] = venue.address
            data['website'] = venue.website if venue.website != None else ''
            data['facebook_link'] = venue.facebook_link if venue.facebook_link != None else ''
            data['image_link'] = venue.image_link if venue.image_link != None else ''
            data['city'] = City.query.get(venue.city_id).name
            data['state'] = State.query.get(venue.state_id).name
            data['genres'] = [genre.name for genre in venue.genres]
            data['seeking_talent'] = venue.seeking_talent
            data['seeking_description'] = venue.seeking_description

            # Retrieve past shows performed at venue and store each show's relative data
            past_shows = []

            old_shows = Show.query.filter_by(venue_id=venue.id).filter(
                Show.start_time < datetime.now()).all()
            data['past_shows_count'] = len(old_shows)

            for old_show in old_shows:
                past_show = {}
                past_show['artist_id'] = old_show.artist.id
                past_show['artist_name'] = old_show.artist.name
                past_show['artist_image_link'] = old_show.artist.image_link
                past_show['start_time'] = str(old_show.start_time)
                past_shows.append(past_show)

            data['past_shows'] = past_shows

            # Retrieve upcoming shows performed at venue and store each show's relative data
            upcoming_shows = []

            next_shows = Show.query.filter_by(venue_id=venue_id).filter(
                Show.start_time > datetime.now()).all()
            data['upcoming_shows_count'] = len(next_shows)

            for next_show in next_shows:
                upcoming_show = {}
                upcoming_show['artist_id'] = next_show.artist.id
                upcoming_show['artist_name'] = next_show.artist.name
                upcoming_show['artist_image_link'] = next_show.artist.image_link
                upcoming_show['start_time'] = str(next_show.start_time)
                upcoming_shows.append(upcoming_show)

            data['upcoming_shows'] = upcoming_shows
  
    except:
        internal_error = True
        print(sys.exc_info())
    
    finally:
        if not_found_error:
            abort(404)

        elif internal_error:
            flash('An error occurred. Could not load Venue')
            return redirect(url_for('index'))

        else:
            return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)


@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        address = request.form.get('address')
        phone = request.form.get('phone')
        facebook_link = request.form.get('facebook_link')
        facebook_link = facebook_link if facebook_link != '' else db.null()
        image_link = request.form.get('image_link')
        image_link = image_link if image_link != '' else db.null()
        website = request.form.get('website_link')
        website = website if website != '' else db.null()
        seeking_description = request.form.get('seeking_description')
        seek_tal = request.form.get('seeking_talent')
        seeking_talent = True if seek_tal == 'y' else False

        state_id = State.query.filter_by(name=state).one().id
        city_row = City.query.filter(and_(City.name==city, City.state_id==state_id)).one_or_none()

        # If the newly created venue's city is not listed, add it
        if city_row is None:
            new_city = City(name=city, state_id=state_id)
            db.session.add(new_city)
            db.session.flush()
            city_id = City.query.filter(and_(City.name==city, 
                City.state_id==state_id)).one().id
            db.session.commit()

        else:
            city_id = city_row.id

        venue = Venue(name=name, city_id=city_id, state_id=state_id, address=address,
                      phone=phone, facebook_link=facebook_link, image_link=image_link,
                      website=website, seeking_talent=seeking_talent, 
                      seeking_description=seeking_description)

        # Associate the newly created venue with its genres
        genres = request.form.getlist('genres')
        for g in genres:
            genre = Genre.query.filter_by(name=g).one()
            venue.genres.append(genre)

        db.session.add(venue)
        db.session.commit()

        flash('Venue ' + request.form['name'] + ' was successfully listed!')


    except exc.IntegrityError:
        db.session.rollback()
        db.session.close()
        flash('Error! This Venue is probably a duplicate')
        return redirect(url_for('create_venue_form'))
    except:
        db.session.rollback()
        db.session.close()
        print(sys.exc_info())
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
        return redirect(url_for('index'))
    
    else:
        db.session.close()
        return redirect(url_for('index'))


@app.route('/venues/<int:venue_id>/delete')
def delete_venue(venue_id):
    # DONE: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # set up error flags
    not_found_error = False
    internal_error = False

    try:
        venue = Venue.query.get(venue_id)
        if venue is  None:
            not_found_error = True

        else:
            venue.genres = []
            db.session.delete(venue)
            db.session.commit()
            flash('Venue ' + venue.name + ' was successfully deleted!')

    except:
        internal_error = True
        db.session.rollback()
        print(sys.exc_info())

    finally:
        if not_found_error:
            abort(404)

        elif internal_error:
            db.session.close()
            flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
            return redirect(url_for('index'))
        else:
            db.session.close()
            return redirect(url_for('index'))

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage


#  Artists
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
    # DONE: replace with real data returned from querying the database
    data = []
    try:
        artists = Artist.query.all()
        for artist in artists:
            artist_obj = {}
            artist_obj['id'] = artist.id
            artist_obj['name'] = artist.name
            data.append(artist_obj)

    except:
        print(sys.exc_info())
        abort(500)
    else:
        return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    ''' 
        Search Method:
        If the search term is a comma-separated string, 
        we search cities by name and return all artists of the matching city
        else we search artists by name and return matching artists
    '''

    # response stores artist data returned by the search
    response = {}

    search_list = request.form.get('search_term').split(',')
    try:
        if len(search_list) > 1:
            city = '%' + search_list[0].strip() + '%'
            state = '%' + search_list[1].strip() +'%'

            state_id = State.query.filter(State.name.ilike(state)).one().id
            city_id = City.query.filter_by(state_id=state_id)\
                .filter(City.name.ilike(city)).first().id
            
            artists = Artist.query.filter_by(city_id=city_id).all()

        else:
            search_term = '%' + request.form.get('search_term') + '%'
            artists = Artist.query.filter(Artist.name.ilike(search_term)).all()
            
        response['count'] = len(artists)
        response['data'] = []
        for artist in artists:
            artist_obj = {}
            artist_obj['id'] = artist.id
            artist_obj['name'] = artist.name
            response['data'].append(artist_obj)

    except:
        print(sys.exc_info())
        abort(500)
    else:
        return render_template('pages/search_artists.html', results=response,
            search_term=request.form.get('search_term', ''))


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the artist page with the given artist_id
    # DONE: replace with real artist data from the artist table, using artist_id
    # DONE: implement artist availability

    # Set up error flags
    not_found_error = False
    internal_error = False

    # data stores artist data and shows performed by him/her
    data = {}

    try:
        artist = Artist.query.get(artist_id)

        # If the requested row doesn't exist, we will skip further processing
        if artist is None:
            not_found_error = True
            
        else:
            data['id'] = artist.id
            data['name'] = artist.name
            data['phone'] = artist.phone
            data['website'] = artist.website if artist.website != None else ''
            data['facebook_link'] = artist.facebook_link if artist.facebook_link != None else ''
            data['image_link'] = artist.image_link if artist.image_link != None else ''
            data['city'] = City.query.get(artist.city_id).name
            data['state'] = State.query.get(artist.state_id).name
            data['genres'] = [genre.name for genre in artist.genres]
            data['seeking_venue'] = artist.seeking_venue
            data['seeking_description'] = artist.seeking_description
            data['availability_start'] = artist.availability_start
            data['availability_end'] = artist.availability_end

            # Retrieve past shows performed by artist and store each show's relative data
            past_shows = []
            old_shows = Show.query.filter_by(artist_id=artist.id).filter(Show.start_time < datetime.now()).all() 
            data['past_shows_count'] = len(old_shows)

            if len(old_shows) > 0:
                for old_show in old_shows:
                    past_show = {}
                    past_show['venue_id'] = old_show.venue.id
                    past_show['venue_name'] = old_show.venue.name
                    past_show['venue_image_link'] = old_show.venue.image_link
                    past_show['start_time'] = str(old_show.start_time)
                    past_shows.append(past_show)

            data['past_shows'] = past_shows

            # Retrieve upcoming shows performed by artist and store each show's relative data
            upcoming_shows = []
            next_shows = Show.query.filter_by(artist_id=artist.id).filter(
                Show.start_time > datetime.now()).all()
            data['upcoming_shows_count'] = len(next_shows)

            if len(next_shows) > 0:
                for next_show in next_shows:
                    upcoming_show = {}
                    upcoming_show['venue_id'] = next_show.venue.id
                    upcoming_show['venue_name'] = next_show.venue.name
                    upcoming_show['venue_image_link'] = next_show.venue.image_link
                    upcoming_show['start_time'] = str(next_show.start_time)
                    upcoming_shows.append(upcoming_show)

            data['upcoming_shows'] = upcoming_shows

    except:
        internal_error = True
        print(sys.exc_info())

    finally:
        if not_found_error:
            abort(404)
            
        elif internal_error:
            flash('An error occurred. Could not load Artist')
            return redirect(url_for('index'))

        else:
            return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    # DONE: populate form with fields from artist with ID <artist_id>
    form = ArtistForm()

    #Set up error flags
    not_found_error = False
    internal_error = False
    try:
        artist_row = Artist.query.get(artist_id)

        # If the requested row doesn't exist, we will skip further processing
        if artist_row is None:
            not_found_error = True

        else:
            artist = {}
            artist['id'] = artist_row.id
            artist['name'] = artist_row.name
            artist['phone'] = artist_row.phone
            artist['website'] = artist_row.website if artist_row.website != None else ''
            artist['facebook_link'] = artist_row.facebook_link if artist_row.facebook_link != None else ''
            artist['image_link'] = artist_row.image_link if artist_row.image_link != None else ''
            artist['city'] = City.query.get(artist_row.city_id).name
            artist['state'] = State.query.get(artist_row.state_id).name
            artist['genres'] = [genre.name for genre in artist_row.genres]
            artist['seeking_description'] = artist_row.seeking_description
            artist['availability_start'] = artist_row.availability_start
            artist['availability_end'] = artist_row.availability_end
        
    except:
        internal_error = True
        print(sys.exc_info())

    finally:
        if not_found_error:
            abort(404)
        elif internal_error:
            abort(500)
        else:
            return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # DONE: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes

    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        facebook_link = request.form.get('facebook_link')
        facebook_link = facebook_link if facebook_link != '' else db.null()
        website = request.form.get('website_link')
        website = website if website != '' else db.null()
        image_link = request.form.get('image_link')
        image_link = image_link if image_link != '' else db.null()
        seeking_description = request.form.get('seeking_description')
        seek_vnu = request.form.get('seeking_venue')
        seeking_venue = True if seek_vnu == 'y' else False
        availability_start = request.form.get('availability_start')
        availability_end = request.form.get('availability_end')

        # if edited artist's city is not listed, add it
        state_id = State.query.filter_by(name=state).one().id
        city_row = City.query.filter(and_(City.name==city, state_id==state_id)).one_or_none()

        if city_row is None:
            new_city = City(name=city, state_id=state_id)
            db.session.add(new_city)
            db.session.flush()
            city_id = City.query.filter(and_(City.name==city, 
                state_id==state_id)).one().id
            db.session.commit()

        else:
            city_id = city_row.id

        artist = Artist.query.get(artist_id)

        # Update artist
        artist.name = name
        artist.city_id = city_id
        artist.state_id = state_id
        artist.phone = phone
        artist.facebook_link = facebook_link
        artist.image_link = image_link
        artist.website = website
        artist.seeking_venue = seeking_venue
        artist.seeking_description = seeking_description
        artist.availability_start = availability_start
        artist.availability_end = availability_end
        
        # Associate artist with his/her genres
        genres = request.form.getlist('genres')
        artist.genres = []
        for g in genres:
            genre = Genre.query.filter_by(name=g).one()
            artist.genres.append(genre)

        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully edited!')

    except exc.IntegrityError:
        db.session.rollback()
        db.session.close()
        flash('Error! This Venue is probably a duplicate')
        return redirect(url_for('edit_artist', venue_id=artist_id))
    except:
        db.session.rollback()
        db.session.close()
        print(sys.exc_info())
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
        return redirect(url_for('show_artist', artist_id=artist_id))
    else:
        db.session.close()
        return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    # DONE: populate form with values from venue with ID <venue_id>
    form = VenueForm()

    #Set up error flags
    not_found_error = False
    internal_error = False

    try:
        venue_row = Venue.query.get(venue_id)    

        # If the requested row doesn't exist, we will skip further processing
        if venue_row is None:
            not_found_error = True

        else:
            venue = {}
            venue['id'] = venue_row.id
            venue['name'] = venue_row.name
            venue['phone'] = venue_row.phone
            venue['address'] = venue_row.address
            venue['website'] = venue_row.website if venue_row.website != None else ''
            venue['facebook_link'] = venue_row.facebook_link if venue_row.facebook_link != None else ''
            venue['image_link'] = venue_row.image_link if venue_row.image_link != None else ''
            venue['city'] = City.query.get(venue_row.city_id).name
            venue['state'] = State.query.get(venue_row.state_id).name
            venue['genres'] = [genre.name for genre in venue_row.genres]
            venue['seeking_description'] = venue_row.seeking_description

    except:
        internal_error = True
        print(sys.exc_info())
    finally:
        if not_found_error:
            abort(404)
        elif internal_error:
            abort(500)
        else:
            return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # DONE: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes

    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        address = request.form.get('address')
        facebook_link = request.form.get('facebook_link')
        facebook_link = facebook_link if facebook_link != '' else db.null()
        image_link = request.form.get('image_link')
        image_link = image_link if image_link != '' else db.null()
        website = request.form.get('website_link')
        website = website if website != '' else db.null()
        seeking_description = request.form.get('seeking_description')
        seek_tal = request.form.get('seeking_talent')
        seeking_talent = True if seek_tal == 'y' else False

        # If the edited venue's city is not listed, add it
        state_id = State.query.filter_by(name=state).one().id
        city_row = City.query.filter(and_(City.name==city, City.state_id==state_id)).one_or_none()

        if city_row is None:
            new_city = City(name=city, state_id=state_id)
            db.session.add(new_city)
            db.session.flush()
            city_id = City.query.filter(and_(City.name==city, 
                City.state_id==state_id)).one().id
            db.session.commit()

        else:
            city_id = city_row.id

        venue = Venue.query.get(venue_id)
        # Update venue
        venue.name = name
        venue.city_id = city_id
        venue.state_id = state_id
        venue.phone = phone
        venue.address = address
        venue.facebook_link = facebook_link
        venue.image_link = image_link
        venue.website = website
        venue.seeking_talent = seeking_talent
        venue.seeking_description = seeking_description

        # Associate venue with its genres
        genres = request.form.getlist('genres')
        venue.genres = []
        for g in genres:
            genre = Genre.query.filter_by(name=g).one()
            venue.genres.append(genre)

        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully edited!')

    except exc.IntegrityError:
        db.session.rollback()
        db.session.close()
        flash('Error! This Venue is probably a duplicate')
        return redirect(url_for('edit_venue', venue_id=venue_id))
    except:
        db.session.rollback()
        db.session.close()
        print(sys.exc_info())
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
        return redirect(url_for('show_venue', venue_id=venue_id))
    
    else:
        db.session.close()
        return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # DONE: insert form data as a new Venue record in the db, instead
    # DONE: modify data to be the data object returned from db insertion

    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        facebook_link = request.form.get('facebook_link')
        facebook_link = facebook_link if facebook_link != '' else db.null()
        image_link = request.form.get('image_link')
        image_link = image_link if image_link != '' else db.null()
        website = request.form.get('website_link')
        website = website if website != '' else db.null()
        seeking_description = request.form.get('seeking_description')
        seek_vnu = request.form.get('seeking_venue')
        seeking_venue = True if seek_vnu == 'y' else False
        availability_start = request.form.get('availability_start')
        availability_end = request.form.get('availability_end')

        # If the newly created artist's city is not listed, add it
        state_id = State.query.filter_by(name=state).one().id
        city_row = City.query.filter(and_(City.name==city, City.state_id==state_id)).one_or_none()

        if city_row is None:
            new_city = City(name=city, state_id=state_id)
            db.session.add(new_city)
            db.session.flush()
            city_id = City.query.filter(and_(City.name==city, 
                City.state_id==state_id)).one().id
            db.session.commit()

        else:
            city_id = city_row.id

        artist = Artist(name=name, city_id=city_id, state_id=state_id,
                        phone=phone, facebook_link=facebook_link, image_link=image_link,
                        website=website, seeking_venue=seeking_venue, seeking_description=seeking_description, 
                        availability_start=availability_start, availability_end=availability_end)

        # Associate artist with his/her genres
        genres = request.form.getlist('genres')
        for g in genres:
            genre = Genre.query.filter_by(name=g).one()
            artist.genres.append(genre)

        db.session.add(artist)
        db.session.commit()

        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    

    except exc.IntegrityError:
        db.session.rollback()
        db.session.close()
        flash('Error! This Artist is probably a duplicate')
        return redirect(url_for('create_artist_form'))
    except:
        db.session.rollback()
        db.session.close()
        print(sys.exc_info())
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
        return redirect(url_for('index'))
    
    else:
        db.session.close()
        return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # DONE: replace with real venues data.

    data = []
    try:
        shows = Show.query.order_by(Show.start_time).all()
        for show in shows:
            body = {}
            body['venue_id'] = show.venue_id
            body['artist_id'] = show.artist_id
            body['start_time'] = str(show.start_time)
            artist_name = show.artist.name
            venue_name = show.venue.name
            artist_image_link = show.artist.image_link
            body['artist_name'] = artist_name
            body['venue_name'] = venue_name
            body['artist_image_link'] = artist_image_link
            data.append(body)

    except:
        print(sys.exc_info())
        abort(500)

    finally:
        return render_template('pages/shows.html', shows=data)


@app.route('/shows/create')
def create_shows():
    # renders form. do not touch.
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)


@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    # called to create new shows in the db, upon submitting new show listing form
    # DONE: insert form data as a new Show record in the db, instead

    # available represents the artist's availability status
    available = False

    try:
        artist_id = request.form.get('artist_id')
        venue_id = request.form.get('venue_id')
        start_time = request.form.get('start_time')
        end_time = request.form.get('end_time')

        # Verify artist availability before inserting show
        artist = Artist.query.get(artist_id)
        availability_start = artist.availability_start
        availability_end = artist.availability_end

        if (availability_start is  None) or (availability_end is None):
            available = True

        else:
            show_start = dateutil.parser.parse(start_time)
            show_end = dateutil.parser.parse(end_time)

            if show_start.time() >= availability_start and show_end.time() <= availability_end:
                available = True

            
        if available:
            show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time, end_time=end_time)
            venue = Venue.query.get(venue_id)

            # Associate show with venue and artist
            show.venue = venue
            show.artist = artist
            db.session.add(show)
            db.session.commit()
            flash('Show was successfully listed!')
        else:
            flash('Artist is not available during the listed time')
            return redirect(url_for('create_shows'))

    except:
        db.session.rollback()
        db.session.close()
        print(sys.exc_info())
        flash('An error occurred. Show could not be listed.')
        return redirect(url_for('index'))

    else:
        db.session.close()
        return redirect(url_for('index'))


@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404


@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''

#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import datetime
import dateutil.parser
import babel
from flask import render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from sqlalchemy import exc
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
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
	# DONE: replace with real venues data.
	#num_shows should be aggregated based on number of upcoming shows per venue.

	data = []
	try:
		cities = City.query.all()
		for city in cities:
			city_obj = {}
			city_obj['city'] = city.name
			state = State.query.filter_by(id=city.state_id).one()
			city_obj['state'] = state.name
			venues = Venue.query.filter_by(city_id=city.id).all()
			city_venues = []
			for venue in venues:
				city_venue = {}
				city_venue['id'] = venue.id
				city_venue['name'] = venue.name
				next_shows_count = Show.query.filter_by(venue_id=venue.id).filter(db.text('start_time > now()')).count()
				city_venue['num_upcoming_shows'] = next_shows_count
				city_venues.append(city_venue)
			city_obj['venues'] = city_venues
			data.append(city_obj)

	except:
		flash('An Error occurred. Venues could not be listed')
		print(sys.exc_info())
	finally:
		return render_template('pages/venues.html', areas=data);
  
 
@app.route('/venues/search', methods=['POST'])
def search_venues():
	# DONE: implement search on venues with partial string search. Ensure it is case-insensitive.
	# seach for Hop should return "The Musical Hop".
	# search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
	search_term = '%' + request.form.get('search_term') + '%'
	response = {}
	try:
		venues = Venue.query.filter(Venue.name.ilike(search_term)).all()
		response['count'] = len(venues)
		response['data'] = []
		for venue in venues:
			venue_obj = {}
			venue_obj['id'] = venue.id
			venue_obj['name'] = venue.name
			next_shows_count = Show.query.filter_by(artist_id=venue.id).filter(db.text('start_time > now()')).count()
			venue_obj['num_upcoming_shows'] = next_shows_count
			response['data'].append(venue_obj)

	except:
		flash('An error occured. Could not search Venues')
		print(sys.exc_info())
	finally:
		return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
	# shows the venue page with the given venue_id
	# DONE: replace with real venue data from the venues table, using venue_id
	data = {}
	try:	
		venue = Venue.query.get(venue_id)
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

		past_shows = []

		old_shows = Show.query.filter_by(venue_id=venue.id).filter(db.text('start_time < now()')).all()
		data['past_shows_count'] = len(old_shows)

		for old_show in old_shows:
			past_show = {}
			past_show['artist_id'] = old_show.artist.id
			past_show['artist_name'] = old_show.artist.name
			past_show['artist_image_link'] = old_show.artist.image_link
			past_show['start_time'] = str(old_show.start_time)
			past_shows.append(past_show)

		data['past_shows'] = past_shows

		upcoming_shows = []

		next_shows = Show.query.filter_by(venue_id=venue_id).filter(db.text('start_time > now()')).all()
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
		flash('An error occurred. Could not show Venue')
		print(sys.exc_info())

	finally:
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
	#TODO: Check for data sanity
	error = False
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
		seeking_talent = True if seek_tal=='y' else False

		state_id = State.query.filter_by(name=state).one().id
		city_row = City.query.filter_by(name=city).first()
		if city_row == None:
			new_city = City(name=city, state_id=state_id)
			db.session.add(new_city)
			db.session.flush()
			city_id = City.query.filter_by(name=city).one().id

		else:
			city_id = city_row.id

		venue = Venue(name=name, city_id=city_id, state_id=state_id, address=address, 
			phone=phone, facebook_link=facebook_link, image_link=image_link, 
			website=website, seeking_talent=seeking_talent, seeking_description=seeking_description)

		genres = request.form.getlist('genres') 		
		for g in genres:
			genre = Genre.query.filter_by(name=g).one()
			venue.genres.append(genre)
			# insert = venue_genres.insert().values(venue_id=venue_id, genre_id=genre_id)

		db.session.add(venue)
		db.session.commit()

		# on successful db insert, flash success
		flash('Venue ' + request.form['name'] + ' was successfully listed!')
		
	# DONE: on unsuccessful db insert, flash an error instead.
	# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
	except exc.IntegrityError:
		flash('Error! This Venue is probably a duplicate')
	except:
		error = True
		db.session.rollback()
		print(sys.exc_info())
		flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
	finally:
		db.session.close()	
	if error:
		abort(500)
	else:
		return render_template('pages/home.html')

@app.route('/venues/<int:venue_id>/delete')
def delete_venue(venue_id):
	# DONE: Complete this endpoint for taking a venue_id, and using
	# SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
	try:
		venue = Venue.query.get(venue_id)
		venue.genres = []
		db.session.delete(venue)
		db.session.commit()
		flash('Venue ' + venue.name + ' was successfully deleted!')

	except:
		db.session.rollback()
		print(sys.exc_info())
		flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')

	finally:
		db.session.close()	

	# BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
	# clicking that button delete it from the db then redirect the user to the homepage
	return render_template('pages/home.html')

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
		flash('An error occurred. Artists could not be listed')
		print(sys.exc_info())
	finally:
		return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
	# DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
	# seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
	# search for "band" should return "The Wild Sax Band".
	search_term = '%' + request.form.get('search_term') + '%'
	response = {}
	try:
		artists = Artist.query.filter(Artist.name.ilike(search_term)).all()
		response['count'] = len(artists)
		response['data'] = []
		for artist in artists:
			artist_obj = {}
			artist_obj['id'] = artist.id
			artist_obj['name'] = artist.name
			next_shows_count = Show.query.filter_by(artist_id=artist.id).filter(db.text('start_time > now()')).count()
			artist_obj['num_upcoming_shows'] = next_shows_count
			response['data'].append(artist_obj)

	except:
		flash('An error occurred. Could not search Artists')
		print(sys.exc_info())
	finally:		
		return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))
	

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
	# shows the artist page with the given artist_id
	# DONE: replace with real artist data from the artist table, using artist_id
	data = {}
	try:	
		artist = Artist.query.get(artist_id)
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

		past_shows = []
		old_shows = Show.query.filter_by(artist_id=artist.id).filter(db.text('start_time < now()')).all()
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

		upcoming_shows = []
		next_shows = Show.query.filter_by(artist_id=artist.id).filter(db.text('start_time > now()')).all()
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
		flash()
		print(sys.exc_info())

	finally:
		return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
	# DONE: populate form with fields from artist with ID <artist_id>
	form = ArtistForm()
	try:
		artist_row = Artist.query.get(artist_id)
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

	except:
		flash()
		print(sys.exc_info())

	finally:
		return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
	# DONE: take values from the form submitted, and update existing
	# artist record with ID <artist_id> using the new attributes
	error = False
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
		seeking_venue = True if seek_vnu=='y' else False

		state_id = State.query.filter_by(name=state).one().id
		city_row = City.query.filter_by(name=city).first()
		if city_row == None:
			new_city = City(name=city, state_id=state_id)
			db.session.add(new_city)
			db.session.flush()
			city_id = City.query.filter_by(name=city).one().id

		else:
			city_id = city_row.id

		artist = Artist.query.get(artist_id)

		artist.name = name
		artist.city_id = city_id
		artist.state_id = state_id
		artist.phone = phone
		artist.facebook_link = facebook_link
		artist.image_link = image_link
		artist.website = website
		artist.seeking_venue = seeking_venue
		artist.seeking_description = seeking_description

		genres = request.form.getlist('genres') 		
		for g in genres:
			genre = Genre.query.filter_by(name=g).one()
			artist.genres.append(genre)

		db.session.add(artist)
		db.session.commit()
		flash('Artist ' + request.form['name'] + ' was successfully edited!')

	except exc.IntegrityError:
		flash('Error! This Artist is probably a duplicate')

	except:
		error = True
		db.session.rollback()
		print(sys.exc_info())
		flash('An error occurred. Artist ' + request.form['name'] + ' could not be edited.')
	finally:
		db.session.close()	
	if error:
		abort(500)
	else:	
		return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
	# DONE: populate form with values from venue with ID <venue_id>
	form = VenueForm()
	try:
		venue_row = Venue.query.get(venue_id)
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
		flash()
		print(sys.exc_info())

	finally:
		return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
	# DONE: take values from the form submitted, and update existing
	# venue record with ID <venue_id> using the new attributes
	error = False
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
		seeking_talent = True if seek_tal=='y' else False

		state_id = State.query.filter_by(name=state).one().id
		city_row = City.query.filter_by(name=city).first()
		if city_row == None:
			new_city = City(name=city, state_id=state_id)
			db.session.add(new_city)
			db.session.flush()
			city_id = City.query.filter_by(name=city).one().id

		else:
			city_id = city_row.id

		venue = Venue.query.get(venue_id)

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

		genres = request.form.getlist('genres') 		
		for g in genres:
			genre = Genre.query.filter_by(name=g).one()
			venue.genres.append(genre)

		db.session.add(venue)
		db.session.commit()
		flash('Venue ' + request.form['name'] + ' was successfully edited!')

	except exc.IntegrityError:
		flash('Error! This Artist is probably a duplicate')
	except:
		error = True
		db.session.rollback()
		print(sys.exc_info())
		flash('An error occurred. Venue ' + request.form['name'] + ' could not be edited.')
	finally:
		db.session.close()	
	if error:
		abort(500)
	else:	
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

	error = False
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
		seeking_venue = True if seek_vnu=='y' else False

		state_id = State.query.filter_by(name=state).one().id
		city_row = City.query.filter_by(name=city).first()
		if city_row == None:
			new_city = City(name=city, state_id=state_id)
			db.session.add(new_city)
			db.session.flush()
			city_id = City.query.filter_by(name=city).one().id

		else:
			city_id = city_row.id

		artist = Artist(name=name, city_id=city_id, state_id=state_id, 
			phone=phone, facebook_link=facebook_link, image_link=image_link, 
			website=website, seeking_venue=seeking_venue, seeking_description=seeking_description)

		genres = request.form.getlist('genres') 		
		for g in genres:
			genre = Genre.query.filter_by(name=g).one()
			artist.genres.append(genre)
			# insert = venue_genres.insert().values(venue_id=venue_id, genre_id=genre_id)

		db.session.add(artist)
		db.session.commit()

		# on successful db insert, flash success
		flash('Artist ' + request.form['name'] + ' was successfully listed!')
		# DONE: on unsuccessful db insert, flash an error instead.
		# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/

	except exc.IntegrityError:
		flash('Error! This Artist is probably a duplicate')
	except:
		error = True
		db.session.rollback()
		print(sys.exc_info())
		flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
	finally:
		db.session.close()	
	if error:
		abort(500)
	else:
		return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
	# displays list of shows at /shows
	# DONE: replace with real venues data.
	# DONE: num_shows should be aggregated based on number of upcoming shows per venue.
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
	error = False
	try:
		artist_id = request.form.get('artist_id')
		venue_id = request.form.get('venue_id')
		start_time = request.form.get('start_time')

		show = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
		artist = Artist.query.get(artist_id)
		venue = Venue.query.get(venue_id)
		show.venue = venue
		show.artist = artist
		venue.artists.append(show)
		db.session.add(show)
		db.session.commit()
		# on successful db insert, flash success
		flash('Show was successfully listed!')
	# DONE: on unsuccessful db insert, flash an error instead.

	except exc.IntegrityError:
		flash('Error! This Show is probably a duplicate')
	except:
		error = True
		db.session.rollback()
		print(sys.exc_info())
		flash('An error occurred. Show could not be listed.')
		# see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
	if error:
		abort(500)
	else:
		return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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

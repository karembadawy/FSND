#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, abort
from flask_moment import Moment
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import load_only
from sqlalchemy import func
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=True)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False, default=[])
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(120), nullable=True)
    seeking_talent = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    shows = db.relationship('Show', backref='venue', lazy=True)

class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False, default=[])
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120), nullable=True)
    seeking_venue = db.Column(db.Boolean, nullable=False, default=False)
    seeking_description = db.Column(db.String(120), nullable=True)
    shows = db.relationship('Show', backref='artist', lazy=True)

class Show(db.Model):
    __tablename__ = 'shows'

    id = db.Column(db.Integer, primary_key=True)
    start_date = db.Column(db.DateTime, nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey(
        'venues.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey(
        'artists.id'), nullable=False)

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  ----------------------------------------------------------------
#  Venues
#  ----------------------------------------------------------------

#  Venues list
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  areasData = [] # empty array to store all the data we need
  # query to retreive all the areas in the system
  areas = Venue.query.with_entities(Venue.state, Venue.city, func.count(
      Venue.id)).group_by(Venue.state, Venue.city).all()

  for area in areas:
    venuesData = [] # empty array to store areas data
    # query to retreive venue data in each area
    venues = Venue.query.filter_by(state=area.state, city=area.city).all()

    for venue in venues:
      # query to get upcoming shows for the venue
      upcoming_shows = Show.query.filter_by(id=venue.id).filter(
          Show.start_date > datetime.now()).all()
      # append venue data to the array
      venuesData.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(upcoming_shows)
      })

    # append area data to the array
    areasData.append({
      "city": area.city,
      "state": area.state,
      "venues": venuesData
    })

  return render_template('pages/venues.html', areas=areasData)

#  Search Venue
#  ----------------------------------------------------------------

@app.route('/venues/search', methods=['POST'])
def search_venues():
  error = False
  try:
    responseData = {}  # empty object to store all the data we need
    # get input from search bar
    search_term = request.form.get('search_term', '')
    # query to search for the input
    venues = Venue.query.filter(
        Venue.name.ilike(f'%{search_term}%')).all()

    venuesData = []  # empty array to store venues data

    for venue in venues:
      body = {} # body item of one venue
      # query to get upcoming shows for the venue
      upcoming_shows = Show.query.filter_by(id=venue.id).filter(
          Show.start_date > datetime.now()).all()
      # assign values to body
      body['id'] = venue.id
      body['name'] = venue.name
      body['num_upcoming_shows'] = len(upcoming_shows)
      # append venue data to the array
      venuesData.append(body)

    # append response data to the object
    responseData['count'] = len(venues)
    responseData['data'] = venuesData
  except:
    error = True
  if error:
    # render 500 if there is a server error
    return render_template('errors/500.html')
  else:
    return render_template('pages/search_venues.html', results=responseData, search_term=request.form.get('search_term', ''))

#  Show Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  error = False
  try:
    venueData = {}  # empty object to store all the data we need
    # query to get specific venue
    venue = Venue.query.get(venue_id)
    if not venue:
      # render 404 if not found
      return render_template('errors/404.html')

    upcomingData = [] # empty array to store shows data
    # query to get upcoming shows for this venue
    upcomingShows = Show.query.join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_date > datetime.now()).all()

    for show in upcomingShows:
      body = {}  # body item of one show
      # assign values to body
      body['artist_id'] = show.artist_id
      body['artist_name'] = show.artist.name
      body['artist_image_link'] = show.artist.image_link
      body['start_date'] = show.start_date.strftime('%Y-%m-%d %H:%M:%S')
      # append show data to the array
      upcomingData.append(body)

    pastData = []  # empty array to store shows data
    # query to get past shows for this venue
    pastShows = Show.query.join(Artist).filter(
        Show.venue_id == venue_id).filter(Show.start_date < datetime.now()).all()

    for show in pastShows:
      body = {}  # body item of one show
      # assign values to body
      body['artist_id'] = show.artist_id
      body['artist_name'] = show.artist.name
      body['artist_image_link'] = show.artist.image_link
      body['start_date'] = show.start_date.strftime('%Y-%m-%d %H:%M:%S')
      # append show data to the array
      pastData.append(body)

    # assign venue data values
    venueData['id'] = venue.id
    venueData['name'] = venue.name
    venueData['city'] = venue.city
    venueData['state'] = venue.state
    venueData['address'] = venue.address
    venueData['phone'] = venue.phone
    venueData['image_link'] = venue.image_link
    venueData['facebook_link'] = venue.facebook_link
    venueData['genres'] = venue.genres
    venueData['website'] = venue.website
    venueData['seeking_talent'] = venue.seeking_talent
    venueData['seeking_description'] = venue.seeking_description
    venueData['upcoming_shows'] = upcomingData
    venueData['upcoming_shows_count'] = len(upcomingData)
    venueData['past_shows'] = pastData
    venueData['past_shows_count'] = len(pastData)
  except:
    error = True
  if error:
    # render 500 if there is a server error
    return render_template('errors/500.html')
  else:
    return render_template('pages/show_venue.html', venue=venueData)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  error = False
  try:
    # get values from form and create record on db
    name = request.form.get('name', '')
    venue = Venue(
      name=name,
      city=request.form.get('city', ''),
      state=request.form.get('state', ''),
      address=request.form.get('address', ''),
      phone=request.form.get('phone', ''),
      image_link=request.form.get('image_link'),
      facebook_link=request.form.get('facebook_link'),
      genres=request.form.getlist('genres'),
      website=request.form.get('website', ''),
      seeking_talent=True if 'seeking_talent' in request.form else False,
      seeking_description=request.form.get('seeking_description', '')
    )

    db.session.add(venue)
    db.session.commit()
  except:
    error = True
    # rollback in case of error happen
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Error occurred: ' +
          name + ' could not be inserted.')
  else:
    flash('Venue ' + name + ' was successfully listed!')
  return render_template('pages/home.html')

#  Delete Venue
#  ----------------------------------------------------------------

@app.route('/venues/<venue_id>/delete', methods=['POST'])
def delete_venue(venue_id):
  error = False
  try:
    # query to get specific venue
    venue = Venue.query.get(venue_id)
    name = venue.name

    db.session.delete(venue)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Error occurred: ' +
          name + ' could not be deleted.')
  else:
    flash('Venue ' + name + ' was successfully deleted!')
  return render_template('pages/home.html')

#  Edit Venue
#  ----------------------------------------------------------------

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  error = False
  try:
    form = VenueForm()
    venueData = {}  # empty object to store all the data we need
    # query to get specific venue
    venue = Venue.query.get(venue_id)
    if not venue:
      # render 404 if not found
      return render_template('errors/404.html')

    # assign venue data values
    venueData['id'] = venue.id
    venueData['name'] = venue.name
    venueData['city'] = venue.city
    venueData['state'] = venue.state
    venueData['address'] = venue.address
    venueData['phone'] = venue.phone
    venueData['image_link'] = venue.image_link
    venueData['facebook_link'] = venue.facebook_link
    venueData['genres'] = venue.genres
    venueData['website'] = venue.website
    venueData['seeking_talent'] = venue.seeking_talent
    venueData['seeking_description'] = venue.seeking_description
  except:
    error = True
  if error:
    # render 500 if there is a server error
    return render_template('errors/500.html')
  else:
    return render_template('forms/edit_venue.html', form=form, venue=venueData)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  error = False
  try:
    # query to get specific venue
    venue = Venue.query.get(venue_id)
    name = venue.name
    # get values from form and Update record on db
    venue.name = request.form.get('name', '')
    venue.city = request.form.get('city', '')
    venue.state = request.form.get('state', '')
    venue.address = request.form.get('address', '')
    venue.phone = request.form.get('phone', '')
    venue.image_link = request.form.get('image_link')
    venue.facebook_link = request.form.get('facebook_link')
    venue.genres = request.form.getlist('genres')
    venue.website = request.form.get('website', '')
    venue.seeking_talent = True if 'seeking_talent' in request.form else False
    venue.seeking_description = request.form.get('seeking_description', '')

    db.session.commit()
  except:
    error = True
    # rollback in case of error happen
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Error occurred: ' +
          name + ' could not be Edited.')
  else:
    flash('Venue ' + name + ' was successfully Edited!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  ----------------------------------------------------------------
#  Artists
#  ----------------------------------------------------------------

#  Artists list
#  ----------------------------------------------------------------

@app.route('/artists')
def artists():
  data = []  # empty array to store all the data we need
  # query to retreive all artists
  artists = Artist.query.all()

  for artist in artists:
    body = {}  # empty object to store artist data
    # append venue data to the array
    body['id'] = artist.id
    body['name'] = artist.name

    # append artist data to the array
    data.append(body)

  return render_template('pages/artists.html', artists=data)

#  Search Artists
#  ----------------------------------------------------------------

@app.route('/artists/search', methods=['POST'])
def search_artists():
  error = False
  try:
    responseData = {}  # empty object to store all the data we need
    # get input from search bar
    search_term = request.form.get('search_term', '')
    # query to search for the input
    artists = Artist.query.filter(
        Artist.name.ilike(f'%{search_term}%')).all()

    artistsData = []  # empty array to store artists data

    for artist in artists:
      body = {}  # body item of one artist
      # query to get upcoming shows for the artist
      upcoming_shows = Show.query.filter_by(id=artist.id).filter(
          Show.start_date > datetime.now()).all()
      # assign values to body
      body['id'] = artist.id
      body['name'] = artist.name
      body['num_upcoming_shows'] = len(upcoming_shows)
      # append artist data to the array
      artistsData.append(body)

    # append response data to the object
    responseData['count'] = len(artists)
    responseData['data'] = artistsData
  except:
    error = True
  if error:
    # render 500 if there is a server error
    return render_template('errors/500.html')
  else:
    return render_template('pages/search_artists.html', results=responseData, search_term=request.form.get('search_term', ''))

#  Show Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  error = False
  try:
    artistData = {}  # empty object to store all the data we need
    # query to get specific artist
    artist = Artist.query.get(artist_id)
    if not artist:
      # render 404 if not found
      return render_template('errors/404.html')

    upcomingData = []  # empty array to store shows data
    # query to get upcoming shows for this artist
    upcomingShows = Show.query.join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_date > datetime.now()).all()

    for show in upcomingShows:
      body = {}  # body item of one show
      # assign values to body
      body['venue_id'] = show.venue_id
      body['venue_name'] = show.venue.name
      body['venue_image_link'] = show.venue.image_link
      body['start_date'] = show.start_date.strftime('%Y-%m-%d %H:%M:%S')
      # append show data to the array
      upcomingData.append(body)

    pastData = []  # empty array to store shows data
    # query to get past shows for this artist
    pastShows = Show.query.join(Venue).filter(
        Show.artist_id == artist_id).filter(Show.start_date < datetime.now()).all()

    for show in pastShows:
      body = {}  # body item of one show
      # assign values to body
      body['venue_id'] = show.venue_id
      body['venue_name'] = show.venue.name
      body['venue_image_link'] = show.venue.image_link
      body['start_date'] = show.start_date.strftime('%Y-%m-%d %H:%M:%S')
      # append show data to the array
      pastData.append(body)

    # assign artist data values
    artistData['id'] = artist.id
    artistData['name'] = artist.name
    artistData['city'] = artist.city
    artistData['state'] = artist.state
    artistData['phone'] = artist.phone
    artistData['genres'] = artist.genres
    artistData['image_link'] = artist.image_link
    artistData['facebook_link'] = artist.facebook_link
    artistData['seeking_venue'] = artist.seeking_venue
    artistData['seeking_description'] = artist.seeking_description
    artistData['upcoming_shows'] = upcomingData
    artistData['upcoming_shows_count'] = len(upcomingData)
    artistData['past_shows'] = pastData
    artistData['past_shows_count'] = len(pastData)
  except:
    error = True
  if error:
    # render 500 if there is a server error
    return render_template('errors/500.html')
  else:
    return render_template('pages/show_artist.html', artist=artistData)

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  error = False
  try:
    # get values from form and create record on db
    name = request.form.get('name', '')
    artist = Artist(
      name=name,
      city=request.form.get('city', ''),
      state=request.form.get('state', ''),
      phone=request.form.get('phone', ''),
      image_link=request.form.get('image_link'),
      facebook_link=request.form.get('facebook_link'),
      genres=request.form.getlist('genres'),
      seeking_venue=True if 'seeking_venue' in request.form else False,
      seeking_description=request.form.get('seeking_description', '')
    )

    db.session.add(artist)
    db.session.commit()
  except:
    error = True
    # rollback in case of error happen
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Error occurred: ' +
          name + ' could not be inserted.')
  else:
    flash('Artist ' + name + ' was successfully listed!')
  return render_template('pages/home.html')

#  Delete Artist
#  ----------------------------------------------------------------

@app.route('/artists/<artist_id>/delete', methods=['POST'])
def delete_artist(artist_id):
  error = False
  try:
    # query to get specific artist
    artist = Artist.query.get(artist_id)
    name = artist.name

    db.session.delete(artist)
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Error occurred: ' +
          name + ' could not be deleted.')
  else:
    flash('Artist ' + name + ' was successfully deleted!')
  return render_template('pages/home.html')

#  Edit Artist
#  ----------------------------------------------------------------

@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  error = False
  try:
    form = ArtistForm()
    artistData = {}  # empty object to store all the data we need
    # query to get specific artist
    artist = Artist.query.get(artist_id)
    if not artist:
      # render 404 if not found
      return render_template('errors/404.html')

    # assign artist data values
    artistData['id'] = artist.id
    artistData['name'] = artist.name
    artistData['city'] = artist.city
    artistData['state'] = artist.state
    artistData['phone'] = artist.phone
    artistData['image_link'] = artist.image_link
    artistData['facebook_link'] = artist.facebook_link
    artistData['genres'] = artist.genres
    artistData['seeking_venue'] = artist.seeking_venue
    artistData['seeking_description'] = artist.seeking_description
  except:
    error = True
  if error:
    # render 500 if there is a server error
    return render_template('errors/500.html')
  else:
    return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  error = False
  try:
    # query to get specific artist
    artist = Artist.query.get(artist_id)
    name = artist.name
    # get values from form and Update record on db
    artist.name = request.form.get('name', '')
    artist.city = request.form.get('city', '')
    artist.state = request.form.get('state', '')
    artist.phone = request.form.get('phone', '')
    artist.image_link = request.form.get('image_link')
    artist.facebook_link = request.form.get('facebook_link')
    artist.genres = request.form.getlist('genres')
    artist.seeking_venue = True if 'seeking_venue' in request.form else False
    artist.seeking_description = request.form.get('seeking_description', '')

    db.session.commit()
  except:
    error = True
    # rollback in case of error happen
    db.session.rollback()
  finally:
    db.session.close()
  if error:
    flash('Error occurred: ' +
          name + ' could not be Edited.')
  else:
    flash('Artist ' + name + ' was successfully Edited!')
  return redirect(url_for('show_artist', artist_id=artist_id))

#  ----------------------------------------------------------------
#  Shows
#  ----------------------------------------------------------------

#  Shows list
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  data = []  # empty array to store all the data we need
  # query to retreive all shows
  shows = Show.query.join(Venue).join(Artist).all()

  for show in shows:
    body = {}  # empty object to store show data
    # append venue data to the array
    body['artist_id'] = show.artist_id
    body['artist_name'] = show.artist.name
    body['artist_image_link'] = show.artist.image_link
    body['venue_id'] = show.venue_id
    body['venue_name'] = show.venue.name
    body['start_date'] = show.start_date.strftime('%Y-%m-%d %H:%M:%S')

    # append artist data to the array
    data.append(body)

  return render_template('pages/shows.html', shows=data)

#  Create Shows
#  ----------------------------------------------------------------

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  error = False
  try:
    # get values from form and create record on db
    show = Show(
        venue_id=request.form.get('venue_id', ''),
        artist_id=request.form.get('artist_id', ''),
        start_date=request.form.get('start_date', '')
    )

    db.session.add(show)
    db.session.commit()
  except:
    error = True
    # rollback in case of error happen
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
  if error:
    flash('Error occurred: show could not be inserted.')
  else:
    flash('Show was successfully listed!')
  return render_template('pages/home.html')

#----------------------------------------------------------------------------#
# Errors Handler.
#----------------------------------------------------------------------------#

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

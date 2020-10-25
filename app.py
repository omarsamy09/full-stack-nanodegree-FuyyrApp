#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for,jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func
from sqlalchemy_utils import ScalarListType
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
from config import SQLALCHEMY_DATABASE_URL
import sys

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_DATABASE_URI']=SQLALCHEMY_DATABASE_URL
db = SQLAlchemy(app)
migrate=Migrate(app,db)


class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    genres= db.Column(db.ARRAY(db.String()))
    shows=db.relationship('Show',backref='venue',lazy=True)
    # Done: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres= db.Column(db.ARRAY(db.String()))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    shows=db.relationship('Show',backref='artist',lazy=True)
    # DONE: implement any missing fields, as a database migration using Flask-Migrate
class Show(db.Model):
    __tablename__='Shows'

    id = db.Column(db.Integer, primary_key=True)
    artist_id=db.Column(db.Integer,db.ForeignKey('Artist.id'))
    venue_id=db.Column(db.Integer,db.ForeignKey('Venue.id'))
    start_time=db.Column(db.DateTime)

# Done: connect to a local postgresql database

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


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Done: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  data=db.session.query(Venue.city,Venue.state).group_by(Venue.city,Venue.state).all()
  areas=[]
  for i in data:
      datas={
      'city':i.city,
      'state':i.state,
      'venues':db.session.query(Venue.name,Venue.id).filter(Venue.city==i.city).filter(Venue.state==i.state).all(),
       }
      areas.append(datas)
  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Done: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
   data_to_find=request.form.get('search_term', '')
   venues=Venue.query.filter(func.lower(Venue.name).contains(func.lower(data_to_find))).all()
   return render_template('pages/search_venues.html', results=venues,count=len(venues), search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  venue_to_find=Venue.query.get(venue_id)
  #I joined between models to get the venues by artist
  venue_to_find.past_shows= db.session.query(Venue, Show).join(Show).join(Artist).filter(Show.venue_id ==venue_id,Show.artist_id == Artist.id,Show.start_time < datetime.now()).all()
  venue_to_find.upcoming_shows=db.session.query(Venue, Show).join(Show).join(Artist).filter(Show.venue_id ==venue_id,Show.artist_id == Artist.id,Show.start_time > datetime.now()).all()
  upcoming_shows_count=len(venue_to_find.upcoming_shows)
  past_shows_count=len(venue_to_find.past_shows)
  return render_template('pages/show_venue.html', venue=venue_to_find,Artist=Artist,Show=Show,past_shows_count=past_shows_count,upcoming_shows_count=upcoming_shows_count)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    form=VenueForm(request.form)
    error=False
    try:
        name=request.form.get('name')
        city=request.form.get('city')
        state=request.form.get('state')
        address=request.form.get('address')
        phone=request.form.get('phone')
        facebook_link=request.form.get('facebook_link')
        image_link=request.form.get('image_link')
        website_link=request.form.get('website_link')
        genres=request.form.getlist('genres')
        venue=Venue(name=name,city=city,state=state,address=address,phone=phone,facebook_link=facebook_link,genres=genres,image_link=image_link,website_link=website_link)
        db.session.add(venue)
        db.session.commit()
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        error=True
        print(sys.exc_info())
    finally:
        db.session.close()
    if  error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html')

  # Done: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  # on successful db insert, flash success

  # done: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
   try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash('Venue deleted successfully')
   except:
    db.session.rollback()
   finally:
    db.session.close()
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
   return render_template('pages/home.html')

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # Done: replace with real data returned from querying the database
  data=Artist.query.all()
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data_to_find=request.form.get('search_term', '')
  artists=Artist.query.filter(func.lower(Artist.name).contains(func.lower(data_to_find))).all()
  return render_template('pages/search_artists.html', results=artists,count=len(artists), search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
      artist_to_find=Artist.query.get(artist_id) #getting artist by id

      #I joined between models to get artists with their past Venues
      artist_to_find.past_shows = db.session.query(Artist, Show).join(Show).join(Venue).filter(Show.venue_id == Venue.id,Show.artist_id == artist_id,Show.start_time < datetime.now()).all()
      #finding shows related to that artist with time>=current time

      artist_to_find.upcoming_shows=db.session.query(Artist, Show).join(Show).join(Venue).filter(Show.venue_id == Venue.id,Show.artist_id == artist_id,Show.start_time > datetime.now()).all()
      #passing the size of lists of upcoming shows and past shows to variables
      upcoming_shows_count=len(artist_to_find.upcoming_shows)

      past_shows_count=len(artist_to_find.past_shows)

      return render_template('pages/show_artist.html', artist=artist_to_find,Show=Show,Venue=Venue,upcoming_shows_count=upcoming_shows_count,past_shows_count=past_shows_count)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  #getting data to the edit form
  artist=Artist.query.get(artist_id)
  form.name.data=artist.name
  form.city.data=artist.city
  form.state.data=artist.state
  form.phone.data=artist.phone
  form.genres.data=artist.genres
  form.facebook_link.data=artist.facebook_link
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  #updating dataa
   new_artist=Artist.query.get(artist_id)
   new_artist.name=request.form.get('name')
   new_artist.city=request.form.get('city')
   new_artist.state=request.form.get('state')
   new_artist.genres=request.form.getlist('genres')
   new_artist.phone=request.form.get('phone')
   new_artist.facebook_link=request.form.get('facebook_link')
   db.session.commit()
   return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # DONE: populate form with values from venue with ID <venue_id>
  venue=Venue.query.get(venue_id)
  form.name.data=venue.name
  form.city.data=venue.city
  form.state.data=venue.state
  form.address.data=venue.address
  form.phone.data=venue.phone
  form.genres.data=venue.genres
  form.facebook_link.data=venue.facebook_link
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form=VenueForm(request.form);
  new_venue=Venue.query.get(venue_id)
  new_venue.name=request.form.get('name')
  new_venue.city=request.form.get('city')
  new_venue.state=request.form.get('state')
  new_venue.address=request.form.get('address')
  new_venue.phone=request.form.get('phone')
  new_venue.genres=request.form.getlist('genres')
  new_venue.facebook_link=request.form.get('facebook_link')
  db.session.commit()
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    form=ArtistForm(request.form)
    error=False
    try:
        name=request.form.get('name')
        city=request.form.get('city')
        state=request.form.get('state')
        phone=request.form.get('phone')
        facebook_link=request.form.get('facebook_link')
        genres=request.form.getlist('genres')
        image_link=request.form.get('image_link')
        website_link=request.form.get('website_link')
        artist=Artist(name=name,city=city,state=state,phone=phone,facebook_link=facebook_link,genres=genres,image_link=image_link,website_link=website_link)
        db.session.add(artist)
        db.session.commit()
        flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        error=True
    finally:
        db.session.close()
    if  error:
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')

    return render_template('pages/home.html')
  # called upon submitting the new artist listing form
  # Done: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # DONE: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')



#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # Done: replace with real venues data.
   #num_shows should be aggregated based on number of upcoming shows per venue.
   shows=Show.query.filter(Show.venue_id==Venue.id).filter(Show.artist_id==Artist.id).all()
   return render_template('pages/shows.html', shows=shows ,Artist=Artist,Venue=Venue)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # Done: insert form data as a new Show record in the db, instead
    form=ShowForm(request.form)
    error=False
    try:
      artist_id=request.form.get('artist_id')
      venue_id=request.form.get('venue_id')
      start_time=request.form.get('start_time')
      show=Show(start_time=start_time,venue_id=venue_id,artist_id=artist_id)
      db.session.add(show)
      db.session.commit()
      flash('Show was successfully listed! ')
    except:
      db.session.rollback()
      error=True
    finally:
      db.session.close()
    if  error:
      flash('An error occurred. Show could not be listed.')
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

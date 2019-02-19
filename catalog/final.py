#!/usr/bin/env python3
from flask import Flask, redirect, request
from flask import render_template, url_for, jsonify, flash
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from fdatabase_setup import Institute, Base, Course, User
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
app = Flask(__name__)
CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "institute application"
engine = create_engine('sqlite:///courses.db',
                       connect_args={'check_same_thread': False}, echo=True)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

institutenames = session.query(Institute)


# login
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    institute = session.query(Institute).all()
    return render_template('login.html', STATE=state, institutes=institute)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
                                            'Current user is already'
                                            'connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    print(login_session['email'])
    login_session['provider'] = 'google'
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;'
    'border-radius: 150px;-webkit-border-radius: 150px;'
    '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


# user helper functions
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                   'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None

# DISCONNECT- Revoke a current user's token and reset their login_session


@app.route('/gdisconnect')
def gdisconnect():
        # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return redirect(url_for('showLogin'))
    else:
        # For whatever reason, the given token was invalid.
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/institutes/<int:institute_id>/menu/JSON')
def courseJSON(institute_id):
    institute = session.query(Institute).filter_by(id=institute_id).one()
    items = session.query(Course).filter_by(institute_id=institute_id).all()
    return jsonify(Course=[i.serialize for i in items])


@app.route('/institutes/<int:institute_id>/menu/<int:course_id>/JSON')
def coursenamesJSON(institute_id, course_id):
    items = session.query(Course).filter_by(id=course_id).one()
    return jsonify(Course=items.serialize)


@app.route('/institutes/JSON')
def institutesJSON():
    institutes = session.query(Institute).all()
    return jsonify(institutes=[r.serialize for r in institutes])


# showing the institutes
@app.route('/')
@app.route('/institutes')
def showinstitute():
    institutes = session.query(Institute).all()
    return render_template('institutes.html', institutes=institutes)


# To create a new institute
@app.route('/institutes/new', methods=['GET', 'POST'])
def newinstitute():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newinstitute = Institute(name=request.form['name'],
                                 user_id=login_session['user_id'])
        session.add(newinstitute)
        session.commit()
        return redirect(url_for('showinstitute'))
    else:
        return render_template('newinstitute.html', institutes=institutenames)


# edit institute
@app.route('/institutes/<int:institute_id>/edit', methods=['GET', 'POST'])
def editinstitute(institute_id):
    editedinstitute = session.query(Institute).filter_by(id=institute_id).one()
    creator = getUserInfo(editedinstitute.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash("You cannot edit this institute."
              "This is belongs to %s" % creator.name)
        return redirect(url_for('showinstitute'))
    else:
        if request.method == 'POST':
            if request.form['name']:
                editedinstitute.name = request.form['name']
                session.add(editedinstitute)
                session.commit()
            return redirect(url_for('showinstitute'))
        else:
            return render_template('editinstitute.html',
                                   institute_id=institute_id,
                                   item=editedinstitute,
                                   institutes=institutenames)


# delete institute
@app.route('/institutes/<int:institute_id>/delete', methods=['GET', 'POST'])
def deleteinstitute(institute_id):
        deletedinstitute = session.query(Institute).filter_by(
                              id=institute_id).one()
        creator = getUserInfo(deletedinstitute.user_id)
        user = getUserInfo(login_session['user_id'])
        if creator.id != login_session['user_id']:
            flash("you cannot delete this institute."
                  "this is belongs to %s" % creator.name)
            return redirect(url_for('showinstitute'))
        if request.method == 'POST':
            session.delete(deletedinstitute)
            session.commit()
            return redirect(url_for('showinstitute'))
        else:
            return render_template('deleteinstitute.html',
                                   institute_id=institute_id,
                                   item=deletedinstitute,
                                   institutes=institutenames)


# showing courses based on institute
@app.route('/institutes/<int:institute_id>')
def courses(institute_id):
    institute = session.query(Institute).filter_by(id=institute_id).one()
    item = session.query(Course).filter_by(institute_id=institute.id).all()
    return render_template('course.html', institute=institute, item=item,
                           institutes=institutenames)


# create new course
@app.route('/institutes/<int:institute_id>/new', methods=['GET', 'POST'])
def newcourse(institute_id):
    institute = session.query(Institute).filter_by(id=institute_id).one()
    creator = getUserInfo(institute.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash("you cannot create newcourse in this instiute."
              "this is belongs to %s" % creator.name)
        return redirect(url_for('courses', institute_id=institute.id))
    if request.method == 'POST':
        newcourse = Course(id=request.form['id'], name=request.form['name'],
                           instructor=request.form['instructor'],
                           department=request.form['department'],
                           duration=request.form['duration'],
                           institute_id=institute_id,
                           user_id=institute.user_id)
        session.add(newcourse)
        session.commit()
        return redirect(url_for('courses', institute_id=institute_id))
    else:
        return render_template('newcourse.html', institute_id=institute_id,
                               institutes=institutenames)


# edit course
@app.route('/institutes/<int:institute_id>/<int:course_id>/edit',
           methods=['GET', 'POST'])
def editcourse(institute_id, course_id):
    editedcourse = session.query(Course).filter_by(id=course_id).one()
    institute = session.query(Institute).filter_by(id=institute_id).one()
    creator = getUserInfo(editedcourse.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
        flash("You can't edit this course"
              "This is belongs to %s" % creator.name)
        return redirect(url_for('courses', institute_id=institute.id))
    # POST method
    if request.method == 'POST':
        if request.form['id']:
            editedcourse.id = request.form['id']
        if request.form['name']:
            editedcourse.name = request.form['name']
        if request.form['instructor']:
            editedcourse.instructor = request.form['instructor']
        if request.form['department']:
            editedcourse.department = request.form['department']
        if request.form['duration']:
            editedcourse.duration = request.form['duration']
        session.add(editedcourse)
        session.commit()
        return redirect(url_for('courses', institute_id=institute_id))
    else:
        return render_template('editcourse.html', institute_id=institute_id,
                               course_id=course_id, item=editedcourse,
                               institutes=institutenames)


# delete course
@app.route('/institutes/<int:institute_id>/<int:course_id>/delete',
           methods=['GET', 'POST'])
def deletecourse(institute_id, course_id):
    deletedcourse = session.query(Course).filter_by(id=course_id).one()
    institute = session.query(Institute).filter_by(id=institute_id).one()
    creator = getUserInfo(deletedcourse.user_id)
    user = getUserInfo(login_session['user_id'])
    if creator.id != login_session['user_id']:
            flash("You can't delete this course"
                  "This is belongs to %s" % creator.name)
            return redirect(url_for('courses', institute_id=institute.id))
    # POST methods
    if request.method == 'POST':
        session.delete(deletedcourse)
        session.commit()
        return redirect(url_for('courses', institute_id=institute_id))
    else:
        return render_template('deletecourse.html', institute_id=institute_id,
                               course_id=course_id, item=deletedcourse,
                               institutes=institutenames)
if __name__ == '__main__':
    global institutenames
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8080)

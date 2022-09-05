import flask
from authlib.client import OAuth2Session
from dateutil import tz
from datetime import datetime, timedelta
from flask_cors import cross_origin

from config import SECRET_KEY, DOMAIN_NAME, EXCLUDE_EMAIL
from dash import google_auth
from dash.google_auth import CLIENT_ID, CLIENT_SECRET, AUTHORIZATION_SCOPE, AUTH_REDIRECT_URI, AUTHORIZATION_URL, \
    AUTH_STATE_KEY, ACCESS_TOKEN_URI, AUTH_TOKEN_KEY, BASE_URI, no_cache
from dash.util import elastic
from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_wtf.csrf import CSRFProtect

import re

app = Flask(__name__)
app.secret_key = SECRET_KEY
csrf = CSRFProtect(app)
app.register_blueprint(google_auth.app)


@app.route('/')
@cross_origin()
def get_dashboard():
    if google_auth.is_logged_in():
        user_info = google_auth.get_user_info()
        email = user_info['email']
        if email == EXCLUDE_EMAIL:
            return render_template('dashboard.html')
        elif email.split('@')[1] != DOMAIN_NAME:
            return redirect(url_for('logout'))
        return render_template('dashboard.html')
    return render_template('login.html')


@app.route('/google/login')
@no_cache
def login():
    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            redirect_uri=AUTH_REDIRECT_URI)

    uri, state = session.authorization_url(AUTHORIZATION_URL)

    flask.session[AUTH_STATE_KEY] = state
    flask.session.permanent = True

    return flask.redirect(uri, code=302)


@app.route('/google/auth')
@no_cache
def google_auth_redirect():
    req_state = flask.request.args.get('state', default=None, type=None)

    if req_state != flask.session[AUTH_STATE_KEY]:
        response = flask.make_response('Invalid state parameter', 401)
        return response

    session = OAuth2Session(CLIENT_ID, CLIENT_SECRET,
                            scope=AUTHORIZATION_SCOPE,
                            state=flask.session[AUTH_STATE_KEY],
                            redirect_uri=AUTH_REDIRECT_URI)

    oauth2_tokens = session.fetch_access_token(
        ACCESS_TOKEN_URI,
        authorization_response=flask.request.url)

    flask.session[AUTH_TOKEN_KEY] = oauth2_tokens

    return flask.redirect(BASE_URI, code=302)


@app.route('/google/logout')
@no_cache
def logout():
    flask.session.pop(AUTH_TOKEN_KEY, None)
    flask.session.pop(AUTH_STATE_KEY, None)

    return flask.redirect(BASE_URI, code=302)


# @app.route('/kubernetes/labels/app/keyword', methods=["GET", "POST"])
# def get_uniq_data(service_key=elastic.get_uniq_item()):
#     if google_auth.is_logged_in():
#         services = service_key
#     else:
#         return redirect(url_for('logout'))
#     return jsonify(services)


@app.route('/search', methods=["GET", "POST"])
def search():
    if not google_auth.is_logged_in():
        return redirect(url_for('logout'))
    # assign value from input form to "data"
    data = request.form
    # function to get utc time and local timezone offset
    from_zone = tz.tzutc()
    to_zone = tz.tzlocal()

    # to check if the value of data for datetime picker is not empty
    if not data['date_timepicker_start']:
        # get 1 hour before current utc time
        epoch_start = datetime.utcnow() - timedelta(hours=1)
    else:
        # get start datetime picker value from string to datetime object
        epoch_start = datetime.strptime(data['date_timepicker_start'], "%Y-%m-%dT%H:%M:%S.%fZ")
    if not data['date_timepicker_end']:
        # get current utc time
        epoch_end = datetime.utcnow()
    else:
        # get end datetime picker value from string to datetime object
        epoch_end = datetime.strptime(data['date_timepicker_end'], "%Y-%m-%dT%H:%M:%S.%fZ")

    return_value = []

    capture_pattern = '[\d-]+T([\d:.]+)\+[\d\:]+'
    match_pattern = 'T[\d:.]+'

    records = elastic.get_data(keyword=data['keyword'],
                               start_time=epoch_start,
                               end_time=epoch_end,
                               service=data['service'])

    # to get array of object in JSON
    for record in records:
        # function to get utc time and local timezone offset
        timestamp = record['_source']['@timestamp']

        match = re.search(capture_pattern, timestamp)
        if match:
            time = match.group(1)
            timestamp = re.sub(match_pattern, 'T' + time[:-3], timestamp)

        record_gmt = datetime.strptime(timestamp, "%Y-%m-%dT%H:%M:%S.%f%z")
        utc_gmt = record_gmt.replace(tzinfo=from_zone)
        local_tz = utc_gmt.astimezone(to_zone)

        log_time = local_tz.strftime("%d/%b/%Y, %H:%M:%S%z")

        return_value.append('<b>' + '[' + str(log_time) + ']' + '</b>' + ': ' + record['_source']['log'])
        list_to_string = (",".join(str(e) for e in return_value))
        linesep = "<br>".join(list_to_string.split("\n"))
        result = linesep.translate({ord(','): None})

    if not return_value:
        result = "Not Found! please check your input and try again."

    return result
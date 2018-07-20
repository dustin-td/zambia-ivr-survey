import flask
from flask import Flask
from flask import render_template, redirect, url_for, request, session, flash
from twilio.twiml.voice_response import Play, VoiceResponse
import sqlite3 as sql
from functools import wraps
import re, json

app = Flask(__name__, static_url_path='/static')

# Setup routes

@app.route('/')
@app.route('/ivr')
def home():
    return render_template('index.html')

@app.route('/ivr/incoming', methods=['GET','POST'])
def incoming():
    response = VoiceResponse()
    response.say('Please leave a message')
    response.record()
    response.hangup()

    return twiml(response)

@app.route('/ivr/init/<string:id>/<string:version>', methods=['GET', 'POST'])
def init(id,version):
    # Load survey
    with open('survey' + version + '.json') as f:
        survey_def = json.loads(f.read())
        questions = survey_def['questions']
        session['questions'] = questions

    # Set response
    response = VoiceResponse()
    # Set ID in database
    with sql.connect('db.sqlite') as conn:
        c = conn.cursor()
        c.execute('INSERT OR IGNORE INTO keypresses (ID) VALUES ({id})'.\
                  format(id=id))
    # Set session ID
    session['id'] = id
    # Start with first question
    session['q'] = 1
    [question] = [x for x in questions if x['ID'] == 1]
    return play_question(response, id, question)


@app.route('/ivr/survey', methods=['GET', 'POST'])
def survey():
    selection = request.form['Digits']
    with sql.connect('db.sqlite') as conn:
        c = conn.cursor()
        c.execute('UPDATE keypresses SET Q{q}=({dg}) WHERE ID=({id})'.\
                  format(q=session['q'], dg=selection, id=session['id']))

    [oq] = [x for x in session['questions'] if x['ID'] == int(session['q'])]

    if str(selection) in oq['keypresses'].keys():
        session['q'] = oq['keypresses'][str(selection)]
        [question] = [x for x in session['questions'] if x['ID'] == int(session['q'])]
        response = VoiceResponse()
        return play_question(response, session['id'], question)

    else:
        response = VoiceResponse()
        return play_question(response, session['id'], oq)

@app.route('/ivr/redirect', methods=['GET','POST'])
def redirect():
    if 'redirect' not in session:
        session['redirect'] = 1
    else:
        session['redirect'] = int(session['redirect']) + 1
    response = VoiceResponse()
    [oq] = [x for x in session['questions'] if x['ID'] == int(session['q'])]
    return play_question(response, session['id'], oq, int(session['redirect']))

# Private methods

def play_question(response, id, question, redir=0):
    if question['keypresses']:
        with response.gather(num_digits=1, action=url_for('survey'), method='POST', timeout=15) as g:
            for audio in question['audio']:
                if re.match("<.*>", audio) is not None:
                    p = '/static/' + audio.replace('<', '').replace('>', '/') + id + '.wav'
                    g.play(p)
                else:
                    g.play(audio)
        if redir <= 2:
            response.redirect(url_for('redirect'), method='GET')
        return twiml(response)
    else:
        response.play(question['audio'][0])
        response.hangup()
        return twiml(response)

def twiml(resp):
    resp = flask.Response(str(resp))
    resp.headers['Content-Type'] = 'text/xml'
    return resp


if __name__ == "__main__":
    app.secret_key = 'asdf8904urasdf89a823urp9sdf0'
    app.run()

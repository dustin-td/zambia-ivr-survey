import flask
from flask import Flask
from flask import render_template, redirect, url_for, request, session, flash
from twilio.twiml.voice_response import Play, VoiceResponse
app = Flask(__name__, static_url_path='/static')



@app.route('/')
@app.route('/ivr')
def home():
    return render_template('index.html')

@app.route('/ivr/welcome/<string:username>', methods=['GET', 'POST'])
def welcome(username):
    response = VoiceResponse()
    with response.gather(num_digits=1, action=url_for('menu'), method='POST') as g:
        #g.play('/static/Untitled.wav')
        g.say("Hello, this the American Institutes for Research calling for " +
              username +
              ". Press 1 to for option 1 or Press 2 for option 2", voice="alice", language="en-US")
    return twiml(response)

@app.route('/ivr/menu', methods=['POST'])
def menu():
    selected_option = request.form['Digits']
    option_actions = {'1': _press1,
                      '2': _press2}
    if option_actions.has_key(selected_option):
        response = VoiceResponse()
        option_actions[selected_option](response)
        return twiml(response)

    return _redirect_welcome()

# Private methods

def _press1(response):
    response.say('Sorry, wrong answer', voice='alice', language='en-GB')
    response.hangup()
    return response

def _press2(response):
    response.say("Horay!", voice='alice', language='en-GB')
    response.hangup()
    return response

def twiml(resp):
    resp = flask.Response(str(resp))
    resp.headers['Content-Type'] = 'text/xml'
    return resp

def _redirect_welcome():
    response = VoiceResponse()
    response.say("Returning to main menu", voice="alice", language="en-GB")
    response.redirect(url_for('welcome'))

if __name__ == "__main__":
    app.run()

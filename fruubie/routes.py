import os
import pathlib

# from http import client
import requests
from flask import Blueprint, Flask, render_template, session, abort, redirect, request, send_from_directory, url_for, flash
from google.oauth2 import id_token
from google_auth_oauthlib.flow import Flow
from pip._vendor import cachecontrol
import google.auth.transport
from pymongo import MongoClient
from fruubie import app, db
from fruubie.models import User, Post
from dotenv import load_dotenv

# maps stuff
# ------------------------

app = Flask(__name__)

main = Blueprint('main', __name__)

MONGO_PASS = os.getenv('MONGO_PASS')

client = MongoClient(f"mongodb+srv://alaJream:{MONGO_PASS}@cluster0.62z5r.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
db = client.test


os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

GOOGLE_CLIENT_ID = "127748775849-qnagr0cq7ip8e3m37cqmoevqbidkr9p7.apps.googleusercontent.com"
client_secrets_file = os.path.join(pathlib.Path(__file__).parent, "client_secret.json")

flow = Flow.from_client_secrets_file(
    client_secrets_file=client_secrets_file,
    scopes=["https://www.googleapis.com/auth/userinfo.profile", "https://www.googleapis.com/auth/userinfo.email", "openid"],
    redirect_uri="http://127.0.0.1:5000/callback"
)



def login_is_required(function):
    def wrapper(*args, **kwargs):
        if "google_id" not in session:
            return abort(401)  # Authorization required
        else:
            return function()

    return wrapper

# -----------------------------------------------------------------------------------------

@main.route("/")
def index():
    return render_template('home.html')

@main.route("/login")
def login():
    authorization_url, state = flow.authorization_url()
    session["state"] = state
    return redirect(authorization_url)

@main.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@main.route("/callback")
def callback():
    flow.fetch_token(authorization_response=request.url)

    if not session["state"] == request.args["state"]:
        abort(500)  # State does not match!

    credentials = flow.credentials
    request_session = requests.session()
    cached_session = cachecontrol.CacheControl(request_session)
    token_request = google.auth.transport.requests.Request(session=cached_session)

    id_info = id_token.verify_oauth2_token(
        id_token=credentials._id_token,
        request=token_request,
        audience=GOOGLE_CLIENT_ID
    )

    session["google_id"] = id_info.get("sub")
    session["name"] = id_info.get("name")
    return redirect("/home")


@main.route("/home")
@login_is_required
def home():
    # return f"Hello {session['name']}! <br/> <a href='/logout'><button>Logout</button></a>"
    return render_template("home.html") 

@main.route("/community/<location>")
# @login_is_required
def get_post():
    context = {
            'post': Post.query.all()
        }
    return render_template('maps.html', **context)

@main.route('/community', methods=['GET'])
def get_posts():
    my_data = db.data.find()
    context = {
        'data': my_data
    }
    return render_template('maps.html', **context)

# -----------------------------------------------------------------------------------------

# @main.route('/create_post', methods=['GET'])
# def create():
#     return render_template('create_post.html')

@main.route('/user/<id>', methods=['GET'])
def get_user(id):
    found_user = main.query.filter_by(google_id=id).first()
    if found_user:
        user_data = {
            'google_id': found_user.google_id,
            'name': found_user.name,
            'email': found_user.email,
            'image': found_user.image
        }
        return user_data, 200
    return {'success': False, 'message':'User not found'}, 400


@main.route('/create')
def my_form():
    return render_template('create.html')

@main.route('/create', methods=['GET','POST'])
def create_post():

    if request.method == "POST":
        location = request.form['location']
        post = {
            'title': request.form['title'],
            'content': request.form['content'],
            'date': request.form['date'],
            'quantity': request.form['quantity'],
            'location': request.form['location']
            # adding user id (authentication, google id, monngo id) render db.post.find
        }
        db.posts.insert_one(post)
    URL = os.getenv('GEOURL')
    # location = input("Enter the location here: ") #taking user input
    api_key = os.getenv('GEOAPI')
    PARAMS = {'apikey':api_key,'q':location} 

# sending get request and saving the response as response object 
    r = requests.get(url = URL, params = PARAMS) 
    data = r.json()
#print(data)

#Acquiring the latitude and longitude from JSON 
    latitude = data['items'][0]['position']['lat']
#print(latitude)
    longitude = data['items'][0]['position']['lng']
    # return render_template('maps.html',apikey=api_key,latitude=latitude,longitude=longitude)
    return redirect(url_for('/community'))



        

# @app.route('/community/<filename>')
# def send_uploaded_file(filename=''):
#     return send_from_directory(app.config["IMAGE_UPLOADS"], filename)s

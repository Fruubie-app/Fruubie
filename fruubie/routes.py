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
    return render_template('index.html')

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

@main.route("/community")
# @login_is_required
def get_post():
    context = {
            'post': Post.query.all()
        }
    return render_template('community.html', **context)

@main.route('/community', methods=['GET'])
def get_posts():
    my_data = db.data.find()
    context = {
        'data': my_data
    }
    return render_template('community.html', **context)

# -----------------------------------------------------------------------------------------

@main.route('/create_post', methods=['GET'])
def create():
    return render_template('create_post.html')

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


@main.route('/create', methods=['GET','POST'])
def create_post():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        # img_url = request.form.get('img_url')
        created_by = request.form.get('created_by')
        date = request.form.get('date')
        # print('Im in the post')
        try:
            # print('Im in the try')
            new_post = {
            'title':title,
            'content':content,
            'created_by':created_by,
            'date':date
        }
            db.data.insert_one(new_post)
            flash('Post created.')
            return redirect(url_for('main.create_post'))
        except ValueError:
            print('there was an error: incorrect datetime format')
    return render_template('create.html')

@app.route('/community/<filename>')
def send_uploaded_file(filename=''):
    return send_from_directory(app.config["IMAGE_UPLOADS"], filename)


from flask import Flask
from GameFinder.config import get_key
from flask_bootstrap import Bootstrap
# TODO configure blueprints


app = Flask(__name__)
app.config['SECRET_KEY'] = get_key()
Bootstrap(app)
# import down here to stop circular import
import GameFinder.GameFindermain.routes



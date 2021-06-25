from flask import Flask, request
from .airbnb_data_model import User, Listing, DB

def create_app():

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
    DB.init_app(app)

    @app.route('/')
    def landing():
        return 'Welcome to my app'

    @app.route('/add_author')
    def add_author():
        twitter_handle = request.args['twitter_handle']
        new_user = upsert_user(twitter_handle, nlp, twitter_api)
        return '{}\'s tweets added to the database: {}'.format(new_user.name , ', '.join([t.text for t in new_user.tweets]))

    @app.route('/predict_author')
    def predict_author():
        tweet_to_classify = request.args['tweet_to_classify']
        users = [user.name for user in User.query.all()]
        most_likely_author = get_most_likely_author(users, tweet_to_classify, nlp)
        return most_likely_author

    @app.errorhandler(404)
    def error_handler(e):
        return 'this is not here: {}'.format(e), 404

    return app



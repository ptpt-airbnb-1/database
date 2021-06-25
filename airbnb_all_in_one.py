from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request
import random

app = Flask(__name__)

DB = SQLAlchemy()

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
DB = SQLAlchemy(app)


class Host(DB.Model):
    id = DB.Column(DB.BigInteger, primary_key=True)
    username = DB.Column(DB.String(20), nullable=False)

    def __repr__(self):
        return '< id %s --- username %s>' % (self.id, self.username)


class Listing(DB.Model):
    id = DB.Column(DB.BigInteger, primary_key=True)
    name = DB.Column(DB.String(50))
    neighborhood = DB.Column(DB.String(50), nullable=False)
    min_nights = DB.Column(DB.Integer, nullable=False)
    room_type = DB.Column(DB.String(20), nullable=False)
    bedrooms = DB.Column(DB.Integer, nullable=False)
    season = DB.Column(DB.String)
    price = DB.Column(DB.Integer, nullable=False)
    predicted_price = DB.Column(DB.Integer, nullable=False)
    host_id = DB.Column(DB.BigInteger, DB.ForeignKey("host.id"), nullable=False)
    host = DB.relationship('Host', backref=DB.backref('listings'), lazy=True)

    def __repr__(self):
        return '<--- id %s --- name %s --- neighborhood %s --- min_nights %s --- room_type %s ' \
               '--- bedrooms %s --- season %s --- price %s --- predicted_price %s ' \
               '--- host_id %s ---host %s>' % (self.id, self.name, self.neighborhood,
                                               self.min_nights, self.room_type, self.bedrooms, self.season,
                                               self.price, self.predicted_price, self.host_id, self.host)


# dummy function for now. Later, it will return ["price"], inputs send as strings
def predict_price(neighborhood, min_nights, room_type, bedrooms):
    if type(bedrooms) == str and type(min_nights) == str:
        return [1]
    else:
        return [2]


@app.route('/')
def root():
    DB.drop_all()
    DB.create_all()
    return str("Welcome to Airbnb Price Predictor, the database is empty and ready to go")


@app.route('/price_predictor')
def price_predictor():
    neighborhood = request.args['neighborhood']
    min_nights = request.args['min_nights']
    room_type = request.args['room_type']
    bedrooms = request.args['bedrooms']
    predicted_price = predict_price(neighborhood, min_nights, room_type, bedrooms)
    return {"predicted_price": int(predicted_price[0])}


@app.route('/add_host')
def add_host():
    host_username = request.args['username']
    if Host.query.filter_by(username=host_username).first():
        return "Existent Host"
    else:
        new_host = Host(id=random.randint(0, 999999), username=host_username)
        DB.session.add(new_host)
        DB.session.commit()
        return {"new_host": str(new_host)}


@app.route('/upsert_listing')
def upsert_listing():
    id = request.args.get('id') #nullable
    name = request.args.get('name')  # nullable
    neighborhood = request.args['neighborhood']
    min_nights = request.args['min_nights']
    room_type = request.args['room_type']
    bedrooms = request.args['bedrooms']
    price = request.args.get('price')  # nullable, auto filled with price_predictor
    host_id = request.args.get('host_id') #nullable when id is provided
    predicted_price = predict_price(neighborhood, min_nights, room_type, bedrooms)[0]
    if price is None:
        price = predicted_price
    if Listing.query.get(id):
        # update listing no host_id needed
        listing = Listing.query.get(id)
        listing.name = name
        listing.neighborhood = neighborhood
        listing.min_nights = int(min_nights)
        listing.room_type = room_type
        listing.bedrooms = int(bedrooms)
        listing.price = int(price)
        listing.predicted_price = predicted_price
        DB.session.commit()
        return str(listing)
    elif Host.query.get(host_id):
        # add listing to a host_id
        listing = Listing(id=random.randint(0, 999999), name=name, neighborhood=neighborhood,
                          min_nights=int(min_nights), room_type=room_type, bedrooms=int(bedrooms),
                          price=int(price), predicted_price=predicted_price, host_id=int(host_id))
        DB.session.add(listing)
        DB.session.commit()
        return str(listing)
    else:
        return "listing_id and/or host_id don't exist"

if __name__ == '__main__':
    app.run()
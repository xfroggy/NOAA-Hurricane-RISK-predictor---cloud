from flask import Flask, request, redirect, render_template, flash
from flask_sqlalchemy import SQLAlchemy
import sys
import geopandas
import cgi
import os
import numpy as np
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
import pandas as pd
from sqlalchemy.types import Integer, Text, String, DateTime, Float
from os import environ
from sqlalchemy import create_engine
from clean import clean
from models import Prediction


application = Flask(__name__)

application.config['DEBUG'] = True
application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:test1234@database-1.cls1yuqwbwzq.us-east-2.rds.amazonaws.com:3306/MyFlaskApp'
application.config['SQLALCHEMY_ECHO'] = True
engine = create_engine('mysql+pymysql://root:test1234@database-1.cls1yuqwbwzq.us-east-2.rds.amazonaws.com:3306/MyFlaskApp', echo=True)

db = SQLAlchemy(application)

# for intial db construction
class Hurricane(db.Model):
    id = db.Column(db.Integer, primary_key =True)
    identifier = db.Column(db.String(20))
    name = db.Column(db.String(50))
    num_pts = db.Column(db.Integer)
    datetime = db.Column(db.DateTime)
    record_id = db.Column(db.String(10))
    status = db.Column(db.String(5))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    max_wind = db.Column(db.Float)
    min_pressure = db.Column(db.Float)
    ne34ktr = db.Column(db.Float)
    se34ktr = db.Column(db.Float)
    sw34ktr = db.Column(db.Float)
    nw34ktr = db.Column(db.Float)
    ne50ktr = db.Column(db.Float)
    se50ktr = db.Column(db.Float)
    sw50ktr = db.Column(db.Float)
    nw50ktr = db.Column(db.Float)
    ne64ktr = db.Column(db.Float)
    se64ktr = db.Column(db.Float)
    sw64ktr = db.Column(db.Float)
    nw64ktr = db.Column(db.Float)

# adds pandas DataFrame data to the database, replacing old with new data
def update_database(hurricane_data):
    hurricane_data.to_sql(
        "hurricane",
        con = engine,
        if_exists='replace',
        index = False,
        dtype= {
            "identifier": String(20),
            "name": String(50,),
            "num_pts": Integer,
            "datetime": DateTime,
            "record_id": String(10),
            "status": String(5),
            "latitude": Float,
            "longitude": Float,
            "max_wind": Float,
            "min_pressure": Float,
            "ne34ktr": Float,
            "se34ktr": Float,
            "sw34ktr": Float,
            "nw34ktr": Float,
            "ne50ktr": Float,
            "se50ktr": Float,
            "sw50ktr": Float,
            "nw50ktr": Float,
            "ne64ktr": Float,
            "se64ktr": Float,
            "sw64ktr": Float,
            "nw64ktr": Float
        }
    )


geolocator = Nominatim(user_agent="new_user")

#this_country = geopandas.read_file("data/gz_2010_us_040_00_5m.json")

@application.route('/update')
def update():
    return render_template('update.html')


@application.route('/', methods=['GET', 'POST'])
def index():
    raw_hurricane_data_from_sql = pd.read_sql_table(
        'hurricane',
        con=engine
    )
    hurricane_data_from_sql = raw_hurricane_data_from_sql[['identifier', 'name', 'num_pts', 'datetime', 'status', 'latitude', 'longitude']]

    if (hurricane_data_from_sql.empty and request.args.get('data_url')== None):
        return redirect('/update')
    elif hurricane_data_from_sql.empty:
        hurricane_data_url = request.args.get('data_url')
        hurricane_data = clean(hurricane_data_url)
        update_database(hurricane_data)
        return "<h1>Data loaded</h1>"
    elif request.method == 'POST' :   
        
        #validate and get location
        location = geolocator.geocode(request.form['location']) 
        
        if not location:
            flash('Invalid Address - enter coordinates, address with city or just city', 'error')
            return render_template('index.html')
            
        # validate and get radius    
        if not request.form['radius'].isnumeric():
           flash('please enter a number for radius', 'error') 
           return render_template('index.html')
        radius = (float(request.form['radius'])/69)
        
        impact = float(request.form['impact'])
        
        my_prediction = Prediction(hurricane_data_from_sql, location, radius, impact)

        return render_template('/analysis.html', prediction = my_prediction)
    else:
        return render_template('/index.html')
if __name__ == '__main__':
    application.secret_key="password123"
    application.run(host="0.0.0.0", port=8080, debug=True)
    #app.run()    
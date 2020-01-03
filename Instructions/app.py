import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
# engine = create_engine("sqlite:///titanic.sqlite")
engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
# Passenger = Base.classes.passenger
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' 
# and return the minimum, average, and maximum temperatures for that range of dates
def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

first_date = session.query(Measurement.date).order_by(Measurement.date).first().date
first_date

last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
last_date


def calc_temps(start_date, end_date):
    """TMIN, TAVG, and TMAX for a list of dates.
    
    Args:
        start_date (string): A date string in the format %Y-%m-%d
        end_date (string): A date string in the format %Y-%m-%d
        
    Returns:
        TMIN, TAVE, and TMAX
    """
    
    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()


#################################################
# Flask Setup
#################################################
app = Flask(__name__)

start_date = input("When are you starting your trip (date format of YYYY-MM-DD)? ")
end_date_question = input("Do you have an end date (y/n)?")
if end_date_question == 'y':
    end_date = input("When are you ending your trip (date format of YYYY-MM-DD)? ")
else:
    end_date = last_date
#Flask routes

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/{start_date}<br/>"
        f"/api/v1.0/{start_date}/{end_date}"
    )

## /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    """return a list of the dates and precipitation from the last year"""
# Convert the query results to a Dictionary using date as the key and prcp as the value.
# Return the JSON representation of your dictionary.
# Query for the dates and precipitation from the last year.
    results = session.query(Measurement.date, Measurement.prcp).all()

# Convert the query results to a Dictionary using date as the key 
# and prcp as the value.
    precipitations = []
    for date, prcp in results:
        row = {}
        row["date"] = date
        row["prcp"] = prcp
        precipitations.append(row)

    return jsonify(precipitations)

## /api/v1.0/stations
@app.route("/api/v1.0/stations")
# Return a json list of stations from the dataset.
def stations():
    """Return a list of stations """
    #Query all stations
    results = session.query(Station.station, Station.name).all()

    #Convert list of tuples into normal list
    all_stations = []
    for station, name in results:
        row = {}
        row["station"] = station
        row["name"] = name
        all_stations.append(row)

    return jsonify(all_stations)


## /api/v1.0/tobs
@app.route("/api/v1.0/tobs")
def temperature():
    """return a list of temperatures from the last year"""
# Return a json list of Temperature Observations (tobs) for the 
# previous year
# Query for the dates and temperatures from the last year.
    results = session.query(Measurement.tobs, Measurement.date).\
    filter(Measurement.date <= last_date).\
    order_by(Measurement.date).all()
# Convert the query results to a Dictionary using date as the key and prcp as the value.
    temperatures = []
    for tobs, date in results:
        row = {}
        row["date"] = date
        row["temp"] = tobs
        temperatures.append(row)

    return jsonify(temperatures)

@app.route(f"/api/v1.0/{start_date}")
def starting():
    trip_results = calc_temps(start_date, last_date)
    # trip_results = calc_temps('2015-04-15', last_date)
    trip_results
# Convert the query results to a Dictionary using date as the key and prcp as the value.
    start_avg = []
    for tmin, tavg, tmax in trip_results:
        row = {}
        row["Min"] = tmin
        row["Avg"] = tavg
        row["Max"] = tmax
        start_avg.append(row)

    return jsonify(start_avg) 

@app.route(f"/api/v1.0/{start_date}/{end_date}")
def range():
    trip_results2 = calc_temps(start_date, end_date)
    trip_results2
# Convert the query results to a Dictionary using date as the key and prcp as the value.
    trip_avg = []
    for tmin, tavg, tmax in trip_results2:
        row = {}
        row["Min"] = tmin
        row["Avg"] = tavg
        row["Max"] = tmax
        trip_avg.append(row)

    return jsonify(trip_avg) 

if __name__ == '__main__':
    app.run(debug=True)
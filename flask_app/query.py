import numpy as np

import datetime as dt
from datetime import date, timedelta

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station
#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Welcome to the Neto's vacation weather explorer for Hawaii<br/>"
        f"Available routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"Please write start and end dates in format YYYY-MM-DD<br>"
        f"/api/v1.0/start/<start><br/>"
        f"/api/v1.0/start/<start>/end/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of precipitation data per date"""
    # Find the last date recorded
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    # last_date

    # Calculate the date 1 year ago from the last data point in the database
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d')-dt.timedelta(days=365)
    
    # Perform a query to retrieve the data and precipitation scores
    prcp_results = session.query(Measurement.date, func.avg(Measurement.prcp)).\
                    filter(Measurement.date >= last_year).\
                    group_by(Measurement.date).all()

    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    prcp_date = []
    for prcp in prcp_results:
        prcp_dict = {}
        prcp_dict["date"] = prcp
        prcp_date.append(prcp_dict)

    return jsonify(prcp_date)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of all stations"""
    # Query all passengers
    stations = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature data per date"""
    # Find the last date recorded
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first().date
    # last_date

    # Calculate the date 1 year ago from the last data point in the database
    last_year = dt.datetime.strptime(last_date, '%Y-%m-%d')-dt.timedelta(days=365)
    
    # List the stations and the counts in descending order.
    most_active = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).\
        order_by(func.count(Measurement.station).desc()).first()

    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram
    tobs_results = session.query(Measurement.date, func.avg(Measurement.tobs)).\
                    filter(Measurement.station == most_active[0]).\
                    filter(Measurement.date >= last_year).\
                    group_by(Measurement.date).all()
        
    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    tobs_date = []
    for tobs in tobs_results:
        tobs_dict = {}
        tobs_dict["date"] = tobs
        tobs_date.append(tobs_dict)

    return jsonify(tobs_date)

@app.route("/api/v1.0/start/<start>")
def start_(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature data from start date"""
    start_date = start
    temps = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).all()
        
    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    start_temp = []
    for tmin, tavg, tmax in temps:
        start_dict = {}
        start_dict["date"] = tmin, tavg, tmax
        start_temp.append(start_dict)

    return jsonify(start_temp)

@app.route("/api/v1.0/start/<start>/end/<end>")
def end_(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of temperature data from start date to end date"""
    start_date = start
    end_date = end
    tempe = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
            filter(Measurement.date >= start).filter(Measurement.date <= end_date).all()
        
    session.close()

    # Create a dictionary from the row data and append to a list of precipitation
    end_temp = []
    for tmin, tavg, tmax in tempe:
        end_dict = {}
        end_dict["date"] = tmin, tavg, tmax
        end_temp.append(end_dict)

    return jsonify(end_temp)

if __name__ == '__main__':
    app.run(debug=True)

import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify, request


import datetime as dt


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

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
        f"Welcome to the Hawaii Temp API<br/>"
        "<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/startdate<br/>"
        f"/api/v1.0/start-end"
    )



@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)

    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    precip_last_year= session.query(Measurement.date, Measurement.prcp).\
                        filter(Measurement.date >= prior_year).all()

    session.close()

    precip_last_12 = []
    for date, prcp in precip_last_year:
        precip_dict = {}
        precip_dict["date"]= date 
        precip_dict["prcp"] = prcp
        precip_last_12.append(precip_dict)

    return jsonify(precip_last_12)




@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    station_list= session.query(Station.station).all()

    session.close()

    station_list = list(np.ravel(station_list))

    return jsonify(station_list)




@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    prior_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    most_active_station= session.query(Measurement.station).\
                        group_by(Measurement.station).\
                        order_by(func.count(Measurement.station).desc()).first()

    
    most_active_info = session.query(Measurement.date, Measurement.tobs).\
                        filter(Measurement.station == most_active_station[0]).\
                            filter(Measurement.date >= prior_year).all()
    
    session.close()

    most_active_temps = []
    for date, tobs in most_active_info: 
        temp_dict={}
        temp_dict["date"] = date 
        temp_dict["tobs"] = tobs 
        most_active_temps.append(temp_dict)

    
    most_active_info = list(np.ravel(most_active_info))

    return jsonify(most_active_info)



@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    start = '2017-02-01'

    temp_query1 = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                    filter(Measurement.date >=start).all()
    
    session.close

    temp_start = []
    for min, max, avg in temp_query:
        temp_start_dict= {}
        temp_start_dict["min_temp"] = min 
        temp_start_dict["max_temp"] = max 
        temp_start_dict["avg_temp"] = avg 

        temp_start.append(temp_start_dict)
    
    return jsonify(temp_start)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    session = Session(engine)

    start = '2016-02-01'
    end = '2017-03-15'

    temp_query2 = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
                    filter(Measurement.date >=start).filter(Measurement.date < end).all()

    session.close

    temp_start_end = []
    for min, max, avg in temp_query2:
        temp_start_dict= {}
        temp_start_dict["min_temp"] = min 
        temp_start_dict["max_temp"] = max 
        temp_start_dict["avg_temp"] = avg 

        temp_start_end.append(temp_start_dict)
    
    return jsonify(temp_start_end)


if __name__ == '__main__':
    app.run(debug=True)
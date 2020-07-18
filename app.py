# import modules
import flask
from flask import Flask, jsonify
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime
from datetime import date, timedelta
from sqlalchemy.ext.automap import automap_base
import numpy as np
import sqlalchemy


import pandas as pd

# Set Up Database-- How to do this?? set up sqlite db with existing 
engine = create_engine("sqlite:///Resources/hawaii.sqlite") 
# reflect database into new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# save reference to classes in the tables:
Measurement = Base.classes.measurement
Station = Base.classes.station

# create API content
app = Flask (__name__)

# define home route
@app.route("/")
def home():
    print("Welcome to the Hawaii API:")
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<start><br/>"
        f"/api/v1.0/start<start>/end<end>"
        )
  
# define other routes  
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Perform a query to retrieve the date and precipitation scores
    prcp_date = session.query(Measurement.prcp, Measurement.date).all()
    # close session
    session.close()
    # Save the query results as a Pandas DataFrame and set the index to the date column
    df = pd.DataFrame(prcp_date, columns=['Precipitation', 'Dates'])
    df.set_index(['Dates'], inplace=True)
    # Sort the dataframe by date nad get rid of empty rows
    df.sort_index(inplace=True)
    df2=df.dropna()
    # Convert to dict
    rainfall=df2.to_dict()
    return jsonify(rainfall)
    
@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # perform query
    stn=session.query(Station.station).all()
    station=list(np.ravel(stn))
    # close session
    session.close()
    # return information
    return jsonify(station)
    

@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # Query the last 12 months of temperature observation data for this station and plot the results as a histogram:\n",
    sel = [Measurement.station, func.count(Measurement.tobs)]
    num_obs=func.count(Measurement.tobs)
    # Last Data point in database
    lst_dt= session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    lst_dt= datetime.strptime(lst_dt, "%Y-%m-%d")
    strt_dt= lst_dt -timedelta(days=365)
    tmp_obs_rank=session.query(*sel).filter(Measurement.date>=strt_dt).group_by(Measurement.station).order_by(num_obs.desc()).all()
    most_tmp_obs=tmp_obs_rank[0][0]
    yr_tmp=session.query(Measurement.date, Measurement.tobs).filter(Measurement.station==most_tmp_obs).filter(Measurement.date>=strt_dt).all()
    df = pd.DataFrame(yr_tmp, columns=['Dates', 'Temperature'])
    df.set_index(['Dates'], inplace=True) 
    temps=df.to_dict()   
    # close session
    session.close()
    # return information
    return jsonify(temps)

@app.route("/api/v1.0/start/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # perform query
    sel=[func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    result=session.query(*sel).filter(Measurement.date>=start).all()
    # close session
    session.close()
    results=list(np.ravel(result))
    # return information
    return jsonify(results)
    
@app.route("/api/v1.0/start/<start>/end/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # perform query
    sel=[func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    result=session.query(*sel).filter(Measurement.date>=start).filter(Measurement.date<=end).all()
       # close session
    session.close()
    # unpack result
    results=list(np.ravel(result))
    # return information
    return jsonify(results)

# to run program 
if __name__ == "__main__":
    app.run(debug=True)
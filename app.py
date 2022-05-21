from weakref import CallableProxyType
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import json
from flask import Flask, jsonify, render_template

engine = create_engine("sqlite:///Resources/california_housing.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)
Seasonal=Base.classes.seasonal_housing
CaCounty=Base.classes.ca_county_data
CaHousing=Base.classes.california_housing


app = Flask(__name__)


@app.route("/")
def welcome():
    return render_template("index.html")
    
@app.route("/map")
def map():
    return render_template("map.html")

@app.route("/history")
def history():
    return render_template("history.html")

@app.route("/covid")
def covid():
    return render_template("covid.html")


@app.route("/api/v1.0/seasonal")
def seasonal():

    session=Session(engine)
    results=session.query(*[Seasonal.Month,Seasonal.Number_Sold,Seasonal.Pending_Sales, Seasonal.Inventory]).all()
    session.close()

    seasonal=[]
    for month, number_sold, pending_sales, inventory in results:
        seasonal_df={}
        seasonal_df['Month']=month
        seasonal_df['Number_Sold']=number_sold
        seasonal_df['Pending_Sales']=pending_sales
        seasonal_df['Inventory']=inventory
        seasonal.append(seasonal_df)

    return jsonify(seasonal)

@app.route("/api/v1.0/county")
def county():

    session=Session(engine)
    results=session.query(*[CaCounty.Year,CaCounty.County,CaCounty.Property_type, CaCounty.mean_inventory, CaCounty.Median_sales_price]).all()
    session.close()

    counties=[]
    for year, county, property, inventory, SalesPrice in results:
        county_df={}
        county_df['Year']=year
        county_df['County']=county
        county_df['Property_type']=property
        county_df['mean_inventory']=inventory
        county_df['median_sales_price']=SalesPrice
        counties.append(county_df)

    return jsonify(counties)

@app.route("/api/v1.0/CaHousing")
def Ca():

    session=Session(engine)
    results=session.query(*[CaHousing.Year,CaHousing.Month,CaHousing.region,CaHousing.state_code,CaHousing.property_type, CaHousing.median_sale_price,CaHousing.median_list_price,CaHousing.median_ppsf,CaHousing.homes_sold,CaHousing.pending_sales,CaHousing.new_listings,CaHousing.inventory,CaHousing.median_dom,CaHousing.avg_sale_to_list,CaHousing.sold_above_list,CaHousing.off_market_in_two_weeks]).all()
    session.close()

    regions=[]
    for year, month, region, state, property, SalePrice, ListPrice, Ppsf, HomeSold, PendingSales, NewListing, Inventory, Dom, SaleToList, SoldAbove, OffMarket in results:
        Ca_df={}
        Ca_df['Year']=year
        Ca_df['month']=month
        Ca_df['region']=region
        Ca_df['state_code']=state
        Ca_df['property_type']=property
        Ca_df['median_sale_price']=SalePrice
        Ca_df['median_list_price']=ListPrice
        Ca_df['median_ppsf']=Ppsf
        Ca_df['homes_sold']=HomeSold
        Ca_df['pending_sale']=PendingSales
        Ca_df['new_listings']=NewListing
        Ca_df['inventory']=Inventory
        Ca_df['median_dom']=Dom
        Ca_df['avg_sale_to_list']=SaleToList
        Ca_df['off_market_in_two_weeks']=OffMarket


       
        regions.append(Ca_df)
    return jsonify(regions)


@app.route("/ca_housing_data")
def housing():
    with open('Resources/ca_county_data2.json', 'r') as f:
        data=json.load(f)
    return jsonify(data)


   

if __name__ == '__main__':
    app.run(debug=True)
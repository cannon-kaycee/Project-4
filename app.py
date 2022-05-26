from weakref import CallableProxyType
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import json
from flask import Flask, jsonify, render_template,request
import pickle
import pandas as pd
import csv
import numpy as np
import plotly.express as px
import plotly

model = pickle.load(open('model.pkl','rb'))


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

@app.route("/predictions")
def predictions():
    return render_template("predictions.html")

@app.route('/predictions', methods=['POST'])
def predict_data():

    year = request.form['Year']
    month = request.form.get('month')
    county = request.form['County']
    house_type = request.form.get('property')
    DOM = request.form['Days']
    
    X=pd.read_csv('Resources/prediction.csv', sep=',')
    prediction_df=X[0:0]
    prediction_df.columns=prediction_df.columns.str.replace("region_", "")
    prediction_df.columns=prediction_df.columns.str.replace(" County", "")
    prediction_df.columns=prediction_df.columns.str.replace("property_type_", "")
    d={'Year': year, 'Month':month, 'median_dom':DOM, f'{county}':1, f'{house_type}':1}
    prediction_df=prediction_df.append(d, ignore_index=True)
    prediction_df=prediction_df.fillna(value=0)
    predictions = model.predict(prediction_df)
    

    years=[2018,2019,2020,2021,2022]
    sales_price2018=[]
    sales_price2019=[]
    sales_price2020=[]
    sales_price2021=[]
    sales_price2022=[]
    sales_price=[]


    ml_df=pd.read_csv('Resources/ml_modeled.csv', sep=',')
    for x, y in ml_df.iterrows():
        if  ((y[1]==2018) and (y[3]==f'{county} County')and (y[4]==house_type)):
            sales_price2018.append(y[6])
        elif ((y[1]==2019) and (y[3]==f'{county} County')and (y[4]==house_type)):
            sales_price2019.append(y[6])
        elif ((y[1]==2020) and (y[3]==f'{county} County')and (y[4]==house_type)):
            sales_price2020.append(y[6])
        elif ((y[1]==2021) and (y[3]==f'{county} County')and (y[4]==house_type)):
            sales_price2021.append(y[6])
        elif ((y[1]==2022) and (y[3]==f'{county} County')and (y[4]==house_type)):
            sales_price2022.append(y[6])
        else:
            next

    years.append(int(year))
    price2018=round(np.mean(sales_price2018),0)
    price2019=round(np.mean(sales_price2019),0)
    price2020=round(np.mean(sales_price2020),0)
    price2021=round(np.mean(sales_price2021),0) 
    price2022=round(np.mean(sales_price2022),0)
    
    sales_price.append(price2018)
    sales_price.append(price2019)
    sales_price.append(price2020)
    sales_price.append(price2021)
    sales_price.append(price2022)
    sales_price.append(predictions[0])
    price_df=pd.DataFrame({"year": years, 'sales price':sales_price})
    price_df=price_df.sort_values("year", ascending=True)

    fig=px.line(price_df, x="year", y="sales price")
    fig.update_layout(
        title=f'{county} County Sales Prices for {house_type}', title_x=0.5,
        xaxis_title="Year",
        yaxis_title="sales price",
        font=dict(
            family="Courier New, monospace",
            size=18,
    )
)

    # fig.show()
    graphJSON=json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template("predictions.html", result=f'${"{:,}".format(int(predictions[0]))}', graphJSON=graphJSON)
    

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
from flask import Flask, render_template, request, jsonify
import requests
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

# MongoDB configuration
Client = MongoClient("mongodb+srv://dhavaljigneshvasant:he88VptlB9Pr06Fg@cluster0.v2sovds.mongodb.net/Stock?ssl=true&ssl_cert_reqs=CERT_NONE")
db=Client.get_database('Stock')
collection = db.Stock


# Function to fetch data from MongoDB
def fetch_data():
    data = collection.find({}, {'_id': 0}).sort('date', 1)
    return list(data)

# Function to generate volume chart using Plotly
def generate_volume_chart():
    data = fetch_data()
    dates = []
    volumes = []

    for entry in data:
        time_series = entry.get('Time Series (Daily)')
        if time_series:
            for date, values in time_series.items():
                dates.append(date)
                volumes.append(int(values.get('5. volume', 0)))

    df = pd.DataFrame({'date': dates, 'volume': volumes})
    df['date'] = pd.to_datetime(df['date'])

    fig = px.bar(df, x='date', y='volume',
                 labels={'date': 'Date', 'volume': 'Volume'},
                 title='IBM Stock Volume')

    return fig

# Function to generate line chart using Plotly
def generate_price_chart():
    data = fetch_data()
    dates = []
    open_prices = []
    high_prices = []
    low_prices = []
    close_prices = []

    for entry in data:
        time_series = entry.get('Time Series (Daily)')
        if time_series:
            for date, values in time_series.items():
                dates.append(date)
                open_prices.append(float(values.get('1. open', 0)))
                high_prices.append(float(values.get('2. high', 0)))
                low_prices.append(float(values.get('3. low', 0)))
                close_prices.append(float(values.get('4. close', 0)))

    df = pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices
    })
    df['date'] = pd.to_datetime(df['date'])

    fig = px.line(df, x='date', y=['open', 'high', 'low', 'close'],
                  labels={'date': 'Date', 'value': 'Price'},
                  title='IBM Stock Prices')

    return fig

# Set up scheduler
scheduler = BackgroundScheduler()
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# Route to display both charts
@app.route('/we_do')
def display_charts():
    volume_chart = generate_volume_chart()
    price_chart = generate_price_chart()
    return render_template('we_do.html', volume_plot=volume_chart.to_html(), price_plot=price_chart.to_html())


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index')
def index1():
    return render_template('index.html')


@app.route('/portfolio')
def portfolio():
    return render_template('portfolio.html')


@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')


# API CREATION 


base_url = "https://jsonplaceholder.typicode.com/users"

@app.route('/api/users', methods=['GET'])
def get_users():
    try:
        response = requests.get(base_url)
        users_data = response.json()
        
        query_params = request.args
        filtered_users = []

        for user in users_data:
            if 'id' in query_params and int(query_params['id']) != user['id']:
                continue
            if 'name' in query_params and query_params['name'] != user['name']:
                continue
            if 'username' in query_params and query_params['username'] != user['username']:
                continue
            if 'email' in query_params and query_params['email'] != user['email']:
                continue
            filtered_users.append(user)
        
        return jsonify(filtered_users)

    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run()

# app.py

from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Define the MTA API endpoint and your API key
API_KEY = '03d62794-825b-44f9-8c79-f05c8ff2e324'
BASE_URL = 'http://bustime.mta.info/api/siri/stop-monitoring.json'

@app.route('/')
def index():
    return render_template('index.html', arrival_time=None)  # Initialize arrival_time to None

@app.route('/get_arrival_time', methods=['POST'])
def get_arrival_time():
    stop_id = request.form['stop_id']
    line_ref = 'MTA NYCT_B63'  # Change this to the desired bus line
    
    parameters = {
        'key': '03d62794-825b-44f9-8c79-f05c8ff2e324',
        'OperatorRef': 'MTA',
        'MonitoringRef': stop_id,
        'LineRef': line_ref
    }
    
    response = requests.get(BASE_URL, params=parameters)
    
    if response.status_code == 200:
        data = response.json()
        try:
            expected_arrival_time = data['Siri']['ServiceDelivery']['StopMonitoringDelivery'][0]['MonitoredStopVisit'][0]['MonitoredVehicleJourney']['MonitoredCall']['ExpectedArrivalTime']
            return render_template('index.html', arrival_time=expected_arrival_time)
        except KeyError:
            return render_template('index.html', error='No data available', arrival_time=None)
    else:
        return render_template('index.html', error=f'Request failed with status code {response.status_code}', arrival_time=None)


if __name__ == '__main__':
    app.run(debug=True)

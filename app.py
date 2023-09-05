from flask import Flask, render_template, request
from datetime import datetime
import requests, csv

app = Flask(__name__)

@app.route('/')
def index():
    opts = get_stops_table()
    return render_template('index.html', options=opts)

@app.route('/get-arrival-time',methods=['POST'])
def get_arrival_time():
    BASE_URL = 'http://bustime.mta.info/api/siri/stop-monitoring.json'
    API_KEY = '03d62794-825b-44f9-8c79-f05c8ff2e324'

    mr = request.form['stop']

    parameters={
        'key':API_KEY,
        'OperatorRef':'MTA',
        'MonitoringRef': mr,
    }

    # Make a GET request to the API
    response = requests.get(BASE_URL, params=parameters)

    # Check if the request was successful. If it was, print the expected arrival time
    if response.status_code == 200:

        #Get the arrival time
        data = response.json()  # Parse the JSON response
        
        #get the name of the stop
        stops=get_stops_table()
        sn = get_stop_name(stops, mr)

        '''
        expected_arrival_time = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"][0]["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"]
        parsed_datetime = datetime.fromisoformat(expected_arrival_time)
        arrival_timestamp = parsed_datetime.strftime("%H:%M")

        expected_arrival_time2 = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"][1]["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"]
        parsed_datetime2 = datetime.fromisoformat(expected_arrival_time2)
        arrival_timestamp2 = parsed_datetime2.strftime("%H:%M")

        expected_arrival_time3 = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"][2]["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"]
        parsed_datetime3 = datetime.fromisoformat(expected_arrival_time3)
        arrival_timestamp3 = parsed_datetime3.strftime("%H:%M")

        arrival_timestamp_list = [arrival_timestamp,arrival_timestamp2,arrival_timestamp3]
        '''

        monitored_stops = data["Siri"]["ServiceDelivery"]["StopMonitoringDelivery"][0]["MonitoredStopVisit"]
        arrival_data = [];

        #there is one monitored vehicle journey (MVJ) in each monitored stop element. Each monitored stop visit contains a MVJ and a recorded-at timestamp
        for i in range(len(monitored_stops)):
            row=[]
            try:
                expected_arrival_time = monitored_stops[i]["MonitoredVehicleJourney"]["MonitoredCall"]["ExpectedArrivalTime"]
                parsed_datetime = datetime.fromisoformat(expected_arrival_time)
                arrival_timestamp = parsed_datetime.strftime("%H:%M")
                dest = monitored_stops[i]["MonitoredVehicleJourney"]["DestinationName"]
                dir = monitored_stops[i]["MonitoredVehicleJourney"]["DirectionRef"]
                status = monitored_stops[i]["MonitoredVehicleJourney"]["MonitoredCall"]["Extensions"]["Distances"]["PresentableDistance"]
                row.append(i+1)
                row.append(dest)
                row.append(dir)
                row.append(status)
                row.append(arrival_timestamp)
            except Exception as e:
                print(f"An error occurred: {e}")
            arrival_data.append(row)


        return render_template('hello.html', stop_name = sn, arrivals=arrival_data)


    else:
        print(f'Error: {response.status_code}')

'''
def main():
    lr = 'MTA NYCT_B63'
    mr = '308209'
    get_arrival_time(lr,mr)
'''

def get_stops_table():
    stops = [] #[stop_id, stop_name]
    # Read Brooklyn stops
    with open('brooklyn_stops.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stops.append((row['stop_id'], row['stop_name']))

    # Read Manhattan stops
    with open('manhattan_stops.csv', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            stops.append((row['stop_id'], row['stop_name']))
    return stops

'''
Take in an 2Darray of stops, where each row is [stop_id, stop_name]
Return the name of a target stop
'''
def get_stop_name(stops, target_id):
    for i in range(len(stops)):
        if stops[i][0]==target_id:
            return stops[i][1]

if __name__ == '__main__':
    app.run(debug=True)
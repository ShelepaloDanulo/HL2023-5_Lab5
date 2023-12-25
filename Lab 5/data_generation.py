import csv
from datetime import datetime,timedelta
import numpy as np
from faker import Faker
from geopy.distance import geodesic as vincenty


def random_date(start,end):
    """Generate a random datetime between `start` and `end`"""
    random_time=start+timedelta(seconds=int(np.random.randint(low=0,high=int((end-start).total_seconds()),size=1)[0]))
    hour = np.random.choice(hours,p=probabilities)
    return random_time.replace(hour=hour)

DRIVERS_NUM=2000
CLIENTS_NUM=4000
RIDES_NUM=10000000
BATCH_SIZE=int(1e3)

TO_DATE=datetime.strptime('2020-01-01',"%Y-%m-%d")
FROM_DATE=datetime.strptime('2010-01-01',"%Y-%m-%d")

FEEDBACK_CATEGORY_DRIVER=['politeness','car','navigation']
FEEDBACK_CATEGORY_CLIENT=['politeness','communication','look']
FEEDBACK_RATE=[-1,0,1]
result_file='rides.txt'
AVG_SPEED=40

hours=[i for i in range(24)]
probabilities=[0.03,0.02,0.02,0.01,0.01,0.01,0.02,0.03,0.03,0.03,0.03,0.04,0.04,0.05,0.05,0.05,0.05,0.06,0.08,0.09,0.08,0.07,0.05,0.05]

commentsFactory=Faker()


def trip_cost(distance, start_datetime):

    base_rate = 2
    rate_per_km = 1.5

    rush_hour_multiplier = 1.5
    night_time_multiplier = 1.2
    normal_multiplier = 1.0

    rush_hours = set([7, 8, 9, 16, 17, 18])
    night_hours = set([0, 1, 2, 3, 4, 5, 23])

    hour = start_datetime.hour
    if hour in rush_hours:
        time_multiplier = rush_hour_multiplier
    elif hour in night_hours:
        time_multiplier = night_time_multiplier
    else:
        time_multiplier = normal_multiplier
    cost = (base_rate + (rate_per_km * distance)) * time_multiplier
    return cost

def main(file):
    RIDES=[]

    with open('London postcodes.csv', 'r') as postcodes:
        codes=list(csv.DictReader(postcodes, delimiter=','))
        DESTINATIONS_NUM=len(codes)

    for i in range(1,RIDES_NUM+1):
        driver_feedback=[]
        client_feedback=[]
        client_rate=0
        driver_rate=0
        if i%10000==0:
            print(str(i)+' rides')

        driver=np.random.randint(0,DRIVERS_NUM-1,1)[0]
        client=np.random.randint(0,CLIENTS_NUM-1,1)[0]

        start,end=np.random.randint(0,DESTINATIONS_NUM-1,1)[0],np.random.randint(0,DESTINATIONS_NUM-1,1)[0]
        if start==end:
            end=(end+i)%DESTINATIONS_NUM

        start_point=(float(codes[start]['Latitude']),float(codes[start]['Longitude']))
        end_point=(float(codes[end]['Latitude']),float(codes[end]['Longitude']))
        distance=float(vincenty(start_point,end_point).kilometers)

        start_datetime=random_date(FROM_DATE,TO_DATE)
        end_datetime=start_datetime+timedelta(hours=distance/AVG_SPEED)

        if i%3==0:
            driver_rate=np.random.choice(a=[i for i in range(6)],p=[0.05,0.2,0.1,0.15,0.2,0.3],size=1)[0]
            client_rate=np.random.choice(a=[i for i in range(6)],p=[0.05,0.2,0.1,0.15,0.2,0.3],size=1)[0]

        for j in range(len(FEEDBACK_CATEGORY_DRIVER)):
            feedback=0
            if i%6==0:
                feedback=np.random.choice(a=FEEDBACK_RATE,size=1)[0]
            driver_feedback.insert(j, feedback)

        for j in range(len(FEEDBACK_CATEGORY_CLIENT)):
            feedback=0
            if i%6==0:
                feedback=np.random.choice(a=FEEDBACK_RATE,size=1)[0]
            client_feedback.insert(j,feedback)

        driver_comment=commentsFactory.sentence()

        trip = {
            'driver': driver,
            'client': client,
            'start_point': start_point,
            'end_point': end_point,
            'distance': distance,
            'start_datetime': start_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            'end_datetime': end_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            'driver_rate': driver_rate,
            'driver_comment': driver_comment,
            'driver_feedback': driver_feedback,
            'client_rate': client_rate,
            'client_feedback': client_feedback,
            'cost': trip_cost(distance,start_datetime)}

        RIDES.append(trip)
        if i % BATCH_SIZE==0:
            lines='\n'.join(str(trip) for trip in RIDES)
            file.write(lines)
            if (i+BATCH_SIZE<=RIDES_NUM):
                file.write('\n')
            RIDES=[]


if __name__ == "__main__":
    with open(result_file,'w') as f:
        main(f)
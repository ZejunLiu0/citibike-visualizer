from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import psycopg2
import logging
import time

filename = time.strftime("%Y%m%d_%H%M%S", time.localtime())
logging.basicConfig(filename='./log/'+filename+'.log', level=logging.INFO)


# instantiate the app
app = Flask(__name__)
app.config.from_object(__name__)

# enable CORS
CORS(app, resources={r'/*': {'origins': '*'}})

DATE = '09/01/2016'
STOP = 'Oakland Ave'

conn = psycopg2.connect(dbname="a3db", user="a3user",
        password="password", host="127.0.0.1", port="5432")
cur = conn.cursor()


@app.route('/', methods=['GET'])
def send_data():
    if request.method == 'GET':
        with open('testdata.json', 'r') as jsonfile:
            data = json.load(jsonfile)
            # print(data)
    return jsonify(data)


@app.route('/stops', methods=['GET'])
def send_stops():
    if request.method == 'GET':
        cur.execute("SELECT * from stations")
        rows = cur.fetchall()[1:]
        data = []
        for row in rows:
            data.append({
                "stopname": row[0],
                "longitude": float(row[1]),
                "latitude": float(row[2]),
                "id": row[3]
            })
    return jsonify(data)

@app.route('/dateAndStop', methods=['POST'])
def dateAndStop():
    logging.info("User requested.")
    start = time.time()

    response_object = {'status': 'success'}
    if request.method == 'POST':
        post_data = request.get_json()
        date = post_data.get('date')
        stop = post_data.get('stop')
        hour = post_data.get('hour')
        hour_min = hour[0]
        hour_max = hour[1]

        date_cond = ''
        
        if stop is not None:
            if type(date) is list:
                logging.info('Has station, is date list.')
                date_list = []
                for d in date:
                    date_cond += "date="
                    date_cond += "'"+d.split('/')[2]+'-'+d.split('/')[1].zfill(2)+'-'+d.split('/')[0].zfill(2)+"'"
                    date_cond += " or "
                date_cond = date_cond[:-4]

                topStations = "select start_station, count(start_station) as total \
                    from bike \
                    where start_time<>'start_time' and start_station='"+str(stop)+"' and ("+date_cond+") \
                    group by start_station \
                    order by total desc;"
         
                tripDistribution = "select hour, \
                    count(hour) as total from bike\
                    where start_time<>'start_time' and start_station='"+str(stop)+"' and ("+date_cond+") \
                    group by hour order by hour asc"
            
                avgDur = "select avg(trip_duration::INTEGER) as avgDur, hour \
                    from bike \
                    where start_time<>'start_time' and start_station='"+str(stop)+"' and ("+date_cond+") \
                    group by hour order by hour asc"
            
                age = "select birth_year from bike\
                    where start_time<>'start_time' and start_station='"+str(stop)+"' and ("+date_cond+") and "+"hour::INTEGER>="+hour_min+" and "+"hour::INTEGER<"+hour_max
            
            elif len(date)==7:
                logging.info('Has station, is month')
                topStations = "select start_station, count(start_station) as total \
                    from bike \
                    where start_time<>'start_time' and start_station='"+str(stop)+"' and yearAndMonth='"+str(date)+"' \
                    group by start_station \
                    order by total desc;"

                tripDistribution = "select date, \
                    count(substring(start_time from 1 for 10)) as total from bike\
                    where start_time<>'start_time' and start_station='"+str(stop)+"' and yearAndMonth='"+str(date)+"' \
                    group by date "

                avgDur = "select avg(trip_duration::INTEGER) as avgDur, date \
                    from bike \
                    where start_time<>'start_time' and start_station='"+str(stop)+"' and yearAndMonth='"+str(date)+"' \
                    group by date"

                age = "select birth_year from bike\
                    where start_time<>'start_time' and start_station='"+str(stop)+"' and yearAndMonth='"+str(date)+"'"+" and "+"hour::INTEGER>="+hour_min+" and "+"hour::INTEGER<"+hour_max

            else:
                response_object['status'] = 'failed'
                return jsonify(response_object)
        else:
            if type(date) is list:
                logging.info('No station, is date list.')
                date_list = []
                for d in date:
                    date_cond += "date="
                    date_cond += "'"+d.split('/')[2]+'-'+d.split('/')[1].zfill(2)+'-'+d.split('/')[0].zfill(2)+"'"
                    date_cond += " or "
                date_cond = date_cond[:-4]

                topStations = "select start_station, count(start_station) as total from bike where start_time<>'start_time' and ("+date_cond+") group by start_station order by total desc" 
                
                tripDistribution = "select hour, \
                    count(hour) as total from bike\
                    where start_time<>'start_time' and ("+date_cond+")  \
                    group by hour order by hour asc"

                avgDur = "select avg(trip_duration::INTEGER) as avgDur, hour \
                    from bike \
                    where start_time<>'start_time' and ("+date_cond+")  \
                    group by hour order by hour asc"

                age = "select birth_year from bike\
                    where start_time<>'start_time' and ("+date_cond+") and "+"hour::INTEGER>="+hour_min+" and "+"hour::INTEGER<"+hour_max
                
            elif len(date)==7:
                logging.info('No station, is month')

                topStations = "select start_station, count(start_station) as total \
                    from bike \
                    where start_time<>'start_time' and yearAndMonth='"+str(date)+"' \
                    group by start_station \
                    order by total desc;"

                tripDistribution = "select date, \
                    count(date) as total from bike\
                    where start_time<>'start_time' and yearAndMonth='"+str(date)+"' \
                    group by date"

                avgDur = "select avg(trip_duration::INTEGER) as avgDur, date \
                    from bike \
                    where start_time<>'start_time' and yearAndMonth='"+str(date)+"' \
                    group by date"

                age = "select birth_year from bike\
                    where start_time<>'start_time' and yearAndMonth='"+str(date)+"'"+" and "+"hour::INTEGER>="+hour_min+" and "+"hour::INTEGER<"+hour_max

            else:
                response_object['status'] = 'failed'
                return jsonify(response_object)
        
        # print('\ntopStations:\n', topStations)
        # print('\ntripDistribution:\n', tripDistribution)
        # print('\navgDur:\n', avgDur)
        # print('\nage:\n',age)

        cur.execute(topStations)
        results = cur.fetchall()
        # print('results:',results)
        name = []
        num = []
        for r, i in zip(results, range(10)):
            name.append(r[0])
            num.append(int(r[1]))
        response_object['topStations'] = {'name':name, 'total':num}

        cur.execute(tripDistribution)
        results = cur.fetchall()
        name = []
        num = []
        for r in results:
            name.append(r[0][-2:])
            num.append(int(r[1]))
        response_object['tripDistribution'] = {'name':name, 'total':num}

        cur.execute(avgDur)
        results = cur.fetchall()
        name = []
        tripDur = []
        for r in results:
            name.append(r[1][-2:])
            tripDur.append(round(float(r[0])/60, 2))
        response_object['avgTripDur'] = {'name':name, 'avg':tripDur}

        cur.execute(age)
        results = cur.fetchall()
        agedict = {'None':0}
        for birthyear in results:
            if birthyear[0] is not None:
                age = 2019-int(float(birthyear[0]))
                key = age
                key = str(int(age/10)*10)+'-'+str(int(age/10)*10+10)
                if key not in agedict:
                    agedict[key] = 0
                agedict[key] += 1
            else:
                agedict['None'] += 1

        age = []
        num = []
        for k in agedict:
            age.append(k)
            num.append(agedict[k])
        data={'age':age, 'total':num}

        response_object['age'] = data
        response_object['message'] = 'get info '+str(DATE)+' and '+str(STOP)

    end = time.time()
    info = 'Total time: '+str(end-start)
    print(info)
    logging.info(info)

    return jsonify(response_object)

if __name__ == '__main__':
    app.run(debug=True)

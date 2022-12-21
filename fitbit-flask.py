from flask import Flask, render_template, jsonify, request, redirect, url_for
import requests

access_token = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiIyM0IzUkIiLCJzdWIiOiI4NkIzRFoiLCJpc3MiOiJGaXRiaXQiLCJ0eXAiOiJhY2Nlc3NfdG9rZW4iLCJzY29wZXMiOiJyc29jIHJzZXQgcmFjdCBybG9jIHJ3ZWkgcmhyIHJudXQgcnBybyByc2xlIiwiZXhwIjoxNjUyMTc0MzA2LCJpYXQiOjE2MjA2MzgzMDZ9.8cPCT1dXpFgYajzzKPm1_MmT1Iin_wC5pEH1IYImDus"

header = {'Authorization': 'Bearer {}'.format(access_token)}
# response = requests.get("https://api.fitbit.com/1.2/user/-/sleep/date/2020-04-02/2020-04-08.json", headers=header).json()

app = Flask(__name__)

from datetime import datetime as dt, timedelta as td
def createDateRangeDict(startdate, enddate):
    start = dt.strptime(startdate,'%Y-%m-%d')
    end = dt.strptime(enddate,'%Y-%m-%d')
    delta = end - start
    for i in range(delta.days+1):
        date = start + td(days=i)
        dict[start + td(days=i)] = date

def sleepDict(oneMonthSleep, stages):
    sleep_summaries = []
    if stages is True:
        for sleep in oneMonthSleep["sleep"]:
            if sleep["isMainSleep"] and sleep["type"] == "stages":
                sleep_summaries.append(dict(
                    date=sleep["dateOfSleep"],
                    # date=pd.to_datetime(sleep["dateOfSleep"]).date(),
                    duration_hours=sleep["duration"] / 1000 / 60 / 60,
                    total_sleep_minutes=sleep["minutesAsleep"],
                    total_time_in_bed=sleep["timeInBed"],
                    start_time=sleep["startTime"],
                    deep_minutes=sleep["levels"]["summary"].get("deep").get("minutes"),
                    light_minutes=sleep["levels"]["summary"].get("light").get("minutes"),
                    rem_minutes=sleep["levels"]["summary"].get("rem").get("minutes"),
                    wake_minutes=sleep["levels"]["summary"].get("wake").get("minutes"),
                ))
        return sleep_summaries
    for sleep in oneMonthSleep["sleep"]:
        if sleep["dateOfSleep"] in sleep_summaries:
            sleep_summaries.append(dict(
                date=sleep["dateOfSleep"],
                duration_hours=sleep["duration"] / 1000 / 60 / 60,
                total_sleep_minutes=sleep["minutesAsleep"],
                total_time_in_bed=sleep["timeInBed"],
                start_time=sleep["startTime"]
            ))
        else:
            sleep_summaries.append(dict(
                date=sleep["dateOfSleep"],
                duration_hours=sleep["duration"] / 1000 / 60 / 60,
                total_sleep_minutes=sleep["minutesAsleep"],
                total_time_in_bed=sleep["timeInBed"],
                start_time=sleep["startTime"]
            ))
    return sleep_summaries


def heartDict(hr_data):
    hr_summaries = []
    for data in hr_data["activities-heart"]:
        hr_summaries.append(dict(
            date=data["dateTime"],
            resting_hr=data["value"]["restingHeartRate"]
            # data["value"]["heartRateZones"].get("minutes"),

        ))
    return hr_summaries


def caloriesDict(calories_data):
    cal_summaries = []
    for data in calories_data["activities-calories"]:
        cal_summaries.append(dict(
            date=data["dateTime"],
            cal_amt=data["value"]
            # data["value"]["heartRateZones"].get("minutes"),

        ))
    return cal_summaries


def stepDict(steps_data):
    steps_summaries = []
    for data in steps_data["activities-steps"]:
        steps_summaries.append(dict(
            date=data["dateTime"],
            steps=data['value']
            # data["value"]["heartRateZones"].get("minutes"),

        ))
    return steps_summaries


def getSleep(startdate, enddate):
    url = 'https://api.fitbit.com/1.2/user/-/sleep/date/' + startdate + '/' + enddate + '.json'
    response = requests.get(url, headers=header).json()
    return response


def getHeartRate(startdate, enddate):
    url = 'https://api.fitbit.com/1/user/-/activities/heart/date/' + startdate + '/' + enddate + '.json'
    response = requests.get(url, headers=header).json()
    return response


def getcalories(startdate, enddate):
    url = 'https://api.fitbit.com/1/user/-/activities/calories/date/' + startdate + '/' + enddate + '.json'
    response = requests.get(url, headers=header).json()
    return response


def getSteps(startdate, enddate):
    url = 'https://api.fitbit.com/1/user/-/activities/steps/date/' + startdate + '/' + enddate + '.json'
    response = requests.get(url, headers=header).json()
    return response


@app.route('/', methods=['GET', 'POST'])
def date():
    if request.method == 'POST':
        startdate = request.form.get('startdate')
        # print(startdate)
        enddate = request.form.get('enddate')
        # print(enddate)
        # print(request.form)
        return redirect(url_for('display_dashboard', startdate=startdate, enddate=enddate))
    else:
        return render_template('date.html')


@app.route('/dashboard/')
def display_dashboard(startdate='2021-04-01', enddate='2021-05-10'):
#def display_dashboard():
    dates = request.args.to_dict()
    print(dates)
    startdate = dates['startdate']
    enddate = dates['enddate']
    response = getHeartRate(startdate, enddate)
    hr_summary = heartDict(response)
    hr_date = [i['date'] for i in hr_summary]
    hr_rhr = [i['resting_hr'] for i in hr_summary]
    response = getSleep(startdate, enddate)
    sleep_summary = sleepDict(response, stages=False)
    sleep_date = [i['date'] for i in sleep_summary]
    sleep_hours = [i['duration_hours'] for i in sleep_summary]
    hr_sleep_hours = [i * 10 for i in sleep_hours]
    sleep_summary = sleepDict(response, stages=True)
    print(sleep_summary)
    sleep_date_stages = [i['date'] for i in sleep_summary]
    sleep_deep = [i['deep_minutes'] for i in sleep_summary]
    sleep_rem = [i['rem_minutes'] for i in sleep_summary]
    sleep_light = [i['light_minutes'] for i in sleep_summary]
    sleep_wake = [i['wake_minutes'] for i in sleep_summary]
    response = getSteps(startdate, enddate)
    steps_summary = stepDict(response)
    steps_date = [i['date'] for i in steps_summary]
    no_steps = [i['steps'] for i in steps_summary]
    return render_template('dashboard.html', hr_date=hr_date, hr_rhr=hr_rhr,
                           hr_sleep_hours=hr_sleep_hours,
                           sleep_date=sleep_date, sleep_hours=sleep_hours,
                           steps_date=steps_date, no_steps=no_steps,
                           sleep_date_stages=sleep_date_stages,
                           sleep_deep=sleep_deep, sleep_rem=sleep_rem,
                           sleep_light=sleep_light, sleep_wake=sleep_wake)


@app.route('/sleeprhr/')
def display_sleeprhr(startdate='2021-04-01', enddate='2021-05-10'):
    url = 'https://api.fitbit.com/1/user/-/activities/heart/date/' + startdate + '/' + enddate + '.json'
    response = requests.get(url, headers=header).json()
    hr_summary = heartDict(response)
    hr_date = [i['date'] for i in hr_summary]
    hr_rhr = [i['resting_hr'] for i in hr_summary]
    url = 'https://api.fitbit.com/1.2/user/-/sleep/date/' + startdate + '/' + enddate + '.json'
    response = requests.get(url, headers=header).json()
    sleep_summary = sleepDict(response, stages=False)
    sleep_date = [i['date'] for i in sleep_summary]
    sleep_hours = [i['duration_hours'] for i in sleep_summary]
    return render_template('sleep_hr_chart.html', hr_date=hr_date, sleep_date=sleep_date,
                           hr_rhr=hr_rhr, sleep_hours=sleep_hours)


@app.route('/sleep/')
def display_sleep(startdate='2021-04-01', enddate='2021-05-10'):
    # startdate = '2021-04-01', enddate = '2021-05-10'
    # oneMonthSleep = getsleep(start_date, end_date)
    url = 'https://api.fitbit.com/1.2/user/-/sleep/date/' + startdate + '/' + enddate + '.json'
    response = requests.get(url, headers=header).json()
    sleep_summary = sleepDict(response, stages=False)
    sleep_date = [i['date'] for i in sleep_summary]
    sleep_hours = [i['duration_hours'] for i in sleep_summary]
    return render_template('sleep_chart.html', sleep_date=sleep_date, sleep_hours=sleep_hours)


@app.route('/calories/')
def display_calories(startdate='2021-04-01', enddate='2021-05-10'):
    # startdate = '2021-04-01', enddate = '2021-05-10'
    # oneMonthSleep = getsleep(start_date, end_date)
    response = getcalories(startdate, enddate)
    # print(response)
    calories_summary = caloriesDict(response)
    calories_date = [i['date'] for i in calories_summary]
    calories_burned = [i['cal_amt'] for i in calories_summary]
    return render_template('calories_chart.html', calories_date=calories_date, calories_burned=calories_burned)


@app.route('/sleep_stages/')
def display_sleep_stages(startdate='2021-04-01', enddate='2021-05-10'):
    url = 'https://api.fitbit.com/1.2/user/-/sleep/date/' + startdate + '/' + enddate + '.json'
    response = requests.get(url, headers=header).json()
    sleep_summary = sleepDict(response, stages=True)
    sleep_date = [i['date'] for i in sleep_summary]
    sleep_deep = [i['deep_minutes'] for i in sleep_summary]
    sleep_rem = [i['rem_minutes'] for i in sleep_summary]
    sleep_light = [i['light_minutes'] for i in sleep_summary]
    sleep_wake = [i['wake_minutes'] for i in sleep_summary]
    return render_template('sleep_stages_chart.html', sleep_date=sleep_date, sleep_deep=sleep_deep,
                           sleep_rem=sleep_rem, sleep_light=sleep_light, sleep_wake=sleep_wake)


@app.route('/rhr/')
def display_rhr(startdate='2021-04-01', enddate='2021-05-10'):
    url = 'https://api.fitbit.com/1/user/-/activities/heart/date/' + startdate + '/' + enddate + '.json'
    response = requests.get(url, headers=header).json()
    hr_summary = heartDict(response)
    hr_date = [i['date'] for i in hr_summary]
    hr_rhr = [i['resting_hr'] for i in hr_summary]
    return render_template('hr_chart.html', hr_date=hr_date, hr_rhr=hr_rhr)


@app.route('/steps/')
def display_steps(startdate='2021-04-01', enddate='2021-05-10'):
    url = 'https://api.fitbit.com/1/user/-/activities/steps/date/' + startdate + '/' + enddate + '.json'
    response = requests.get(url, headers=header).json()
    steps_summary = stepDict(response)
    steps_date = [i['date'] for i in steps_summary]
    no_steps = [i['steps'] for i in steps_summary]
    return render_template('steps_chart.html', steps_date=steps_date, no_steps=no_steps)


if __name__ == '__main__':
    app.debug = True
    app.run(host="localhost", port=6000, debug=True)

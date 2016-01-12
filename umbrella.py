#!/usr/bin/python3

import json
import requests
from twilio.rest import TwilioRestClient
import datetime
from settings import settings


TWILIO_ACCOUNT_SID = settings['TWILIO_ACCOUNT_SID']
TWILIO_AUTH_TOKEN  = settings['TWILIO_AUTH_TOKEN']
OPEN_WEATHER_API_KEY = settings['OPEN_WEATHER_API_KEY']
CITY_ID = settings['CITY_ID']
TWILIO_FROM_NUMBER = settings['TWILIO_FROM_NUMBER']
NUMBERS_TO_TEXT = settings['NUMBERS_TO_TEXT']
CONDITIONS = set()
RAIN_WORDS = ['rain', 'drizzle', 'thunderstorm']


def send_message(body):
    """
    Sends an SMS message with body to each of the phone numbers in the
    NUMBERS_TO_TEXT list.
    :param body: the body or payload of the SMS message
    :return: returns the sid numbers twilio generates
    """
    client = TwilioRestClient(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    sids = []
    for n in NUMBERS_TO_TEXT:
        message = client.messages.create(body=body, to=n, from_=TWILIO_FROM_NUMBER)
        sids.append(message.sid)
    return sids


def it_will_rain(date=None):
    """
    Builds the url, makes the request to the weather API and parses the response
    to see if it calls for rain. The conditions are added to the CONDITIONS set.
    :param date: if provided, checks for rain on given day, otherwises uses today.
    :return: Boolean
    """
    if not date:
        today = datetime.date.today().isoformat()
    else:
        today = date
    base_url = 'http://api.openweathermap.org/'
    url_path = 'data/2.5/forecast/city'
    q_string = '?id={}&APPID={}'.format(CITY_ID, OPEN_WEATHER_API_KEY)
    full_url = '{}{}{}'.format(base_url, url_path, q_string)

    res = requests.get(full_url).json()

    for forecast in res['list']:
        if not forecast['dt_txt'].startswith(today):
            break
        for word in RAIN_WORDS:
            for weather_info in forecast['weather']:
                if word in weather_info['description']:
                    CONDITIONS.add(weather_info['description'])

    return len(CONDITIONS) != 0


def check_and_text():
    if it_will_rain():
        body = "Pack an umbrella!\n\nThe forecast calls for {}.".format(
            " and ".join(list(CONDITIONS)))
        send_message(body)


if __name__ == "__main__":
    check_and_text()




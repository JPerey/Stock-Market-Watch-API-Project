import requests
from datetime import datetime
import os
from twilio.rest import Client

API_KEY = os.environ.get("AV_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
TWILIO_SID = os.environ.get("TWILIO_SID")
TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN")
TWILIO_PHONE = os.environ.get("TWILIO_PHONE")

STOCK_NAME = "TSLA"

# Functions

def get_current_date():
    current_date_data = str(datetime.now())
    print(f"current date: {current_date_data}")
    current_split = current_date_data.split()
    current_date = current_split[0]
    print(f"current date: {current_date}")
    return current_date


def get_stocks_closing() -> []:
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY_' \
          f'ADJUSTED&symbol={STOCK_NAME}&apikey={API_KEY}'
    r = requests.get(url)
    r.raise_for_status()
    data = r.json()["Time Series (Daily)"]
    closing_prices = [value['4. close'] for (key, value) in data.items()]
    print(f"closing prices: {closing_prices}")

    return closing_prices


def get_specific_closing_prices(dates_to_check):
    dates_to_check1 = dates_to_check[0]
    dates_to_check2 = dates_to_check[1]
    return dates_to_check1, dates_to_check2


def stock_price_difference(day1, day2):
    price_dif = float(day1) - float(day2)
    percentage_dif = abs(price_dif / float(day2))
    print(f"percentage dif: {percentage_dif}")
    return percentage_dif


def get_news(current_date_result):
    url = f"https://newsapi.org/v2/everything?q={STOCK_NAME}&from={current_date_result}&language=en&sortBy" \
          f"=publishedAt&apiKey={NEWS_API_KEY}"

    r = requests.get(url)
    r.raise_for_status()
    data = r.json()["articles"][:3]
    data_sources = [article["source"]["name"] for article in data]
    data_titles = [article["title"] for article in data]
    data_urls = [article["url"] for article in data]

    print(data)
    print(f"sources: {data_sources}")
    print(f"article titles: {data_titles}")
    print(f"urls: {data_urls}")
    return data_sources, data_titles, data_urls


def send_messages(sources, titles, urls, stock_price_dif):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    i = 0
    for title_name in titles:
        message = client.messages \
            .create(
            body=f"{STOCK_NAME}: {stock_price_dif}\nSource: {sources[i]}Headline: \n{title_name}\nLink: {urls[i]}️",
            from_=f"{TWILIO_PHONE}",
            to='+16502191358'
        )
        i += 1
        print(message)


current_date_result = get_current_date()
closing_prices_result = get_stocks_closing()
previous_day_closing, previous_day_closing2 = get_specific_closing_prices(closing_prices_result)
stock_price_difference_result = stock_price_difference(previous_day_closing, previous_day_closing2)
# stock_price_difference_result_auto = 0.06

if stock_price_difference_result >= 0.05:
    sources, titles, urls = get_news(current_date_result)
    send_messages(sources, titles, urls, stock_price_difference_result)

import config
import requests
from twilio.rest import Client

STOCK_NAME = "TSLA"
COMPANY_NAME = "Tesla Inc"
STOCK_ENDPOINT = "https://www.alphavantage.co/query"
NEWS_ENDPOINT = "https://newsapi.org/v2/everything"
ACCOUNT_SID = "ACa7ed0198af7e3fb440305525344edd42"
AUTH_TOKEN = config.AUTH_TOKEN
PHONE_NUMBER = config.PHONE_NUMBER

stock_parameters = {
    "function": "TIME_SERIES_DAILY",
    "symbol": STOCK_NAME,
    "apikey": config.STOCK_API_KEY,
}

news_parameters = {
    "q": COMPANY_NAME,
    "apiKey": config.NEWS_API_KEY,
}

# Gets daily stock price at closing time
stock_response = requests.get(STOCK_ENDPOINT, stock_parameters)
stock_response.raise_for_status()
stock_data = stock_response.json()
yesterday_closing_price = stock_data['Time Series (Daily)']['2023-10-12']['4. close']
day_before_closing_price = stock_data['Time Series (Daily)']['2023-10-11']['4. close']

# Calculates the difference in price and percentage value
pos_difference = int(round(float(yesterday_closing_price) - float(day_before_closing_price), 0))
up_down = None
if pos_difference > 0:
    up_down = "📈"
else:
    up_down = "📉"
percentage_value = round(((float(day_before_closing_price) - float(yesterday_closing_price)) /
                          abs(float(yesterday_closing_price)) * 100), 0)

# Check if percentage value is over 5%
if abs(percentage_value) > 1:
    # Gets the 3 most recent news articles for COMPANY_NAME
    news_response = requests.get(NEWS_ENDPOINT, news_parameters)
    news_response.raise_for_status()
    news_data = news_response.json()
    most_recent_news = news_data['articles'][0:3]

    # Creates a new list and send an SMS message for each news article
    headlines = [(most_recent_news[i]['title'], most_recent_news[i]['description'])
                 for i in range(len(most_recent_news))]
    for (key, value) in headlines:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        message = client.messages \
            .create(
                body=f"{STOCK_NAME}: {up_down}{percentage_value}%\nHeadline: {key}\nBrief: {value}",
                from_='+18339622234',
                to=PHONE_NUMBER,
            )

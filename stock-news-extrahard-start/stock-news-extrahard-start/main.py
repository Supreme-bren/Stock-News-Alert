import requests
import os
from dotenv import load_dotenv
from twilio.rest import Client
load_dotenv()

API_KEY_STOCK = os.environ.get("API_KEY_STOCK")
API_KEY_NEWS = os.environ.get("API_KEY_NEWS")
ACCOUNT_SID = os.environ.get("ACCOUNT_SID")
AUTH_TOKEN = os.environ.get("AUTH_TOKEN")
STOCK = "IBM"
COMPANY_NAME = "IBM"

def get_stock():

    stock_endpoint = 'https://www.alphavantage.co/query'
    stock_parmas = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": API_KEY_STOCK
    }

    stock_response = requests.get(url=stock_endpoint, params=stock_parmas)
    stock_response.raise_for_status()
    stock_data = stock_response.json()
    daily_stock_data = stock_data["Time Series (Daily)"]
    daily_stock_data = [value for value in daily_stock_data.values()]

    for i in range(2):
        if i == 0:
            recent_stock_close = daily_stock_data[i]["4. close"]
        elif i == 1:
            previous_stock_close = daily_stock_data[i]["4. close"]
    recent_stock_close = float(recent_stock_close)
    previous_stock_close = float(previous_stock_close)

    if recent_stock_close / previous_stock_close < 1:
         stock_change = recent_stock_close / previous_stock_close
         stock_change = 1 - stock_change
         stock_percentage_change = round(stock_change*100,2)
         return stock_percentage_change, False
    else:
        stock_change = recent_stock_close / previous_stock_close
        stock_change-=1
        stock_percentage_change = round(stock_change*100,2)
        return stock_percentage_change, True

def get_news():
    news_endpoint = "https://newsapi.org/v2/everything"
    news_params = {
        "qInTitle": COMPANY_NAME,
        "sortBy": "relevancy",
        "apiKey": API_KEY_NEWS

    }
    news_response = requests.get(url=news_endpoint,params=news_params)
    news_response.raise_for_status()
    news_data = news_response.json()["articles"]
    news_articles = []
    for i in range(3):
        news_articles.append(
            {
                "title": news_data[i]["title"],
                "description": news_data[i]["description"]
            }
        )
    return news_articles


def send_message():
    (stock_price_change, increase) = get_stock()
    news_articles = get_news()
    if increase:
        client = Client(ACCOUNT_SID,AUTH_TOKEN)
        for i in range(len(news_articles)):
            message = client.messages.create(
                body=f"{STOCK} 🔼 {stock_price_change}%. "
                     f"Headline: {news_articles[i]["title"]}"
                     f"\nBrief:{news_articles[i]["description"]}",
                from_="whatsapp:+1XXXXXXXXXX",
                to="whatsapp:1XXXXXXXXXX"
            )
    elif not increase:
        client = Client(ACCOUNT_SID, AUTH_TOKEN)
        for i in range(len(news_articles)):
            message = client.messages.create(
                body=f"{STOCK} 🔻 {stock_price_change}%."
                     f"Headline: {news_articles[i]["title"]}"
                     f"\nBrief:{news_articles[i]["description"]}",
                from_="whatsapp:+1XXXXXXXXXX",
                to="whatsapp:1XXXXXXXXX"
            )

send_message()







































## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""


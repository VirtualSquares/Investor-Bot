import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime
from flask import Flask, render_template, request
import os

app = Flask(__name__)

def fetchData(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1mo")
    return data

def priceDrop(ticker):
    data = fetchData(ticker)
    peakData = data["High"].max()
    curData = data["Close"].iloc[-1]

    if ((peakData - curData) / peakData) * 100 >= 7:
        return True, data, peakData, curData
    else:
        return False, data, peakData, curData

def plotStockData(ticker, data, price1, price2, stockStatus):
    plt.figure(figsize=(10, 6))
    plt.plot(data.index, data["Close"], label='Close Price', color='blue', linewidth=2)

    if stockStatus == "yes":
        plt.axhline(price1, color='orange', linestyle='--', label=f"Purchase Price: {price1}")
        plt.axhline(price2, color='red', linestyle='--', label=f"Current Price: {price2}")
        plt.text(data.index[-1], price1 + (price1 * 0.01), f"Purchase Price: {price1}", color='orange', fontsize=10)
        plt.text(data.index[-1], price2 - (price2 * 0.01), f"Current Price: {price2}", color='red', fontsize=10)
    else:
        plt.axhline(price1, color='green', linestyle='--', label=f"Peak Price: {price1}")
        plt.axhline(price2, color='red', linestyle='--', label=f"Current Price: {price2}")
        plt.text(data.index[-1], price1 + (price1 * 0.01), f"Peak Price: {price1}", color='green', fontsize=10)
        plt.text(data.index[-1], price2 - (price2 * 0.01), f"Current Price: {price2}", color='red', fontsize=10)

    plt.title(f'{ticker} Stock Price with Current and Peak/Purchase Price', fontsize=14)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Price (USD)', fontsize=12)
    plt.xticks(rotation=45)
    plt.legend()
    plt.grid(True)
    plt.tight_layout()

    plot_path = f"{ticker}_stock_plot.png"  
    plt.savefig(os.path.join("static", plot_path))
    plt.close()

    return plot_path

def checkIfSell(ticker, purchaseDate):
    stock = yf.Ticker(ticker)
    data = stock.history(period="max")

    if purchaseDate.tzinfo is not None:
        purchaseDate = purchaseDate.replace(tzinfo=None)

    data.index = data.index.tz_localize(None)

    if purchaseDate in data.index:
        closestDate = purchaseDate
    else:
        closestDate = min(data.index, key=lambda x: abs(x - purchaseDate))

    purchaseData = data.loc[closestDate]["Close"]
    currentData = data["Close"].iloc[-1]

    gainPercent = ((currentData - purchaseData) / purchaseData) * 100

    timeDifference = (datetime.now() - purchaseDate).days

    plot_path = plotStockData(ticker, data, purchaseData, currentData, "yes")

    if gainPercent >= 7:
        statement = "Good time to sell " + stock.ticker
    else:
        statement = "Not a good time to sell " + stock.ticker

    return {
        "purchaseDate": closestDate.date(),
        "purchasePrice": purchaseData,
        "currentPrice": currentData,
        "gainPercent": gainPercent,
        "profit": currentData - purchaseData,
        "timeDifference": timeDifference,
        "plotPath": plot_path,
        "data": data,  
        "statement": statement
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/check_stock', methods=['POST'])
def check_stock():
    ticker = request.form['ticker']
    stockStatus = request.form['stockStatus']

    if stockStatus == "no":
        is_purchase, data, peakPrice, curPrice = priceDrop(ticker)
        plot_path = plotStockData(ticker, data, peakPrice, curPrice, "no")
        message = f"{ticker} is a possible purchase!" if is_purchase else f"Not a good time to buy {ticker}"
        return render_template('index.html', message=message, plot_path=plot_path)

    elif stockStatus == "yes":
        purchase_date_str = request.form['purchaseDate']
        if purchase_date_str:
            purchaseDate = datetime.strptime(purchase_date_str, "%Y-%m-%d")
            result = checkIfSell(ticker, purchaseDate)

            plot_path = plotStockData(ticker, result['data'], result['purchasePrice'], result['currentPrice'], "yes")

            return render_template('index.html', **result, plot_path=plot_path)
        else:
            return render_template('index.html', message="Please provide a valid purchase date.")

    else:
        return render_template('index.html', message="Invalid input.")

if __name__ == '__main__':
    app.run(debug=True)

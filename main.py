import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

def fetchData(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1mo")
    return data

def priceDrop(ticker):
    data = fetchData(ticker)
    peakData = data["High"].max()
    curData = data["Close"].iloc[-1]

    if ((peakData - curData) / peakData) * 100 >= 7:
        print(f"{ticker} is a possible purchase!")
        plotStockData(ticker, data, peakData, curData, "no")
        return True
    else:
        print(f"Not a good time to buy {ticker}")
        plotStockData(ticker, data, peakData, curData, "no")
        return False

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
    plt.show()

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

    # Calculate the time difference
    timeDifference = (datetime.now() - purchaseDate).days

    print("------------------------------------")
    print(f"Purchase date: {closestDate.date()}, Purchase price: {purchaseData}")
    print(f"Current price: {currentData}")
    print(f"Percent gain: {gainPercent:.2f}%")
    print("Profit per share: $", (currentData - purchaseData))

    if timeDifference > 365:
        print("You have a long-term tax gain.")
    else:
        print("You have a short-term tax gain.")

    plotStockData(ticker, data, purchaseData, currentData, "yes")

    if gainPercent >= 10:
        print(f"Good time to sell {ticker}!")
    else:
        print(f"Not a good time to sell {ticker}.")

ticker = input("Enter stock ticker: ")
stockStatus = input("Have you already bought the stock? (yes/no): ").lower()

if stockStatus == "no":
    priceDrop(ticker)

elif stockStatus == "yes":
    purchaseDate = input("Enter the purchase date (YYYY-MM-DD): ")
    purchaseDate = datetime.strptime(purchaseDate, "%Y-%m-%d")
    checkIfSell(ticker, purchaseDate)
else:
    print("Invalid input.")

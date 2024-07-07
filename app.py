from flask import Flask, render_template, request, send_file
import pandas as pd
import yfinance as yf
import os

app = Flask(__name__)


def fetch_adjusted_close(tickers, start_date=None, end_date=None):
    data = pd.DataFrame()

    for ticker in tickers:
        try:
            # Fetch data from Yahoo Finance
            ticker_data = yf.download(ticker, start=start_date, end=end_date)

            # Extract adjusted close prices
            if not ticker_data.empty:
                ticker_data = ticker_data[['Adj Close']].rename(columns={'Adj Close': ticker})
                data = pd.concat([data, ticker_data], axis=1)
            else:
                print(f"No data found for {ticker}")

        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")

    return data


def calculate_returns(tickers, start_date=None, end_date=None):
    returns_data = pd.DataFrame()

    for ticker in tickers:
        try:
            # Fetch data from Yahoo Finance
            ticker_data = yf.download(ticker, start=start_date, end=end_date)

            # Calculate daily returns
            if not ticker_data.empty:
                ticker_data['Return'] = ticker_data['Adj Close'].pct_change()
                returns_data[ticker] = ticker_data['Return']
            else:
                print(f"No data found for {ticker}")

        except Exception as e:
            print(f"Error fetching data for {ticker}: {str(e)}")

    return returns_data


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form inputs
        tickers = [ticker.strip() for ticker in request.form['tickers'].split(',')]
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        # Fetch data from Yahoo Finance
        try:
            # Fetch adjusted close prices
            adjusted_close_data = fetch_adjusted_close(tickers, start_date=start_date, end_date=end_date)

            # Fetch returns data
            returns_data = calculate_returns(tickers, start_date=start_date, end_date=end_date)

            # Check if data fetched
            if adjusted_close_data.empty or returns_data.empty:
                return render_template('index.html', error="No data found for the specified ticker(s) and date range.")

            # Prepare Excel files
            adjusted_prices_file = 'static/adjusted_prices.xlsx'
            returns_file = 'static/returns_data.xlsx'

            # Create 'static' directory if it doesn't exist
            os.makedirs('static', exist_ok=True)

            # Save data to Excel files
            with pd.ExcelWriter(adjusted_prices_file) as writer:
                adjusted_close_data.to_excel(writer, sheet_name='Adjusted Prices', index=True)
            with pd.ExcelWriter(returns_file) as writer:
                returns_data.to_excel(writer, sheet_name='Returns Data', index=True)

            # Provide download links for the user
            return render_template('index.html', adjusted_prices_file=adjusted_prices_file, returns_file=returns_file)

        except Exception as e:
            error_message = f"Error fetching data: {str(e)}"
            return render_template('index.html', error=error_message)

    # Render initial form template
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)

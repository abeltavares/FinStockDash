"""
This module provides functions for retrieving financial data from the Financial Modeling Prep and Alpha Vantage API.
"""

# Import necessary libraries
import requests
import pandas as pd
import numpy as np
import streamlit as st


FMP_API_KEY = st.secrets["FMP_API_KEY"] # replace with your Financial Modeling Prep API key
ALPHA_API_KEY = st.secrets["ALPHA_API_KEY"] # replace with your Alpha Vantage API key


def get_company_info(symbol: str) -> dict:
    """
    Returns a dictionary containing information about a company with the given stock symbol.
    
    Parameters:
        symbol (str): Stock symbol
        
    Returns:
        dict: Dictionary containing information about the company
    """
    # Set the API endpoint URL
    api_endpoint = f'https://financialmodelingprep.com/api/v3/profile/{symbol}/'
    params = {
        'apikey': FMP_API_KEY,  
    }

    try:
        # Make an HTTP GET request to the API with the specified parameters
        response = requests.get(api_endpoint, params=params)

        # Check for any errors in the HTTP response status code
        response.raise_for_status()

        # Convert the response data to a Python dictionary
        data = response.json()

        # Extract the first (and only) item from the list of company data
        data = data[0]

        # Extract the desired company information from the dictionary
        company_info = {
            'Name': data['companyName'],
            'Exchange': data['exchangeShortName'],
            'Currency': data['currency'],
            'Country': data['country'],            
            'Sector': data['sector'],
            'Market Cap':  data['mktCap'],
            'Price': data['price'],
            'Beta': data['beta'],
            'Price change': data['changes'],
            'Website': data['website'],
            'Image': data['image']
        }

        # Return the company information dictionary
        return company_info

    except requests.exceptions.RequestException as e:
        # Handle any errors that occur while making the API request
        print(f"Error occurred while fetching data from API: {e}")
        return None

    except ValueError as e:
        # Handle any errors that occur while parsing the response data
        print(f"Error occurred while parsing JSON response: {e}")
        return None


def get_stock_price(symbol: str) -> pd.DataFrame:
    """
    Returns a Pandas DataFrame containing the monthly adjusted closing prices of a given stock symbol
    for the last 5 years.
    
    Parameters:
        symbol (str): Stock symbol
        
    Returns:
        pd.DataFrame: Pandas DataFrame containing the monthly adjusted closing prices of the stock
    """
    api_endpoint = 'https://www.alphavantage.co/query'
    params = {
        'function': 'TIME_SERIES_MONTHLY_ADJUSTED',
        'symbol': symbol,  
        'apikey': ALPHA_API_KEY,  
    }

    try:
        # Make an HTTP GET request to the API
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()  # raise exception for any bad HTTP status code

        # Parse the response JSON data into a Pandas DataFrame
        data = response.json()['Monthly Adjusted Time Series']
        df = pd.DataFrame.from_dict(data, orient='index')
        df.index = pd.to_datetime(df.index)
        df = df[:12*5] # get data for the last 5 years
        df = df[['4. close']].astype(float)
        df = df.rename(columns={'4. close': 'Price'})

        return df

    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching data from API: {e}")
        return None

    except ValueError as e:
        print(f"Error occurred while parsing JSON response: {e}")
        return None


def get_income_statement(symbol: str) -> pd.DataFrame:
    """
    Retrieves the income statement data for a given stock symbol from the Financial Modeling Prep API.

    Args:
        symbol (str): The stock symbol to retrieve the income statement data for.

    Returns:
        pd.DataFrame: A Pandas DataFrame containing the income statement data.
    """
    # define the API endpoint and parameters
    api_endpoint = f'https://financialmodelingprep.com/api/v3/income-statement/{symbol}/'
    params = {
        'limit': 5,
        'apikey': FMP_API_KEY,  
    }
    try:
        # create an empty list to store the income statement data
        income_statement_data = []

        # make an HTTP GET request to the API
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()  # raise exception for any bad HTTP status code

        # parse the response JSON data into a list of dictionaries
        response_data = response.json()

        # extract the income statement data from the list of dictionaries
        for report in response_data:
            year = report['calendarYear'] 
            income_statement_data.append({
                'Year': year,
                'Revenue': (report['revenue']),
                '(-) Cost of Revenue': (report['costOfRevenue']),
                '= Gross Profit': (report['grossProfit']),
                '(-) Operating Expense': (report['operatingExpenses']),
                '= Operating Income': (report['operatingIncome']),
                '(+-) Other Income/Expenses': (report['totalOtherIncomeExpensesNet']),
                '= Income Before Tax': (report['incomeBeforeTax']),                
                '(+-) Tax Income/Expense': (report['incomeTaxExpense']),
                '= Net Income': (report['netIncome']),
            })

        # create a Pandas DataFrame from the list of dictionaries and return it
        income_statement = pd.DataFrame(income_statement_data).set_index('Year')

        return income_statement
        
    except requests.exceptions.RequestException as e:
        print(f"Error occurred while fetching data from API: {e}")
        return None

    except ValueError as e:
        print(f"Error occurred while parsing JSON response: {e}")
        return None


def get_balance_sheet(symbol: str) -> pd.DataFrame:
    """
    Retrieves the balance sheet data for a given stock symbol.

    Args:
        symbol (str): Stock symbol to retrieve balance sheet data for.

    Returns:
        pd.DataFrame: Pandas DataFrame containing the balance sheet data.
    """
    # Define the API endpoint and parameters
    api_endpoint = f'https://financialmodelingprep.com/api/v3/balance-sheet-statement/{symbol}'
    params = {
        'limit': 5,
        'apikey': FMP_API_KEY,  
    }

    try:
        # Create an empty list to store the balance sheet data
        balance_sheet_data = []

        # Make an HTTP GET request to the API
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()  # Raise exception for any bad HTTP status code

        # Parse the response JSON data into a list of dictionaries
        response_data = response.json()

        # Extract the balance sheet data from the list of dictionaries
        for report in response_data:
            year = report['calendarYear']
            balance_sheet_data.append({
                'Year': year,
                'Assets': report['totalAssets'],
                'Current Assets': report['totalCurrentAssets'],
                'Non-Current Assets': report['totalNonCurrentAssets'],
                'Current Liabilities': report['totalCurrentLiabilities'],
                'Non-Current Liabilities': report['totalNonCurrentLiabilities'],
                'Liabilities': report['totalLiabilities'],
                'Equity': report['totalEquity']
            })

        # Create a Pandas DataFrame from the list of dictionaries and return it
        balance_sheet_df = pd.DataFrame(balance_sheet_data).set_index('Year')

        return balance_sheet_df
    
    except requests.exceptions.RequestException as e:
        # If an error occurs, print the error message and return None
        print('Error getting balance sheet data:', e)
        return None
    

def get_cash_flow(symbol: str) -> pd.DataFrame:
    """
    Retrieve cash flow data for a given stock symbol from the Financial Modeling Prep API.
    
    Args:
        symbol (str): The stock symbol for the company.
    
    Returns:
        pd.DataFrame: A Pandas DataFrame containing cash flow data for the company.
    """
    # Define the API endpoint and parameters
    api_endpoint = f'https://financialmodelingprep.com/api/v3/cash-flow-statement/{symbol}'
    params = {
        'limit': 5,
        'apikey': FMP_API_KEY,  
    }
    
    try:
        # Create an empty list to store the cash flow data
        cashflow_data = []

        # Make an HTTP GET request to the API
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()  # Raise an exception for any bad HTTP status code

        # Parse the response JSON data into a list of dictionaries
        response_data = response.json()

        # Extract the cash flow data from the list of dictionaries
        for report in response_data:
            year = report['date'].split('-')[0]
            cashflow_data.append({
                'Year': year,
                "Cash flows from operating activities": report['netCashProvidedByOperatingActivities'],
                'Cash flows from investing activities': report['netCashUsedForInvestingActivites'],
                'Cash flows from financing activities': report['netCashUsedProvidedByFinancingActivities'],
                'Free cash flow': report['freeCashFlow']
            })

        # Create a Pandas DataFrame from the list of dictionaries and set the 'Year' column as the index
        cashflow_df = pd.DataFrame(cashflow_data).set_index('Year')

        return cashflow_df
    
    except requests.exceptions.RequestException as e:
        # If an error occurs, print the error message and return None
        print('Error getting cash flow data:', e)
        return None


def get_key_metrics(symbol: str) -> pd.DataFrame:
    """
    Returns a Pandas DataFrame containing the key financial metrics of a given company symbol for the last 10 years.

    Parameters:
        symbol (str): Company symbol.

    Returns:
        pd.DataFrame: Pandas DataFrame containing the key financial metrics.
    """
    # Define the API endpoint and parameters.
    api_endpoint = f'https://financialmodelingprep.com/api/v3/key-metrics/{symbol}'
    params = {
        'limit': 5,  # Get data for the last 10 years.
        'apikey': FMP_API_KEY, 
    }

    try:
        # Create an empty list to store the ratios data.
        metrics_data = []

        # Make an HTTP GET request to the API.
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()  # Raise exception for any bad HTTP status code.

        # Parse the response JSON data into a list of dictionaries.
        response_data = response.json()

        # Extract the ratios data from the list of dictionaries.
        for report in response_data:
            year = report['date'].split('-')[0]  # Extract the year from the date string.
            metrics_data.append({
                'Year': year,
                "Market Cap": report['marketCap'],
                'Working Capital': report['workingCapital'],
                'D/E ratio': report['debtToEquity'],
                'P/E Ratio': report['peRatio'],
                'ROE': report['roe'], 
                'Dividend Yield': report['dividendYield']
            })

        # Create a Pandas DataFrame from the list of dictionaries and return it.
        metrics_df = pd.DataFrame(metrics_data).set_index('Year')
        return metrics_df
    
    except requests.exceptions.RequestException as e:
        # If an error occurs, print the error message and return None.
        print(f"Error occurred while fetching data from API: {e}")
        return None


def get_financial_ratios(symbol: str) -> pd.DataFrame:
    """
    Fetches financial ratios for a given stock symbol using the Financial Modeling Prep API.

    Parameters:
    symbol (str): The stock symbol to fetch the ratios for.

    Returns:
    pandas.DataFrame: A DataFrame containing the financial ratios data.
    """

    # Define the API endpoint and parameters
    api_endpoint = f'https://financialmodelingprep.com/api/v3/ratios/{symbol}'
    params = {
        'limit': 5,
        'apikey': FMP_API_KEY, 
    }

    try:
        # Create an empty list to store the ratios data
        ratios_data = []

        # Make an HTTP GET request to the API
        response = requests.get(api_endpoint, params=params)
        response.raise_for_status()  # Raise exception for any bad HTTP status code

        # Parse the response JSON data into a list of dictionaries
        response_data = response.json()

        # Extract the ratios data from the list of dictionaries
        for report in response_data:
            year = report['date'].split('-')[0]
            ratios_data.append({
                'Year': year,
                'Current Ratio': report['currentRatio'],
                'Quick Ratio': report['quickRatio'],
                'Cash Ratio': report['cashRatio'],
                'Days of Sales Outstanding': report['daysOfSalesOutstanding'],
                'Days of Inventory Outstanding': report['daysOfInventoryOutstanding'],
                'Operating Cycle': report['operatingCycle'],
                'Days of Payables Outstanding': report['daysOfPayablesOutstanding'],
                'Cash Conversion Cycle': report['cashConversionCycle'],
                'Gross Profit Margin': report['grossProfitMargin'], 
                'Operating Profit Margin': report['operatingProfitMargin'],
                'Pretax Profit Margin': report['pretaxProfitMargin'],
                'Net Profit Margin': report['netProfitMargin'],
                'Effective Tax Rate': report['effectiveTaxRate'],
                'Return on Assets': report['returnOnAssets'],
                'Return on Equity': report['returnOnEquity'],
                'Return on Capital Employed': report['returnOnCapitalEmployed'],
                'Net Income per EBT': report['netIncomePerEBT'],
                'EBT per EBIT': report['ebtPerEbit'],
                'EBIT per Revenue': report['ebitPerRevenue'],
                'Debt Ratio': report['debtRatio'],
                'Debt Equity Ratio': report['debtEquityRatio'],
                'Long-term Debt to Capitalization': report['longTermDebtToCapitalization'],
                'Total Debt to Capitalization': report['totalDebtToCapitalization'],
                'Interest Coverage': report['interestCoverage'],
                'Cash Flow to Debt Ratio': report['cashFlowToDebtRatio'],
                'Company Equity Multiplier': report['companyEquityMultiplier'],
                'Receivables Turnover': report['receivablesTurnover'],
                'Payables Turnover': report['payablesTurnover'],
                'Inventory Turnover': report['inventoryTurnover'],
                'Fixed Asset Turnover': report['fixedAssetTurnover'],
                'Asset Turnover': report['assetTurnover'],
                'Operating Cash Flow per Share': report['operatingCashFlowPerShare'],
                'Free Cash Flow per Share': report['freeCashFlowPerShare'],
                'Cash per Share': report['cashPerShare'],
                'Payout Ratio': report['payoutRatio'],
                'Operating Cash Flow Sales Ratio': report['operatingCashFlowSalesRatio'],
                'Free Cash Flow Operating Cash Flow Ratio': report['freeCashFlowOperatingCashFlowRatio'],
                'Cash Flow Coverage Ratios': report['cashFlowCoverageRatios'],
                'Price to Book Value Ratio': report['priceToBookRatio'],
                'Price to Earnings Ratio': report['priceEarningsRatio'],
                'Price to Sales Ratio': report['priceToSalesRatio'],
                'Dividend Yield': report['dividendYield'],
                'Enterprise Value to EBITDA': report['enterpriseValueMultiple'],
                'Price to Fair Value': report['priceFairValue']
            })

        # Create a Pandas DataFrame from the list of dictionaries and return it
        ratios_df = pd.DataFrame(ratios_data).set_index('Year')

        return ratios_df

    except requests.exceptions.RequestException as e:
        # If an error occurs, print the error message and return None
        print('Error getting ratios data:', e)
        return None

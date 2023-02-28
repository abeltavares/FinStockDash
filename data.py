"""
This module provides functions for retrieving financial data from the Financial Modeling Prep and Alpha Vantage API.
"""


import requests
import pandas as pd
import numpy as np
import streamlit as st


FMP_API_KEY = 'e18f8efccbac4ac741c48162fec73d2e'  # replace with your Financial Modeling Prep API key
ALPHA_API_KEY = 'S1HB81M1BIAB0ML2'  # replace with your Alpha Vantage API key


def get_company_info(symbol: str) -> dict:
    """
    Returns a dictionary containing information about a company with the given stock symbol.
    
    Parameters:
        symbol (str): Stock symbol
        
    Returns:
        dict: Dictionary containing information about the company
    """
    # Define the API endpoint and parameters for the Alpha Vantage API
    api_endpoint = 'https://www.alphavantage.co/query'
    params = {
        'function': 'OVERVIEW',
        'symbol': symbol,  
        'apikey': ALPHA_API_KEY, 
    }

    try:
        # Make an HTTP GET request to the API with the specified parameters
        response = requests.get(api_endpoint, params=params)

        # Check for any errors in the HTTP response status code
        response.raise_for_status()

        # Convert the response data to a Python dictionary
        data = response.json()

        # Extract the desired company information from the dictionary
        company_info = {
            'Name': data.get('Name'),
            'Exchange': data.get('Exchange'),
            'Currency': data.get('Currency'),
            'Sector': data.get('Sector'),
            'Market Cap':  data.get('MarketCapitalization'),
            'P/E ratio': data.get('PERatio'),
            'Dividends (Yield)': data.get('DividendYield'),
            'Profit Margin': data.get('ProfitMargin'),
            'Beta': data.get('Beta'),
            'EPS': data.get('EPS')
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
                '(+/-) Other Income/Expenses': (report['totalOtherIncomeExpensesNet']),
                '= Income Before Tax': (report['incomeBeforeTax']),                
                '(+/-) Tax Income/Expense': (report['incomeTaxExpense']),
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
                'Current Ratio': round(report['currentRatio'], 2),
                'Quick Ratio': round(report['quickRatio'], 2),
                'Cash Ratio': round(report['cashRatio'], 2),
                'Days of Sales Outstanding': round(report['daysOfSalesOutstanding'], 2),
                'Days of Inventory Outstanding': round(report['daysOfInventoryOutstanding'], 2),
                'Operating Cycle': round(report['operatingCycle'], 2),
                'Days of Payables Outstanding': round(report['daysOfPayablesOutstanding'], 2),
                'Cash Conversion Cycle': round(report['cashConversionCycle'], 2),
                'Gross Profit Margin': report['grossProfitMargin'], 
                'Operating Profit Margin': round(report['operatingProfitMargin'], 2),
                'Pretax Profit Margin': round(report['pretaxProfitMargin'], 2),
                'Net Profit Margin': report['netProfitMargin'],
                'Effective Tax Rate': round(report['effectiveTaxRate'], 2),
                'Return on Assets': round(report['returnOnAssets'], 2),
                'Return on Equity': round(report['returnOnEquity'], 2),
                'Return on Capital Employed': round(report['returnOnCapitalEmployed'], 2),
                'Net Income per EBT': round(report['netIncomePerEBT'], 2),
                'EBT per EBIT': round(report['ebtPerEbit'], 2),
                'EBIT per Revenue': round(report['ebitPerRevenue'], 2),
                'Debt Ratio': round(report['debtRatio'], 2),
                'Debt Equity Ratio': round(report['debtEquityRatio'], 2),
                'Long-term Debt to Capitalization': round(report['longTermDebtToCapitalization'], 2),
                'Total Debt to Capitalization': round(report['totalDebtToCapitalization'], 2),
                'Interest Coverage': round(report['interestCoverage'], 2),
                'Cash Flow to Debt Ratio': round(report['cashFlowToDebtRatio'], 2),
                'Company Equity Multiplier': round(report['companyEquityMultiplier'], 2),
                'Receivables Turnover': round(report['receivablesTurnover'], 2),
                'Payables Turnover': round(report['payablesTurnover'], 2),
                'Inventory Turnover': round(report['inventoryTurnover'], 2),
                'Fixed Asset Turnover': round(report['fixedAssetTurnover'], 2),
                'Asset Turnover': round(report['assetTurnover'], 2),
                'Operating Cash Flow per Share': round(report['operatingCashFlowPerShare'], 2),
                'Free Cash Flow per Share': round(report['freeCashFlowPerShare'], 2),
                'Cash per Share': round(report['cashPerShare'], 2),
                'Payout Ratio': round(report['payoutRatio'], 2),
                'Operating Cash Flow Sales Ratio': round(report['operatingCashFlowSalesRatio'], 2),
                'Free Cash Flow Operating Cash Flow Ratio': round(report['freeCashFlowOperatingCashFlowRatio'], 2),
                'Cash Flow Coverage Ratios': round(report['cashFlowCoverageRatios'], 2),
                'Price to Book Value Ratio': round(report['priceToBookRatio'], 2),
                'Price to Earnings Ratio': round(report['priceEarningsRatio'], 2),
                'Price to Sales Ratio': round(report['priceToSalesRatio'], 2),
                'Dividend Yield': report['dividendYield'],
                'Enterprise Value to EBITDA': round(report['enterpriseValueMultiple'], 2),
                'Price to Fair Value': round(report['priceFairValue'], 2)
            })

        # Create a Pandas DataFrame from the list of dictionaries and return it
        ratios_df = pd.DataFrame(ratios_data).set_index('Year')

        return ratios_df

    except requests.exceptions.RequestException as e:
        # If an error occurs, print the error message and return None
        print('Error getting ratios data:', e)
        return None

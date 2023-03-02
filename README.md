# Financial Dashboard App
The Financial Dashboard is a web application that allows users to analyze stock data using various financial ratios, balance sheets, income statements, and other financial metrics. User can enter a stock ticker symbol to retrieve relevant financial information, view stock prices over time, and generate visualizations to gather insights on the company performance. The application makes use of APIs provided by Financial Modeling Prep and Alpha Vantage to retrieve real-time stock data.


### Requirements

To run this app locally, you will need Python 3.x installed, as well as the required libraries listed in the requirements.txt file.

### Files

- app.py: This file contains the main code for the Streamlit app. It imports functions from the data.py and utils.py files to retrieve and display financial data.
- data.py: This file contains functions for retrieving financial data from various APIs such as Financial Modeling Prep and Alpha Vantage.
- utils.py: This file contains various utility functions that are used in the main app to create menus, cards, and other display elements.


### Setup
To run the app locally, follow these steps:

1. Clone the repository: <br>

       $ git clone https://github.com/abeltavares/financial_dashboard_app.git 

2. Create and activate a virtual environment: <br>

       $ python3 -m venv venv
       $ source venv/bin/activate

3. Install the required libraries:<br>

       $ pip install -r requirements.txt

4. Create the database and schema:<br>

       $ psql -f schema_tables.sql

5. Run the app:

       $ streamlit run app.py


## Usage

1. Enter a valid stock ticker symbol in the search bar to retrieve financial data for the corresponding company. <br>
2. Use the various options provided to visualize and analyze financial data. <br>
3. Click on the "Download Data" button to download an Excel file with relevant financial information for the selected stock. <br>

## Contributions

Contributions are welcome! Please feel free to open an issue or submit a pull request.

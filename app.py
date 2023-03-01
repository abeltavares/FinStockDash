"""
This is a financial analysis application that allows users to input a stock symbol and receive various financial
metrics and visualizations for the corresponding company.
"""

# Import necessary libraries
import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from plotly.graph_objs import layout
from millify import millify
from utils import (
    config_menu_footer, generate_card, empty_lines, get_delta
)
from data import (
    get_income_statement, get_balance_sheet, get_stock_price, get_company_info,
    get_financial_ratios, get_key_metrics, get_cash_flow
)


# Define caching functions for each API call
@st.cache_data
def company_info(symbol):
    return get_company_info(symbol)

@st.cache_data
def income_statement(symbol):
    return get_income_statement(symbol)

@st.cache_data
def balance_sheet(symbol):
    return get_balance_sheet(symbol)

@st.cache_data
def stock_price(symbol):
    return get_stock_price(symbol)

@st.cache_data
def financial_ratios(symbol):
    return get_financial_ratios(symbol)

@st.cache_data
def key_metrics(symbol):
    return get_key_metrics(symbol)

@st.cache_data
def cash_flow(symbol):
    return get_cash_flow(symbol)

# Define caching function for delta
@st.cache_data
def delta(df,key):
    return get_delta(df,key)

# Initialize the state of the button as False when the app is first loaded
if 'btn_clicked' not in st.session_state:
    st.session_state['btn_clicked'] = False

# Define a callback function for when the "Go" button is clicked
def callback():
    # change state value
    st.session_state['btn_clicked'] = True

# Configure the app page
st.set_page_config(
    page_title='Financial Dashboard',
    page_icon='📈',
    layout="centered",
)

# Configure the menu and footer with the user's information
config_menu_footer('abeltavares','abeltavares','abeltavares')

# Display the app title
st.title("Financial Dashboard 📈")

# Create a text input field for the user to enter a stock ticker
symbol_input = st.text_input("Enter a stock ticker").upper()

# Check if the "Go" button has been clicked
if st.button('Go',on_click=callback) or st.session_state['btn_clicked']:
    
    # Check if the user has entered a valid ticker symbol
    if not symbol_input:
        st.warning('Please input a ticker.')
        st.stop()

    try:
        # Call the API functions to get the necessary data for the dashboard
        company_data = company_info(symbol_input)
        metrics_data = key_metrics(symbol_input)
        income_data = income_statement(symbol_input)
        performance_data = stock_price(symbol_input)
        ratios_data = financial_ratios(symbol_input)
        balance_sheet_data = balance_sheet(symbol_input)
        cashflow_data = cash_flow(symbol_input)

    except Exception as e:
        st.error('Not possible to retrieve data for that ticker. Please check if its valid and try again')
        st.error(f"An error occurred: {e}")

    # Display dashboard
    try:
        empty_lines(2)
        generate_card(company_data['Name'])

        # Define columns for the top row
        col1, col2, col3 = st.columns((2,2,2))

        # Display company info
        with col1:
            empty_lines(1)
            generate_card(company_data['Exchange'])
            empty_lines(2)

        with col2:
            empty_lines(1)
            generate_card(company_data['Currency'])
            empty_lines(2)

        with col3:
            empty_lines(1)
            # Capitalize first letter of each word in sector
            sector = company_data['Sector'].title()
            generate_card(sector)
            empty_lines(2)

        # Define columns for the bottom row
        col4, col5, col6 = st.columns((2,2,3))

        # Display key metrics  
        with col4:
            empty_lines(3)
            st.metric(label="Market Cap", value=millify(metrics_data['Market Cap'][0], precision=2), delta=delta(metrics_data,'Market Cap'))
            st.write("")
            st.metric(label="D/E Ratio", value = round(metrics_data['D/E ratio'][0],2), delta=delta(metrics_data,'D/E ratio'))
            st.write("")
            st.metric(label="ROE", value = str(round(metrics_data['ROE'][0] * 100, 2)) + '%', delta=delta(metrics_data,'ROE'))

        with col5:
            empty_lines(3)
            st.metric(label="Working Capital", value = millify(metrics_data['Working Capital'][0], precision = 2), delta=delta(metrics_data,'Working Capital'))
            st.write("")
            st.metric(label="P/E Ratio", value = round(metrics_data['P/E Ratio'][0],2), delta=delta(metrics_data,'P/E Ratio'))
            st.write("")
            st.metric(label="Dividends (yield)", value = str(round(metrics_data['Dividend Yield'][0]* 100, 2)) + '%', delta=delta(metrics_data,'Dividend Yield'))

        # Define the income statement data
        income_statement = income_data.T
        income_statement = income_statement.applymap(lambda x: millify(x, precision=2))

        # Display income statement
        with col6:
            # Add the subheader to the left column
            st.markdown('**Income Statement**')
            # Display selectbox to choose year
            year = st.selectbox('All numbers in thousands', income_statement.columns, label_visibility='visible')
            # Show the data for the selected year
            income_statement = income_statement.loc[:, [year]]
            st.dataframe(income_statement)


        # Display market performance
        # Determine the color of the line based on the first and last prices
        line_color = 'rgb(60, 179, 113)' if performance_data.iloc[0]['Price'] > performance_data.iloc[-1]['Price'] else 'rgb(255, 87, 48)'

        # Create the line chart 
        fig = go.Figure(
            go.Scatter(
                x=performance_data.index,
                y=performance_data['Price'],
                mode='lines',
                name='Price',
                line=dict(color=line_color)
            )
        )

        # Add chart title
        fig.update_layout(
            title={
                'text': 'Market Performance',
            }
        )

        # Render the line chart 
        st.plotly_chart(fig, use_container_width=True)


        # Display net income
        # Create the line chart 
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=income_data.index, 
                y=income_data["= Net Income"], 
                mode="lines+markers", 
                line=dict(
                    color="purple"), 
                    marker=dict(
                        size=5
                    )
                )
            )

        # Customize the chart layout
        fig.update_layout(
            title="Net Income",
            xaxis=dict(
                tickmode='array', 
                tickvals=income_data.index,
            )
        )

        # Display the graph
        st.plotly_chart(fig)


        # Display profitability margins
        # Create an horizontal bar chart of profitability margins
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=ratios_data.index,
            x=ratios_data['Gross Profit Margin'],
            name='Gross Profit Margin',
            marker=dict(color='rgba(60, 179, 113, 0.85)'),
            orientation='h',
        ))
        fig.add_trace(go.Bar(
            y=ratios_data.index,
            x=ratios_data['Operating Profit Margin'],
            name='EBIT Margin',
            marker=dict(color='rgba(30, 144, 255, 0.85)'),
            orientation='h',
        ))

        fig.add_trace(go.Bar(
            y=ratios_data.index,
            x=ratios_data['Net Profit Margin'],
            name='Net Profit Margin',
            marker=dict(color='rgba(173, 216, 230, 0.85)'),
            orientation='h',
        ))

        # Update layout
        fig.update_layout(
            title='Profitability Margins',
            bargap=0.1,
            xaxis=dict(tickformat='.0%')
        )

        # Display the plot 
        st.plotly_chart(fig)


        #Display balance sheet
        # Create a vertical bar chart of Assets and Liabilities
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=balance_sheet_data.index,
            y=balance_sheet_data['Assets'],
            name='Assets',
            marker=dict(color='rgba(60, 179, 113, 0.85)'),
            width=0.3,
        ))
        fig.add_trace(go.Bar(
            x=balance_sheet_data.index,
            y=balance_sheet_data['Liabilities'],
            name='Liabilities',
            marker=dict(color='rgba(255, 99, 71, 0.85)'),
            width=0.3,
        ))

        # Add a line for assets
        fig.add_trace(go.Scatter(
            x=balance_sheet_data.index,
            y=balance_sheet_data['Equity'],
            mode='lines+markers',
            name='Equity',
            line=dict(color='rgba(173, 216, 230, 1)', width=2),
            marker=dict(symbol='circle', size=8, color='rgba(173, 216, 230, 1)', line=dict(width=1, color='rgba(173, 216, 230, 1)'))
        ))

        # Update layout
        fig.update_layout(
            title='Balance Sheet',
            bargap=0.4,
        )

        # Display the plot 
        st.plotly_chart(fig)


        # Display ROE and ROA
        # Create the line chart 
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=ratios_data.index,
            y=ratios_data['Return on Equity'],
            name='ROE',
            line=dict(color='rgba(60, 179, 113, 0.85)'),
        ))
        fig.add_trace(go.Scatter(
            x=ratios_data.index,
            y=ratios_data['Return on Assets'],
            name='ROA',
            line=dict(color='rgba(30, 144, 255, 0.85)'),
        ))

        # Update layout
        fig.update_layout(
            title='ROE and ROA',
            yaxis=dict(tickformat='0%')
        )

        # Display the plot in Streamlit
        st.plotly_chart(fig)


        # Display cash flows
        # Create a vertical bar chart of Cash flows
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=cashflow_data.index,
            y=cashflow_data['Cash flows from operating activities'],
            name='Cash flows from operating activities',
            marker=dict(color='rgba(60, 179, 113, 0.85)'),
            width=0.3,
        ))
        fig.add_trace(go.Bar(
            x=cashflow_data.index,
            y=cashflow_data['Cash flows from investing activities'],
            name='Cash flows from investing activities',
            marker=dict(color='rgba(30, 144, 255, 0.85)'),
            width=0.3,
        ))

        fig.add_trace(go.Bar(
            x=cashflow_data.index,
            y=cashflow_data['Cash flows from financing activities'],
            name='Cash flows from financing activities',
            marker=dict(color='rgba(173, 216, 230, 0.85)'),
            width=0.3,
        ))

        # Add a line for Free cash flow
        fig.add_trace(go.Scatter(
            x=cashflow_data.index,
            y=cashflow_data['Free cash flow'],
            mode='lines+markers',
            name='Free cash flow',
            line=dict(color='rgba(255, 140, 0, 1)', width=2),
            marker=dict(symbol='circle', size=5, color='rgba(255, 140, 0, 1)', line=dict(width=0.8, color='rgba(255, 140, 0, 1)'))
        ))

        # Update layout
        fig.update_layout(
            title='Cash flows',
            bargap=0.1,
        )

        # Display the plot 
        st.plotly_chart(fig)

        #Display financial ratios table 
        st.markdown('**Financial Ratios**')
        ratios_table = round(ratios_data.T,2)
        ratios_table = ratios_table.sort_index(axis=1, ascending=True)
        st.dataframe(ratios_table, width=800, height=400)
    except Exception as e:
        st.error('Not possible to develop dashboard. Please try again.')
        st.error(f"An error occurred: {e}")
        

    #Add download button
    empty_lines(2)
    try:
        # Create dataframes for each financial statement
        company_data = pd.DataFrame.from_dict(company_data, orient='index')
        company_data = (
            company_data.reset_index()
            .rename(columns={'index':'Key', 0:'Value'})
            .set_index('Key')
        )
        metrics_data = metrics_data.round(2).T
        income_data = income_data.round(2)
        ratios_data = ratios_data.round(2).T
        balance_sheet_data = balance_sheet_data.round(2).T
        cashflow_data = cashflow_data.T

        # Clean up income statement column names and transpose dataframe
        income_data.columns = income_data.columns.str.replace(r'[\/\(\)\-\+=]\s?', '', regex=True)
        income_data = income_data.T

        # Combine all dataframes into a dictionary
        dfs = {
            'Stock': company_data,
            'Market Performance': performance_data,    
            'Income Statement': income_data,
            'Balance Sheet': balance_sheet_data,
            'Cash flow': cashflow_data,
            'Key Metrics': metrics_data,
            'Financial Ratios': ratios_data
        }

        # Write the dataframes to an Excel file, with special formatting for the Market Performance sheet
        writer = pd.ExcelWriter(symbol_input + '_financial_data.xlsx', engine='xlsxwriter')
        for sheet_name, df in dfs.items():
            if sheet_name == 'Market Performance':
                # Rename index column and format date column
                df.index.name = 'Date'
                df = df.reset_index()
                df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
                # Write dataframe to Excel sheet without index column
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            else:
                # Write dataframe to Excel sheet with index column
                df.to_excel(writer, sheet_name=sheet_name, index=True)
            # Autofit columns in Excel sheet
            writer.sheets[sheet_name].autofit()

        # Close the Excel writer object
        writer.close()

        # Create a download button for the Excel file
        with open(symbol_input + '_financial_data.xlsx', 'rb') as f:
            data = f.read()
            if st.download_button(
                label='Download Data',
                data=data,
                file_name=symbol_input + '_financial_data.xlsx',
                mime='application/octet-stream'
            ):
                st.success('Download successful!')
    except Exception as e:
        st.info('Data not available for download')

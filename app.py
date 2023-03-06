"""
This is a financial analysis application that allows users to input a stock symbol and receive various financial
metrics and visualizations for the corresponding company.
"""

# Import necessary libraries
import streamlit as st
from io import BytesIO
from millify import millify
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from io import BytesIO
import sys
from utils import (
    config_menu_footer, generate_card, empty_lines, get_delta, color_highlighter
)
from data import (
    get_income_statement, get_balance_sheet, get_stock_price, get_company_info,
    get_financial_ratios, get_key_metrics, get_cash_flow
)


# Define caching functions for each API call
@st.cache_data(ttl=60*60*24*30) # cache output for 30 days
def company_info(symbol):
    return get_company_info(symbol)

@st.cache_data(ttl=60*60*24*30) # cache output for 30 days
def income_statement(symbol):
    return get_income_statement(symbol)

@st.cache_data(ttl=60*60*24*30) # cache output for 30 days
def balance_sheet(symbol):
    return get_balance_sheet(symbol)

@st.cache_data(ttl=60*60*24*30) # cache output for 30 days
def stock_price(symbol):
    return get_stock_price(symbol)

@st.cache_data(ttl=60*60*24*30) # cache output for 30 days
def financial_ratios(symbol):
    return get_financial_ratios(symbol)

@st.cache_data(ttl=60*60*24*30) # cache output for 30 days
def key_metrics(symbol):
    return get_key_metrics(symbol)

@st.cache_data(ttl=60*60*24*30) # cache output for 30 days
def cash_flow(symbol):
    return get_cash_flow(symbol)

# Configure the app page
st.set_page_config(
    page_title='Financial Dashboard',
    page_icon='📈',
    layout="centered",
)

# Define caching function for delta
@st.cache_data(ttl=60*60*24*30) # cache output for 30 days
def delta(df,key):
    return get_delta(df,key)

# Configure the menu and footer with the user's information
config_menu_footer('abeltavares','abeltavares','Abel Tavares')

# Display the app title
st.title("Financial Dashboard 📈")

# Initialize the state of the button as False when the app is first loaded
if 'btn_clicked' not in st.session_state:
    st.session_state['btn_clicked'] = False

# Define a callback function for when the "Go" button is clicked
def callback():
    # change state value
    st.session_state['btn_clicked'] = True

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
        company_data = get_company_info(symbol_input)
        metrics_data = key_metrics(symbol_input)
        income_data = income_statement(symbol_input)
        performance_data = stock_price(symbol_input)
        ratios_data = financial_ratios(symbol_input)
        balance_sheet_data = balance_sheet(symbol_input)
        cashflow_data = cash_flow(symbol_input)

    except Exception:
        st.error('Not possible to retrieve data for that ticker. Please check if its valid and try again.')
        sys.exit()

    # Display dashboard
    empty_lines(2)
    try:
        # Display company info
        col1, col2 = st.columns((8.5,1.5))
        with col1:
            generate_card(company_data['Name'])
        with col2:
            # display image and make it clickable
            image_html = f"<a href='{company_data['Website']}' target='_blank'><img src='{company_data['Image']}' alt='{company_data['Name']}' height='75' width='95'></a>"
            st.markdown(image_html, unsafe_allow_html=True)

        col3, col4, col5, col6, col7 = st.columns((0.2,1.4,1.4,2,2.6))

        with col4:
            empty_lines(1)
            st.metric(label="Price", value=company_data['Price'], delta=company_data['Price change'])
            empty_lines(2)

        with col5:
            empty_lines(1)
            generate_card(company_data['Currency'])
            empty_lines(2)

        with col6:
            empty_lines(1)
            generate_card(company_data['Exchange'])
            empty_lines(2)

        with col7:
            empty_lines(1)
            generate_card(company_data['Sector'])            
            empty_lines(2)

        # Define columns for key metrics and IS
        col8, col9, col10 = st.columns((2,2,3))

        # Display key metrics  
        with col8:
            empty_lines(3)
            st.metric(label="Market Cap", value=millify(metrics_data['Market Cap'][0], precision=2), delta=delta(metrics_data,'Market Cap'))
            st.write("")
            st.metric(label="D/E Ratio", value = round(metrics_data['D/E ratio'][0],2), delta=delta(metrics_data,'D/E ratio'))
            st.write("")
            st.metric(label="ROE", value = str(round(metrics_data['ROE'][0] * 100, 2)) + '%', delta=delta(metrics_data,'ROE'))

        with col9:
            empty_lines(3)
            st.metric(label="Working Capital", value = millify(metrics_data['Working Capital'][0], precision = 2), delta=delta(metrics_data,'Working Capital'))
            st.write("")
            st.metric(label="P/E Ratio", value = round(metrics_data['P/E Ratio'][0],2), delta=delta(metrics_data,'P/E Ratio'))
            st.write("")
            # Check if the company pays dividends
            if metrics_data['Dividend Yield'][0] == 0:
                st.metric(label="Dividends (yield)", value = '0')
            else:
                st.metric(label="Dividends (yield)", value = str(round(metrics_data['Dividend Yield'][0]* 100, 2)) + '%', delta=delta(metrics_data,'Dividend Yield'))
        with col10:      
            # Transpose the income data so that the years are the columns
            income_statement_data = income_data.T

            # Display a markdown header for the income statement
            st.markdown('**Income Statement**')
                        
            # Allow the user to select a year to display
            year = st.selectbox('All numbers in thousands', income_statement_data.columns, label_visibility='collapsed')

            # Slice the income data to only show the selected year and format numbers with millify function
            income_statement_data = income_statement_data.loc[:, [year]]
            income_statement_data = income_statement_data.applymap(lambda x: millify(x, precision=2))
                        
            # Apply the color_highlighter function to highlight negative numbers
            income_statement_data = income_statement_data.style.applymap(color_highlighter)

            # Style the table headers with black color
            headers = {
                'selector': 'th:not(.index_name)',
                'props': [('color', 'black')]
            }

            income_statement_data.set_table_styles([headers])

            # Display the income statement table in Streamlit
            st.table(income_statement_data)


        # Configure the plots bar
        config = {
            'displaylogo': False, 
            'modeBarButtonsToRemove': ['zoom2d', 'pan2d', 'select2d', 'lasso2d', 'hoverClosestCartesian', 'hoverCompareCartesian', 'autoScale2d', 'toggleSpikelines', 'resetScale2d', 'zoomIn2d', 'zoomOut2d', 'hoverClosest3d', 'hoverClosestGeo', 'hoverClosestGl2d', 'hoverClosestPie', 'toggleHover', 'resetViews', 'toggleSpikeLines', 'resetViewMapbox', 'resetGeo', 'hoverClosestGeo', 'sendDataToCloud', 'hoverClosestGl']
        }

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

        # Customize the chart layout
        fig.update_layout(
            title={
                'text': 'Market Performance',
            },
            dragmode='pan',
            xaxis=dict(
            fixedrange=True
            ),
        yaxis=dict(
            fixedrange=True
            )
        )

        # Render the line chart 
        st.plotly_chart(fig, config=config, use_container_width=True)


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
            dragmode='pan',
            xaxis=dict(
                tickmode='array', 
                tickvals=income_data.index,
                fixedrange=True
            ),
            yaxis=dict(
                fixedrange=True
            ),
        )

        # Display the graph
        st.plotly_chart(fig, config=config, use_container_width=True)


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
            dragmode='pan',
            xaxis=dict(
                fixedrange=True,
                tickformat='.0%'
            ),
            yaxis=dict(
            fixedrange=True
             )
        )

        # Display the plot 
        st.plotly_chart(fig, config=config, use_container_width=True)


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
            dragmode='pan',
            xaxis=dict(
                fixedrange=True
            ),
                yaxis=dict(
                fixedrange=True,
             )
        )

        # Display the plot 
        st.plotly_chart(fig, config=config, use_container_width=True)


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
            dragmode='pan',
            xaxis=dict(
                fixedrange=True
            ),
            yaxis=dict(
                fixedrange=True,
                tickformat='.0%'
            )
        )

        # Display the plot in Streamlit
        st.plotly_chart(fig, config=config, use_container_width=True)


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
                xaxis=dict(
                fixedrange=True,
            ),
            yaxis=dict(
                fixedrange=True,
            )
        )

        # Display the plot 
        st.plotly_chart(fig, config=config, use_container_width=True)

        #Display financial ratios table 
        empty_lines(1)
        st.markdown('**Financial Ratios**')
        # Rename keys and format values as needed
        ratios_table = ratios_data.rename(columns={
            'Days of Sales Outstanding': 'Days of Sales Outstanding (days)',
            'Days of Inventory Outstanding': 'Days of Inventory Outstanding (days)',
            'Operating Cycle': 'Operating Cycle (days)',
            'Days of Payables Outstanding': 'Days of Payables Outstanding (days)',
            'Cash Conversion Cycle': 'Cash Conversion Cycle (days)',
            'Gross Profit Margin': 'Gross Profit Margin (%)', 
            'Operating Profit Margin': 'Operating Profit Margin (%)',
            'Pretax Profit Margin': 'Pretax Profit Margin (%)',
            'Net Profit Margin': 'Net Profit Margin (%)',
            'Effective Tax Rate': 'Effective Tax Rate (%)',
            'Return on Assets': 'Return on Assets (%)',
            'Return on Equity': 'Return on Equity (%)',
            'Return on Capital Employed': 'Return on Capital Employed (%)',
            'EBIT per Revenue': 'EBIT per Revenue (%)',
            'Debt Ratio': 'Debt Ratio (%)',
            'Long-term Debt to Capitalization': 'Long-term Debt to Capitalization (%)',
            'Total Debt to Capitalization': 'Total Debt to Capitalization (%)',
            'Payout Ratio': 'Payout Ratio (%)',
            'Operating Cash Flow Sales Ratio': 'Operating Cash Flow Sales Ratio (%)',
            'Dividend Yield': 'Dividend Yield (%)',
        })

        # Multiply values in columns with "%" symbol by 100
        for col in ratios_table.columns:
            if "%" in col:
                ratios_table[col] = ratios_table[col] * 100

        ratios_table = round(ratios_table.T,2)
        

        ratios_table = ratios_table.sort_index(axis=1, ascending=True)

        # Display ratios table
        st.dataframe(ratios_table, width=800, height=400)

    except Exception:
        st.error('Not possible to develop dashboard. Please try again.')
        sys.exit()

    #Add download button
    empty_lines(3)
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
            'Financial Ratios': ratios_table
        }

        # Write the dataframes to an Excel file, with special formatting for the Market Performance sheet
        output = BytesIO()
        writer = pd.ExcelWriter(output, engine='xlsxwriter')
        for sheet_name, df in dfs.items():
            if sheet_name == 'Market Performance':
                # Rename index column and format date column
                df.index.name = 'Date'
                df = df.reset_index()
                df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d')
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
        data = output.getvalue()
        st.download_button(
            label='Download ' + symbol_input + ' Financial Data (.xlsx)',
            data=data,
            file_name=symbol_input + '_financial_data.xlsx',
            mime='application/octet-stream'
        )
    except Exception:
        st.info('Data not available for download')

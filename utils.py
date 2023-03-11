"""
This module contains utility functions for the financial analysis application.
"""

# Import necessary libraries
import streamlit as st
import pandas as pd


def config_menu_footer() -> None:
    """
    Hides the Streamlit menu and replaces footer.
    """
    app_style = """
        <style>
            #MainMenu {
              visibility: hidden;
            }
            footer {
                visibility: hidden;
            }
            footer:before {
            content:"Copyright © 2023 Abel Tavares";
            visibility: visible;
            display: block;
            position: relative;
            text-align: center;
            }
        </style>
    """

    st.markdown(app_style, unsafe_allow_html=True)


def get_delta(df: pd.DataFrame, key: str) -> str:
    """
    Calculates the real percentage difference between the first two values for a given key in a Pandas DataFrame.

    Parameters:
        df (pandas.DataFrame): DataFrame containing financial data.
        key (str): The key for which to calculate the percentage difference.

    Returns:
        str: A string representation of the percentage difference with a percent sign at the end.
    """
    if key not in df.columns:
        return f"Key '{key}' not found in DataFrame columns."

    if len(df) < 2:
        return "DataFrame must contain at least two rows."

    val1 = df[key][1]
    val2 = df[key][0]

    # Handle cases where either value is negative or zero
    if val1 <= 0 or val2 <= 0:
        delta = (val2 - val1) / abs(val1) * 100
    else:
        delta = (val2 - val1) / val1 * 100

    # Round to two decimal places and return the result
    return f"{delta:.2f}%"


def empty_lines(n: int) -> None:
    """
    Inserts empty lines to separate content.

    Parameters:
        n (int): The number of empty lines to insert.
    """
    for _ in range(n):
        st.write("")


def generate_card(text: str) -> None:
    """
    Generates a styled card with a title and icon.

    Parameters:
        text (str): The title text for the card.
    """
    st.markdown(f"""
        <div style='border: 1px solid #e6e6e6; border-radius: 5px; padding: 10px; display: flex; justify-content: center; align-items: center'>
            <i class='fas fa-chart-line' style='font-size: 24px; color: #0072C6; margin-right: 10px'></i>
            <h3 style='text-align: center'>{text}</h3>
        </div>
         """, unsafe_allow_html=True)


def color_highlighter(val: str) -> str:
    """
    Returns CSS styling for a pandas DataFrame cell based on whether its value is positive or negative.

    Parameters:
        val (str): The cell value.

    Returns:
        str: The CSS styling string.
    """
    if val.startswith('-'):
        return 'color: rgba(255, 0, 0, 0.9);'
    else:
        return None

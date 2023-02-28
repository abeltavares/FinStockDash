import streamlit as st

def get_delta(df, key):
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

def empty_lines(n):
    """
    Inserts empty lines to separate content.

    Parameters:
        n (int): The number of empty lines to insert.
    """
    for _ in range(n):
        st.write("")

def generate_card(text):
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

def config_menu_footer(github_user,linkedin_user, author_name):
    """
    Hides the Streamlit menu and replaces footer.

    Parameters:
        github_user (str): The username for the GitHub account.
        linkedin_user (str): The username for the LinkedIn account.
        author_name (str): The name of the author.
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
            content:f'Produced by {author_name} | GitHub: {github_user} | LinkedIn: {linkedin_user}'; 
            visibility: visible;
            display: block;
            position: relative;
            text-align: center;
            }
        </style>
    """

    st.markdown(app_style, unsafe_allow_html=True)

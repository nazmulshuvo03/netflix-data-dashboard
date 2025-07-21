import streamlit as st
import pandas as pd


@st.cache_data
def load_data():
    """
    Loads, cleans, and preprocesses the Netflix dataset from a remote URL.
    The @st.cache_data decorator ensures the data is loaded only once,
    improving the app's performance.

    Returns:
        pandas.DataFrame: The cleaned and preprocessed Netflix data.
    """
    url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-04-20/netflix_titles.csv"
    try:
        df = pd.read_csv(url)

        # --- Data Cleaning and Preprocessing ---
        # Convert 'date_added' to datetime objects, coercing errors
        df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
        df["year_added"] = df["date_added"].dt.year

        # Drop rows with missing essential data
        df.dropna(
            subset=["rating", "release_year", "year_added", "country"], inplace=True
        )

        # Ensure correct data types for numeric columns
        df["release_year"] = df["release_year"].astype(int)
        df["year_added"] = df["year_added"].astype(int)

        return df
    except Exception as e:
        st.error(f"Error loading or processing data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame on error

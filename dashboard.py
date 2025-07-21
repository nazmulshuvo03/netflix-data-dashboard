import streamlit as st
import data
import ui


def main():
    """
    The main function that orchestrates the Streamlit app.
    """
    # --- Page Configuration ---
    st.set_page_config(
        page_title="Netflix Dashboard",
        page_icon="🎬",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # --- Load Data ---
    # This uses the function from our data.py module
    df = data.load_data()

    if not df.empty:
        # --- Create Sidebar and Get Filters ---
        # This uses the function from our ui.py module
        content_type, selected_countries, year_range = ui.create_sidebar(df)

        # --- Filter Data Based on Selections ---
        filtered_df = df[
            (df["release_year"] >= year_range[0])
            & (df["release_year"] <= year_range[1])
        ]

        if content_type != "All":
            filtered_df = filtered_df[filtered_df["type"] == content_type]

        if selected_countries:
            filtered_df = filtered_df[
                filtered_df["country"].apply(
                    lambda x: any(c in x for c in selected_countries)
                )
            ]

        # --- Create Main Page Layout ---
        # This uses the main page function from our ui.py module
        ui.create_main_page(filtered_df, content_type)


if __name__ == "__main__":
    main()

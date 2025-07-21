import streamlit as st
import plotly.express as px


def create_sidebar(df):
    """
    Creates the sidebar with all the interactive filters.

    Args:
        df (pandas.DataFrame): The dataframe containing Netflix data.

    Returns:
        tuple: A tuple containing the selected values from the filters
               (content_type, selected_countries, year_range).
    """
    st.sidebar.header("Dashboard Filters")

    # Content Type Filter
    content_type = st.sidebar.selectbox(
        "Select Content Type:", options=["All", "Movie", "TV Show"], index=0
    )

    # Country Filter
    # Explode the 'country' column to get a unique list of all countries
    all_countries = sorted(df["country"].str.split(", ").explode().unique())
    selected_countries = st.sidebar.multiselect(
        "Select Country/Countries:",
        options=all_countries,
        default=["United States", "India"],
    )

    # Release Year Slider
    min_year, max_year = int(df["release_year"].min()), int(df["release_year"].max())
    year_range = st.sidebar.slider(
        "Select Release Year Range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )

    return content_type, selected_countries, year_range


def create_main_page(filtered_df):
    """
    Creates the main page layout with key metrics and charts.

    Args:
        filtered_df (pandas.DataFrame): The dataframe filtered based on user selections.
    """
    st.title("🎬 Netflix Content Analysis Dashboard")
    st.markdown("An interactive dashboard to explore movies and TV shows on Netflix.")

    # --- Key Metrics ---
    st.markdown("### 📊 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Titles", f"{filtered_df.shape[0]:,}")
    col2.metric("Movies", f"{filtered_df[filtered_df['type'] == 'Movie'].shape[0]:,}")
    col3.metric(
        "TV Shows", f"{filtered_df[filtered_df['type'] == 'TV Show'].shape[0]:,}"
    )
    st.markdown("---")

    # --- Charts ---
    col1, col2 = st.columns(2)

    with col1:
        # Chart 1: Content Distribution by Type
        st.subheader("Content by Type")
        type_counts = filtered_df["type"].value_counts()
        fig1 = px.pie(
            names=type_counts.index,
            values=type_counts.values,
            hole=0.3,
            color_discrete_sequence=["#E50914", "#B3B3B3"],
        )
        fig1.update_layout(legend_title_text="Type")
        st.plotly_chart(fig1, use_container_width=True)

    with col2:
        # Chart 2: Top 10 Countries
        st.subheader("Top Content-Producing Countries")
        country_counts = (
            filtered_df["country"].str.split(", ").explode().value_counts().nlargest(10)
        )
        fig2 = px.bar(
            x=country_counts.values,
            y=country_counts.index,
            orientation="h",
            labels={"x": "Number of Titles", "y": "Country"},
            color_discrete_sequence=["#E50914"],
        )
        fig2.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig2, use_container_width=True)

    # Chart 3: Content Added Over Time
    st.subheader("Content Added to Netflix Over Time")
    added_by_year = filtered_df.groupby("year_added")["title"].count().reset_index()
    fig3 = px.line(
        added_by_year,
        x="year_added",
        y="title",
        labels={"year_added": "Year", "title": "Number of Titles"},
    )
    fig3.update_traces(line_color="#E50914", line_width=3)
    st.plotly_chart(fig3, use_container_width=True)

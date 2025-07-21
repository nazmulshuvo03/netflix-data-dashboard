import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pycountry


def get_iso_alpha(country_name):
    """Converts country name to ISO 3166-1 alpha-3 code."""
    country_map = {
        "United States": "USA",
        "United Kingdom": "GBR",
        "South Korea": "KOR",
        "West Germany": "DEU",
        "Soviet Union": "RUS",
        "Czech Republic": "CZE",
    }
    if country_name in country_map:
        return country_map[country_name]
    try:
        return pycountry.countries.get(name=country_name).alpha_3
    except AttributeError:
        try:
            return pycountry.countries.search_fuzzy(country_name)[0].alpha_3
        except LookupError:
            return None


def create_sidebar(df):
    """Creates the sidebar with all the interactive filters."""
    st.sidebar.header("Dashboard Filters")
    content_type = st.sidebar.selectbox(
        "Select Content Type:", options=["All", "Movie", "TV Show"], index=0
    )
    all_countries = sorted(df["country"].str.split(", ").explode().unique())
    selected_countries = st.sidebar.multiselect(
        "Select Country/Countries:",
        options=all_countries,
        default=["United States", "India"],
    )
    min_year, max_year = int(df["release_year"].min()), int(df["release_year"].max())
    year_range = st.sidebar.slider(
        "Select Release Year Range:",
        min_value=min_year,
        max_value=max_year,
        value=(min_year, max_year),
    )
    return content_type, selected_countries, year_range


def create_world_map(filtered_df):
    """Creates and displays an improved choropleth world map with a solid background."""
    st.subheader("🌎 Global Content Production Hotspots")
    st.markdown(
        "The map below shows the density of content production across the globe. "
        "Darker shades of red indicate a higher number of titles produced. "
        "Hover over a country for precise numbers."
    )

    country_counts = (
        filtered_df["country"].str.split(", ").explode().value_counts().reset_index()
    )
    country_counts.columns = ["country", "count"]
    country_counts["iso_alpha"] = country_counts["country"].apply(get_iso_alpha)
    country_counts = country_counts.dropna(subset=["iso_alpha"])

    fig = px.choropleth(
        country_counts,
        locations="iso_alpha",
        color="count",
        hover_name="country",
        hover_data={"iso_alpha": False, "count": True},
        color_continuous_scale=px.colors.sequential.Reds,
        projection="natural earth",
    )

    # --- FIX FOR MAP BACKGROUND ---
    # Set the background for the entire chart area
    fig.update_layout(
        margin={"r": 0, "t": 30, "l": 0, "b": 0},
        paper_bgcolor="#0E1117",
        font=dict(color="white"),
    )
    # Explicitly set the ocean color to match the background
    fig.update_geos(
        showocean=True,
        oceancolor="#0E1117",  # This forces the ocean to have a solid color
        showframe=False,
        showcoastlines=False,
    )

    st.plotly_chart(fig, use_container_width=True)


def create_genre_chart(filtered_df):
    """Creates and displays a bar chart for top genres."""
    st.subheader("Top Content Genres")
    genre_counts = (
        filtered_df["listed_in"].str.split(", ").explode().value_counts().nlargest(15)
    )
    fig = px.bar(
        x=genre_counts.values,
        y=genre_counts.index,
        orientation="h",
        labels={"x": "Number of Titles", "y": "Genre"},
        color_discrete_sequence=["#E50914"],
    )
    fig.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig, use_container_width=True)


def create_duration_histogram(filtered_df, content_type):
    """Creates and displays a histogram for content duration."""
    st.subheader("Content Duration Analysis")
    analysis_type = content_type if content_type != "All" else "Movie"
    if content_type == "All":
        st.info(
            "Displaying duration analysis for Movies. Select 'TV Show' to see season analysis."
        )

    if analysis_type == "Movie":
        movie_durations = (
            filtered_df[filtered_df["type"] == "Movie"]["duration"]
            .str.extract(r"(\d+)")
            .astype(float)
        )
        fig = px.histogram(
            movie_durations,
            x=0,
            nbins=30,
            title="Distribution of Movie Runtimes (in minutes)",
            labels={"0": "Runtime (minutes)"},
            color_discrete_sequence=["#E50914"],
        )
        st.plotly_chart(fig, use_container_width=True)

    elif analysis_type == "TV Show":
        tv_seasons = (
            filtered_df[filtered_df["type"] == "TV Show"]["duration"]
            .str.extract(r"(\d+)")
            .astype(float)
        )
        season_counts = tv_seasons[0].value_counts().sort_index()
        fig = px.bar(
            x=season_counts.index,
            y=season_counts.values,
            title="Distribution of TV Show Seasons",
            labels={"x": "Number of Seasons", "y": "Number of TV Shows"},
            color_discrete_sequence=["#E50914"],
        )
        st.plotly_chart(fig, use_container_width=True)


def create_description_wordcloud(filtered_df):
    """Creates and displays a word cloud from content descriptions."""
    st.subheader("Common Words in Descriptions")
    if not filtered_df.empty and "description" in filtered_df.columns:
        text = " ".join(desc for desc in filtered_df["description"].dropna())
        if text:
            wordcloud = WordCloud(
                background_color="white", width=800, height=400, colormap="Reds"
            ).generate(text)
            fig, ax = plt.subplots()
            ax.imshow(wordcloud, interpolation="bilinear")
            ax.axis("off")
            st.pyplot(fig)
        else:
            st.warning("No descriptions available for the selected filters.")
    else:
        st.warning("No data to generate a word cloud.")


def create_main_page(filtered_df, content_type):
    """Creates the main page layout with key metrics and charts."""
    st.title("🎬 Netflix Content Analysis Dashboard")
    st.markdown("An interactive dashboard to explore movies and TV shows on Netflix.")

    st.markdown("### 📊 Key Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Titles", f"{filtered_df.shape[0]:,}")
    col2.metric("Movies", f"{filtered_df[filtered_df['type'] == 'Movie'].shape[0]:,}")
    col3.metric(
        "TV Shows", f"{filtered_df[filtered_df['type'] == 'TV Show'].shape[0]:,}"
    )
    st.markdown("---")

    create_world_map(filtered_df)
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
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

    st.markdown("---")
    create_genre_chart(filtered_df)

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        create_duration_histogram(filtered_df, content_type)
    with col2:
        create_description_wordcloud(filtered_df)

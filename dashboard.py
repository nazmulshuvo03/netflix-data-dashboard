import streamlit as st
import pandas as pd
import plotly.express as px

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Netflix Dashboard",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)


# --- DATA LOADING AND CACHING ---
# Cache the data loading to improve performance
@st.cache_data
def load_data():
    """Loads and preprocesses the Netflix dataset."""
    # URL to the raw CSV file of the Netflix dataset
    url = "https://raw.githubusercontent.com/rfordatascience/tidytuesday/master/data/2021/2021-04-20/netflix_titles.csv"
    df = pd.read_csv(url)

    # Data cleaning and preprocessing
    df["date_added"] = pd.to_datetime(df["date_added"].str.strip(), errors="coerce")
    df["year_added"] = df["date_added"].dt.year
    df = df.dropna(subset=["rating", "release_year", "year_added", "country"])
    df["release_year"] = df["release_year"].astype(int)
    df["year_added"] = df["year_added"].astype(int)

    return df


df = load_data()

# --- SIDEBAR FILTERS ---
st.sidebar.header("Dashboard Filters")

# Content Type Filter
content_type = st.sidebar.selectbox(
    "Select Content Type:",
    options=["All", "Movie", "TV Show"],
    index=0,  # Default to 'All'
)

# Country Filter (Multiselect for more flexibility)
all_countries = sorted(df["country"].str.split(", ").explode().unique())
selected_countries = st.sidebar.multiselect(
    "Select Country/Countries:",
    options=all_countries,
    default=["United States", "India"],  # Default selection
)

# Release Year Slider
min_year, max_year = int(df["release_year"].min()), int(df["release_year"].max())
year_range = st.sidebar.slider(
    "Select Release Year Range:",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),  # Default to full range
)

# --- FILTERING DATA BASED ON SIDEBAR SELECTIONS ---
filtered_df = df[
    (df["release_year"] >= year_range[0]) & (df["release_year"] <= year_range[1])
]

if content_type != "All":
    filtered_df = filtered_df[filtered_df["type"] == content_type]

if selected_countries:
    # Filter rows where at least one of the selected countries is in the 'country' column
    filtered_df = filtered_df[
        filtered_df["country"].apply(lambda x: any(c in x for c in selected_countries))
    ]


# --- MAIN PAGE LAYOUT ---
st.title("🎬 Netflix Content Analysis Dashboard")
st.markdown("An interactive dashboard to explore movies and TV shows on Netflix.")

# Key Metrics
st.markdown("### 📊 Key Metrics")
col1, col2, col3 = st.columns(3)
col1.metric("Total Titles", f"{filtered_df.shape[0]:,}")
col2.metric("Movies", f"{filtered_df[filtered_df['type'] == 'Movie'].shape[0]:,}")
col3.metric("TV Shows", f"{filtered_df[filtered_df['type'] == 'TV Show'].shape[0]:,}")

st.markdown("---")


# --- CHARTS ---
# Create two columns for the first row of charts
col1, col2 = st.columns(2)

# Chart 1: Content Distribution by Type (Pie Chart)
with col1:
    st.subheader("Content by Type")
    type_counts = filtered_df["type"].value_counts()
    fig1 = px.pie(
        names=type_counts.index,
        values=type_counts.values,
        title="Distribution of Movies vs. TV Shows",
        hole=0.3,
        color_discrete_sequence=["#E50914", "#B3B3B3"],
    )
    fig1.update_layout(legend_title_text="Type")
    st.plotly_chart(fig1, use_container_width=True)

# Chart 2: Top 10 Countries (Bar Chart)
with col2:
    st.subheader("Top Content-Producing Countries")
    # Explode countries and count them
    country_counts = (
        filtered_df["country"].str.split(", ").explode().value_counts().nlargest(10)
    )
    fig2 = px.bar(
        x=country_counts.values,
        y=country_counts.index,
        orientation="h",
        title="Top 10 Countries by Content Volume",
        labels={"x": "Number of Titles", "y": "Country"},
        color_discrete_sequence=["#E50914"],
    )
    fig2.update_layout(yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig2, use_container_width=True)

# Chart 3: Content Added Over Time (Line Chart)
st.subheader("Content Added to Netflix Over Time")
added_by_year = filtered_df.groupby("year_added")["title"].count().reset_index()
fig3 = px.line(
    added_by_year,
    x="year_added",
    y="title",
    title="Number of Titles Added Per Year",
    labels={"year_added": "Year", "title": "Number of Titles"},
)
fig3.update_traces(line_color="#E50914", line_width=3)
st.plotly_chart(fig3, use_container_width=True)

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title=" 1970 -2020 YouTube Analytics Dashboard", layout="wide")

# =========================
# UTILITY FUNCTIONS
# =========================
def format_number(num):
    if pd.isna(num):
        return "0"
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    return f"{num:.0f}"

# =========================
# LOAD DATA
# =========================
@st.cache_data
def load_data():
    try:
        df = pd.read_csv("Global YouTube Statistics.csv", encoding='utf-8')
    except:
        df = pd.read_csv("Global YouTube Statistics.csv", encoding='latin-1')

    df.columns = df.columns.str.strip().str.lower()

    numeric_cols = [
        'subscribers','video views','uploads',
        'video_views_for_the_last_30_days',
        'lowest_monthly_earnings','highest_monthly_earnings',
        'lowest_yearly_earnings','highest_yearly_earnings',
        'subscribers_for_last_30_days','Population',
        'Unemployment rate','Urban_population',
        'Latitude','Longitude'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df.fillna({
        'category': 'Unknown',
        'Country': 'Unknown',
        'channel_type': 'Unknown'
    }, inplace=True)

    return df

with st.spinner("Loading data..."):
    df = load_data()

# =========================
# SIDEBAR FILTERS
# =========================
st.sidebar.header("Filters")

countries = st.sidebar.multiselect(
    "Country",
    df['Country'].dropna().unique(),
    default=df['Country'].dropna().unique()
)

categories = st.sidebar.multiselect(
    "Category",
    df['category'].dropna().unique(),
    default=df['category'].dropna().unique()
)

channel_types = st.sidebar.multiselect(
    "Channel Type",
    df['channel_type'].dropna().unique(),
    default=df['channel_type'].dropna().unique()
)

filtered_df = df[
    (df['Country'].isin(countries)) &
    (df['category'].isin(categories)) &
    (df['channel_type'].isin(channel_types))
]

# =========================
# HEADER
# =========================
st.markdown("""
#  YouTube Analytics Dashboard  
### Insights on Growth, Engagement & Revenue
""")

st.markdown(f"""
**Active Filters:**  
-  Countries: {len(countries)}  
-  Categories: {len(categories)}  
- Channel Types: {len(channel_types)}  
""")

# =========================
# OVERVIEW
# =========================
st.header("Overview")

col1, col2, col3, col4 = st.columns(4, gap="large")

col1.metric("Total Channels", format_number(len(filtered_df)))
col2.metric("Avg Subscribers", format_number(filtered_df['subscribers'].mean()))
col3.metric("Avg Views", format_number(filtered_df['video views'].mean()))
col4.metric("Avg Earnings", format_number(filtered_df['highest_monthly_earnings'].mean()))

# =========================
# TOP CHANNELS
# =========================
st.subheader("Top Channels")

sort_option = st.selectbox(
    "Sort Top Channels By:",
    ["subscribers", "video views", "uploads"]
)

top10 = filtered_df.nlargest(10, sort_option)

fig = px.bar(
    top10,
    x=sort_option,
    y='Youtuber',
    orientation='h',
    color=sort_option,
    title="Top 10 Channels"
)
st.plotly_chart(fig, use_container_width=True)
st.caption("Insight: A few channels dominate the platform significantly.")

# =========================
# GROWTH ANALYSIS
# =========================
st.header("Growth Analysis")

col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(
        filtered_df,
        x='subscribers',
        y='video views',
        color='category',
        title="Subscribers vs Views"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Strong positive relationship between subscribers and views.")

with col2:
    fig = px.histogram(
        filtered_df,
        x='subscribers_for_last_30_days',
        nbins=30,
        title="Subscriber Growth Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Most channels experience moderate growth.")

# =========================
# REVENUE ANALYSIS
# =========================
st.header("Revenue Analysis")

col1, col2 = st.columns(2)

with col1:
    fig = px.scatter(
        filtered_df,
        x='subscribers',
        y='highest_monthly_earnings',
        color='category',
        title="Earnings vs Subscribers"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Higher audience size drives revenue.")

with col2:
    fig = px.box(
        filtered_df,
        x='category',
        y='highest_monthly_earnings',
        title="Earnings by Category"
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption("📌 Entertainment categories dominate earnings.")

# =========================
# CONTENT STRATEGY
# =========================
st.header("Content Strategy")

col1, col2 = st.columns(2)

with col1:
    views_by_category = filtered_df.groupby('category')['video views'].mean().reset_index()
    fig = px.bar(
        views_by_category,
        x='category',
        y='video views',
        title="Average Views by Category"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.pie(
        filtered_df,
        names='channel_type',
        title="Channel Type Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)

with col3:
    fig = px.scatter(
        filtered_df,
        x='uploads',
        y='video views',
        color='category',
        title="Uploads vs Views"
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================
# GEOGRAPHIC INSIGHTS
# =========================
st.header("Geographic Insights")

col1, col2 = st.columns(2)

with col1:
    country_counts = filtered_df['Country'].value_counts().reset_index()
    country_counts.columns = ['Country', 'Count']
    fig = px.bar(
        country_counts.head(10),
        x='Country',
        y='Count',
        title="Top Countries"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    fig = px.scatter_geo(
        filtered_df,
        lat='Latitude',
        lon='Longitude',
        hover_name='Youtuber',
        size='subscribers',
        color='category',
        projection="natural earth",
        title="Global Distribution"
    )
    st.plotly_chart(fig, use_container_width=True)

# =========================
# CORRELATION
# =========================
st.header("Correlation Analysis")

numeric_df = filtered_df.select_dtypes(include=np.number)
corr = numeric_df.corr()

fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(corr, cmap='coolwarm', ax=ax)

st.pyplot(fig)
st.caption("Identifies relationships between key metrics.")

# =========================
# EXPORT
# =========================
st.header("Data Export")

if st.checkbox("Show Raw Data"):
    st.dataframe(filtered_df)

csv = filtered_df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="Download Filtered Data",
    data=csv,
    file_name='filtered_youtube_data.csv',
    mime='text/csv'
)
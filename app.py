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
        'population','unemployment rate','urban_population',
        'latitude','longitude'
    ]
    
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    df.fillna({
        'category': 'Unknown',
        'country': 'Unknown',
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
    df['country'].dropna().unique(),
    default=df['country'].dropna().unique()
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
    (df['country'].isin(countries)) &
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
    y='youtuber',
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
    hist_data = filtered_df[['video_views_for_the_last_30_days']].dropna()
    if not hist_data.empty:
        fig = px.histogram(
            hist_data,
            x='video_views_for_the_last_30_days',
            nbins=30,
            title="Video Views Growth (Last 30 Days)"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for video views growth visualization.")

# =========================
# REVENUE ANALYSIS
# =========================
st.header("Revenue Analysis")

col1, col2 = st.columns(2)

with col1:
    scatter_data = filtered_df[['subscribers', 'highest_monthly_earnings', 'category']].dropna()
    if not scatter_data.empty:
        fig = px.scatter(
            scatter_data,
            x='subscribers',
            y='highest_monthly_earnings',
            color='category',
            title="Earnings vs Subscribers"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Higher audience size drives revenue.")
    else:
        st.info("No data available for earnings analysis.")

with col2:
    box_data = filtered_df[['category', 'highest_monthly_earnings']].dropna()
    if not box_data.empty:
        fig = px.box(
            box_data,
            x='category',
            y='highest_monthly_earnings',
            title="Earnings by Category"
        )
        st.plotly_chart(fig, use_container_width=True)
        st.caption("📌 Entertainment categories dominate earnings.")
    else:
        st.info("No earnings data available by category.")

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
    uploads_data = filtered_df[['uploads', 'video views', 'category']].dropna()
    if not uploads_data.empty:
        fig = px.scatter(
            uploads_data,
            x='uploads',
            y='video views',
            color='category',
            title="Uploads vs Views"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No data available for uploads vs views analysis.")

# =========================
# GEOGRAPHIC INSIGHTS
# =========================
st.header("Geographic Insights")

col1, col2 = st.columns(2)

with col1:
    country_counts = filtered_df['country'].value_counts().reset_index()
    country_counts.columns = ['country', 'Count']
    fig = px.bar(
        country_counts.head(10),
        x='country',
        y='Count',
        title="Top Countries"
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    geo_data = filtered_df[['latitude', 'longitude', 'youtuber', 'subscribers', 'category']].dropna()
    if not geo_data.empty:
        fig = px.scatter_geo(
            geo_data,
            lat='latitude',
            lon='longitude',
            hover_name='youtuber',
            size='subscribers',
            color='category',
            projection="natural earth",
            title="Global Distribution"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No geographic data available.")

# =========================
# CORRELATION
# =========================
st.header("Correlation Analysis")

numeric_df = filtered_df.select_dtypes(include=np.number).dropna(how='all')
if not numeric_df.empty and numeric_df.shape[1] > 1:
    corr = numeric_df.corr()
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(corr, cmap='coolwarm', ax=ax)
    st.pyplot(fig)
    st.caption("Identifies relationships between key metrics.")
else:
    st.info("Not enough numeric data for correlation analysis.")

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
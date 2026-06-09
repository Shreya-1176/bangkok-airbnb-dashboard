import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(page_title="Bangkok Airbnb Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    url = "https://raw.githubusercontent.com/Shreya-1176/bangkok-airbnb-dashboard/main/listings.csv"
    df = pd.read_csv(url)
    df.drop(columns=['neighbourhood_group', 'license'], inplace=True)
    df.dropna(subset=['price'], inplace=True)
    df = df[df['price'].le(50000)]
    df = df[df['minimum_nights'].le(365)]
    return df

df = load_data()

# Title
st.title("🏠 Bangkok Airbnb Dashboard")
st.markdown("Interactive analysis of **23,000+ Airbnb listings** in Bangkok, Thailand")

# Key stats
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Listings", f"{len(df):,}")
col2.metric("Avg Price/Night", f"฿{df['price'].mean():.0f}")
col3.metric("Median Price/Night", f"฿{df['price'].median():.0f}")
col4.metric("Neighbourhoods", df['neighbourhood'].nunique())

st.divider()

# Sidebar filters
st.sidebar.header("🔍 Filter Listings")
room_types = st.sidebar.multiselect(
    "Room Type",
    options=df['room_type'].unique(),
    default=df['room_type'].unique()
)
price_range = st.sidebar.slider(
    "Price Range (THB/night)",
    min_value=int(df['price'].min()),
    max_value=10000,
    value=(0, 5000)
)

# Apply filters
filtered_df = df[
    (df['room_type'].isin(room_types)) &
    (df['price'] >= price_range[0]) &
    (df['price'] <= price_range[1])
]

st.markdown(f"### Showing **{len(filtered_df):,}** listings")

# Charts row 1
col1, col2 = st.columns(2)

with col1:
    st.subheader("Room Type Distribution")
    fig, ax = plt.subplots(figsize=(8,5))
    sns.countplot(data=filtered_df, x='room_type',
                  order=filtered_df['room_type'].value_counts().index, ax=ax)
    plt.xticks(rotation=15)
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.subheader("Price Distribution")
    fig, ax = plt.subplots(figsize=(8,5))
    sns.histplot(filtered_df[filtered_df['price'] <= 5000]['price'],
                 bins=50, color='teal', ax=ax)
    plt.tight_layout()
    st.pyplot(fig)

# Charts row 2
col1, col2 = st.columns(2)

with col1:
    st.subheader("Top 10 Most Expensive Neighbourhoods")
    top_n = filtered_df.groupby('neighbourhood')['price'].median().sort_values(ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8,5))
    top_n.plot(kind='barh', color='coral', ax=ax)
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.subheader("Top 10 Neighbourhoods by Listings")
    top_listed = filtered_df['neighbourhood'].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(8,5))
    top_listed.plot(kind='barh', color='steelblue', ax=ax)
    plt.tight_layout()
    st.pyplot(fig)

# Map
st.subheader("🗺️ Listings Map (colored by price)")
df_map = filtered_df[filtered_df['price'] <= 5000]
fig, ax = plt.subplots(figsize=(12,7))
scatter = ax.scatter(df_map['longitude'], df_map['latitude'],
                     c=df_map['price'], cmap='YlOrRd',
                     alpha=0.4, s=2)
plt.colorbar(scatter, label='Price per Night (THB)')
plt.tight_layout()
st.pyplot(fig)

st.markdown("---")
st.markdown("Built with ❤️ using Python & Streamlit | Data: Inside Airbnb")

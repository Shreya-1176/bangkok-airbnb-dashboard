import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page config
st.set_page_config(
    page_title="Bangkok Airbnb Analytics",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .metric-card {
        background: linear-gradient(135deg, #1e2130, #2d3250);
        padding: 20px;
        border-radius: 12px;
        border-left: 4px solid #FF385C;
        margin: 8px 0;
    }
    .title-text {
        font-size: 42px;
        font-weight: 800;
        background: linear-gradient(90deg, #FF385C, #FF8C69);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .subtitle-text {
        font-size: 16px;
        color: #888;
        margin-bottom: 30px;
    }
    .section-header {
        font-size: 22px;
        font-weight: 700;
        color: #FF385C;
        margin: 20px 0 10px 0;
        border-bottom: 2px solid #FF385C;
        padding-bottom: 5px;
    }
    </style>
""", unsafe_allow_html=True)

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

# Header
st.markdown('<p class="title-text">🏠 Bangkok Airbnb Analytics</p>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Interactive analysis of 23,000+ Airbnb listings across 50 neighbourhoods in Bangkok, Thailand</p>', unsafe_allow_html=True)

# Key metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("🏘️ Total Listings", f"{len(df):,}")
col2.metric("💰 Avg Price/Night", f"฿{df['price'].mean():.0f}")
col3.metric("📊 Median Price/Night", f"฿{df['price'].median():.0f}")
col4.metric("📍 Neighbourhoods", df['neighbourhood'].nunique())

st.divider()

# Sidebar
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/a9/Airbnb_Logo_B%C3%A9lo.svg/2560px-Airbnb_Logo_B%C3%A9lo.svg.png", width=150)
st.sidebar.markdown("## 🔍 Filter Listings")

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

neighbourhood_filter = st.sidebar.multiselect(
    "Neighbourhood (optional)",
    options=sorted(df['neighbourhood'].unique()),
    default=[]
)

st.sidebar.divider()
st.sidebar.markdown("### 📌 About")
st.sidebar.markdown("Built with Python & Streamlit using real data from [Inside Airbnb](http://insideairbnb.com)")

# Apply filters
filtered_df = df[
    (df['room_type'].isin(room_types)) &
    (df['price'] >= price_range[0]) &
    (df['price'] <= price_range[1])
]
if neighbourhood_filter:
    filtered_df = filtered_df[filtered_df['neighbourhood'].isin(neighbourhood_filter)]

st.markdown(f"### 📋 Showing **{len(filtered_df):,}** listings")

# Charts row 1
st.markdown('<p class="section-header">Room Type & Price Analysis</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(8,5))
    fig.patch.set_facecolor('#1e2130')
    ax.set_facecolor('#1e2130')
    colors = ['#FF385C', '#FF8C69', '#FFB347', '#87CEEB']
    order = filtered_df['room_type'].value_counts().index
    sns.countplot(data=filtered_df, x='room_type', order=order, palette=colors, ax=ax)
    ax.set_title('Room Type Distribution', color='white', fontsize=14, fontweight='bold')
    ax.set_xlabel('Room Type', color='#888')
    ax.set_ylabel('Number of Listings', color='#888')
    ax.tick_params(colors='white')
    plt.xticks(rotation=15)
    for spine in ax.spines.values():
        spine.set_edgecolor('#333')
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8,5))
    fig.patch.set_facecolor('#1e2130')
    ax.set_facecolor('#1e2130')
    data = filtered_df[filtered_df['price'] <= 5000]['price']
    sns.histplot(data, bins=50, color='#FF385C', ax=ax, alpha=0.8)
    ax.set_title('Price Distribution', color='white', fontsize=14, fontweight='bold')
    ax.set_xlabel('Price per Night (THB)', color='#888')
    ax.set_ylabel('Number of Listings', color='#888')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333')
    plt.tight_layout()
    st.pyplot(fig)

# Charts row 2
st.markdown('<p class="section-header">Neighbourhood Insights</p>', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    fig, ax = plt.subplots(figsize=(8,5))
    fig.patch.set_facecolor('#1e2130')
    ax.set_facecolor('#1e2130')
    top_n = filtered_df.groupby('neighbourhood')['price'].median().sort_values(ascending=True).tail(10)
    top_n.plot(kind='barh', color='#FF385C', ax=ax, alpha=0.85)
    ax.set_title('Top 10 Most Expensive Neighbourhoods', color='white', fontsize=14, fontweight='bold')
    ax.set_xlabel('Median Price/Night (THB)', color='#888')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333')
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    fig, ax = plt.subplots(figsize=(8,5))
    fig.patch.set_facecolor('#1e2130')
    ax.set_facecolor('#1e2130')
    top_listed = filtered_df['neighbourhood'].value_counts().head(10).sort_values(ascending=True)
    top_listed.plot(kind='barh', color='#FF8C69', ax=ax, alpha=0.85)
    ax.set_title('Top 10 Neighbourhoods by Listings', color='white', fontsize=14, fontweight='bold')
    ax.set_xlabel('Number of Listings', color='#888')
    ax.tick_params(colors='white')
    for spine in ax.spines.values():
        spine.set_edgecolor('#333')
    plt.tight_layout()
    st.pyplot(fig)

# Map
st.markdown('<p class="section-header">Geographic Distribution</p>', unsafe_allow_html=True)
df_map = filtered_df[filtered_df['price'] <= 5000]
fig, ax = plt.subplots(figsize=(14,8))
fig.patch.set_facecolor('#1e2130')
ax.set_facecolor('#0e1117')
scatter = ax.scatter(df_map['longitude'], df_map['latitude'],
                     c=df_map['price'], cmap='YlOrRd',
                     alpha=0.5, s=3)
cbar = plt.colorbar(scatter, label='Price per Night (THB)')
cbar.ax.yaxis.set_tick_params(color='white')
plt.setp(cbar.ax.yaxis.get_ticklabels(), color='white')
cbar.set_label('Price per Night (THB)', color='white')
ax.set_title('Bangkok Airbnb Listings Map', color='white', fontsize=16, fontweight='bold')
ax.set_xlabel('Longitude', color='#888')
ax.set_ylabel('Latitude', color='#888')
ax.tick_params(colors='white')
for spine in ax.spines.values():
    spine.set_edgecolor('#333')
plt.tight_layout()
st.pyplot(fig)

# Key insights
st.markdown('<p class="section-header">💡 Key Insights</p>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.info("🏠 **70% of listings** are entire apartments — Bangkok Airbnb is commercially dominated")
with col2:
    st.info("📍 **Pathum Wan** is the most expensive neighbourhood — Bangkok's luxury shopping hub")
with col3:
    st.info("💰 **Sweet spot price** is ฿800-1,500/night — best value for budget travellers")

# Footer
st.divider()
st.markdown("Built with ❤️ using Python & Streamlit | Data source: [Inside Airbnb](http://insideairbnb.com) | © 2024")

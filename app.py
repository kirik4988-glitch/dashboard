import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 2. Set up the Streamlit page configuration
st.set_page_config(
    page_title="Bakery Data Analysis Dashboard",
    layout="wide"
)

# 3. Create a function to load and preprocess data
@st.cache_data
def load_data():
    df = pd.read_csv('/content/Bakery.csv')
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    df['Year'] = df['DateTime'].dt.year
    df['Month'] = df['DateTime'].dt.month
    df['Day'] = df['DateTime'].dt.day
    df['Hour'] = df['DateTime'].dt.hour
    df['DayOfWeek'] = df['DateTime'].dt.dayofweek
    df['Date'] = df['DateTime'].dt.date

    # Map DayOfWeek to DayName
    day_map = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
    df['DayName'] = df['DayOfWeek'].map(day_map)
    return df

# 4. Call load_data() and cache the result
df = load_data()

# 5. Set the main title for the Streamlit application
st.title("Bakery Data Analysis Dashboard")

# 6. Implement a sidebar
st.sidebar.title("Dashboard Controls")

selected_visualization = st.sidebar.radio(
    "Select Visualization Type",
    ('Count Plot', 'Pie Chart', 'Hourly-Daily Transaction Scatter')
)

selected_column = None
top_n = None

if selected_visualization in ('Count Plot', 'Pie Chart'):
    selected_column = st.sidebar.selectbox(
        "Select Categorical Column",
        ('Items', 'Daypart', 'DayType', 'DayName', 'Hour')
    )
    if selected_column == 'Items':
        top_n = st.sidebar.slider(
            "Top N Items",
            min_value=1,
            max_value=df['Items'].nunique(),
            value=10
        )

summary_button = st.sidebar.button("Generate Summary Report")

# 7. Main section for visualizations
if selected_visualization == 'Count Plot':
    st.subheader(f"Count Plot of {selected_column}")
    fig, ax = plt.subplots(figsize=(12, 6))
    if selected_column == 'Items':
        plot_data = df['Items'].value_counts().head(top_n)
        sns.barplot(x=plot_data.index, y=plot_data.values, ax=ax)
        ax.set_xlabel('Items')
        ax.set_ylabel('Number of Purchases')
        ax.set_title(f'Top {top_n} Most Popular Items')
        plt.xticks(rotation=45, ha='right')
    else:
        plot_data = df[selected_column].value_counts()
        sns.barplot(x=plot_data.index, y=plot_data.values, ax=ax)
        ax.set_xlabel(selected_column)
        ax.set_ylabel('Count')
        ax.set_title(f'Counts by {selected_column}')
        if selected_column in ['DayName', 'Hour']:
            plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    st.pyplot(fig)

elif selected_visualization == 'Pie Chart':
    st.subheader(f"Pie Chart of {selected_column}")
    fig, ax = plt.subplots(figsize=(10, 10))
    if selected_column == 'Items':
        plot_data = df['Items'].value_counts().head(top_n)
        ax.pie(plot_data, labels=plot_data.index, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
        ax.set_title(f'Distribution of Top {top_n} Items')
    else:
        plot_data = df[selected_column].value_counts()
        ax.pie(plot_data, labels=plot_data.index, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
        ax.set_title(f'Distribution by {selected_column}')
    ax.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
    plt.tight_layout()
    st.pyplot(fig)

elif selected_visualization == 'Hourly-Daily Transaction Scatter':
    st.subheader("Hourly-Daily Transaction Scatter Plot")
    # Aggregate data for scatter plot
    hourly_daily_transactions = df.groupby(['DayOfWeek', 'Hour'])['TransactionNo'].nunique().reset_index()
    hourly_daily_transactions['DayName'] = hourly_daily_transactions['DayOfWeek'].map(day_map)

    fig, ax = plt.subplots(figsize=(15, 8))
    sns.scatterplot(
        x='Hour',
        y='DayName',
        size='TransactionNo',
        sizes=(50, 1000),
        hue='TransactionNo',
        data=hourly_daily_transactions,
        ax=ax
    )
    ax.set_title('Unique Transactions by Hour and Day of Week')
    ax.set_xlabel('Hour of Day')
    ax.set_ylabel('Day of Week')
    ax.set_yticks(range(len(day_map)))
    ax.set_yticklabels([day_map[i] for i in range(7)])
    plt.tight_layout()
    st.pyplot(fig)

# 8. If summary_button is clicked
if summary_button:
    st.subheader("Summary Report")
    st.write("### Descriptive Statistics")
    st.write(df.describe())

    st.write("### Value Counts for Key Categorical Columns")
    for col in ['Items', 'Daypart', 'DayType', 'DayName', 'Hour']:
        st.write(f"#### {col}")
        st.write(df[col].value_counts().reset_index().rename(columns={'index': col, 'count': 'Count'}))

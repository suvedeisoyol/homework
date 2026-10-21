import streamlit as st
import matplotlib.pyplot as plt
import datetime as dt
import seaborn as sns
import pandas as pd

# Set page configuration
st.set_page_config(page_title="Ride Metrics Dashboard", layout="wide")

st.title("🚗 Ride Metrics Dashboard")

# 1. Add a file uploader widget in the sidebar or main page
st.sidebar.header("Data Configuration")
uploaded_file = st.sidebar.file_uploader("Upload your T1_orders CSV file", type=["csv"])

# 2. Function to load and cache the uploaded CSV data
@st.cache_data
def load_csv_data(file):
    df_orders = pd.read_csv(file)
    if "request_ts" in df_orders.columns:
        df_orders["request_ts"] = pd.to_datetime(df_orders["request_ts"])
    df_orders["week_start"] = df_orders["request_ts"].dt.to_period("W").dt.start_time
    df_orders["date"] = df_orders["request_ts"].dt.to_period("D").dt.start_time
    df_orders["hour"] = df_orders["request_ts"].dt.hour
    df_orders["day_of_week"] = df_orders["request_ts"].dt.day_name()
    df_orders["weekday"] = df_orders["request_ts"].dt.day_name().isin(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"])
    
    if "status" in df_orders.columns:
        df_orders = pd.get_dummies(df_orders, columns=["status"], dtype=int)
        
    return df_orders


# 3. Conditional logic: Load data if file is provided, otherwise show instructions
if uploaded_file is not None:
    df_orders = load_csv_data(uploaded_file)
    
    st.success(f"Successfully loaded `{uploaded_file.name}`!")
    
    # Quick data preview
    with st.expander("Preview Raw Data"):
        st.dataframe(df_orders.head())
        
    # --- Put the rest of your dashboard charts/metrics below this line ---
    st.write(f"Total rows loaded: {len(df_orders)}")
    




    st.title("🚗 Ride-Sharing Operations Dashboard")
    st.markdown("Exploring the sudden drop in Fullfillment rate")


    # 1. Frequency Selection
    freq_option = st.radio("Select Frequency", ["Weekly", "Daily"])
    group_col = "week_start" if freq_option == "Weekly" else "date"

    # 2. Date Range Filter
    min_date = df_orders["date"].min().date()
    max_date = df_orders["date"].max().date()
    date_range = st.date_input("Select Date Range", [min_date, max_date], min_value=min_date, max_value=max_date)

    if len(date_range) == 2:
        start_date, end_date = date_range
        mask = (df_orders["date"].dt.date >= start_date) & (df_orders["date"].dt.date <= end_date)
        df_filtered = df_orders.loc[mask]
    else:
        df_filtered = df_orders

    # --- Data Aggregation ---
    df_agg = df_filtered.groupby(group_col).agg(
        number_of_rides=("order_id", "count"),
        fulfillment_ratio=("status_completed", "mean"),
        total_unique_riders=("rider_id", "nunique"),
        total_unique_drivers=("driver_id", "nunique"),
        status_driver_cancelled=('status_driver_cancelled', 'sum'),
        status_no_driver_found=('status_no_driver_found', 'sum'),
        status_rider_cancelled=('status_rider_cancelled', 'sum')
    ).reset_index()

    df_agg["driver_to_rider_ratio"] = df_agg["total_unique_drivers"] / df_agg["total_unique_riders"]

    # --- Plotting Two Separate Graphs ---
    # Plot 1: Total Number of Rides (Placed First)
    st.subheader("Total Number of Rides")
    fig1, ax1 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=df_agg, x=group_col, y="number_of_rides", color="red", ax=ax1, marker="o")
    ax1.set_ylabel("Total Rides")
    ax1.set_xlabel(f"Time ({freq_option})")
    ax1.tick_params(axis='x', rotation=45)
    ax1.grid(True, linestyle="--", alpha=0.6)
    st.pyplot(fig1)

    # Plot 2: Ratios (Fulfillment & Driver-to-Rider Ratio)
    st.subheader("Operational Ratios")
    fig2, ax2 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=df_agg, x=group_col, y="fulfillment_ratio", color="blue", ax=ax2, marker="o", label="Fulfillment Ratio")
    sns.lineplot(data=df_agg, x=group_col, y="driver_to_rider_ratio", color="green", ax=ax2, marker="s", label="Driver-to-Rider Ratio")
    ax2.set_ylabel("Ratio Value")
    ax2.set_xlabel(f"Time ({freq_option})")
    ax2.tick_params(axis='x', rotation=45)
    ax2.grid(True, linestyle="--", alpha=0.6)
    ax2.legend(loc="upper left")
    st.pyplot(fig2)




    # Plot 1: Total Number of Rides (Placed First)
    st.subheader("Plotting each unfulfilled Orders")
    st.markdown("Please ovserve the Driver Cancelled incomplete requiest remained same throughout why other two increased substantially")
    fig3, ax1 = plt.subplots(figsize=(10, 4))
    sns.lineplot(data=df_agg, x=group_col, y="status_driver_cancelled", color="red", ax=ax1, marker="o")


    # Ensure week_start is sorted and formatted for plotting
    # Plot Rider Cancelled
    sns.lineplot(
        data=df_agg, x=group_col,
        y='status_rider_cancelled',
        marker='o',
        linewidth=2.5,
        label='Rider Cancelled',
        color='#ff7f0e'
    )

    # Plot No Driver Found
    sns.lineplot(
        data=df_agg, x=group_col,
        y='status_no_driver_found',
        marker='s',
        linewidth=2.5,
        label='No Driver Found',
        color='#1f77b4'
    )

    # Plot Driver Cancelled
    sns.lineplot(
        data=df_agg, x=group_col,
        y='status_driver_cancelled',
        marker='^',
        linewidth=2.5,
        label='Driver Cancelled',
        color='#d62728'
    )


    plt.title('Weekly Trends of Unfulfilled Orders', fontsize=14, fontweight='bold')
    plt.xlabel(f"Time ({freq_option})", fontsize=12)
    plt.ylabel("Total Rides", fontsize=12)
    plt.xticks(rotation=45)
    plt.legend(fontsize=11)
    plt.tight_layout()
    st.pyplot(fig3)








    # --- Section 2: Cutoff Date Split for Incomplete Orders ---

    st.subheader("2.Hourly Incomplete Orders: Before vs. After Cutoff Date")
    st.markdown("warning: Please wait for couple second for the graph.")
    st.markdown("Analyze overall volume, operational ratios, and hourly incomplete orders dynamically.")


    # 2. Date Range Filter

    min_date = df_orders["date"].min().date()
    max_date = df_orders["date"].max().date()

    date_range2 = st.date_input("Select Date Range:", [min_date, max_date], min_value=min_date, max_value=max_date)

    # 3. Cutoff Date Selection

    default_cutoff = dt.date(2026, 8, 31) if dt.date(2026, 8, 31) <= max_date else min_date

    cutoff_date_input = st.date_input("Select Cutoff Date", value=default_cutoff, min_value=min_date, max_value=max_date)
    cutoff_date = pd.to_datetime(cutoff_date_input)


    # 4. Day Type Selection
    day_type = st.selectbox("Day Type", ["Both", "Weekdays Only", "Weekends Only"])

    # 5. Status Selection
    status_cols_all = [col.replace("status_", "") for col in df_orders.columns if col.startswith("status_")]
    selected_statuses = st.multiselect("Select Statuses to Include", status_cols_all, default=status_cols_all)

    # --- Apply Filters ---
    df_filtered = df_orders.copy()

    if len(date_range2) == 2:
        start_d, end_d = date_range2
        df_filtered = df_filtered[(df_filtered["date"].dt.date >= start_d) & (df_filtered["date"].dt.date <= end_d)]

    if day_type == "Weekdays Only":
        df_filtered = df_filtered[df_filtered["weekday"] == True]
    elif day_type == "Weekends Only":
        df_filtered = df_filtered[df_filtered["weekday"] == False]

    if selected_statuses:
        dummy_cols = [f"status_{s}" for s in selected_statuses]
        # Keep rows where at least one selected status dummy column equals 1
        df_filtered = df_filtered[df_filtered[dummy_cols].sum(axis=1) > 0]




    df_before = df_filtered[df_filtered['request_ts'] < cutoff_date].copy()
    df_after = df_filtered[df_filtered['request_ts'] >= cutoff_date].copy()

    days_before = df_before['request_ts'].dt.normalize().nunique()
    days_after = df_after['request_ts'].dt.normalize().nunique()

    st.info(f"📅 **Period Breakdown:** Days Before Cutoff: **{days_before} days** | Days After Cutoff: **{days_after} days**")

    def process_period(df, num_days, period_label):
        if num_days == 0:
            return pd.DataFrame(columns=['hour', 'status', 'count', 'period'])

        df = df.copy()
        df['hour'] = df['request_ts'].dt.hour

        incomplete_cols = [c for c in ['status_driver_cancelled', 'status_rider_cancelled', 'status_no_driver_found'] if c in df.columns]
        if not incomplete_cols:
            return pd.DataFrame(columns=['hour', 'status', 'count', 'period'])
            
        df_incomplete = df[(df[incomplete_cols] == 1).any(axis=1)]

        df_melted = df_incomplete.melt(
            id_vars=['hour'],
            value_vars=incomplete_cols,
            var_name='status',
            value_name='is_active'
        )
        df_melted = df_melted[df_melted['is_active'] == 1]
        df_melted['status'] = df_melted['status'].str.replace('status_', '').str.replace('_', ' ').str.title()

        trend = df_melted.groupby(['hour', 'status']).size().reset_index(name='count')
        trend['count'] = trend['count'] / num_days
        trend['period'] = period_label
        return trend

    trend_before = process_period(df_before, days_before, f'Before ({days_before} days)')
    trend_after = process_period(df_after, days_after, f'After ({days_after} days)')
    combined_trend = pd.concat([trend_before, trend_after], ignore_index=True)

    if combined_trend.empty:
        st.warning("No incomplete order data available for the selected filters.")
    else:
        sns.set_theme(style="whitegrid")
        g = sns.catplot(
            data=combined_trend,
            kind='bar',
            x='hour',
            y='count',
            hue='status',
            col='period',
            palette='Set2',
            height=4.5,
            aspect=1.2,
            sharey=True
        )

        g.set_axis_labels('Hour of Day (0-23)', 'Average Daily Incomplete Orders')
        g.set_titles(col_template='{col_name}')
        g.fig.suptitle(f'Incomplete Orders Comparison (Cutoff: {cutoff_date.strftime("%B %d, %Y")})', y=1.05, fontsize=13, fontweight='bold')

        for ax in g.axes.flat:
            ax.set_xticks(range(0, 24, 2))
            ax.tick_params(axis='x', rotation=0)

        st.pyplot(g.fig)

else:
    st.warning("⚠️ Please upload your `T1_orders.csv` file using the sidebar to view the dashboard.")
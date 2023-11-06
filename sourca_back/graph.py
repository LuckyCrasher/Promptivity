import base64
from io import BytesIO

import pandas as pd
import matplotlib.pyplot as plt

def create_and_save_graphs(data_website_reason, data_website_duration):
    # Convert list of tuples to DataFrame
    df_reason = pd.DataFrame(data_website_reason, columns=['Website', 'Reason'])
    df_duration = pd.DataFrame(data_website_duration, columns=['Website', 'Duration'])

    # Merge the two dataframes on the 'Website' column
    merged_df = pd.merge(df_reason, df_duration, on='Website')

    # Convert seconds to minutes for plotting
    merged_df['Duration'] = merged_df['Duration'] / 60  # Conversion to minutes

    # Group by Reason and aggregate (summing duration in minutes)
    aggregated_data_reason = merged_df.groupby('Reason').agg({
        'Duration': 'sum'
    }).reset_index()

    # Plotting the bar graph for activity and duration
    fig1, ax1 = plt.subplots(figsize=(10,6))
    ax1.bar(aggregated_data_reason['Reason'], aggregated_data_reason['Duration'], color='skyblue')
    ax1.set_title('Duration of Different Activities')
    ax1.set_xlabel('Activity')
    ax1.set_ylabel('Duration (minutes)')
    ax1.set_xticks(aggregated_data_reason['Reason'])
    ax1.set_xticklabels(aggregated_data_reason['Reason'], rotation=45)
    ax1.grid(axis='y')

    # Group by Website and aggregate (summing duration in minutes)
    aggregated_data_website = df_duration.groupby('Website').agg({
        'Duration': 'sum'
    }).reset_index()

    # Plotting the pie chart for websites and time
    fig2, ax2 = plt.subplots(figsize=(10,6))
    ax2.pie(aggregated_data_website['Duration'], labels=aggregated_data_website['Website'], autopct='%1.1f%%', startangle=140, colors=plt.cm.Paired.colors)
    ax2.set_title('Proportion of Time Spent on Different Websites')
    ax2.axis('equal')

    # Save the bar graph as an image file
    buffer_bar = BytesIO()
    fig1.savefig(buffer_bar, format='png')
    buffer_bar.seek(0)
    bar_base64 = base64.b64encode(buffer_bar.read()).decode()

    buffer_pie = BytesIO()
    fig2.savefig(buffer_pie, format='png')
    buffer_pie.seek(0)
    pie_bas64 = base64.b64encode(buffer_pie.read()).decode()

    # Return the base64 of the saved graphs
    return bar_base64, pie_bas64

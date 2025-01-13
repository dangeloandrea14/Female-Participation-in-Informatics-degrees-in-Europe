import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D


# Load dataset
data = pd.read_csv("master_df.csv", index_col=0)
data.rename(columns={'Zone': 'Geographic Area'}, inplace=True)

# Define the cluster variable
cluster_variable = 'GDP Quartile'

# Cleanup function for the dataset
def cleanup_df(data):
    data.replace('n.a.', pd.NA, inplace=True)
    data.replace('tbp', pd.NA, inplace=True)
    data.dropna(how='any', inplace=True)
    for column in data.columns:
        if column not in ['Country', 'Type', 'Grade', 'stat_type', 'Geographic Area', 'Economic Zone']:
            data[column] = data[column].astype(float).round(4)
    return data

# Function to compute temporal trends
def compute_temporal_trend(df, attribute='female_p'):
    result_df = df[['Country', 'Geographic Area', 'Economic Zone', 'GDP Quartile']].copy()
    for column in df.columns:
        if attribute in column:
            year = 2000 + int(column.split("_")[-1])
            result_df.loc[:, year] = df[column].values
    return result_df

# Filter and process data for bachelor, master, and PhD students
type_data = "(RU)"
stat_type = "Awarded"

# Process data for Bachelor students
data_bachelor = data.loc[(data.Type == type_data) & (data.Grade == 'bachelor') & (data.stat_type == stat_type)]
data_bachelor = cleanup_df(data_bachelor)
data_bachelor = compute_temporal_trend(data_bachelor)
data_bachelor = data_bachelor[[col for col in data_bachelor if col in list(range(2010, 2022)) + ['Country', cluster_variable]]]

# Process data for Master students
data_master = data.loc[(data.Type == type_data) & (data.Grade == 'master') & (data.stat_type == stat_type)]
data_master = cleanup_df(data_master)
data_master = compute_temporal_trend(data_master)
data_master = data_master[[col for col in data_master if col in list(range(2010, 2022)) + ['Country', cluster_variable]]]

# Process data for PhD students
data_phd = data.loc[(data.Type == type_data) & (data.Grade == 'PhD') & (data.stat_type == stat_type)]
data_phd = cleanup_df(data_phd)
data_phd = compute_temporal_trend(data_phd)
data_phd = data_phd[[col for col in data_phd if col in list(range(2010, 2022)) + ['Country', cluster_variable]]]

# Prepare data for plotting
df_long_bachelor = data_bachelor.melt(id_vars=['Country', cluster_variable], var_name='Year', value_name='Value')
df_long_bachelor['Year'] = df_long_bachelor['Year'].astype(int)

df_long_master = data_master.melt(id_vars=['Country', cluster_variable], var_name='Year', value_name='Value')
df_long_master['Year'] = df_long_master['Year'].astype(int)

df_long_phd = data_phd.melt(id_vars=['Country', cluster_variable], var_name='Year', value_name='Value')
df_long_phd['Year'] = df_long_phd['Year'].astype(int)

# Define zones based on cluster variable
if cluster_variable == 'Geographic Area':
    zones = ['North', 'South', 'West']
elif cluster_variable == 'Economic Zone':
    zones = [0, 1, 2]
elif cluster_variable == 'GDP Quartile':
    zones = [1, 2, 3, 4]
else:
    zones = []

num_zones = len(zones)
x_ticks = [2012, 2014, 2016, 2018, 2020]
x_limits = (2010, 2022)
# Determine global min and max for consistent y-axis scaling
y_min = min(df_long_bachelor['Value'].min(), df_long_master['Value'].min(), df_long_phd['Value'].min())
y_max = max(df_long_bachelor['Value'].max(), df_long_master['Value'].max(), df_long_phd['Value'].max())

# Create a gridspec for flexible layout
fig = plt.figure(figsize=(16, 10))  # Adjust height for three rows
gs = gridspec.GridSpec(3, num_zones)  # Three rows: bachelor, master, PhD

axes_bachelor = [fig.add_subplot(gs[0, i]) for i in range(num_zones)]
axes_master = [fig.add_subplot(gs[1, i]) for i in range(num_zones)]
axes_phd = [fig.add_subplot(gs[2, i]) for i in range(num_zones)]

# Create a color map for all unique countries
unique_countries = pd.concat([df_long_bachelor['Country'], df_long_master['Country'], df_long_phd['Country']]).unique()
color_map = {country: plt.cm.tab20(i % 20) for i, country in enumerate(unique_countries)}

# Plotting loop for Bachelor Students
for i, zone in enumerate(zones):
    ax = axes_bachelor[i]
    zone_data = df_long_bachelor[df_long_bachelor[cluster_variable] == zone]
    for country, country_data in zone_data.groupby('Country'):
        ax.plot(country_data['Year'], country_data['Value'], label=country, linewidth=1.2, color=color_map[country])
    mean_data = zone_data.groupby('Year')['Value'].mean().reset_index()
    ax.plot(mean_data['Year'], mean_data['Value'], label="_nolegend_", color='black', linewidth=2, linestyle='--')
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=8)
    ax.set_title(f'{cluster_variable} {zone}')
    ax.set_ylim(y_min, y_max)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xticks(x_ticks)
    ax.set_xlim(x_limits) 

# Plotting loop for Master Students
for i, zone in enumerate(zones):
    ax = axes_master[i]
    zone_data = df_long_master[df_long_master[cluster_variable] == zone]
    for country, country_data in zone_data.groupby('Country'):
        ax.plot(country_data['Year'], country_data['Value'], label=country, linewidth=1.2, color=color_map[country])
    mean_data = zone_data.groupby('Year')['Value'].mean().reset_index()
    ax.plot(mean_data['Year'], mean_data['Value'], label="_nolegend_", color='black', linewidth=2, linestyle='--')
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=8)
    ax.set_ylim(y_min, y_max)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xticks(x_ticks)  
    ax.set_xlim(x_limits) 

# Plotting loop for PhD Students
for i, zone in enumerate(zones):
    ax = axes_phd[i]
    zone_data = df_long_phd[df_long_phd[cluster_variable] == zone]
    for country, country_data in zone_data.groupby('Country'):
        ax.plot(country_data['Year'], country_data['Value'], label=country, linewidth=1.2, color=color_map[country])
    mean_data = zone_data.groupby('Year')['Value'].mean().reset_index()
    ax.plot(mean_data['Year'], mean_data['Value'], label="_nolegend_", color='black', linewidth=2, linestyle='--')
    #ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.2), ncol=2, fontsize=8)
    ax.set_ylim(y_min, y_max)
    ax.grid(True, linestyle='--', alpha=0.6)
    ax.set_xticks(x_ticks)
    ax.set_xlim(x_limits)   

#legend
for i, zone in enumerate(zones):
    # Get countries that exist in this zone across Bachelor and Master
    zone_countries = pd.concat([
        df_long_bachelor[df_long_bachelor[cluster_variable] == zone]['Country'],
        df_long_master[df_long_master[cluster_variable] == zone]['Country'],
        df_long_phd[df_long_phd[cluster_variable] == zone]['Country']
    ]).drop_duplicates().values  # Unique country list for this zone
    
    # Create legend elements for these countries
    legend_elements = [Line2D([0], [0], color=color_map[country], lw=2, label=country) for country in zone_countries]
    print(legend_elements)
    # Place legend below each column
    axes_phd[i].legend(
        handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.2), 
        ncol=2, fontsize=8
    )
    
# Add row labels
fig.text(0.06, 0.8, 'Bachelor', fontsize=16, rotation='vertical', va='center')
fig.text(0.06, 0.5, 'Master', fontsize=16, rotation='vertical', va='center')
fig.text(0.06, 0.2, 'PhD', fontsize=16, rotation='vertical', va='center')

# Create a unified title
fig.suptitle(
    f"Female percentage of bachelor, master, and PhD {stat_type} by {cluster_variable}",
    fontsize=14,
    y=0.97
)

# Save the plot
os.makedirs(os.path.join("new_plots", cluster_variable), exist_ok=True)
plt.savefig(os.path.join("new_plots", cluster_variable, f"newplot_{stat_type}_{cluster_variable}_{type_data}_bachelor_master_phd.png"), bbox_inches='tight')
#plt.show()

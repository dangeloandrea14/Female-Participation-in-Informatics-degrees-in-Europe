import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.lines import Line2D

# Load dataset
data = pd.read_csv("master_df.csv", index_col=0)
data.rename(columns={'Zone': 'Geographic Area'}, inplace=True)

# Define the cluster variable
cluster_variable = 'Geographic Area'

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

# Filter and process data for First Year Bachelor Students
type_data = "(RU)"
stat_type = "First Year Students"

data_bachelor = data.loc[(data.Type == type_data) & (data.Grade == 'bachelor') & (data.stat_type == stat_type)]
data_bachelor = cleanup_df(data_bachelor)
data_bachelor = compute_temporal_trend(data_bachelor)

data_bachelor = data_bachelor[[col for col in data_bachelor if col in list(range(2010, 2022)) + ['Country', cluster_variable]]]

# Prepare data for plotting
df_long_bachelor = data_bachelor.melt(id_vars=['Country', cluster_variable], var_name='Year', value_name='Value')
df_long_bachelor['Year'] = df_long_bachelor['Year'].astype(int)

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

# Determine global min and max for consistent y-axis scaling
y_min = df_long_bachelor['Value'].min()
y_max = df_long_bachelor['Value'].max()

# Create a gridspec for a single row
fig = plt.figure(figsize=(16, 7))  # Adjust height for one row
gs = gridspec.GridSpec(1, num_zones)  # One row for bachelor students

axes_bachelor = [fig.add_subplot(gs[0, i]) for i in range(num_zones)]

# Create a color map for all unique countries
unique_countries = df_long_bachelor['Country'].drop_duplicates().values
color_map = {country: plt.cm.tab20(i % 20) for i, country in enumerate(unique_countries)}

# Plotting loop for Bachelor Students
for i, zone in enumerate(zones):
    ax = axes_bachelor[i]
    zone_data = df_long_bachelor[df_long_bachelor[cluster_variable] == zone]
    for country, country_data in zone_data.groupby('Country'):
        ax.plot(country_data['Year'], country_data['Value'], label=country, linewidth=1.2, color=color_map[country])
    mean_data = zone_data.groupby('Year')['Value'].mean().reset_index()
    ax.plot(mean_data['Year'], mean_data['Value'], label="_nolegend_", color='black', linewidth=2, linestyle='--')
    ax.set_title(f'{cluster_variable} {zone}')
    ax.set_ylim(y_min, 0.4)
    ax.grid(True, linestyle='--', alpha=0.6)

# Create legends for each column
for i, zone in enumerate(zones):
    zone_countries = df_long_bachelor[df_long_bachelor[cluster_variable] == zone]['Country'].drop_duplicates().values
    legend_elements = [Line2D([0], [0], color=color_map[country], lw=2, label=country) for country in zone_countries]
    axes_bachelor[i].legend(
        handles=legend_elements, loc='upper center', bbox_to_anchor=(0.5, -0.2), 
        ncol=2, fontsize=8
    )


# Adjust layout
plt.tight_layout(rect=[0, 0.1, 1, 0.92])

# Save the plot
os.makedirs(os.path.join("new_plots", cluster_variable), exist_ok=True)
plt.savefig(os.path.join("new_plots", cluster_variable, f"newplot_{stat_type}_{cluster_variable}_{type_data}_bachelor_first_year.png"), bbox_inches='tight')
#plt.show()

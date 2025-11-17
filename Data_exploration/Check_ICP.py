import pandas as pd
from pathlib import Path

# Define the path to the database
db_path = Path("..") / "Datasets" / "ICP" / "AFSCDB-LII_to_share"

# Read the Excel file
excel_file = db_path / "AFSCDB.II.2.2_to_share.xlsx"
df = pd.read_excel(excel_file)

# Display basic info
print(df.head())
print(f"\nShape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")

# Check all sheets in the Excel file
xls = pd.ExcelFile(excel_file)
print("Available sheets:", xls.sheet_names)


#check PLS sheet
pls = pd.read_excel(excel_file, sheet_name='PLS')
print("PLS columns:")
print(pls.columns.tolist())
print("\nFirst few rows:")
print(pls.head())

#check country code sheet and some others
country_key = pd.read_excel(excel_file, sheet_name='key code_country')
print("\nCountry key:")
print(country_key.head())

humus_key = pd.read_excel(excel_file, sheet_name='key code_humus')
print(humus_key)

prf = pd.read_excel(excel_file, sheet_name='PRF')
print(prf.columns.tolist())

pfh = pd.read_excel(excel_file, sheet_name='PFH')
print(pfh.columns.tolist())
print(pfh.head())

#### Can't find aboveground info!!!


# Read SOM sheet
som = pd.read_excel(excel_file, sheet_name='SOM')

# Explore the structure
print("Column names:")
print(som.columns.tolist())
print(f"\nShape: {som.shape}")
print("\nFirst few rows:")
print(som.head())
print("\nData types:")
print(som.dtypes)








import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Load data
db_path = Path("..") / "Datasets" / "ICP" / "AFSCDB-LII_to_share"
# excel_file = Path("..") / "Datasets" / "ICP" / "AFSCDB-LII_to_share" / "AFSCDB.II.2.2_to_share.xlsx"
excel_file = db_path / "AFSCDB.II.2.2_to_share.xlsx"

print("Loading data...")
som = pd.read_excel(excel_file, sheet_name='SOM')
pls = pd.read_excel(excel_file, sheet_name='PLS')
country_key = pd.read_excel(excel_file, sheet_name='key code_country')

print(f"SOM data: {som.shape[0]} rows")
print(f"PLS data: {pls.shape[0]} rows")
print(f"Countries: {country_key.shape[0]} countries")

# Merge datasets
print("\nMerging datasets...")
merged = som.merge(pls[['code_plot', 'code_country']], 
                   on=['code_plot', 'code_country'], 
                   how='left')
merged = merged.merge(country_key, 
                      left_on='code_country', 
                      right_on='code', 
                      how='left')

# Calculate depth midpoint
merged['depth_mid'] = (merged['layer_limit_superior'] + merged['layer_limit_inferior']) / 2

# Filter out missing data (coded as -999999 or negative)
print("\nFiltering data...")
print(f"Before filtering: {merged.shape[0]} rows")

# Keep only valid SOC and depth values
merged_clean = merged[
    (merged['organic_carbon_total'] > 0) & 
    (merged['organic_carbon_total'] < 900) &  # Remove unrealistic values
    (merged['layer_limit_superior'] >= 0) &
    (merged['layer_limit_inferior'] > 0) &
    (merged['depth_mid'] >= 0)
].copy()

print(f"After filtering: {merged_clean.shape[0]} rows")
print(f"Countries in dataset: {merged_clean['lib_country'].nunique()}")
print(merged_clean['lib_country'].value_counts())


# %%
# ============================================================================
# PLOT 1: Scatterplot - SOC vs Depth by Country
# ============================================================================
print("\nCreating scatterplot...")

fig, ax = plt.subplots(figsize=(12, 10))

# Get unique countries and assign colors
countries = merged_clean['lib_country'].dropna().unique()
colors = sns.color_palette("tab10", n_colors=len(countries))
markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h']

for i, country in enumerate(sorted(countries)):
    data = merged_clean[merged_clean['lib_country'] == country]
    ax.scatter(data['organic_carbon_total'], 
               data['depth_mid'],
               label=country,
               alpha=0.6,
               s=50,
               c=[colors[i % len(colors)]],
               marker=markers[i % len(markers)],
               edgecolors='black',
               linewidths=0.5)

# Invert y-axis (depth increases downward)
ax.invert_yaxis()

ax.set_xlabel('Organic Carbon Total (g/kg)', fontsize=12, fontweight='bold')
ax.set_ylabel('Depth (cm)', fontsize=12, fontweight='bold')
ax.set_title('Soil Organic Carbon Distribution by Depth and Country', 
             fontsize=14, fontweight='bold', pad=20)
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('soc_depth_scatterplot.png', dpi=300, bbox_inches='tight')
print("Saved: soc_depth_scatterplot.png")
plt.close()

# ============================================================================
# PLOT 2: Boxplots - Mineral Topsoil SOC by Country
# ============================================================================
print("\nCreating boxplots for mineral topsoil...")

# Filter for mineral topsoil (Min layers, shallow depth)
topsoil = merged_clean[
    (merged_clean['laytype'] == 'Min') &
    (merged_clean['layer_limit_superior'] < 20)  # Top 20 cm
].copy()

print(f"Topsoil samples: {topsoil.shape[0]} rows")
print(f"By country:")
print(topsoil.groupby('lib_country').size())

# Create boxplot
fig, ax = plt.subplots(figsize=(14, 8))

# Sort countries by median SOC for better visualization
country_order = (topsoil.groupby('lib_country')['organic_carbon_total']
                 .median()
                 .sort_values(ascending=False)
                 .index.tolist())

sns.boxplot(data=topsoil, 
            x='lib_country', 
            y='organic_carbon_total',
            order=country_order,
            palette='Set2',
            ax=ax)

ax.set_xlabel('Country', fontsize=12, fontweight='bold')
ax.set_ylabel('Organic Carbon Total (g/kg)', fontsize=12, fontweight='bold')
ax.set_title('Mineral Topsoil (0-20 cm) Organic Carbon by Country', 
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3, axis='y')

# Rotate x-axis labels for readability
plt.xticks(rotation=45, ha='right')

# Add sample sizes
for i, country in enumerate(country_order):
    n = topsoil[topsoil['lib_country'] == country].shape[0]
    ax.text(i, ax.get_ylim()[1] * 0.95, f'n={n}', 
            ha='center', va='top', fontsize=9)

plt.tight_layout()
plt.savefig('soc_topsoil_boxplot.png', dpi=300, bbox_inches='tight')
print("Saved: soc_topsoil_boxplot.png")
plt.close()

# ============================================================================
# Summary statistics
# ============================================================================
print("\n" + "="*70)
print("SUMMARY STATISTICS")
print("="*70)

print("\nOverall SOC statistics (all layers):")
print(merged_clean['organic_carbon_total'].describe())

print("\nMineral topsoil SOC by country:")
summary = topsoil.groupby('lib_country')['organic_carbon_total'].agg([
    'count', 'mean', 'std', 'median', 'min', 'max'
]).round(2)
print(summary.sort_values('median', ascending=False))

print("\nDepth range in dataset:")
print(f"Min depth: {merged_clean['layer_limit_superior'].min()} cm")
print(f"Max depth: {merged_clean['layer_limit_inferior'].max()} cm")

print("\n" + "="*70)
print("Analysis complete!")
print("="*70)






# ============================================================================
# TEMPORAL TRENDS FOR FINLAND
# ============================================================================


# Filter for Finland only
finland_data = merged_clean[merged_clean['lib_country'] == 'Finland'].copy()

print(f"Finnish data: {finland_data.shape[0]} observations")
print(f"Number of Finnish plots: {finland_data['code_plot'].nunique()}")

# Calculate mean SOC by plot and year
finland_temporal = finland_data.groupby(['code_plot', 'survey_year'])['organic_carbon_total'].mean().reset_index()

# Check which plots have multiple years
plot_years = finland_temporal.groupby('code_plot')['survey_year'].count()
repeated_finnish = plot_years[plot_years > 1]

print(f"\nFinnish plots with repeated measurements: {len(repeated_finnish)}")
print(f"Finnish plots with single measurement: {(plot_years == 1).sum()}")

# Create the plot
fig, ax = plt.subplots(figsize=(14, 8))

# Get unique plots
plots = sorted(finland_temporal['code_plot'].unique())
colors = sns.color_palette("husl", n_colors=len(plots))  # More colors for many plots

# Plot each plot as a line
for i, plot in enumerate(plots):
    plot_data = finland_temporal[finland_temporal['code_plot'] == plot]
    
    # Use thicker line for plots with multiple measurements
    linewidth = 2.5 if len(plot_data) > 1 else 1.5
    alpha = 0.8 if len(plot_data) > 1 else 0.4
    
    ax.plot(plot_data['survey_year'], 
            plot_data['organic_carbon_total'],
            label=f'Plot {plot}',
            color=colors[i],
            marker='o',
            markersize=6,
            linewidth=linewidth,
            alpha=alpha)

ax.set_xlabel('Survey Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Mean Organic Carbon (g/kg)', fontsize=12, fontweight='bold')
ax.set_title('Temporal Trends in Soil Organic Carbon - Finnish Plots', 
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)

# Legend - only if not too many plots
if len(plots) <= 20:
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, fontsize=8)
else:
    ax.text(0.98, 0.98, f'{len(plots)} plots shown', 
            transform=ax.transAxes, ha='right', va='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.tight_layout()
plt.savefig('finland_soc_temporal_by_plot.png', dpi=300, bbox_inches='tight')
plt.close()

print("\nPlot saved: finland_soc_temporal_by_plot.png")






# ============================================================================
# CHECK FOR REPEATED MEASUREMENTS ACROSS ALL COUNTRIES
# ============================================================================

# Count how many years each plot was measured
plot_year_counts = merged_clean.groupby('code_plot')['survey_year'].nunique()

print("="*70)
print("REPEATED MEASUREMENTS ANALYSIS - ALL COUNTRIES")
print("="*70)

print(f"\nTotal unique plots: {len(plot_year_counts)}")
print(f"Plots with 1 measurement: {(plot_year_counts == 1).sum()}")
print(f"Plots with 2+ measurements: {(plot_year_counts > 1).sum()}")

print("\nDistribution of measurement frequency:")
print(plot_year_counts.value_counts().sort_index())

# Get plots with repeated measurements
repeated_plots = plot_year_counts[plot_year_counts > 1]

if len(repeated_plots) > 0:
    print(f"\n{'='*70}")
    print(f"PLOTS WITH REPEATED MEASUREMENTS: {len(repeated_plots)}")
    print(f"{'='*70}")
    
    # Show details for each repeated plot
    for plot_id in repeated_plots.index[:20]:  # Show first 20
        plot_data = merged_clean[merged_clean['code_plot'] == plot_id]
        country = plot_data['lib_country'].iloc[0]
        years = sorted(plot_data['survey_year'].unique())
        n_samples = len(plot_data)
        
        print(f"  Plot {plot_id} ({country}): {years} - {n_samples} total samples")
    
    if len(repeated_plots) > 20:
        print(f"  ... and {len(repeated_plots) - 20} more plots with repeats")
    
    # Summary by country
    print(f"\n{'='*70}")
    print("REPEATED PLOTS BY COUNTRY")
    print(f"{'='*70}")
    
    repeated_plot_ids = repeated_plots.index
    repeated_data = merged_clean[merged_clean['code_plot'].isin(repeated_plot_ids)]
    
    country_summary = repeated_data.groupby('lib_country').agg({
        'code_plot': 'nunique',
        'survey_year': lambda x: f"{x.min()}-{x.max()}"
    }).rename(columns={'code_plot': 'n_plots', 'survey_year': 'year_range'})
    
    print(country_summary.sort_values('n_plots', ascending=False))
    
else:
    print("\nNo plots have repeated measurements - all plots sampled only once")




# ============================================================================
# TEMPORAL PLOT FOR PLOTS WITH REPEATED MEASUREMENTS
# ============================================================================

# Filter for only plots with repeated measurements
repeated_plot_ids = plot_year_counts[plot_year_counts > 1].index
repeated_data = merged_clean[merged_clean['code_plot'].isin(repeated_plot_ids)].copy()

# Calculate mean SOC per plot per year
plot_temporal = repeated_data.groupby(['code_plot', 'lib_country', 'survey_year'])['organic_carbon_total'].mean().reset_index()

print(f"\nPlotting {len(repeated_plot_ids)} plots with repeated measurements...")

# Create the plot
fig, ax = plt.subplots(figsize=(16, 10))

# Get unique countries in repeated plots
countries = sorted(plot_temporal['lib_country'].unique())
country_colors = dict(zip(countries, sns.color_palette("tab10", n_colors=len(countries))))

# Line styles and markers for variety
linestyles = ['-', '--', '-.', ':', (0, (3, 1, 1, 1)), (0, (5, 2, 1, 2))]
markers = ['o', 's', '^', 'D', 'v', '<', '>', 'p', '*', 'h', 'X', 'P']

# Plot each plot with repeated measurements
for i, plot_id in enumerate(sorted(repeated_plot_ids)):
    plot_data = plot_temporal[plot_temporal['code_plot'] == plot_id]
    country = plot_data['lib_country'].iloc[0]
    
    ax.plot(plot_data['survey_year'], 
            plot_data['organic_carbon_total'],
            label=f'Plot {plot_id} ({country})',
            color=country_colors[country],
            marker=markers[i % len(markers)],
            linestyle=linestyles[i % len(linestyles)],
            markersize=7,
            linewidth=2,
            alpha=0.7)

ax.set_xlabel('Survey Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Mean Organic Carbon (g/kg)', fontsize=12, fontweight='bold')
ax.set_title('Temporal Trends in SOC for Plots with Repeated Measurements (n=35)', 
             fontsize=14, fontweight='bold', pad=20)
ax.grid(True, alpha=0.3)

# Legend outside plot - might be crowded with 35 plots
ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', frameon=True, fontsize=8, ncol=1)

plt.tight_layout()
plt.savefig('soc_repeated_plots_temporal.png', dpi=300, bbox_inches='tight')
plt.close()

print("Plot saved: soc_repeated_plots_temporal.png")
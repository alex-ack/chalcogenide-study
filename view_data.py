import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from config import DATA_DIR

def plot_my_data(csv_file):
    """
    Make some quick plots to see what my data looks like!
    """
    # Load my data
    df = pd.read_csv(csv_file)
    
    # Set up a nice plot style
    plt.style.use('seaborn')
    
    # Create a figure with multiple subplots
    fig, axs = plt.subplots(2, 2, figsize=(15, 10))
    
    # 1. Bandgap distribution
    sns.histplot(data=df, x='band_gap', ax=axs[0,0])
    axs[0,0].set_title('My Bandgap Distribution')
    axs[0,0].set_xlabel('Bandgap (eV)')
    
    # 2. Bandgap vs Volume scatter
    sns.scatterplot(data=df, x='volume', y='band_gap', 
                   hue='chalcogen', ax=axs[0,1])
    axs[0,1].set_title('Bandgap vs Volume')
    
    # 3. Formation energy distribution
    sns.boxplot(data=df, x='chalcogen', y='formation_energy_per_atom', 
                ax=axs[1,0])
    axs[1,0].set_title('Formation Energies by Chalcogen')
    
    # 4. Crystal system distribution
    df['crystal_system'].value_counts().plot(kind='bar', ax=axs[1,1])
    axs[1,1].set_title('Crystal Systems in My Dataset')
    
    plt.tight_layout()
    
    # Save my plot
    plt.savefig(f"{DATA_DIR}/my_analysis_plots.png")
    print(f"✨ Saved plots to {DATA_DIR}/my_analysis_plots.png")
    
    # Show some basic stats
    print("\n📊 Quick Stats:")
    print(f"Average bandgap: {df['band_gap'].mean():.2f} eV")
    print(f"Most common crystal system: {df['crystal_system'].mode()[0]}")
    print(f"Number of different compositions: {len(df['formula'].unique())}")

if __name__ == "__main__":
    # Find my most recent data file
    data_files = list(Path(DATA_DIR).glob("*.csv"))
    if data_files:
        latest_file = max(data_files, key=lambda x: x.stat().st_mtime)
        print(f"📂 Using data from: {latest_file}")
        plot_my_data(latest_file)
    else:
        print("❌ No data files found! Run data_collector.py first")
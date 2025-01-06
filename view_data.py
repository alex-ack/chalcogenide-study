import pandas as pd
import matplotlib.pyplot as plt
from mp_api.client import MPRester
import json
from datetime import datetime
import os
from config import API_KEY, CHALCOGENS, CATIONS, MAX_SAMPLES, DATA_DIR

class DataCollector:
    def __init__(self):
        print("Starting up my data collector...")
        if not os.path.exists(DATA_DIR):
            print(f"Creating my data directory at {DATA_DIR}")
            os.makedirs(DATA_DIR)
        self.api_key = API_KEY

    def visualize_data(self, df):
        if df is None or len(df) == 0:
            print("\n🔮 No data to visualize!")
            return

        # Histogram of Volume
        plt.figure(figsize=(8, 6))
        plt.hist(df['volume'].dropna(), bins=20, edgecolor='black')
        plt.xlabel('Volume (Å³)')
        plt.ylabel('Frequency')
        plt.title('Volume Distribution')
        plt.savefig(f"{DATA_DIR}/volume_distribution.png")
        plt.close()

        # Histogram of Density
        plt.figure(figsize=(8, 6))
        plt.hist(df['density'].dropna(), bins=20, edgecolor='black')
        plt.xlabel('Density (g/cm³)')
        plt.ylabel('Frequency')
        plt.title('Density Distribution')
        plt.savefig(f"{DATA_DIR}/density_distribution.png")
        plt.close()

        # Scatter Plot: Volume vs Density
        plt.figure(figsize=(8, 6))
        plt.scatter(df['volume'], df['density'], alpha=0.6)
        plt.xlabel('Volume (Å³)')
        plt.ylabel('Density (g/cm³)')
        plt.title('Volume vs Density')
        plt.savefig(f"{DATA_DIR}/volume_vs_density.png")
        plt.close()

        # Countplot for Crystal Systems
        if 'crystal_system' in df.columns:
            plt.figure(figsize=(8, 6))
            df['crystal_system'].value_counts().plot(kind='bar')
            plt.xlabel('Crystal System')
            plt.ylabel('Count')
            plt.title('Crystal System Distribution')
            plt.xticks(rotation=45)
            plt.savefig(f"{DATA_DIR}/crystal_system_distribution.png")
            plt.close()

        # Histogram of Band Gaps
        if 'band_gap' in df.columns:
            plt.figure(figsize=(8, 6))
            plt.hist(df['band_gap'].dropna(), bins=20, edgecolor='black')
            plt.xlabel('Band Gap (eV)')
            plt.ylabel('Frequency')
            plt.title('Band Gap Distribution')
            plt.savefig(f"{DATA_DIR}/band_gap_distribution.png")
            plt.close()

        # Scatter Plot: Band Gap vs Formation Energy
        if 'band_gap' in df.columns and 'formation_energy_per_atom' in df.columns:
            plt.figure(figsize=(8, 6))
            plt.scatter(df['band_gap'], df['formation_energy_per_atom'], alpha=0.6)
            plt.xlabel('Band Gap (eV)')
            plt.ylabel('Formation Energy (eV/atom)')
            plt.title('Band Gap vs Formation Energy')
            plt.savefig(f"{DATA_DIR}/bandgap_vs_formation_energy.png")
            plt.close()

if __name__ == "__main__":
    collector = DataCollector()
    # Load data from a saved CSV file instead of fetching new data
    compounds_df = pd.read_csv("/Users/Student/Desktop/chalcogenide-study/data/chalcogenides_20250105_2111.csv")
    collector.visualize_data(compounds_df)

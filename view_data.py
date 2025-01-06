import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from config import DATA_DIR

class DataVisualizer:
    def __init__(self, filename):
        self.filepath = os.path.join(DATA_DIR, filename)
        self.df = pd.read_csv(self.filepath)

    def visualize_data(self):
        print("\n📊 Starting Exploratory Data Analysis (EDA)...")

        # Distribution of Band Gap
        plt.figure(figsize=(8, 6))
        sns.histplot(self.df['band_gap'], bins=30, kde=True)
        plt.xlabel('Band Gap (eV)')
        plt.ylabel('Frequency')
        plt.title('Band Gap Distribution')
        plt.savefig(f"{DATA_DIR}/band_gap_distribution.png")
        plt.close()

        # Distribution of Formation Energy
        plt.figure(figsize=(8, 6))
        sns.histplot(self.df['formation_energy_per_atom'], bins=30, kde=True)
        plt.xlabel('Formation Energy per Atom (eV)')
        plt.ylabel('Frequency')
        plt.title('Formation Energy Distribution')
        plt.savefig(f"{DATA_DIR}/formation_energy_distribution.png")
        plt.close()

        # Scatter Plot: Band Gap vs Formation Energy
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x='formation_energy_per_atom', y='band_gap', data=self.df, alpha=0.6)
        plt.xlabel('Formation Energy (eV/atom)')
        plt.ylabel('Band Gap (eV)')
        plt.title('Band Gap vs Formation Energy')
        plt.savefig(f"{DATA_DIR}/formation_vs_band_gap.png")
        plt.close()

        # Boxplot for Density and Volume
        plt.figure(figsize=(8, 6))
        sns.boxplot(data=self.df[['density', 'volume']])
        plt.title('Boxplot for Density and Volume')
        plt.savefig(f"{DATA_DIR}/boxplot_density_volume.png")
        plt.close()

        # Correlation Matrix (Numeric Columns Only)
        numeric_df = self.df.select_dtypes(include=['float64', 'int64'])
        plt.figure(figsize=(10, 8))
        correlation = numeric_df.corr()
        sns.heatmap(correlation, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
        plt.title('Correlation Matrix')
        plt.savefig(f"{DATA_DIR}/correlation_matrix.png")
        plt.close()

        # Pair Plot for Features
        pairplot_features = ['band_gap', 'formation_energy_per_atom', 'density', 'volume']
        sns.pairplot(self.df[pairplot_features], diag_kind='kde')
        plt.savefig(f"{DATA_DIR}/pairplot_features.png")
        plt.close()

        # Crystal System Distribution
        plt.figure(figsize=(8, 6))
        sns.countplot(data=self.df, x='crystal_system', order=self.df['crystal_system'].value_counts().index)
        plt.xlabel('Crystal System')
        plt.ylabel('Count')
        plt.title('Crystal System Distribution')
        plt.xticks(rotation=45)
        plt.savefig(f"{DATA_DIR}/crystal_system_distribution.png")
        plt.close()

        # Separate Metals and Semiconductors
        semiconductors = self.df[self.df['band_gap'] > 0]
        metals = self.df[self.df['band_gap'] == 0]

        # Histogram for Band Gap (Semiconductors)
        plt.figure(figsize=(8, 6))
        sns.histplot(semiconductors['band_gap'], bins=30, kde=True)
        plt.xlabel('Band Gap (eV)')
        plt.ylabel('Frequency')
        plt.title('Semiconductor Band Gap Distribution')
        plt.savefig(f"{DATA_DIR}/semiconductor_band_gap_distribution.png")
        plt.close()

        print("\n✅ Visualizations saved!")

if __name__ == "__main__":
    visualizer = DataVisualizer("chalcogenides_20250106_1353.csv")
    visualizer.visualize_data()

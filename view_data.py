import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from scipy.stats import pearsonr, spearmanr
from config import DATA_DIR

class DataAnalyzer:
    def __init__(self, filename):
        self.filepath = os.path.join(DATA_DIR, filename)
        self.df = pd.read_csv(self.filepath)
        self.numeric_df = self.df.select_dtypes(include=['float64', 'int64'])
        self.scaler = StandardScaler()

    def correlation_analysis(self):
        print("\n📊 Correlation Analysis...")
        correlations = self.numeric_df.corr()
        plt.figure(figsize=(10, 8))
        sns.heatmap(correlations, annot=True, cmap='coolwarm', fmt='.2f', linewidths=0.5)
        plt.title('Correlation Matrix')
        plt.savefig(f"{DATA_DIR}/correlation_matrix.png")
        plt.close()

        # Pearson and Spearman correlations for Band Gap vs Formation Energy
        pearson_corr, _ = pearsonr(self.df['formation_energy_per_atom'], self.df['band_gap'])
        spearman_corr, _ = spearmanr(self.df['formation_energy_per_atom'], self.df['band_gap'])
        print(f"Pearson correlation: {pearson_corr:.3f}")
        print(f"Spearman correlation: {spearman_corr:.3f}")

    def clustering_analysis(self):
        print("\n📊 Clustering Analysis...")

        # Standardize features for clustering
        scaled_data = self.scaler.fit_transform(self.numeric_df)

        # PCA for visualization
        pca = PCA(n_components=2)
        reduced_data = pca.fit_transform(scaled_data)

        # Apply KMeans clustering
        kmeans = KMeans(n_clusters=3, random_state=42)
        clusters = kmeans.fit_predict(scaled_data)
        self.df['cluster'] = clusters

        # Plot PCA with clusters
        plt.figure(figsize=(8, 6))
        sns.scatterplot(x=reduced_data[:, 0], y=reduced_data[:, 1], hue=clusters, palette='viridis')
        plt.xlabel('Principal Component 1')
        plt.ylabel('Principal Component 2')
        plt.title('PCA Clustering Analysis')
        plt.savefig(f"{DATA_DIR}/pca_clustering.png")
        plt.close()

    def trend_analysis(self):
        print("\n📊 Trend Analysis...")

        # Relationships with Band Gap
        features = ['avg_bond_length', 'electronegativity_diff', 'symmetry_deviation']
        for feature in features:
            plt.figure(figsize=(8, 6))
            sns.scatterplot(x=self.df[feature], y=self.df['band_gap'], alpha=0.6)
            plt.xlabel(feature)
            plt.ylabel('Band Gap (eV)')
            plt.title(f'Band Gap vs {feature}')
            plt.savefig(f"{DATA_DIR}/band_gap_vs_{feature}.png")
            plt.close()

        # Relationships with Formation Energy
        for feature in features:
            plt.figure(figsize=(8, 6))
            sns.scatterplot(x=self.df[feature], y=self.df['formation_energy_per_atom'], alpha=0.6)
            plt.xlabel(feature)
            plt.ylabel('Formation Energy per Atom (eV)')
            plt.title(f'Formation Energy vs {feature}')
            plt.savefig(f"{DATA_DIR}/formation_energy_vs_{feature}.png")
            plt.close()

        print("✅ Trend visualizations saved!")

if __name__ == "__main__":
    analyzer = DataAnalyzer("chalcogenides_20250106_1734.csv")
    analyzer.correlation_analysis()
    analyzer.clustering_analysis()
    analyzer.trend_analysis()

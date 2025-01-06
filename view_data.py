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

    def get_compounds(self):
        print("\n🔍 Looking for compounds with these elements:")
        print(f"Chalcogens: {CHALCOGENS}")
        print(f"Metals: {CATIONS}")

        try:
            compounds_data = []
            with MPRester(self.api_key) as mpr:
                for metal in CATIONS:
                    for chalcogen in CHALCOGENS:
                        print(f"\nLooking for {metal}-{chalcogen} compounds...")

                        # Use the updated API v3 query
                        entries = mpr.materials.search(
                            elements=[metal, chalcogen],
                            num_elements=2,
                            fields=["material_id", "formula_pretty", "volume", "density", "symmetry", "nsites", "elements", "chemsys"]
                        )

                        print(f"Found {len(entries)} compounds")

                        for entry in entries:
                            # Debug available fields
                            if len(compounds_data) == 0:
                                print("\nDebug: Available data fields:")
                                print(vars(entry).keys())

                            # Safely access symmetry data
                            symmetry_data = getattr(entry, 'symmetry', None)
                            crystal_system = None
                            if symmetry_data:
                                crystal_system = str(getattr(symmetry_data, 'crystal_system', None))

                            # Convert elements to strings for serialization
                            elements = [str(e) for e in getattr(entry, 'elements', [])]

                            # Collect data
                            data = {
                                'material_id': getattr(entry, 'material_id', None),
                                'formula': getattr(entry, 'formula_pretty', None),
                                'volume': getattr(entry, 'volume', None),
                                'density': getattr(entry, 'density', None),
                                'crystal_system': crystal_system,
                                'nsites': getattr(entry, 'nsites', None),
                                'elements': elements,
                                'chemsys': getattr(entry, 'chemsys', None),
                                'metal': metal,
                                'chalcogen': chalcogen
                            }
                            compounds_data.append(data)

                            # Debug first compound
                            if len(compounds_data) == 1:
                                print("\nDebug: First compound data:")
                                print(json.dumps(data, indent=2))

            if not compounds_data:
                print("No compounds found!")
                return None

            # Convert to DataFrame
            df = pd.DataFrame(compounds_data)
            print(f"\nProcessed {len(df)} total compounds")

            # Check columns
            print("\nColumns in my dataset:")
            for col in df.columns:
                non_null = df[col].count()
                print(f"{col}: {non_null} non-null values")

            return df

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("API Key being used:", self.api_key[:5] + "..." if self.api_key else "None")
            return None

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

if __name__ == "__main__":
    collector = DataCollector()
    compounds_df = collector.get_compounds()
    collector.visualize_data(compounds_df)

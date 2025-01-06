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

    def flatten_results(self, results, fields):
        """Flattens query results to extract specified fields."""
        flat_data = []
        for result in results:
            flat_entry = {}
            for field in fields:
                value = getattr(result, field, None)
                if isinstance(value, list):
                    value = tuple(value)  # Make lists hashable
                flat_entry[field] = value
            flat_data.append(flat_entry)
        return flat_data

    def clean_and_visualize(self, df):
        print("\n🧹 Cleaning and Visualizing Data...")

        # Remove duplicates
        df = df.drop_duplicates()
        print(f"After removing duplicates: {len(df)} rows")

        # Ensure 'elements' column is hashable by converting lists to strings
        if 'elements' in df.columns:
            df['elements'] = df['elements'].apply(lambda x: ', '.join(map(str, x)) if isinstance(x, list) else str(x))

        # Ensure 'chemsys' is treated as a string
        if 'chemsys' in df.columns:
            df['chemsys'] = df['chemsys'].astype(str)

        # Check if 'band_gap' column exists
        if 'band_gap' not in df.columns:
            df['band_gap'] = 0.0  # Fill missing column with default value

        # Check if 'formation_energy_per_atom' exists
        if 'formation_energy_per_atom' not in df.columns:
            df['formation_energy_per_atom'] = 0.0

        # Visualization 1: Band Gap Distribution
        plt.figure(figsize=(8, 6))
        plt.hist(df['band_gap'].dropna(), bins=30, edgecolor='black')
        plt.xlabel('Band Gap (eV)')
        plt.ylabel('Frequency')
        plt.title('Band Gap Distribution')
        plt.savefig(f"{DATA_DIR}/band_gap_distribution.png")
        plt.close()

        # Visualization 2: Formation Energy vs Band Gap
        plt.figure(figsize=(8, 6))
        plt.scatter(df['formation_energy_per_atom'].dropna(), df['band_gap'].dropna(), alpha=0.6)
        plt.xlabel('Formation Energy (eV/atom)')
        plt.ylabel('Band Gap (eV)')
        plt.title('Formation Energy vs Band Gap')
        plt.savefig(f"{DATA_DIR}/formation_vs_band_gap.png")
        plt.close()

        # Visualization 3: Crystal System Distribution
        plt.figure(figsize=(8, 6))
        df['crystal_system'].value_counts().plot(kind='bar')
        plt.xlabel('Crystal System')
        plt.ylabel('Count')
        plt.title('Crystal System Distribution')
        plt.xticks(rotation=45)
        plt.savefig(f"{DATA_DIR}/crystal_system_distribution.png")
        plt.close()

        # Visualization 4: Density vs Volume
        plt.figure(figsize=(8, 6))
        plt.scatter(df['volume'], df['density'], alpha=0.6)
        plt.xlabel('Volume (Å³)')
        plt.ylabel('Density (g/cm³)')
        plt.title('Density vs Volume')
        plt.savefig(f"{DATA_DIR}/density_vs_volume.png")
        plt.close()

        print("\n📊 Visualizations saved!")
        return df

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
                            elements = ', '.join([str(e) for e in getattr(entry, 'elements', [])])

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

            # Visualize and clean data
            df = self.clean_and_visualize(df)

            return df

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print("API Key being used:", self.api_key[:5] + "..." if self.api_key else "None")
            return None

    def save_data(self, df):
        if df is None or len(df) == 0:
            print("❌ No data to save!")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{DATA_DIR}/chalcogenides_{timestamp}.csv"

        df.to_csv(filename, index=False)
        print(f"\n👌 Saved {len(df)} compounds to {filename}")

        print("\n📊 Quick summary:")
        print(f"Total compounds: {len(df)}")
        print("\nCompounds per metal:")
        print(df['metal'].value_counts())
        print("\nCompounds per chalcogen:")
        print(df['chalcogen'].value_counts())

if __name__ == "__main__":
    collector = DataCollector()
    compounds_df = collector.get_compounds()
    collector.save_data(compounds_df)

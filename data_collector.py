import pandas as pd
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

    def save_data(self, df):
        if df is None or len(df) == 0:
            print("❌ No data to save!")
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"{DATA_DIR}/chalcogenides_{timestamp}.csv"

        df.to_csv(filename, index=False)
        print(f"\n✅ Saved {len(df)} compounds to {filename}")

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

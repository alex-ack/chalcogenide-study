import pandas as pd
import matplotlib.pyplot as plt
from mp_api.client import MPRester
import json
from datetime import datetime
import os
from pymatgen.core.structure import Structure
from pymatgen.analysis.local_env import CrystalNN
from pymatgen.core.periodic_table import Element
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
                flat_entry[field] = value
            flat_data.append(flat_entry)
        return flat_data

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
                            fields=["material_id", "formula_pretty", "volume", "density", "symmetry", "nsites", "elements", "chemsys", "structure"]
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
                                'chalcogen': chalcogen,
                                'structure': json.loads(getattr(entry, 'structure').to_json()) if getattr(entry, 'structure', None) else None
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

            # Query and merge band_gap and formation_energy_per_atom
            print("\n🔍 Querying Band Gap and Formation Energy...")
            material_ids = df['material_id'].tolist()
            with MPRester(self.api_key) as mpr:
                band_gap_data = mpr.materials.electronic_structure.search(
                    material_ids=material_ids, fields=["material_id", "band_gap"]
                )
                formation_energy_data = mpr.materials.thermo.search(
                    material_ids=material_ids, fields=["material_id", "formation_energy_per_atom"]
                )

            band_gap_flat = self.flatten_results(band_gap_data, ["material_id", "band_gap"])
            formation_energy_flat = self.flatten_results(formation_energy_data, ["material_id", "formation_energy_per_atom"])

            df_band_gap = pd.DataFrame(band_gap_flat)
            df_formation_energy = pd.DataFrame(formation_energy_flat)
            df = pd.merge(df, df_band_gap, on="material_id", how="left")
            df = pd.merge(df, df_formation_energy, on="material_id", how="left")

            # Compute additional features
            features = []
            for index, row in df.iterrows():
                try:
                    structure = Structure.from_dict(row['structure'])
                    nn = CrystalNN()
                    coordination_numbers = [nn.get_cn(structure, i) for i in range(len(structure))]
                    avg_coordination = sum(coordination_numbers) / len(coordination_numbers)
                    bond_lengths = []
                    for i in range(len(structure)):
                        neighbors = nn.get_nn_info(structure, i)
                        for n in neighbors:
                            bond_lengths.append(n['weight'])
                    avg_bond_length = sum(bond_lengths) / len(bond_lengths)

                    elements = [Element(el) for el in row['elements']]
                    electronegativity_diff = max([e.X for e in elements]) - min([e.X for e in elements])
                    radii_ratio = max([e.atomic_radius for e in elements]) / min([e.atomic_radius for e in elements])
                    avg_atomic_mass = sum([e.atomic_mass for e in elements]) / len(elements)

                    features.append({
                        'material_id': row['material_id'],
                        'avg_coordination': avg_coordination,
                        'avg_bond_length': avg_bond_length,
                        'electronegativity_diff': electronegativity_diff,
                        'radii_ratio': radii_ratio,
                        'avg_atomic_mass': avg_atomic_mass
                    })
                except Exception as e:
                    print(f"Error processing {row['material_id']}: {e}")

            df_features = pd.DataFrame(features)
            df = pd.merge(df, df_features, on='material_id', how='left')

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

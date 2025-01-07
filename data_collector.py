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

                        entries = mpr.summary.search(
                            elements=[metal, chalcogen],
                            num_elements=2,
                            fields=[
                                "material_id", "formula_pretty", "volume", "density", "symmetry",
                                "nsites", "elements", "chemsys", "band_gap", "formation_energy_per_atom",
                                "structure"
                            ]
                        )

                        print(f"Found {len(entries)} compounds")

                        for entry in entries:
                            symmetry_data = getattr(entry, 'symmetry', None)
                            crystal_system = getattr(symmetry_data, 'crystal_system', 'Unknown') if symmetry_data else 'Unknown'

                            structure = Structure.from_dict(entry.structure.as_dict()) if entry.structure else None

                            avg_coordination, avg_bond_length, electronegativity_diff, radii_ratio, avg_atomic_mass = None, None, None, None, None
                            packing_efficiency, symmetry_deviation = None, None

                            if structure:
                                try:
                                    nn = CrystalNN()
                                    coordination_numbers = [nn.get_cn(structure, i) for i in range(len(structure))]
                                    avg_coordination = sum(coordination_numbers) / len(coordination_numbers)

                                    bond_lengths = []
                                    for i in range(len(structure)):
                                        neighbors = nn.get_nn_info(structure, i)
                                        for n in neighbors:
                                            dist = structure.get_distance(i, n['site_index'])
                                            bond_lengths.append(dist)
                                    avg_bond_length = sum(bond_lengths) / len(bond_lengths)

                                    elements = [Element(el) for el in entry.elements]
                                    electronegativity_diff = max([e.X for e in elements]) - min([e.X for e in elements])
                                    radii_ratio = max([e.atomic_radius for e in elements]) / min([e.atomic_radius for e in elements])
                                    avg_atomic_mass = sum([e.atomic_mass for e in elements]) / len(elements)

                                    # Additional features
                                    packing_efficiency = entry.density / (sum([e.atomic_mass for e in elements]) / len(elements))
                                    symmetry_deviation = 1 if crystal_system not in ['Cubic', 'Hexagonal'] else 0

                                except Exception as e:
                                    print(f"Error calculating features for {entry.material_id}: {e}")

                            data = {
                                'material_id': entry.material_id,
                                'formula': entry.formula_pretty,
                                'volume': entry.volume,
                                'density': entry.density,
                                'crystal_system': crystal_system,
                                'nsites': entry.nsites,
                                'elements': ', '.join([str(el) for el in entry.elements]),
                                'chemsys': entry.chemsys,
                                'band_gap': entry.band_gap,
                                'formation_energy_per_atom': entry.formation_energy_per_atom,
                                'avg_coordination': avg_coordination,
                                'avg_bond_length': avg_bond_length,
                                'electronegativity_diff': electronegativity_diff,
                                'radii_ratio': radii_ratio,
                                'avg_atomic_mass': avg_atomic_mass,
                                'packing_efficiency': packing_efficiency,
                                'symmetry_deviation': symmetry_deviation
                            }
                            compounds_data.append(data)

            if not compounds_data:
                print("No compounds found!")
                return None

            df = pd.DataFrame(compounds_data)
            print(f"\nProcessed {len(df)} total compounds")
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
        print(f"\n📊 Saved {len(df)} compounds to {filename}")

        print("\n📊 Quick summary:")
        print(f"Total compounds: {len(df)}")
        print("\nCompounds per metal:")
        print(df['chemsys'].value_counts())

if __name__ == "__main__":
    collector = DataCollector()
    compounds_df = collector.get_compounds()
    collector.save_data(compounds_df)

# new branch
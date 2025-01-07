import pandas as pd
from mp_api.client import MPRester
from pymatgen.core.structure import Structure
from pymatgen.analysis.local_env import CrystalNN
import os
from config import API_KEY

# Configurations
DATA_DIR = "/Users/Student/Desktop/chalcogenide-study/data"
FILENAME = "test_bond_lengths.csv"

# Ensure data directory exists
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Initialize MPRester
mpr = MPRester(API_KEY)

# Define test query
elements = ["Cu", "S"]  # Test with Cu-S compounds
try:
    entries = mpr.materials.summary.search(
        elements=elements,
        num_elements=2,
        fields=["material_id", "formula_pretty", "structure"]
    )
    print(f"Found {len(entries)} compounds")

    # Process data
    data = []
    for entry in entries:
        try:
            structure = Structure.from_dict(entry.structure.as_dict())
            nn = CrystalNN()

            # Calculate bond lengths
            bond_lengths = []
            for i in range(len(structure)):
                neighbors = nn.get_nn_info(structure, i)
                for n in neighbors:
                    bond_length = structure[i].distance(n['site'])  # Euclidean distance
                    bond_lengths.append(bond_length)

            # Average bond length
            avg_bond_length = sum(bond_lengths) / len(bond_lengths) if bond_lengths else None

            # Save data
            data.append({
                'material_id': entry.material_id,
                'formula': entry.formula_pretty,
                'avg_bond_length': avg_bond_length
            })

        except Exception as e:
            print(f"Error processing {entry.material_id}: {e}")

    # Save results to CSV
    df = pd.DataFrame(data)
    filepath = os.path.join(DATA_DIR, FILENAME)
    df.to_csv(filepath, index=False)
    print(f"✅ Saved test results to {filepath}")

except Exception as e:
    print(f"❌ Error during query: {e}")

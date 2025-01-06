import pandas as pd
from mp_api.client import MPRester
from config import API_KEY

# Configuration
TEST_METALS = ['Cu']
TEST_CHALCOGENS = ['S']
FIELDS = [
    "material_id", "formula_pretty", "volume", "density", "symmetry.crystal_system",
    "nsites", "elements", "chemsys", "band_gap", "formation_energy_per_atom"
]


def test_query():
    with MPRester(API_KEY) as mpr:
        # Confirm available fields for summary endpoint
        available_fields = mpr.summary.available_fields
        print("Available Fields:", available_fields)

        # Query compounds with the `summary.search` endpoint
        results = mpr.summary.search(
            elements=TEST_METALS + TEST_CHALCOGENS,
            num_elements=2,
            band_gap=(0.01, 10.0),  # Filter out metallic compounds
            fields=FIELDS
        )

        # Process results
        data = []
        for entry in results:
            # Handle symmetry data using dot notation
            symmetry = getattr(entry, 'symmetry', None)
            crystal_system = getattr(symmetry, 'crystal_system', 'Unknown') if symmetry else 'Unknown'

            # Prepare data
            data.append({
                'material_id': entry.material_id,
                'formula': entry.formula_pretty,
                'volume': entry.volume,
                'density': entry.density,
                'crystal_system': crystal_system,
                'nsites': entry.nsites,
                # Convert Element objects to strings
                'elements': ', '.join([str(e) for e in entry.elements]),
                'chemsys': entry.chemsys,
                'band_gap': entry.band_gap,
                'formation_energy_per_atom': entry.formation_energy_per_atom
            })

        # Convert to DataFrame and save results
        df = pd.DataFrame(data)
        print(df.head())
        df.to_csv("test_query_results.csv", index=False)
        print("\n✅ Test query results saved!")


if __name__ == "__main__":
    test_query()

import pandas as pd
from mp_api.client import MPRester
from config import API_KEY


# Initialize the MPRester
def flatten_results(results, fields):
    """Flattens query results to extract specified fields."""
    flat_data = []
    for result in results:
        flat_entry = {}
        for field in fields:
            # Extract field or use None if missing
            value = getattr(result, field, None)
            flat_entry[field] = value
        flat_data.append(flat_entry)
    return flat_data

# Initialize the MPRester
with MPRester(API_KEY) as mpr:
    try:
        # Query base materials to get material_ids
        print("\n🔍 Querying Materials Data...")
        materials_data = mpr.materials.search(
            elements=["Cu", "S"], num_elements=2, fields=["material_id"]
        )
        material_ids = [entry.material_id for entry in materials_data]
        print(f"Found {len(material_ids)} material IDs.")

        # Query band_gap from electronic_structure endpoint
        print("\n🔍 Querying Band Gap Data...")
        band_gap_data = mpr.materials.electronic_structure.search(
            material_ids=material_ids, fields=["material_id", "band_gap"]
        )
        band_gap_flat = flatten_results(band_gap_data, ["material_id", "band_gap"])
        print(f"Band Gap Results: {len(band_gap_flat)} entries")

        # Query formation_energy_per_atom from thermo endpoint
        print("\n🔍 Querying Formation Energy Data...")
        formation_energy_data = mpr.materials.thermo.search(
            material_ids=material_ids, fields=["material_id", "formation_energy_per_atom"]
        )
        formation_energy_flat = flatten_results(formation_energy_data, ["material_id", "formation_energy_per_atom"])
        print(f"Formation Energy Results: {len(formation_energy_flat)} entries")

        # Convert to DataFrame
        df_band_gap = pd.DataFrame(band_gap_flat)
        df_formation_energy = pd.DataFrame(formation_energy_flat)

        # Print sample results
        print("\nBand Gap Data Sample:")
        print(df_band_gap.head())

        print("\nFormation Energy Data Sample:")
        print(df_formation_energy.head())

        # Merge the results based on material_id
        merged_df = pd.merge(df_band_gap, df_formation_energy, on="material_id", how="inner")

        # Print merged data sample
        print("\nMerged Data Sample:")
        print(merged_df.head())

    except Exception as e:
        print(f"❌ Error: {str(e)}")
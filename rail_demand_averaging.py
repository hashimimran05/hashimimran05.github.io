import pandas as pd
import os
import zipfile
import glob
import shutil

# ==========================================================
# Configuration
# ==========================================================

zip_file = (
    "/lakehouse/default/Files/11-09-2026 Updated Outputs.zip"
)

extract_folder = (
    "/lakehouse/default/Files/20260911_RailExtracted"
)

target_folder = (
    "/lakehouse/default/Files/20260911_RailAveraged"
)

os.makedirs(extract_folder, exist_ok=True)
os.makedirs(target_folder, exist_ok=True)

# ==========================================================
# Unzip
# ==========================================================

print("Extracting rail files...")

with zipfile.ZipFile(zip_file, "r") as z:
    z.extractall(extract_folder)

print("Finished extraction.")

# ==========================================================
# Find all CSV files recursively
# ==========================================================

all_csv_files = glob.glob(
    os.path.join(
        extract_folder,
        "**",
        "*.csv"
    ),
    recursive=True
)

print(f"\nFound {len(all_csv_files)} CSV files.")

# ==========================================================
# Copy GJT and Yield files unchanged
# ==========================================================

print("\nCopying GJT and Yield files...")

for source_file in all_csv_files:

    filename = os.path.basename(source_file)

    if (
        "GJT" in filename
        or "Yield" in filename
    ):

        shutil.copy2(
            source_file,
            os.path.join(
                target_folder,
                filename
            )
        )

print("Finished copying GJT and Yield files.")

# ==========================================================
# Average Demand files
# ==========================================================

print("\nCreating averaged Demand files...")

dm_files = glob.glob(
    os.path.join(
        extract_folder,
        "**",
        "*DM Demand*.csv"
    ),
    recursive=True
)

for dm_file in sorted(dm_files):

    dm_name = os.path.basename(dm_file)

    ds_name = dm_name.replace(
        "DM Demand",
        "DS Demand"
    )

    ds_matches = glob.glob(
        os.path.join(
            extract_folder,
            "**",
            ds_name
        ),
        recursive=True
    )

    if len(ds_matches) != 1:

        raise ValueError(
            f"Expected exactly one DS file:\n"
            f"{ds_name}\n"
            f"Found: {len(ds_matches)}"
        )

    ds_file = ds_matches[0]

    dm = pd.read_csv(dm_file)
    ds = pd.read_csv(ds_file)

    # ------------------------------------------------------
    # Validation
    # ------------------------------------------------------

    if len(dm) != len(ds):

        raise ValueError(
            f"Row mismatch:\n"
            f"{dm_name}\n"
            f"{ds_name}"
        )

    if not dm.iloc[:, :2].equals(
        ds.iloc[:, :2]
    ):

        raise ValueError(
            f"OD mismatch:\n"
            f"{dm_name}\n"
            f"{ds_name}"
        )

    # ------------------------------------------------------
    # Average demand column
    # ------------------------------------------------------

    avg = dm.copy()

    avg.iloc[:, 2] = (
        pd.to_numeric(dm.iloc[:, 2])
        + pd.to_numeric(ds.iloc[:, 2])
    ) / 2

    avg_name = dm_name.replace(
        "DM Demand",
        "AVG Demand"
    )

    avg_output = os.path.join(
        target_folder,
        avg_name
    )

    avg.to_csv(
        avg_output,
        index=False
    )

    print(f"Created: {avg_name}")

# ==========================================================
# Validation
# ==========================================================

files = os.listdir(target_folder)

avg_count = len(
    [
        f for f in files
        if "AVG Demand" in f
    ]
)

gjt_count = len(
    [
        f for f in files
        if "GJT" in f
    ]
)

yield_count = len(
    [
        f for f in files
        if "Yield" in f
    ]
)

print("\n-----------------------------")
print("Validation")
print("-----------------------------")
print(f"AVG Demand files : {avg_count}")
print(f"GJT files        : {gjt_count}")
print(f"Yield files      : {yield_count}")
print(f"Total files      : {len(files)}")

print("\nFinished.")
print(f"Output folder: {target_folder}")

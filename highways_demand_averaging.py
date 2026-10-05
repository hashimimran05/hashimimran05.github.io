import pandas as pd
import os
import glob
import shutil

# ------------------------------------------------------------------
# Configuration
# ------------------------------------------------------------------

source_folder = (
    "/lakehouse/default/Files/aggregated_final_2037_2052"
)

target_folder = (
    "/lakehouse/default/Files/aggregated_final_avg"
)

os.makedirs(target_folder, exist_ok=True)

print(f"Source folder : {source_folder}")
print(f"Target folder : {target_folder}")

# ------------------------------------------------------------------
# Copy Distance and Time files unchanged
# ------------------------------------------------------------------

print("\nCopying Distance and Time files...")

for source_file in glob.glob(f"{source_folder}/*.csv"):

    filename = os.path.basename(source_file)

    if (
        filename.startswith("Dis_")
        or filename.startswith("Tim_")
    ):
        shutil.copy2(
            source_file,
            os.path.join(
                target_folder,
                filename
            )
        )

print("Distance and Time files copied.")

# ------------------------------------------------------------------
# Create averaged demand files
# ------------------------------------------------------------------

print("\nCreating averaged demand files...")

dm_files = sorted(
    glob.glob(
        f"{source_folder}/Demand_DM_*.csv"
    )
)

for dm_file in dm_files:

    ds1_file = dm_file.replace(
        "Demand_DM_",
        "Demand_DS1_"
    )

    ds2_file = dm_file.replace(
        "Demand_DM_",
        "Demand_DS2_"
    )

    if not os.path.exists(ds1_file):
        raise FileNotFoundError(
            f"Matching DS1 file not found:\n{ds1_file}"
        )

    if not os.path.exists(ds2_file):
        raise FileNotFoundError(
            f"Matching DS2 file not found:\n{ds2_file}"
        )

    dm = pd.read_csv(
        dm_file,
        header=None
    )

    ds1 = pd.read_csv(
        ds1_file,
        header=None
    )

    ds2 = pd.read_csv(
        ds2_file,
        header=None
    )

    # --------------------------------------------------------------
    # Safety checks
    # --------------------------------------------------------------

    for scenario_name, scenario_df in [
        ("DS1", ds1),
        ("DS2", ds2)
    ]:

        if len(dm) != len(scenario_df):
            raise ValueError(
                f"Row count mismatch:\n"
                f"{os.path.basename(dm_file)}\n"
                f"{scenario_name}"
            )

        if not dm.iloc[:, :2].equals(
            scenario_df.iloc[:, :2]
        ):
            raise ValueError(
                f"OD mismatch:\n"
                f"{os.path.basename(dm_file)}\n"
                f"{scenario_name}"
            )

    # --------------------------------------------------------------
    # AVG DS1
    # --------------------------------------------------------------

    avg_ds1 = dm.copy()

    avg_ds1[2] = (
        pd.to_numeric(dm[2])
        + pd.to_numeric(ds1[2])
    ) / 2

    avg_ds1_filename = (
        os.path.basename(dm_file)
        .replace(
            "Demand_DM_",
            "Demand_AVG_DS1_"
        )
    )

    avg_ds1.to_csv(
        os.path.join(
            target_folder,
            avg_ds1_filename
        ),
        header=False,
        index=False
    )

    # --------------------------------------------------------------
    # AVG DS2
    # --------------------------------------------------------------

    avg_ds2 = dm.copy()

    avg_ds2[2] = (
        pd.to_numeric(dm[2])
        + pd.to_numeric(ds2[2])
    ) / 2

    avg_ds2_filename = (
        os.path.basename(dm_file)
        .replace(
            "Demand_DM_",
            "Demand_AVG_DS2_"
        )
    )

    avg_ds2.to_csv(
        os.path.join(
            target_folder,
            avg_ds2_filename
        ),
        header=False,
        index=False
    )

    print(f"Created: {avg_ds1_filename}")
    print(f"Created: {avg_ds2_filename}")

# ------------------------------------------------------------------
# File count validation
# ------------------------------------------------------------------

files = os.listdir(target_folder)

avg_ds1_count = len(
    [
        f for f in files
        if f.startswith("Demand_AVG_DS1_")
    ]
)

avg_ds2_count = len(
    [
        f for f in files
        if f.startswith("Demand_AVG_DS2_")
    ]
)

dis_count = len(
    [
        f for f in files
        if f.startswith("Dis_")
    ]
)

tim_count = len(
    [
        f for f in files
        if f.startswith("Tim_")
    ]
)

print("\n-----------------------------")
print("Validation")
print("-----------------------------")
print(f"Demand_AVG_DS1 files : {avg_ds1_count}")
print(f"Demand_AVG_DS2 files : {avg_ds2_count}")
print(f"Dis files            : {dis_count}")
print(f"Tim files            : {tim_count}")
print(f"Total files          : {len(files)}")

print("\nFinished.")
print(f"New folder: {target_folder}")

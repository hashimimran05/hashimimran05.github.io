import pandas as pd
import os
import numpy as np

# ==========================================================
# Configuration
# ==========================================================

lookup_file = "/lakehouse/default/Files/sat2wita.xlsx"

year_config = {
    2037: {
        "year_name": "OY",
        "root": "/lakehouse/default/Files/WITA_RESTRUCTURED"
    },
    2052: {
        "year_name": "FY",
        "root": "/lakehouse/default/Files/WITA_RESTRUCTURED"
    }
}

output_folder = (
    "/lakehouse/default/Files/aggregated_final_2037_2052"
)

os.makedirs(output_folder, exist_ok=True)

# ==========================================================
# Load SATURN -> WITA lookup
# ==========================================================

s2w = pd.read_excel(lookup_file)

origin_lookup = s2w.rename(
    columns={
        "Saturn_Zone": "origin_saturn",
        "WITA_Zone": "origin_wita"
    }
)

destination_lookup = s2w.rename(
    columns={
        "Saturn_Zone": "destination_saturn",
        "WITA_Zone": "destination_wita"
    }
)

# ==========================================================
# Create full WITA OD matrix index
# ==========================================================

all_wita = sorted(
    s2w["WITA_Zone"].unique()
)

full_index = pd.MultiIndex.from_product(
    [all_wita, all_wita],
    names=[
        "origin_wita",
        "destination_wita"
    ]
)

# ==========================================================
# Functions
# ==========================================================

def apply_wita_lookup(df):

    df = df.merge(
        origin_lookup,
        on="origin_saturn",
        how="left"
    )

    df = df.merge(
        destination_lookup,
        on="destination_saturn",
        how="left"
    )

    return df


def aggregate_demand(demand_file):

    demand_df = pd.read_csv(
        demand_file,
        header=None,
        names=[
            "origin_saturn",
            "destination_saturn",
            "demand"
        ]
    )

    demand_df = apply_wita_lookup(demand_df)

    wita_demand = (
        demand_df
        .groupby(
            ["origin_wita", "destination_wita"],
            as_index=False
        )["demand"]
        .sum()
    )

    wita_demand = (
        wita_demand
        .set_index(
            ["origin_wita", "destination_wita"]
        )
        .reindex(
            full_index,
            fill_value=0
        )
        .reset_index()
    )

    return demand_df, wita_demand


def aggregate_weighted_skim(
    skim_file,
    detailed_demand_df
):

    skim_df = pd.read_csv(
        skim_file,
        header=None,
        names=[
            "origin_saturn",
            "destination_saturn",
            "skim_value"
        ]
    )

    skim_df = skim_df.merge(
        detailed_demand_df[
            [
                "origin_saturn",
                "destination_saturn",
                "demand"
            ]
        ],
        on=[
            "origin_saturn",
            "destination_saturn"
        ],
        how="left"
    )

    skim_df = apply_wita_lookup(skim_df)

    skim_df["weighted_value"] = (
        skim_df["skim_value"]
        * skim_df["demand"]
    )

    grouped = (
        skim_df
        .groupby(
            ["origin_wita", "destination_wita"],
            as_index=False
        )
        .agg(
            {
                "weighted_value": "sum",
                "demand": "sum"
            }
        )
    )

    grouped["skim_value"] = 0.0

    mask = grouped["demand"] != 0

    grouped.loc[mask, "skim_value"] = (
        grouped.loc[mask, "weighted_value"]
        / grouped.loc[mask, "demand"]
    )

    result = grouped[
        [
            "origin_wita",
            "destination_wita",
            "skim_value"
        ]
    ]

    result = (
        result
        .set_index(
            ["origin_wita", "destination_wita"]
        )
        .reindex(
            full_index,
            fill_value=0
        )
        .reset_index()
    )

    result["skim_value"] = (
        result["skim_value"]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
    )

    return result


# ==========================================================
# Main Process
# ==========================================================

for year in [2037, 2052]:

    year_name = year_config[year]["year_name"]
    root = year_config[year]["root"]

    for sc in ["DM", "DS1", "DS2"]:

        demand_folder = (
            f"{root}/{year} Core OD {sc} Demand"
        )

        skim_folder = (
            f"{root}/{year} Core OD {sc} Skims"
        )

        for peak in ["AM", "IP", "PM", "OP"]:

            for uc in range(1, 10):

                print(
                    f"Processing "
                    f"{year} "
                    f"{sc} "
                    f"{peak} "
                    f"UC{uc}"
                )

                # ------------------------------------------
                # Demand
                # ------------------------------------------

                demand_file = (
                    f"{demand_folder}/"
                    f"{year}_{year_name}_{sc}_{peak}_MAT_UC{uc}.txt"
                )

                if not os.path.exists(demand_file):
                    print(
                        f"Missing demand file: {demand_file}"
                    )
                    continue

                detailed_demand_df, wita_demand_df = (
                    aggregate_demand(demand_file)
                )

                output_demand = (
                    f"{output_folder}/"
                    f"Demand_{sc}_{year}_{peak}_UC{uc}.csv"
                )

                wita_demand_df.to_csv(
                    output_demand,
                    header=False,
                    index=False
                )

                print(
                    "Demand total:",
                    round(
                        detailed_demand_df[
                            "demand"
                        ].sum(),
                        6
                    )
                )

                # ------------------------------------------
                # Distance
                # ------------------------------------------

                dis_file = (
                    f"{skim_folder}/"
                    f"{year}_{year_name}_{sc}_{peak}_DIS_UC{uc}.txt"
                )

                dis_df = aggregate_weighted_skim(
                    dis_file,
                    detailed_demand_df
                )

                dis_output = (
                    f"{output_folder}/"
                    f"Dis_{sc}_{year}_{peak}_UC{uc}.csv"
                )

                dis_df.to_csv(
                    dis_output,
                    header=False,
                    index=False
                )

                print(
                    "DIS rows:",
                    len(dis_df)
                )

                # ------------------------------------------
                # Time
                # ------------------------------------------

                tim_file = (
                    f"{skim_folder}/"
                    f"{year}_{year_name}_{sc}_{peak}_TIM_UC{uc}.txt"
                )

                tim_df = aggregate_weighted_skim(
                    tim_file,
                    detailed_demand_df
                )

                tim_output = (
                    f"{output_folder}/"
                    f"Tim_{sc}_{year}_{peak}_UC{uc}.csv"
                )

                tim_df.to_csv(
                    tim_output,
                    header=False,
                    index=False
                )

                print(
                    "TIM rows:",
                    len(tim_df)
                )

                print(
                    "TIM min/max:",
                    tim_df["skim_value"].min(),
                    tim_df["skim_value"].max()
                )

print("\nFinished recreating aggregated outputs.")
print(f"Output folder: {output_folder}")

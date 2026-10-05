import os

highway_variants = [
    "DS1",
    "DS2",
    "AVG_DS1",
    "AVG_DS2"
]

rail_variants = [
    "RAW",
    "AVG"
]

user_class_sets = [
    [1, 2],
    [1, 2, 4, 5]
]

template_file = (
    "/lakehouse/default/Files/"
    "02_TUBA_Scheme_File_WITA.txt"
)

for highway_variant in highway_variants:

    for rail_variant in rail_variants:

        for user_classes in user_class_sets:

            print(
                f"\nGenerating "
                f"{highway_variant} | "
                f"{rail_variant} | "
                f"{user_classes}"
            )

            uc_string = "".join(
                str(x)
                for x in user_classes
            )

            output_file = (
                "/lakehouse/default/Files/WITA_Scheme_Files/"
                f"WITA_{highway_variant}"
                f"_UC{uc_string}"
                f"_RAIL{rail_variant}.txt"
            )

            # ==========================================================
            # SCHEME FILE OUTPUT FOLDER
            # ==========================================================

            scheme_folder = (
                "/lakehouse/default/Files/WITA_TestRuns_SchemeFiles_CHANGED"
            )

            os.makedirs(
                scheme_folder,
                exist_ok=True
            )

            # ==========================================================
            # HIGHWAY FOLDERS
            # ==========================================================

            highway_noav_folder = (
                r"C:\Users\LocalUser\Downloads"
                r"\aggregated_final_2037_2052 1"
            )

            highway_avg_folder = (
                r"C:\Users\LocalUser\Downloads"
                r"\aggregated_final_Averaged"
            )

            # ==========================================================
            # RAIL FOLDERS
            # ==========================================================

            rail_raw_folder = (
                r"C:\Users\LocalUser\Downloads"
                r"\WITA_TestRuns"
                r"\Rail"
                r"\20260911_RailExtracted"
            )

            rail_avg_folder = (
                r"C:\Users\LocalUser\Downloads"
                r"\WITA_TestRuns"
                r"\Rail"
                r"\20260911_RailAveraged"
            )

            # ==========================================================
            # OUTPUT FILE NAME
            # ==========================================================

            uc_string = "".join(
                str(x)
                for x in user_classes
            )

            output_file = (
                f"{scheme_folder}/"
                f"WITA_{highway_variant}"
                f"_UC{uc_string}"
                f"_RAIL{rail_variant}.txt"
            )

            # ==========================================================
            # YEARS
            # ==========================================================

            years = [2037, 2052]

            rail_year_mapping = {
                2037: 2036,
                2052: 2051
            }

            # ==========================================================
            # LOOKUPS
            # ==========================================================

            peak_lookup = {
                "AM": 1,
                "IP": 2,
                "PM": 3,
                "OP": 4
            }

            highway_factors = {
                "V": 1,
                "D": 0.001,
                "T": 0.000278,
                "R": 0.001
            }

            rail_factors = {
                "P": 1,
                "T": 0.016667,
                "C1": 0.010000
            }

            highway_userclass_lookup = {
                1: (1, 1, 1),
                2: (1, 2, 1),
                4: (2, 1, 1),
                5: (2, 2, 1)
            }

            rail_userclass_lookup = {
                6: (8, 1, 2),
                7: (8, 2, 2),
                8: (8, 3, 2)
            }

            rail_userclasses = {
                "B": 6,
                "C": 7,
                "O": 8
            }

            # ==========================================================
            # HIGHWAY VARIANT LOGIC
            # ==========================================================

            if highway_variant == "DS1":

                highway_folder = highway_noav_folder

                dm_demand = "Demand_DM"
                ds_demand = "Demand_DS1"

                dm_dis = "Dis_DM"
                ds_dis = "Dis_DS1"

                dm_tim = "Tim_DM"
                ds_tim = "Tim_DS1"

            elif highway_variant == "DS2":

                highway_folder = highway_noav_folder

                dm_demand = "Demand_DM"
                ds_demand = "Demand_DS2"

                dm_dis = "Dis_DM"
                ds_dis = "Dis_DS2"

                dm_tim = "Tim_DM"
                ds_tim = "Tim_DS2"

            elif highway_variant == "AVG_DS1":

                highway_folder = highway_avg_folder

                dm_demand = "Demand_AVG_DS1"
                ds_demand = "Demand_AVG_DS1"

                dm_dis = "Dis_DM"
                ds_dis = "Dis_DS1"

                dm_tim = "Tim_DM"
                ds_tim = "Tim_DS1"

            elif highway_variant == "AVG_DS2":

                highway_folder = highway_avg_folder

                dm_demand = "Demand_AVG_DS2"
                ds_demand = "Demand_AVG_DS2"

                dm_dis = "Dis_DM"
                ds_dis = "Dis_DS2"

                dm_tim = "Tim_DM"
                ds_tim = "Tim_DS2"

            # ==========================================================
            # RAIL VARIANT LOGIC
            # ==========================================================

            if rail_variant == "RAW":

                rail_folder = rail_raw_folder

                dm_rail = "DM"
                ds_rail = "DS"

            elif rail_variant == "AVG":

                rail_folder = rail_avg_folder

                dm_rail = "AVG"
                ds_rail = "AVG"

            # ==========================================================
            # READ TEMPLATE
            # ==========================================================

            with open(template_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

            user_classes_start = None
            input_start = None
            sectors_start = None

            for i, line in enumerate(lines):

                if line.strip() == "USER_CLASSES":
                    user_classes_start = i

                if line.strip() == "INPUT_MATRICES":
                    input_start = i

                if line.strip() == "SECTORS":
                    sectors_start = i

            header_lines = lines[:user_classes_start]

            footer_lines = lines[sectors_start:]

            # ==========================================================
            # BUILD USER_CLASSES SECTION
            # ==========================================================

            user_class_lines = []

            user_class_lines.append(
                "USER_CLASSES\n"
            )

            user_class_lines.append(
                "*no.     Veh/submode     purpose       person_type\n"
            )

            # ----------------------------------------------------------
            # Highway classes
            # ----------------------------------------------------------

            for uc in user_classes:

                veh_submode, purpose, person_type = (
                    highway_userclass_lookup[uc]
                )

                user_class_lines.append(
                    f"{uc:>4}"
                    f"{veh_submode:>11}"
                    f"{purpose:>15}"
                    f"{person_type:>15}\n"
                )

            # ----------------------------------------------------------
            # Rail classes always included
            # ----------------------------------------------------------

            for uc, values in rail_userclass_lookup.items():

                veh_submode, purpose, person_type = values

                user_class_lines.append(
                    f"{uc:>4}"
                    f"{veh_submode:>11}"
                    f"{purpose:>15}"
                    f"{person_type:>15}\n"
                )

            print("".join(user_class_lines))

            # ==========================================================
            # BUILD INPUT_MATRICES
            # ==========================================================

            new_matrix_lines = []

            new_matrix_lines.append(
                "INPUT_MATRICES\n"
            )

            new_matrix_lines.append(
                "* no.  userclasses timeslice  type  format  scenario  year      factor    filename\n"
            )

            row_number = 1

            # ==========================================================
            # HIGHWAYS
            # ==========================================================

            for year in years:

                for peak, timeslice in peak_lookup.items():

                    for uc in user_classes:

                        # ------------------------------------------
                        # DM
                        # ------------------------------------------

                        dm_items = [

                            (
                                "V",
                                highway_factors["V"],
                                f"{dm_demand}_{year}_{peak}_UC{uc}.csv"
                            ),

                            (
                                "D",
                                highway_factors["D"],
                                f"{dm_dis}_{year}_{peak}_UC{uc}.csv"
                            ),

                            (
                                "T",
                                highway_factors["T"],
                                f"{dm_tim}_{year}_{peak}_UC{uc}.csv"
                            )

                        ]

                        for matrix_type, factor, filename in dm_items:

                            full_path = (
                                f"{highway_folder}\\{filename}"
                            )

                            new_matrix_lines.append(
                                f"{row_number:>5}"
                                f"{uc:>10}"
                                f"{timeslice:>10}"
                                f"{matrix_type:>8}"
                                f"{2:>8}"
                                f"{0:>10}"
                                f"{year:>8}"
                                f"{factor:>12.6f}"
                                f"    {full_path}\n"
                            )

                            row_number += 1

                        # ------------------------------------------
                        # DS1
                        # ------------------------------------------

                        ds_items = [

                            (
                                "V",
                                highway_factors["V"],
                                f"{ds_demand}_{year}_{peak}_UC{uc}.csv"
                            ),

                            (
                                "D",
                                highway_factors["D"],
                                f"{ds_dis}_{year}_{peak}_UC{uc}.csv"
                            ),

                            (
                                "T",
                                highway_factors["T"],
                                f"{ds_tim}_{year}_{peak}_UC{uc}.csv"
                            )

                        ]

                        for matrix_type, factor, filename in ds_items:

                            full_path = (
                                f"{highway_folder}\\{filename}"
                            )

                            new_matrix_lines.append(
                                f"{row_number:>5}"
                                f"{uc:>10}"
                                f"{timeslice:>10}"
                                f"{matrix_type:>8}"
                                f"{2:>8}"
                                f"{1:>10}"
                                f"{year:>8}"
                                f"{factor:>12.6f}"
                                f"    {full_path}\n"
                            )

                            row_number += 1

            # ==========================================================
            # REFERENCE ROWS (R)
            # ==========================================================

            for uc in user_classes:

                reference_file = (
                    f"{highway_folder}\\"
                    f"Dis_DM_2037_AM_UC{uc}.csv"
                )

                new_matrix_lines.append(
                    f"{row_number:>5}"
                    f"{uc:>10}"
                    f"{'X':>10}"
                    f"{'R':>8}"
                    f"{2:>8}"
                    f"{'X':>10}"
                    f"{'XXXX':>8}"
                    f"{highway_factors['R']:>12.6f}"
                    f"    {reference_file}\n"
                )

                row_number += 1

            # ==========================================================
            # RAIL
            # ==========================================================

            for wita_year, rail_year in (
                rail_year_mapping.items()
            ):

                for timeslice in [1, 2, 3, 4]:

                    # ------------------------------------------
                    # Scenario 0
                    # ------------------------------------------

                    for letter, uc in rail_userclasses.items():

                        dm_items = [

                            (
                                "P",
                                rail_factors["P"],
                                f"194 {rail_year} {dm_rail} Demand {letter}.csv"
                            ),

                            (
                                "T",
                                rail_factors["T"],
                                f"194 {rail_year} DM GJT {letter}.csv"
                            ),

                            (
                                "C1",
                                rail_factors["C1"],
                                f"194 {rail_year} DM Yield {letter}.csv"
                            )

                        ]

                        for matrix_type, factor, filename in dm_items:

                            full_path = (
                                f"{rail_folder}\\{filename}"
                            )

                            new_matrix_lines.append(
                                f"{row_number:>5}"
                                f"{uc:>10}"
                                f"{timeslice:>10}"
                                f"{matrix_type:>8}"
                                f"{2:>8}"
                                f"{0:>10}"
                                f"{wita_year:>8}"
                                f"{factor:>12.6f}"
                                f"    {full_path}\n"
                            )

                            row_number += 1

                    # ------------------------------------------
                    # Scenario 1
                    # ------------------------------------------

                    for letter, uc in rail_userclasses.items():

                        ds_items = [

                            (
                                "P",
                                rail_factors["P"],
                                f"194 {rail_year} {ds_rail} Demand {letter}.csv"
                            ),

                            (
                                "T",
                                rail_factors["T"],
                                f"194 {rail_year} DS GJT {letter}.csv"
                            ),

                            (
                                "C1",
                                rail_factors["C1"],
                                f"194 {rail_year} DS Yield {letter}.csv"
                            )

                        ]

                        for matrix_type, factor, filename in ds_items:

                            full_path = (
                                f"{rail_folder}\\{filename}"
                            )

                            new_matrix_lines.append(
                                f"{row_number:>5}"
                                f"{uc:>10}"
                                f"{timeslice:>10}"
                                f"{matrix_type:>8}"
                                f"{2:>8}"
                                f"{1:>10}"
                                f"{wita_year:>8}"
                                f"{factor:>12.6f}"
                                f"    {full_path}\n"
                            )

                            row_number += 1

            # ==========================================================
            # WRITE FILE
            # ==========================================================

            print("\n" + "=" * 60)
            print(
                f"Creating "
                f"{highway_variant} | "
                f"{rail_variant} | "
                f"UC{uc_string}"
            )
            print("=" * 60)

            final_lines = (
                header_lines
                + user_class_lines
                + new_matrix_lines
                + footer_lines
            )

            with open(
                output_file,
                "w",
                encoding="utf-8"
            ) as f:
                f.writelines(final_lines)

            print("Created:")
            print(output_file)

            print()
            print("INPUT_MATRICES rows:")
            print(row_number - 1)

            print()
            print("Total file lines:")
            print(len(final_lines))

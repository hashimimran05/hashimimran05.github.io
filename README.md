# Hashim Imran | Transport Modelling Automation

Portfolio: https://hashimimran05.github.io

GitHub: https://github.com/hashimimran05

This repository contains the portfolio website and four Python workflows for preparing **WITA (Wider Impacts in Transport Appraisal)** inputs. Open `index.html` for the website, or follow the workflow documentation below.

WITA is the Department for Transport's wider-impacts appraisal software. It runs alongside TUBA and reuses the shared scheme-file format, economics inputs, and transport matrices, with additional economic and correspondence data for wider-impact calculations. This repository documents the input-preparation work around that process; it does not contain the WITA application itself.

## Project Overview

This project brings together four scripts that automate repeatable file-processing steps across transport scenarios, model years, time periods, and user classes. The scripts use pandas and NumPy for tabular processing, alongside Python's file, archive, and text-handling tools.

| Script | Purpose | Techniques |
| --- | --- | --- |
| [WITA zone aggregation](tuba_aggregation.py) | Map transport-model zones to WITA zones, sum demand, and calculate flow-weighted distance and time values | Table joins, grouped aggregation, weighted means, complete origin-destination indexing |
| [Highway demand averaging](highways_demand_averaging.py) | Average DM demand separately with DS1 and DS2 demand; copy distance and time files | Batch processing, paired-file discovery, row and origin-destination checks |
| [Rail demand averaging](rail_demand_averaging.py) | Extract rail inputs, average matching DM and DS demand, and copy GJT and Yield files | ZIP extraction, recursive discovery, unique-match validation |
| [Shared WITA/TUBA scheme-file generation](scheme_file_generation.py) | Generate combinations of highway variants, rail variants, and user-class sets in the shared scheme-file format | Configuration mappings, nested iteration, formatted text generation |

DM denotes Do Minimum; DS denotes Do Something. OD means origin-destination. A skim is a table of journey attributes, such as distance or travel time, between zones.

## Workflow

1. Aggregate highway demand and skims from transport-model zones to WITA zones.
2. Create averaged highway demand files from the aggregated outputs.
3. Separately extract and average rail demand files.
4. Generate shared-format scheme files referencing the chosen highway and rail variants for WITA/TUBA runs.

The scheme generator currently defines **16 combinations**: four highway variants x two rail variants x two highway user-class sets. This is the configured scope, not a claim that the files have been generated or validated in this repository.

## Methods

### WITA zone aggregation

A transport-model-to-WITA lookup assigns each source zone to a target WITA zone. Demand is summed for each target OD pair. Distance and time are flow-weighted using demand:

`weighted skim = sum(skim value * demand) / sum(demand)`

The output includes every combination of target origin and destination zone. Missing combinations are filled with zero. The current implementation also uses zero for zero-demand or non-finite weighted results.

Illustrative calculation with invented values: two source movements mapping to the same WITA OD pair have demands of 10 and 30, and distances of 4 and 8. Aggregated demand is 40; weighted distance is (10 x 4 + 30 x 8) / 40 = 7.

### Scenario demand averaging

`averaged demand = (DM demand + DS demand) / 2`

For highways, the script calculates this separately for DS1 and DS2. Both averaging scripts require the same row count and matching first two columns in the same order before averaging the third column.

Illustrative calculation with invented values: DM demand of 100 and DS demand of 140 produce averaged demand of 120. This averages scenarios, not model years. It is a project-specific preparation choice, not a statement that WITA requires every input to be averaged this way.

### WITA cost averaging context

The WITA manual describes a separate process for flow-weighted generalised costs. WITA aggregates costs spatially, across relevant purposes and time periods, and sometimes across modes. Its four cost-averaging methods use fixed or variable weights and may average over modes. The aggregation script here prepares flow-weighted distance and time values; the arithmetic DM/DS demand-average scripts prepare scenario files. They should not be described as the same WITA method.

### Scheme generation

WITA runs alongside TUBA and reuses the shared Scheme File, Economics Data File, and input matrices. The generator replaces the template's user-class and input-matrix sections, preserving the header and the content beginning at SECTORS. It writes matrix references with scenario numbers, time slices, model years, and configured conversion factors. Averaged variants reference the same averaged demand for both scenarios while retaining scenario-specific distance/time or GJT/Yield files.

## Files and Dependencies

The original source was supplied as four text files. This repository presents it as Python scripts; processing logic is unchanged.

Install the dependencies in a Python environment:

```sh
python -m pip install -r requirements.txt
```

The requirements list reflects imports and Excel input support. Versions are not pinned because the original execution environment was not supplied.

These are environment-specific workflow scripts. Their paths currently point to a Lakehouse-style filesystem, and the scheme generator writes Windows paths into its outputs. Configure the scripts before running them locally.

| Script | Required inputs | Configuration to update |
| --- | --- | --- |
| WITA zone aggregation | Excel lookup with Saturn_Zone and WITA_Zone columns; headerless three-column demand/distance/time files | lookup_file, year_config, output_folder |
| Highway averaging | Headerless three-column Demand_DM, Demand_DS1, Demand_DS2 CSVs and Dis_/Tim_ CSVs | source_folder, target_folder |
| Rail averaging | ZIP containing matching DM Demand and DS Demand CSVs with headers; GJT/Yield CSVs | zip_file, extract_folder, target_folder |
| Scheme generation | Existing scheme template containing USER_CLASSES, INPUT_MATRICES, and SECTORS | template_file, scheme_folder, highway/rail folders, years, mappings and factors |

The original filenames encode years, scenarios, time periods, and user classes. Preserve the expected naming conventions or adapt the filename construction in the scripts.

After configuring paths and supplying the inputs, the workflow commands are:

```sh
python tuba_aggregation.py
python highways_demand_averaging.py
python rail_demand_averaging.py
python scheme_file_generation.py
```

The rail processing branch can run independently of the highway branch. The generated scheme paths must point to the actual matrix locations on the machine that will run WITA/TUBA, including any subfolders in extracted rail inputs.

## Validation and Current Limits

- All four scripts passed Python syntax compilation during portfolio preparation.
- Full processing has not been run for this repository: source matrices, the Excel lookup, the rail archive, and the scheme template were not supplied.
- The averaging scripts reject mismatched row counts or OD ordering. Rail processing additionally requires exactly one matching DS file.
- Printed file counts and demand totals are diagnostics; they are not assertions of expected counts or demand conservation.
- The aggregation script assumes a complete, unique zone lookup and consistent source matrices. It does not explicitly reject unmapped zones or duplicate lookup keys.
- WITA appraisals require complete, consistent connectivity inputs, including appropriate OD coverage and intra-zonal data. The scripts prepare files but do not determine whether a model is suitable for a TAG-consistent wider-impacts appraisal.
- Scheme generation assumes a valid template and does not verify that referenced matrices exist or that TUBA accepts the generated files.
- Reusing output folders can overwrite matching files or leave stale results. Use fresh folders for a reproducible run.

No measured runtime improvements or production validation results are claimed. The repository documents the implementation and its current boundaries.

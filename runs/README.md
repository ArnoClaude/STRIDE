# Run outputs directory - each run creates a timestamped subfolder

This directory contains all optimization run outputs, organized by run name.

Structure:
```
runs/
└── 2026-01-07_base_schmid_test_50d/   # Example run
    ├── manifest.yaml                   # Full traceability (inputs, git, params)
    ├── config.yaml                     # Copy of STRIDE config used
    ├── scenario_template.csv           # Copy of input scenario template
    ├── settings.csv                    # Generated settings (output path modified)
    ├── settings_original.csv           # Original settings (for reference)
    ├── stages/                         # Generated per-stage scenarios
    │   ├── scenario_stage_2025.csv
    │   └── ...
    ├── revoletion/                     # REVOL-E-TION outputs (contained!)
    │   ├── 260107_175156_scenario_stage_2025/
    │   └── ...
    ├── multi_stage_results.json        # Aggregated results
    ├── investment_timeline.csv
    └── plots/
```

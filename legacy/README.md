# Historical implementation

This directory contains selected Python files from the author's 2024 thesis working directory. Begin with `simulator.py`, `prompt_library_s.py`, `baseline_simulator_simplified.py` and `evaluation_jaccard.py`; the [architecture guide](../docs/ARCHITECTURE.md) maps the other components.

## Publication changes

- Hardcoded provider credentials and the private endpoint were replaced with environment-variable configuration.
- Embedded demonstration/session examples were blanked. They are not silently replaced with real participant material.
- Comments and standalone explanatory/example strings were removed, including disabled credentials, participant-like examples and copied reference prose. English documentation describes the retained code.
- Original executable Chinese task and prompt text remains in place.

Each published source file has original and published fingerprints in [source-manifest.json](../source-manifest.json). These changes make the source suitable for inspection; they do not repair all historical bugs or establish a fully reproducible run.

## Do not run the whole directory blindly

Some analysis modules execute file operations or initialise models at import time. The scripts expect excluded local research data, corpora and output directories. Live generation uses a historical provider interface; the main simulator's output-state initialisation was commented out in the archive. See [known issues](../docs/REPRODUCIBILITY.md).

Use the repository's dependency-free offline preview and tests for the supported review path. No claim is made that arbitrary historical scripts run successfully against current library versions.

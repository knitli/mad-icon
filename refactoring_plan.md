# Refactoring Plan: `mad_icon` Icon Generation

**Goal:** Simplify `generate_icons.py`, `icon_generation_utils.py`, and `image_processing.py` by maximizing the use of data structures (`icon_generation_types.py`, `models.py`) and consolidating logic into appropriate classes/methods.

**Core Strategy:** Introduce a central context object, streamline data flow (especially for configuration and sizes), move decision-making logic closer to the data types, and simplify the main generation loop.

---

## Phase 1: Establish Context & Configuration Flow

1. **Introduce `IconGenerationContext` Class:**
    * **Location:** Add to `types/icon_generation_types.py`.
    * **Purpose:** To hold the state and configuration needed throughout the generation process, replacing the large `cli_config` dictionary.
    * **Attributes:**
        * `mad_model: MadIconModel` (Loaded model)
        * `source_images: dict[IconSourceKey, tuple[bytes, str]]` (Mapping source key enum to (data, type='svg'/'raster'))
        * `output_paths: dict[str, Path]` (Logical paths like 'base_icon_path', 'html_dest_path')
        * `active_configs: list[IconGenerationConfig]` (List of configs for flags enabled via CLI)
        * `html_destination: Path`
        * `destination_dir: Path`
        * `icon_name_prefix: str` (e.g., 'apple-touch-icon')
        * `generate_html: bool`
        * `generate_manifest: bool`
    * **Rationale:** Encapsulates shared state, improves type safety, reduces function parameter complexity.

2. **Refactor `generate_icons.py` (Initialization):**
    * **Modify `generate_icons` function:**
        * Instead of creating `cli_config = locals()`, gather necessary arguments explicitly.
        * Load `MadIconModel` using `utilities.retrieve_model`.
        * Call `icon_generation_utils.determine_source_images` (to be refactored in Phase 2) to get source image data and types.
        * Call `icon_generation_utils.prepare_output_directories` to get output paths.
        * Determine active `IconGenerationFlag`s based on boolean CLI options (`masked`, `darkmode`, etc.).
        * Generate a list of `IconGenerationConfig` objects for active flags using `types.get_flag_config`.
        * Instantiate `IconGenerationContext` with the gathered data.
    * **Rationale:** Centralizes context creation, removes reliance on `locals()`, prepares for a cleaner main loop.

---

## Phase 2: Streamline Source Image & Size Handling

1. **Refactor `determine_source_images` (`icon_generation_utils.py`):**
    * **Modify Function:**
        * Accept the base icon data/type and the relevant CLI file arguments (e.g., `masked_icon`, `apple_darkmode_icon`).
        * Iterate through potential `IconSourceKey` values (MASKED, MONOCHROME, DARK, TINTED, TILE_RECTANGLE).
        * For each key, check if an explicit CLI argument was provided (`read_source_from_arg` can be reused).
        * If not provided, use the `IconSourceKey.fallback_strategy` property repeatedly until a valid source (explicitly provided or ultimately `BASE` or `MASKED`) is found.
        * Return a dictionary mapping `IconSourceKey` enums to `tuple[bytes, str]` (data, type).
    * **Rationale:** Implements robust fallback logic based on the enum definition, making it more maintainable and directly tied to the types. Removes the need for separate `source_data` and `source_type` dicts passed around later.

2. **Refactor Size Retrieval:**
    * **Remove `utilities.process_models`:** This function becomes redundant.
    * **Remove `icon_generation_utils.get_target_sizes`:** This function is replaced by direct access to the model.
    * **Modify `process_icon_category` (`icon_generation_utils.py`):**
        * Accept the `IconGenerationContext` and the `IconGenerationConfig` for the current category.
        * Access the required list of `Resolution` objects directly from `context.mad_model` using the `config.model_attr` (`IconSizeGroup`) value.
    * **Rationale:** Eliminates redundant size processing, simplifies data flow, accesses size information directly from the validated Pydantic model.

---

## Phase 3: Consolidate Processing Logic

1. **Refactor Image Processing Decision Logic:**
    * **Modify `process_single_icon` (`icon_generation_utils.py`):**
        * Remove the `apply_post_processing` helper function call.
        * Directly use the boolean flags (`needs_desat`, `needs_opaque`, `needs_trans`, `needs_clip`) from the `IconGenerationConfig` passed down via `process_icon_category`.
        * Call the relevant functions from `image_processing.py` based on these flags *after* initial rendering/resizing but *before* saving.
    * **Rationale:** Moves the decision logic for *which* post-processing steps to apply directly into the function that orchestrates the generation of a single icon, guided by the `IconGenerationConfig`.

2. **Refactor `process_icon_category` (`icon_generation_utils.py`):**
    * **Modify Function:**
        * Accept `IconGenerationContext` and `IconGenerationConfig`.
        * Retrieve the correct source image data/type from `context.source_images` using `config.source_key`. Handle potential `None` if source couldn't be determined (log warning/skip).
        * Retrieve target resolutions as described in Step 4.
        * Iterate through `target_resolutions`.
        * For each resolution, call `process_single_icon`, passing the context, config, current source data/type, resolution, and output path details.
    * **Rationale:** Simplifies the function signature, uses the context object, clarifies data flow for source images and sizes.

---

## Phase 4: Simplify Main Flow & Cleanup

1. **Refactor `generate_icons.py` (Main Loop):**
    * **Modify `generate_icons` function:**
        * After creating the `IconGenerationContext`, iterate through `context.active_configs`.
        * For each `config` in `context.active_configs`:
            * If `config['is_icon_flag']` is true:
                * Call the refactored `process_icon_category(context, config)`.
                * Aggregate the returned HTML tags and manifest entries.
        * Call `generate_output_files` with the aggregated metadata, context, etc.
    * **Rationale:** Creates a much cleaner main loop driven by the list of active configurations, directly calling the category processing function.

2. **Eliminate Redundancy & Cleanup:**
    * Remove any obsolete functions or code segments that are no longer necessary due to the refactoring.
    * Ensure consistent use of `IconGenerationContext` instead of passing multiple individual parameters.
    * Update imports across files.
    * **Rationale:** Removes dead code and simplifies the utility modules.

---

### Visual Plan (Mermaid Sequence Diagram - Simplified Flow)

```mermaid
graph TD;
    A[Start Refactoring Process] --> B[Refactor process_icon_category];
    B --> C[Update to accept IconGenerationContext and IconGenerationConfig];
    C --> D[Ensure correct retrieval of source images and sizes];
    D --> E[Finalize process_single_icon logic];
    E --> F[Conduct tests on refactored functions];
    F --> G[Cleanup redundant code];
    G --> H[Update documentation and comments];
    H --> I[Complete Refactoring Process];

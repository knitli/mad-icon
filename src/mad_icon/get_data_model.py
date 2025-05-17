# sourcery skip: avoid-global-variables
"""
`get_data_model.py` module. - Retrieves the Mad Icon pydantic data model.

`get_data_model` is a convenience function to get the Mad Icon data model for use in other scripts. You can't get the data model from the CLI, but you can use mad_icon as a library for this purpose.

If you would rather have the data model as a JSON file, use the [`get-data`](get_data.py) command.

(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).
"""

from mad_icon.models import MadIconModel, get_mad_model
from mad_icon.utilities import data_path, load_file


def get_data_model() -> MadIconModel:
    """
    Retrieves the pydantic data model for the Mad Icon `data.json` file. This isn't intended for cli use, but is offered as an API for other Python scripts to use the Mad Icon data model and included Apple device data.

    Example usage:
    ```python
    from mad_icon import get_data_model

    mad_model = get_data_model()
    apple_devices = mad_model.apple.devices
    print(apple_devices)
    ```
    """
    data = load_file(data_path())
    try:
        content = data.read()  # Read bytes from BufferedReader
        return get_mad_model(content)
    finally:
        data.close()  # Ensure file is closed

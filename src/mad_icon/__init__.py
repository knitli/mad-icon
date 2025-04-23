"""
Mad Icon
===================
A command-line tool for generating progressive web app (PWA) icons and splash screens for your webapp. **Because Apple hates webapps.** (as far as I can tell)

The tool also offers an API function for retrieving the pydantic data model and associated Apple device data, `get_data_model()`. You can use this data as a library for your own scripts, such as:

```python
import mad_icon as mad

data = mad.get_data_model()
print(mad.apple.devices)
```
You can use the entire package programmatically, of course, but it's designed as a CLI tool. The entrypoints and parameters for the main functions are the same as the CLI commands (`generate`, `generate-launch-screens`, and `generate-icons`), only adjusted for python syntax (those functions are `generate`, `generate_launch_screens`, and `generate_icons`, respectively).

(c) 2025 Stash AI Inc., All rights reserved.
Licensed under the [Plain Apache License](https://plainlicense.org/licenses/permissive/apache-2-0/).
"""

import mad_icon.__main__ as main

from mad_icon.get_data_model import get_data_model as get_data_model


__version__ = "0.1.0"

if __name__ == "__main__":
    # Run the main app
    main.app()


__all__ = ["get_data_model", "main"]


# Metadata
__title__ = "mad_icon"
__description__ = "A command-line tool for generating progressive web app (PWA) icons and splash screens for your webapp."
__url__ = "https://github.com/knitli/mad-icon"
__author__ = "Stash AI Inc."
__license__ = "Apache-2.0"
__copyright__ = "Copyright (c) 2025 Stash AI Inc."

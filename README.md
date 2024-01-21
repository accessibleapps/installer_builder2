Installer Builder 2
===================

Installer Builder 2 is a Python package designed to simplify the process of building installable and updatable applications for multiple platforms. It provides a streamlined workflow for compiling your Python code into standalone executables, creating installer packages for Windows, and disk images for macOS.

Features
--------
- Cross-platform support for Windows and macOS.
- Compiles Python code into standalone executables using Nuitka.
- Generates installer packages for Windows using Inno Setup.
- Creates disk images (.dmg) for macOS applications.
- Supports inclusion of additional modules and packages.
- Allows inclusion of data files and directories in the build.
- Customizable application metadata (name, version, author, etc.).
- Option to run the application at startup (Windows).
- Console mode compilation for command-line applications.
- Easy to use API for automating the build process.

Requirements
------------
- Python 3.6 or higher
- attrs
- innosetup_builder
- nuitka
- ordered_set

Installation
------------
To install Installer Builder 2, you can use pip:

```bash
pip install installer_builder2
```

Usage
-----
To use Installer Builder 2, create an instance of `InstallerBuilder` and configure it with your application's details and preferences. Then, call the `build` method to start the build process.

```python
from installer_builder2 import InstallerBuilder

builder = InstallerBuilder(
    app_name="MyApp",
    main_module="main.py",
    version="1.0.0",
    author="Your Name",
    run_at_startup=True,
    console=False,
    # Additional configuration...
)

builder.build()
```

For more detailed instructions and configuration options, please refer to the documentation provided within the package.

Contributing
------------
Contributions to Installer Builder 2 are welcome! Please feel free to submit pull requests or create issues for bugs and feature requests.

License
-------
Installer Builder 2 is released under the MIT License. See the LICENSE file for more details.

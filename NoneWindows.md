# Tow Truck Server: Known Issues on Non-Windows Platforms

This document provides information on known issues when running Tow Truck Server on operating systems other than Windows. Tow Truck Server makes no guarantees that the software will function as expected on non-Windows platforms. Users proceeding on such platforms do so at their own risk.

## Ubuntu Linux

**Issue ER1: Path Handling Issues**

- **Description**: Tow Truck Server encounters path handling issues on Ubuntu Linux. Specifically, the `os.chdir` function does not behave as expected, leading to difficulties in locating files and directories.
- **Implications**: As a result, Tow Truck Server fails to find necessary files and directories when executed.

**Additional Known Issues**:

1. **Main Window Icon**: The main window icon is disabled on Ubuntu Linux due to loading failures.
2. **Server Execution**: Servers will not run on Ubuntu Linux. Although the server installs correctly, it does not install in the designated servers directory, resulting in execution failures.

For any further questions or assistance, please contact support at tristanjkuhn007@gmail.com.

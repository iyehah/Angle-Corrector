# Angle Corrector

**Angle Corrector** is a graphical Python application built with `tkinter` that allows users to input a series of polygon interior angles (in Degrees–Minutes–Seconds format). It automatically detects any error in the total sum and provides corrected angles so that their sum matches the theoretical total for a polygon with the given number of sides.  
**The app can also draw the polygon and visualize the angles.**

<div style="display: flex; gap: 10px; flex-wrap: wrap;">
  <img src="/img/polygon_20250604_1604.png" width="32%"/>
  <img src="/img/polygon_20250604_1620.png" width="32%"/>
  <img src="/img/polygon_20250604_1635.png" width="32%"/>
</div>

## Features

* Input angles in either `D:M:S` or `D M S` format.
* Dynamically add or remove input fields.
* Automatically detects and corrects angular sum errors.
* Displays both raw and corrected angles in a clear table format.
* Highlights the correction error and final corrected sum.
* Friendly GUI for ease of use.
* **Visual drawing of the polygon and its angles.**

## Installation

1. **Clone the repository or download the files.**
2. Make sure you have Python 3.x installed.
3. Run the application:

```bash
python main.py

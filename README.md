===============================================
NDPA Annotation Transformer with Reference Pins
===============================================

Description:
------------
This Python script processes paired NDPA files (from NDP.view), specifically `C_` and `Crop_C_` annotation files.  
It extracts two reference pins (`Reflm1` and `Reflm2`) from both files, calculates linear transformation models,  
and applies these models to copy and transform all annotations from the `C_` file into the `Crop_C_` coordinate space.

Features:
---------
- Automatically detects and validates `C_` and `Crop_C_` file pairs.
- Extracts reference pins (`Reflm1`, `Reflm2`) from each file to build transformation models.
- Applies linear (1st-degree polynomial) transformation to all annotation coordinates.
- Copies all annotation types including single points, coordinate lists, and polygons.
- Graphical interface for file and folder selection using `tkinter`.
- Saves transformed NDPA files with the original `Crop_` file names.

Requirements:
-------------
- tkinter (included in most Python distributions)
- pandas
- numpy
- lxml
- pathlib (part of the Python standard library)

Installation:
-------------
Install the required packages with pip:
pip install pandas
pip install numpy
pip install lxml


If `tkinter` is not available (common in some Linux distros), install it with:

sudo apt-get install python3-tk


Usage:
------
1. Run the script:

python coordNDPA.py

2. Select an **even number** of NDPA files including both `C_*.ndpa` and their corresponding `Crop_C_*.ndpa` files.

3. Select a folder where the transformed NDPA files will be saved.

4. The script will:
- Match each `Crop_C_` file to its corresponding `C_` file.
- Extract the reference pins.
- Calculate X and Y transformations.
- Apply the transformation to all annotations.
- Save the transformed annotations as new NDPA files.

5. A summary message will be shown with how many files were processed or skipped due to errors.

Reference Pins:
---------------
Each NDPA file must include **two** reference pins named `Reflm1` and `Reflm2`.  
These are used to calculate the linear transformation for X and Y coordinates.

If any of the pins are missing or mismatched between the `C_` and `Crop_C_` file, the pair will be skipped.

Output:
-------
Transformed NDPA files are saved in the selected output folder, using the original name of the `Crop_` file (without the `Crop_` prefix).

Author:
-------
This script was developed by **Daurys De Alba** and **Brian Alzate**.

Contact:
--------
- Email: daurysdealbaherra@gmail.com  
- Email: bsalzateh@eafit.edu.co


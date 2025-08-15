# NDPA-Annotation-Transformer
This Python script processes paired NDPA files (from NDP.view), specifically `C_` and `Crop_C_` annotation files.   It extracts two reference pins (`Reflm1` and `Reflm2`) from both files, calculates linear transformation models,   and applies these models to copy and transform all annotations from the `C_` file into the `Crop_C_` coordinate space.

import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import pandas as pd
import numpy as np
from lxml import etree

# ----------------------------------------------------
# Extracts reference pins Reflm1 and Reflm2 from an NDPA file.
# Returns a DataFrame with their titles and coordinates.

def extract_reference_pins(file_path):
    xml = etree.parse(str(file_path))
    viewstates = xml.xpath("//ndpviewstate")
    target_titles = {"reflm1", "reflm2"}
    pins = []

    for vs in viewstates:
        title_node = vs.find("./title")
        if title_node is None or title_node.text is None:
            continue
        title_text = title_node.text.strip().lower()
        if title_text in target_titles:
            annotation = vs.find(".//annotation[@type='pin']")
            if annotation is not None:
                x_text = annotation.findtext("./x")
                y_text = annotation.findtext("./y")
                if x_text and y_text:
                    try:
                        x = float(x_text)
                        y = float(y_text)
                        pins.append({"title": title_text, "x": x, "y": y})
                    except ValueError:
                        continue

    df = pd.DataFrame(pins)
    return df.sort_values("title").reset_index(drop=True)

# ----------------------------------------------------
# Copies all annotations from a source NDPA file to a target,
# applies coordinate transformation using provided models.
# Saves the transformed NDPA to output_path.

def copy_and_transform_annotations(source_path, target_path, model_x, model_y, output_path):
    source_tree = etree.parse(str(source_path))
    target_tree = etree.parse(str(target_path))
    source_annotations = source_tree.xpath("//ndpviewstate/annotation")
    target_root = target_tree.getroot()

    for ann in source_annotations:
        ann_copy = etree.fromstring(etree.tostring(ann))

        for node in ann_copy.xpath(".//x | .//y"):
            try:
                val = float(node.text)
                transformed_val = model_x(val) if node.tag == "x" else model_y(val)
                node.text = str(round(transformed_val))
            except (TypeError, ValueError):
                continue

        for point in ann_copy.xpath(".//coordinates/point"):
            x_node = point.find("x")
            y_node = point.find("y")
            if x_node is not None and y_node is not None:
                try:
                    x_val = float(x_node.text)
                    y_val = float(y_node.text)
                    x_node.text = str(round(model_x(x_val)))
                    y_node.text = str(round(model_y(y_val)))
                except (TypeError, ValueError):
                    continue

        coords = ann_copy.find("coordinates")
        if coords is not None:
            x_node = coords.find("x")
            y_node = coords.find("y")
            if x_node is not None and y_node is not None:
                try:
                    x_val = float(x_node.text)
                    y_val = float(y_node.text)
                    x_node.text = str(round(model_x(x_val)))
                    y_node.text = str(round(model_y(y_val)))
                except (TypeError, ValueError):
                    continue

        new_vs = etree.Element("ndpviewstate")
        new_vs.append(ann_copy)
        target_root.append(new_vs)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    target_tree.write(str(output_path), pretty_print=True, xml_declaration=True, encoding="utf-8")

# ----------------------------------------------------
# Main workflow for selecting files and processing NDPA pairs.
# Validates the input, builds transformation models, and saves output.

def select_and_process_ndpa_files():
    root = tk.Tk()
    root.withdraw()

    file_paths = filedialog.askopenfilenames(
        title="Select NDPA files (must include C_ and Crop_C_ pairs)",
        filetypes=[("NDPA files", "*.ndpa")]
    )

    if len(file_paths) % 2 != 0 or len(file_paths) == 0:
        messagebox.showwarning("Warning", "You must select an EVEN number of NDPA files (C_ and Crop_C_ pairs).")
        return

    output_dir = filedialog.askdirectory(title="Select folder to save transformed NDPA files")
    if not output_dir:
        return

    file_paths = sorted(Path(p) for p in file_paths)
    crop_files = [p for p in file_paths if p.name.startswith("Crop_")]
    output_base = Path(output_dir)
    pairs = []

    for crop in crop_files:
        base_name = crop.name.replace("Crop_", "")
        c_match = next((p for p in file_paths if p.name == base_name), None)
        if c_match:
            pairs.append((c_match, crop))
        else:
            messagebox.showwarning("Missing file", f"No matching C_ file found for: {crop.name}")
            return

    if not pairs:
        messagebox.showinfo("No valid pairs", "No valid file pairs detected for processing.")
        return

    total_ok = 0
    total_skipped = 0

    for c_file, crop_file in pairs:
        pins_c = extract_reference_pins(c_file)
        pins_crop = extract_reference_pins(crop_file)

        if len(pins_c) != 2 or len(pins_crop) != 2:
            messagebox.showwarning("Missing references", f"Reflm1 and Reflm2 not found in:\n- {c_file.name}\n- {crop_file.name}")
            total_skipped += 1
            continue

        if not all(pins_c["title"] == pins_crop["title"]):
            messagebox.showwarning("Reference mismatch", f"Reference names do not match between:\n- {c_file.name}\n- {crop_file.name}")
            total_skipped += 1
            continue

        model_x = np.poly1d(np.polyfit(pins_c["x"], pins_crop["x"], 1))
        model_y = np.poly1d(np.polyfit(pins_c["y"], pins_crop["y"], 1))

        # Use original Crop_ name without prefixing "C_"
        output_filename = f"{crop_file.stem}.ndpa"
        output_path = output_base / output_filename

        copy_and_transform_annotations(c_file, crop_file, model_x, model_y, output_path)
        total_ok += 1

    messagebox.showinfo("Processing complete", f"Files processed: {total_ok}\nFiles skipped: {total_skipped}")


if __name__ == "__main__":
    select_and_process_ndpa_files()

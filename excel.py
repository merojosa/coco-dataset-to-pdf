import json
import pandas as pd
from openpyxl import Workbook


def read_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


json_data = read_json_file("dataset/_annotations.coco.json")


def get_category_name(category_id):
    for category in json_data["categories"]:
        if category["id"] == category_id:
            return category["name"]

    return ""


# Group annotations by image_id
image_annotations = {}
for annotation in json_data["annotations"]:
    image_id = annotation["image_id"]
    if image_id not in image_annotations:
        image_annotations[image_id] = []
    image_annotations[image_id].append(annotation)


def generate_data_frames(batch_size):
    excel_rows = []
    data_frames = []

    for image in json_data["images"]:
        image_id = image["id"]
        # Every PDF has batch_size images
        page = (
            int(image_id) % batch_size
        ) + 2  # + 2 because the image_id starts at 0 and we need to ignore the legend page at the beginning

        # Let's append what we have every batch and reset excel_rows
        if page == 2 and len(excel_rows) > 0:
            data_frames.append(
                pd.DataFrame(
                    excel_rows,
                    columns=["Page", "Annotation Id", "Annotation Name", "Correct?"],
                )
            )
            excel_rows = []

        if image_id in image_annotations:
            for i, annotation in enumerate(image_annotations[image_id]):
                if i == 0:
                    excel_rows.append(
                        [
                            page,
                            annotation["id"],
                            get_category_name(annotation["category_id"]),
                            "",
                        ]
                    )
                else:
                    excel_rows.append(
                        [
                            "",
                            annotation["id"],
                            get_category_name(annotation["category_id"]),
                            "",
                        ]
                    )
        else:
            excel_rows.append([page, "-", "-", "-"])

    # Append the rest of the images that didn't make it inside the for
    data_frames.append(
        pd.DataFrame(
            excel_rows,
            columns=["Page", "Annotation Id", "Annotation Name", "Correct?"],
        )
    )
    return data_frames


dfs = generate_data_frames(batch_size=300)

# Generate Excel with multiple sheets
with pd.ExcelWriter("image_annotations_output.xlsx", engine="openpyxl") as writer:
    for i, df in enumerate(dfs):
        df.to_excel(writer, sheet_name=f"batch {i + 1}", index=False)


print(f"Excel file has been created successfully.")

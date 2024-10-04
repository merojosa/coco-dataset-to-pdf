import json
import pandas as pd


def read_json_file(file_path):
    with open(file_path, "r") as file:
        return json.load(file)


json_data = read_json_file("dataset/_annotations.coco.json")


def get_category_name(category_id):
    for category in json_data["categories"]:
        if category["id"] == category_id:
            return category["name"]

    return ""


# Create a dictionary to store image_id: [annotations]
image_annotations = {}

# Group annotations by image_id
for annotation in json_data["annotations"]:
    image_id = annotation["image_id"]
    if image_id not in image_annotations:
        image_annotations[image_id] = []
    image_annotations[image_id].append(annotation)

# Create a list to store the rows for the Excel file
excel_rows = []


# Generate rows for the Excel file
for image in json_data["images"]:
    image_id = image["id"]
    # Every PDF has 300 images.
    page = (int(image_id) % 300) + 2

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
        excel_rows.append([page, "", "", ""])


# Create a pandas DataFrame
df = pd.DataFrame(
    excel_rows,
    columns=["Page", "Annotation Id", "Annotation Name", "Correct?"],
)

# Export to Excel
excel_filename = "image_annotations_output.xlsx"
df.to_excel(excel_filename, index=False, engine="openpyxl")

print(f"Excel file '{excel_filename}' has been created successfully.")

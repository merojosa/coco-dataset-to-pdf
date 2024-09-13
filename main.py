import json
import os
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import Table, TableStyle


def load_coco_json(json_path):
    with open(json_path, "r") as f:
        return json.load(f)


def from_number_to_color(number):
    local_colors = [
        "red",
        "blue",
        "green",
        "yellow",
        "purple",
        "orange",
        "pink",
        "cyan",
        "magenta",
        "lime",
        "indigo",
        "violet",
        "teal",
        "maroon",
        "navy",
        "olive",
        "salmon",
        "turquoise",
        "gold",
        "silver",
        "coral",
    ]

    if number >= len(local_colors) or number < 0:
        raise ValueError("Input number must be between 0 and 20 inclusive.")

    return local_colors[number]


def create_legend_page(c, categories):
    c.setPageSize(letter)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Legend: Categories and Colors")

    data = [["Category", "Color"]]
    for category in categories:
        data.append([category["name"], ""])

    table = Table(data, colWidths=[200, 100])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 14),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                (
                    "BACKGROUND",
                    (1, 1),
                    (1, -1),
                    colors.white,
                ),
            ]
        )
    )

    for i, category in enumerate(categories, start=1):
        table.setStyle(
            TableStyle(
                [("BACKGROUND", (1, i), (1, i), from_number_to_color(category["id"]))]
            )
        )

    table.wrapOn(c, 400, 600)
    table.drawOn(c, 50, 600)

    c.showPage()


def draw_bounding_box(image, bbox, category):
    draw = ImageDraw.Draw(image)
    x, y, w, h = bbox
    draw.rectangle(
        [x, y, x + w, y + h], outline=from_number_to_color(category), width=2
    )
    return image


def process_image_batch(batch, coco_data, dataset_folder, c):
    for img_data in batch:
        img_path = dataset_folder + img_data["file_name"]

        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                # Draw bounding boxes
                for ann in coco_data["annotations"]:
                    if ann["image_id"] == img_data["id"]:
                        img = draw_bounding_box(img, ann["bbox"], ann["category_id"])

                # Add image to PDF
                img_width, img_height = img.size
                c.setPageSize((img_width, img_height))
                c.drawImage(ImageReader(img), 0, 0)
                c.showPage()
        else:
            print("Image path does not exist:", img_path)


def create_pdf_with_batched_images(coco_data, dataset_folder, output_name, batch_size):

    if not os.path.exists("results"):
        os.mkdir("results")

    images = coco_data["images"]
    for i in range(0, len(images), batch_size):
        c = canvas.Canvas(f"results/{output_name}{i//batch_size + 1}.pdf")
        create_legend_page(c, coco_data["categories"])
        batch = images[i : i + batch_size]
        process_image_batch(batch, coco_data, dataset_folder, c)
        c.save()
        print(f"Processed batch {i//batch_size + 1} of {len(images)//batch_size + 1}")


# Usage
dataset_folder = "dataset/"

coco_data = load_coco_json(dataset_folder + "_annotations.coco.json")
create_pdf_with_batched_images(coco_data, dataset_folder, "batch", 300)

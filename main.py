import json
import os
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import Table, TableStyle


def load_coco_json(json_path):
    with open(json_path, "r") as f:
        return json.load(f)


def from_number_to_color(number):
    local_colors = [
        "red", "blue", "green", "yellow", "purple", "orange", "pink", "cyan",
        "magenta", "lime", "indigo", "violet", "teal", "maroon", "navy",
        "olive", "salmon", "turquoise", "gold", "silver", "coral",
    ]

    if number >= len(local_colors) or number < 0:
        raise ValueError("Input number must be between 0 and 20 inclusive.")

    return local_colors[number]


def create_legend_page(c, categories, page_num):
    c.setPageSize(A4)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, 750, "Legend: Categories and Colors")

    data = [["Category", "Color"]]
    for category in categories:
        data.append([category["name"], ""])

    table = Table(data, colWidths=[200, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 14),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
        ("BACKGROUND", (1, 1), (1, -1), colors.white),
    ]))

    for i, category in enumerate(categories, start=1):
        table.setStyle(TableStyle([
            ("BACKGROUND", (1, i), (1, i),
             from_number_to_color(category["id"]))
        ]))

    table.wrapOn(c, 400, 600)
    table.drawOn(c, 50, 600)

    add_page_number(c, page_num)
    c.showPage()


def draw_bounding_box(image, bbox, color, label):
    draw = ImageDraw.Draw(image)
    x, y, w, h = bbox
    draw.rectangle([x, y, x + w, y + h], outline=color, width=2)

    font = ImageFont.load_default(12)

    # Use textbbox to get label dimensions
    label_bbox = draw.textbbox((0, 0), label, font=font)
    label_w = label_bbox[2] - label_bbox[0]
    label_h = label_bbox[3] - label_bbox[1]

    # Above the bounding box
    vertical_padding = int(label_h * 0.3)
    total_label_h = label_h + 2 * vertical_padding
    label_x = x
    label_y = max(0, y - total_label_h)

    # Label
    draw.rectangle(
        [label_x, label_y, label_x + label_w, label_y + label_h + 3], fill="black"
    )
    draw.text((label_x, label_y), label, font=font, fill="white")

    return image


def add_page_number(c, page_num):
    c.setFont("Helvetica", 10)
    c.drawCentredString(A4[0] / 2, 30, f"Page {page_num}")


def process_image_batch(batch, coco_data, dataset_folder, c, start_page_num):
    page_num = start_page_num
    for img_data in batch:
        img_path = dataset_folder + img_data["file_name"]

        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                # Draw bounding boxes
                for ann in coco_data["annotations"]:
                    if ann["image_id"] == img_data["id"]:
                        color = from_number_to_color(ann["category_id"])
                        label = ""
                        for category in coco_data["categories"]:
                            if category.get("id") == ann["category_id"]:
                                label = category.get("name")
                        img = draw_bounding_box(img, ann["bbox"], color, label)

                # Add image to PDF
                c.setPageSize(A4)
                img_width, img_height = img.size
                # 90% of max possible size
                scale = min(A4[0] / img_width, A4[1] / img_height) * 0.9
                scaled_width = img_width * scale
                scaled_height = img_height * scale
                x = (A4[0] - scaled_width) / 2
                y = (A4[1] - scaled_height) / 2
                c.drawImage(ImageReader(img), x, y,
                            width=scaled_width, height=scaled_height)

                add_page_number(c, page_num)
                c.showPage()
                page_num += 1
        else:
            print("Image path does not exist:", img_path)

    return page_num


def create_pdf_with_batched_images(coco_data, dataset_folder, output_name, batch_size):
    if not os.path.exists("results"):
        os.mkdir("results")

    images = coco_data["images"]
    page_num = 1
    for i in range(0, len(images), batch_size):
        c = canvas.Canvas(
            f"results/{output_name}{i//batch_size + 1}.pdf", pagesize=A4)
        create_legend_page(c, coco_data["categories"], page_num)
        page_num += 1
        batch = images[i: i + batch_size]
        process_image_batch(
            batch, coco_data, dataset_folder, c, page_num)
        c.save()
        page_num = 1
        print(f"Processed batch {i//batch_size + 1} of {len(images)//batch_size + 1}")


# Usage
dataset_folder = "dataset/"

coco_data = load_coco_json(dataset_folder + "_annotations.coco.json")
create_pdf_with_batched_images(coco_data, dataset_folder, "batch", 300)

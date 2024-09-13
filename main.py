import json
import os
from PIL import Image, ImageDraw
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


def load_coco_json(json_path):
    with open(json_path, "r") as f:
        return json.load(f)


def draw_bounding_box(image, bbox):
    draw = ImageDraw.Draw(image)
    x, y, w, h = bbox
    draw.rectangle([x, y, x + w, y + h], outline="red", width=2)
    return image


def process_image_batch(batch, coco_data, dataset_folder, c):
    for img_data in batch:
        img_path = dataset_folder + img_data["file_name"]

        if os.path.exists(img_path):
            with Image.open(img_path) as img:
                # Draw bounding boxes
                for ann in coco_data["annotations"]:
                    if ann["image_id"] == img_data["id"]:
                        img = draw_bounding_box(img, ann["bbox"])

                # Add image to PDF
                img_width, img_height = img.size
                c.setPageSize((img_width, img_height))
                c.drawImage(ImageReader(img), 0, 0)
                c.showPage()
        else:
            print("Image path does not exist:", img_path)


def create_pdf_with_batched_images(
    coco_data, dataset_folder, output_pdf, batch_size=100
):
    c = canvas.Canvas(output_pdf)

    images = coco_data["images"]
    for i in range(0, len(images), batch_size):
        batch = images[i : i + batch_size]
        process_image_batch(batch, coco_data, dataset_folder, c)
        print(f"Processed batch {i//batch_size + 1} of {len(images)//batch_size + 1}")

    c.save()


# Usage
dataset_folder = "dataset/"

coco_data = load_coco_json(dataset_folder + "_annotations.coco.json")
create_pdf_with_batched_images(coco_data, dataset_folder, "result.pdf", 100)

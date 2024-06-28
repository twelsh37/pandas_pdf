import fitz
import pandas as pd
from io import BytesIO
from PIL import Image
import matplotlib.pyplot as plt


def extract_pdf_data(pdf_path):
    with fitz.open(pdf_path) as doc:
        text_data = []
        table_data = []
        image_data = []

        for page in doc:
            # Extract text
            text = page.get_text("text")
            text_data.append(text)

            # Extract tables
            tables = page.get_text("dict")["blocks"]
            for table in tables:
                if table["type"] == 1:
                    if "lines" in table:
                        cells = table["lines"]
                        table_rows = []
                        for row in cells:
                            if "spans" in row:
                                row_data = [cell["text"] for cell in row["spans"]]
                                table_rows.append(row_data)
                        table_data.append(table_rows)

            # Extract images
            for img in page.get_images():
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_data.append(Image.open(BytesIO(base_image["image"])))

    # Create DataFrames
    text_df = pd.DataFrame({"page": range(len(text_data)), "text": text_data})
    table_df = pd.DataFrame(table_data)
    image_df = pd.DataFrame({"page": range(len(image_data)), "image": image_data})

    return text_df, table_df, image_df

# Usage
pdf_path = "derryyard.pdf"
text_df, table_df, image_df = extract_pdf_data(pdf_path)

# Display text
print("Extracted Text:")
for index, row in text_df.iterrows():
    print(f"Page {row['page']}:")
    print(row['text'])
    print("---")

# Display tables
print("Extracted Tables:")
if not table_df.empty:
    print(table_df.to_string(index=False))
else:
    print("No tables found in the PDF.")

# Display images
for index, row in image_df.iterrows():
    plt.figure(figsize=(10, 10))
    plt.imshow(row['image'])
    plt.axis('off')
    plt.title(f"Image from Page {row['page']}")
    plt.show()

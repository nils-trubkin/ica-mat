import os
import re
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt

# Function to extract items from the text
def extract_items_from_text(text):
    pattern = r"(\*?)(.*?)\s+(\d{13})\s+([\d.]+)\s+(\d+)\s+(.*?)\s+([\d.]+)"
    matches = re.findall(pattern, text, re.MULTILINE)
    items = []
    print(f"Matches found: {len(matches)}")
    for match in matches:
        discount = match[0].strip()
        name = match[1].strip()
        barcode = match[2].strip()
        price = float(match[3])
        amount = int(match[4])
        unit = match[5].strip()
        total = float(match[6])
        items.append((discount, name, barcode, price, amount, total))
    return items

# Function to process a PDF file
def process_pdf_file(file_path):
    print(f"Processing file: {file_path}")
    with open(file_path, "rb") as file:
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        print(f"Text length: {len(text)}")
        items = extract_items_from_text(text)
        print(f"Items found: {len(items)}")
        for item in items:
            print(item)
        return items

# Function to generate a graph for purchases
def generate_purchase_graph(items, output_file):
    prices = []
    names = []
    for item in items:
        prices.append(item[5])
        names.append(item[1])

    plt.figure(figsize=(10, 6))
    plt.bar(names, prices)
    plt.xlabel('Items')
    plt.ylabel('Total Price (SEK)')
    plt.xticks(rotation=90)
    plt.title('Purchases')

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# Main function
def main():
    input_dir = "src"
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)

    pdf_files = [file for file in os.listdir(input_dir) if file.endswith(".pdf")]

    for file in pdf_files:
        file_path = os.path.join(input_dir, file)
        items = process_pdf_file(file_path)

        output_file = os.path.splitext(file)[0] + "_graph.png"
        output_path = os.path.join(output_dir, output_file)

        generate_purchase_graph(items, output_path)
        print(f"Graph created: {output_path}")

if __name__ == "__main__":
    main()


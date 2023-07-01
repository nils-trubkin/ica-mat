import os
import re
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt

# Class for item
class Item:
    def __init__(self, name, barcode, price, amount, unit, total):
        self.name = name
        self.barcode = barcode
        self.price = price
        self.amount = amount
        self.unit = unit
        self.total = total
        self.discount_name = ""
        self.discount = 0

    def __str__(self):
        return f"{self.name} {self.price} {self.amount} {self.unit} {self.total}"

# Function to extract items from the text
def extract_items_from_text(text):
    #pattern = r"(\*?)(.*?)\s+(\d{13})\s+([\d.]+)\s+([\d.]+)\s+(.*?)\s+([\d.]+)"
    pattern = r"(\*?)(.*?)\s+(\d{13})\s+([\d.]+)\s+([\d.]+)\s+(.*?)\s+([\d.]+)(?:\n|Total)(?:(.*) - ([\d.]+))?"
    matches = re.findall(pattern, text, re.MULTILINE)
    items = []
    print(f"Matches found: {len(matches)}")
    try:
        for match in matches:
            discount = match[0].strip()
            name = match[1].strip()
            barcode = match[2].strip()
            price = float(match[3])
            amount = float(match[4])
            unit = match[5].strip()
            total = float(match[6])
            discount_name = match[7].strip()
            # if empty, set to 0
            if match[8].strip() == "":
                discount = 0
            else:
                discount = float(match[8])
            items.append((discount, name, barcode, price, amount, unit, total, discount_name, discount))
    except ValueError:
        print(f"Error: {match}")
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

# Function to generate a bar graph for purchases (sorted by price descending)
def generate_purchase_bar_graph(items, output_file):
    sorted_items = sorted(items, key=lambda x: x[6], reverse=True)
    prices = [item[6] - item[8] for item in sorted_items] # prices with discount
    # prices = [item[6] for item in sorted_items] # prices without discount
    names = [item[1] for item in sorted_items]

    plt.figure(figsize=(20, 12))
    plt.bar(names, prices)
    plt.xlabel('Items', fontsize=24)
    plt.ylabel('Total Price (SEK)', fontsize=24)
    plt.xticks(rotation=90, fontsize=18)
    plt.yticks(fontsize=18)
    plt.title('Purchases (Ordered by Price Descending)', fontsize=36)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# Function to generate a pie chart for categorizing items by type
def generate_purchase_pie_chart(items, output_file):
    type_count = {}
    for item in items:
        item_type = item[6]  # Assuming the item type is at index 6, adjust if needed.
        type_count[item_type] = type_count.get(item_type, 0) + 1

    types = list(type_count.keys())
    counts = list(type_count.values())

    plt.figure(figsize=(8, 8))
    plt.pie(counts, labels=types, autopct='%1.1f%%', startangle=140)
    plt.axis('equal')
    plt.title('Purchase Items Categorized by Type')

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

        generate_purchase_bar_graph(items, output_path)
        print(f"Bar graph created: {output_path}")

        pie_output_file = os.path.splitext(file)[0] + "_pie_chart.png"
        pie_output_path = os.path.join(output_dir, pie_output_file)

        generate_purchase_pie_chart(items, pie_output_path)
        print(f"Pie chart created: {pie_output_path}")

if __name__ == "__main__":
    main()


import os
import re
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# df
df = None

# Class for item
class Item:
    def __init__(self, discount, name, barcode, price, quantity, unit, total, discount_name, discount_total):
        self.discount = discount
        self.name = name
        self.barcode = barcode
        self.price = price
        self.quantity = quantity
        self.unit = unit
        self.total = total
        self.discount_name = discount_name
        self.discount_total = discount_total

    def __str__(self):
        return f"{self.name} {self.price} {self.quantity} {self.unit} {self.total}"

# Function to extract items from the text
def extract_items_from_text(text):
    global df
    #pattern = r"(\*?)(.*?)\s+(\d{13})\s+([\d.]+)\s+([\d.]+)\s+(.*?)\s+([\d.]+)"
    #pattern = r"(\*?)(.*?)\s+(\d{13})\s+([\d.]+)\s+([\d.]+)\s+(.*?)\s+([\d.]+)(?:\n|Total)(?:(.*) - ([\d.]+))?"
    pattern = r"(?P<discount>\*?)(?P<name>.*?)\s+(?P<barcode>\d{13})\s+(?P<price>[\d.]+)\s+(?P<quantity>[\d.]+)\s+(?P<unit>.*?)\s+(?P<total>[\d.]+)(?:\n|Total)(?:(?P<discount_name>.*?) - (?P<discount_total>[\d.]+))?"
    matches = re.finditer(pattern, text, re.MULTILINE)
    items = []
    #print(f"Matches found: {len(matches)}")
    try:
        for match in matches:
            print(match)
            discount = match.group("discount").strip()
            name = match.group("name").strip()
            barcode = match.group("barcode").strip()
            price = float(match.group("price"))
            quantity = float(match.group("quantity"))
            unit = match.group("unit").strip()
            total = float(match.group("total"))
            discount_name = None
            discount_total = 0.0

            if discount == "*":
                discount_name_match = match.group("discount_name")
                if discount_name_match is not None:
                    discount_name = discount_name_match.strip()
                discount_total_match = match.group("discount_total")
                if discount_total_match is not None and discount_total_match != "":
                    discount_total = float(discount_total_match)
                else:
                    discount_total = 0.0
            
            #item = Item(discount, name, barcode, price, quantity, unit, total, discount_name, discount_total)
            #items.append(item)

            # add to dataframe
            
            data = pd.DataFrame({
                'Discount': discount,
                'Name': name,
                'Barcode': barcode,
                'Price': price,
                'Quantity': quantity,
                'Unit': unit,
                'Total': total,
                'Discount Name': discount_name,
                'Discount Total': discount_total
            })
            print(f"Item: {data}")

            #df = df.append(data, ignore_index=True)

            items.append(data)
            #items.append((discount, name, barcode, price, quantity, unit, total, discount_name, discount_value))
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
    sorted_items = sorted(items, key=lambda x: x.total, reverse=True)
    prices_no_discount = [item.total for item in sorted_items] # prices without discount
    prices_discount = [item.total - item.discount_total for item in sorted_items] # prices with discount
    names = [item.name for item in sorted_items]
    
    x = np.arange(len(names))  # the label locations
    width = 0.35  # the width of the bars

    plt.figure(figsize=(20, 12))
    plt.bar(x, prices_no_discount, width, label='Price (No Discount)', color='red')
    plt.bar(x, prices_discount, width, label='Price (With Discount)', color='blue')
    plt.xlabel('Items', fontsize=24)
    plt.ylabel('Total Price (SEK)', fontsize=24)
    plt.xticks(x, names, rotation=90, fontsize=18)
    plt.yticks(fontsize=18)
    plt.title('Purchases (Ordered by Price Descending)', fontsize=36)
    plt.legend(fontsize=18)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# Function to generate a pie chart for categorizing items by type
def generate_purchase_pie_chart(items, output_file):
    type_count = {}
    for item in items:
        item_type = item.name  # Assuming the item type is at index 6, adjust if needed.
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
    global df
    input_dir = "src"
    output_dir = "out"
    os.makedirs(output_dir, exist_ok=True)

    pdf_files = [file for file in os.listdir(input_dir) if file.endswith(".pdf")]

    # DataFrame
    df = pd.DataFrame(columns=['Discount', 'Name', 'Barcode', 'Price', 'Quantity', 'Unit', 'Total Price', 'Discount Name', 'Discount Total', 'Date', 'Time', 'Store'])

    for file in pdf_files:
        file_path = os.path.join(input_dir, file)
        items = process_pdf_file(file_path)

        output_file = os.path.splitext(file)[0] + "_graph.png"
        output_path = os.path.join(output_dir, output_file)

        generate_purchase_bar_graph(items, output_path)
        print(f"Bar graph created: {output_path}")

 #       pie_output_file = os.path.splitext(file)[0] + "_pie_chart.png"
 #       pie_output_path = os.path.join(output_dir, pie_output_file)

 #       generate_purchase_pie_chart(items, pie_output_path)
 #       print(f"Pie chart created: {pie_output_path}")

if __name__ == "__main__":
    main()


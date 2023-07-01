import os
import re
import sys
from PyPDF2 import PdfReader
import matplotlib.pyplot as plt

# Function to extract items from the text
def extract_items_from_text(text):
    pattern = r"(\*?)(.*?)\s+(\d{13})\s+([\d.]+)\s+([\d.]+)\s+(.*?)\s+([\d.]+)"
    matches = re.findall(pattern, text, re.MULTILINE)
    items = []
    print(f"Matches found: {len(matches)}")
    for match in matches:
        discount = match[0].strip()
        name = match[1].strip()
        barcode = match[2].strip()
        price = float(match[3])
        amount = float(match[4])
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

# Function to generate a graph based on the given type
def generate_graph(items, graph_type, output_file):
    # print sizes of tuples of first and last item
    print(f"First item: {sys.getsizeof(items[0])}")
    sorted_items = sorted(items, key=lambda x: x[6], reverse=True)
    if graph_type == "bar":
        prices = [item[6] for item in sorted_items]
        names = [item[1] for item in sorted_items]

        plt.figure(figsize=(20, 12))
        plt.bar(names, prices)
        plt.xlabel('Items', fontsize = 24)
        plt.ylabel('Total Price (SEK)', fontsize = 24)
        plt.xticks(rotation=90)
        plt.title('Purchases', fontsize = 36)

    elif graph_type == "line":
        prices = [item[5] for item in items]
        plt.figure(figsize=(10, 6))
        plt.plot(prices)
        plt.xlabel('Index')
        plt.ylabel('Total Price (SEK)')
        plt.title('Purchases')

    elif graph_type == "scatter":
        prices = [item[5] for item in items]
        amounts = [item[4] for item in items]
        plt.figure(figsize=(10, 6))
        plt.scatter(amounts, prices)
        plt.xlabel('Amount')
        plt.ylabel('Total Price (SEK)')
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

        output_prefix = os.path.splitext(file)[0]

        # Generate bar graph
        output_file = output_prefix + "_bar_graph.png"
        output_path = os.path.join(output_dir, output_file)
        generate_graph(items, "bar", output_path)
        print(f"Bar graph created: {output_path}")

        # Generate line graph
        output_file = output_prefix + "_line_graph.png"
        output_path = os.path.join(output_dir, output_file)
        generate_graph(items, "line", output_path)
        print(f"Line graph created: {output_path}")

        # Generate scatter plot
        output_file = output_prefix + "_scatter_plot.png"
        output_path = os.path.join(output_dir, output_file)
        generate_graph(items, "scatter", output_path)
        print(f"Scatter plot created: {output_path}")

if __name__ == "__main__":
    main()


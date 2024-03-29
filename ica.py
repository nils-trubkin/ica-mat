import os
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import mplfinance as mpf
import logging

from itertools import tee
from PyPDF2 import PdfReader

# df
input_dir = "src"
output_dir = "out"
df_columns = [
    'Discount',
    'Name',
    'Barcode',
    'Price',
    'Quantity',
    'Unit',
    'Total',
    'Discount Name',
    'Discount Total',
    'Date',
    'Time',
    'Store'
]
df = pd.DataFrame(columns=df_columns)

# Function to extract items from the text
def extract_items_from_text(text, store_metadata):
    global df
    #pattern = r"(\*?)(.*?)\s+(\d{13})\s+([\d.]+)\s+([\d.]+)\s+(.*?)\s+([\d.]+)"
    #pattern = r"(\*?)(.*?)\s+(\d{13})\s+([\d.]+)\s+([\d.]+)\s+(.*?)\s+([\d.]+)(?:\n|Total)(?:(.*) - ([\d.]+))?"
    pattern = r"(?P<discount>\*?)(?P<name>.*?)\s+(?P<barcode>\d{13})\s+(?P<price>[\d.]+)\s+(?P<quantity>[\d.]+)\s+(?P<unit>.*?)\s+(?P<total>[\d.]+)(?:\n|Total)(?:(?P<discount_name>.*?) - (?P<discount_total>[\d.]+))?"
    matches = re.finditer(pattern, text, re.MULTILINE)
    matches_copy, matches = tee(matches)
    # print amount of matches
    logging.debug("Found {} matches".format(len(list(matches_copy))))
    items_df = pd.DataFrame(columns=df_columns)

    try:
        for match in matches:
            logging.debug(f"\nMatch: {match}")
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
            
            data = {
                'Discount': discount,
                'Name': name,
                'Barcode': barcode,
                'Price': price,
                'Quantity': quantity,
                'Unit': unit,
                'Total': total,
                'Discount Name': discount_name,
                'Discount Total': discount_total,
                'Date': store_metadata['date'],
                'Time': store_metadata['time'],
                'Store': store_metadata['store']
            }
            logging.debug(f"Item: {data}")

            # add to list
            items_df = pd.concat([items_df, pd.DataFrame(data, index=[0])], ignore_index=True)

    except ValueError:
        logging.debug(f"Error: {match}")
    df = pd.concat([df, items_df], ignore_index=True)
    return items_df

# Function to process a PDF file
def process_pdf_file(file_path):
    logging.debug(f"Processing file: {file_path}")
    with open(file_path, "rb") as file:
        pdf = PdfReader(file)
        text = ""
        for page in pdf.pages:
            text += page.extract_text()
        logging.debug(f"Text length: {len(text)}")
        store_metadata = extract_store_metadata_from_text(text)
        items = extract_items_from_text(text, store_metadata)
        logging.debug(f"Items found: {len(items)}")
        return items

# Function to generate a bar graph for purchases (sorted by price descending)
def generate_purchase_bar_graph(items, output_file):
    sorted_df = items.sort_values('Total', ascending=False)
    prices_no_discount = sorted_df['Total'].tolist()  # prices without discount
    prices_discount = (sorted_df['Total'] - sorted_df['Discount Total']).tolist()  # prices with discount
    names = sorted_df['Name'].tolist()

    # print sizes
    #logging.debug(f"Prices (No Discount): {len(prices_no_discount)}")
    #logging.debug(f"Prices (Discount): {len(prices_discount)}")
    #logging.debug(f"Names: {len(names)}")
    
    x = np.arange(len(names))  # the label locations
    width = 0.35  # the width of the bars

    plt.figure(figsize=(20, 12))
    plt.bar(x, prices_no_discount, width, label='Price (No Discount)', color='red')
    plt.bar(x, prices_discount, width, label='Price (With Discount)', color='blue')
    plt.xlabel('Items', fontsize=24)
    plt.ylabel('Total Price (SEK)', fontsize=24)
    plt.xticks(x, names, rotation=90, fontsize=14)
    plt.yticks(fontsize=18)
    plt.title('Purchases (Ordered by Price Descending)', fontsize=36)
    plt.legend(fontsize=18)

    plt.tight_layout()
    plt.savefig(output_file)
    plt.close()

# Function to generate a candlestick graph for purchases
def generate_purchase_candlestick_graph(grouped_items, items, output_file):
    sorted_df = items.sort_values('Total', ascending=False)
    prices_no_discount = sorted_df['Total'].tolist()  # prices without discount
    prices_discount = (sorted_df['Total'] - sorted_df['Discount Total']).tolist()  # prices with discount
    names = sorted_df['Name'].tolist()

    # Iterate over grouped items to calculate price differences
    price_lowest = []
    price_highest = []

    for index, row in sorted_df.iterrows():
        barcode = row['Barcode']
        store = row['Store']
        
        # Boolean indexing to filter the DataFrame
        same_items = grouped_items[(grouped_items['Barcode'] == barcode) & (grouped_items['Store'] == store)]

        logging.debug(f'row: {row}\nfound: {same_items}')

        # Access the prices
        low_price = same_items['low_price'].iloc[0]
        high_price = same_items['high_price'].iloc[0]

        # Append the price difference to the list
        price_lowest.append(low_price)
        price_highest.append(high_price)

    # print sizes
    #logging.debug(f"Prices (No Discount): {len(prices_no_discount)}")
    #logging.debug(f"Prices (Discount): {len(prices_discount)}")
    #logging.debug(f"Names: {len(names)}")
    
    x = np.arange(len(names))  # the label locations
    width = 0.35  # the width of the bars
    size = 20

    #plt.figure(figsize=(20, 12))
    plt.figure(figsize=(40, 24))
    #plt.figure(figsize=(80, 48))
    plt.bar(x-width/2, prices_no_discount, width, label='Price (No Discount)', color='#f77f00') # red
    plt.bar(x-width/2, prices_discount, width, label='Price (With Discount)', color='#003049') # darkest blue
    plt.scatter(x+width/2, price_highest, size, label='Price Highest', color='#f77f00', marker='^') # orange
    plt.scatter(x+width/2, price_lowest, size, label='Price Lowest', color='#003049', marker='v') # darkest blue
    plt.xlabel('Items', fontsize=24)
    plt.ylabel('Total Price (SEK)', fontsize=24)
    plt.xticks(x, names, rotation=90, fontsize=14)
    plt.yticks(fontsize=18)
    plt.title('Purchases (Ordered by Price Descending)', fontsize=36)
    plt.legend(fontsize=18)

    plt.tight_layout()
    plt.savefig(output_file, dpi=600)
    plt.close()

def extract_store_metadata_from_text(text):
    name_pattern = r"Kvitto\n(.+)"
    date_pattern = r"Datum: (\d{4}-\d{2}-\d{2})"
    time_pattern = r"Tid: (\d{2}:\d{2})"

    store= re.search(name_pattern, text).group(1)
    date = re.search(date_pattern, text).group(1)
    time = re.search(time_pattern, text).group(1)

    return {"store": store, "date": date, "time": time}

def generate_single_graphs(pdf_files):
    for file in pdf_files:
        file_path = os.path.join(input_dir, file)
        items = process_pdf_file(file_path)

        output_file = os.path.splitext(file)[0] + ".png"
        output_path = os.path.join(output_dir, output_file)

        generate_purchase_bar_graph(items, output_path)
        logging.debug(f"Bar graph created: {output_path}")

# Main function
def main():
    try:
        logging.basicConfig(level=logging.INFO)
        logging.info("Starting ica-mat v0.1")
        created = os.makedirs(output_dir, exist_ok=True)
        if not created:
            logging.info("Output directory created.")
        else:
            logging.info("Output directory already exists.")


        logging.info("Reading PDF files...")
        pdf_files = [file for file in os.listdir(input_dir) if file.endswith(".pdf")]
        logging.info(f"Found {len(pdf_files)} PDF files.")

        logging.info("Generating single graphs...")
        generate_single_graphs(pdf_files)
        logging.info("Single graphs generated.")

        logging.info("Generating total graph...")
        generate_purchase_bar_graph(df, os.path.join(output_dir, "total.png"))
        logging.info("Total graph generated.")

        grouped_df = df.groupby(['Barcode', 'Store']).agg(
            high_price=('Price', 'max'),
            low_price=('Price', 'min')
        ).reset_index()

        # Print grouped_df
        logging.debug(grouped_df)

        logging.info("Generating candlestick graph...")
        generate_purchase_candlestick_graph(grouped_df, df, os.path.join(output_dir, "candlestick.png"))
        logging.info("Candlestick graph generated.")


        # Aggredate items with same barcode and store
        aggregated_df = df.groupby(['Barcode', 'Store']).agg(
            total_price=('Price', 'sum'),
            total_quantity=('Quantity', 'sum'),
        ).reset_index()

        logging.info("Generating merged candlestick graph...")
        generate_purchase_candlestick_graph(merged_df, df, os.path.join(output_dir, "candlestick_merged.png"))
        logging.info("Merged candlestick graph generated.")


        logging.info("\n✅\n")
    except KeyboardInterrupt:
        # emoji for cancel
        logging.info("\n🚫\n")
        exit(1)
    except Exception as e:
        logging.info(f"❌ {e}")
        exit(1)
    
if __name__ == "__main__":
    main()


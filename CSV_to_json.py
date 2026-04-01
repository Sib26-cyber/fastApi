import csv
import json

input_csv = "products.csv"
output_json = "products.json"

data = []

with open(input_csv, mode="r", encoding="utf-8") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    
    for row in csv_reader:
        data.append(row)

with open(output_json, mode="w", encoding="utf-8") as json_file:
    json.dump(data, json_file, indent=4)

print("CSV file successfully converted to JSON.")
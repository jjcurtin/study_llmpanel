import csv
import argparse
import os
from pathlib import Path

def split_csv_by_modulo(input_file, n, output_dir = None):
    if output_dir is None:
        output_dir = os.path.dirname(input_file)
    
    os.makedirs(output_dir, exist_ok=True)
    
    input_path = Path(input_file)
    base_name = input_path.stem
    extension = input_path.suffix
    
    output_files = []
    writers = []
    file_handles = []
    
    for i in range(n):
        output_file = os.path.join(output_dir, f"{base_name}_part_{i+1}{extension}")
        output_files.append(output_file)
        
        file_handle = open(output_file, 'w', newline='', encoding='utf-8')
        file_handles.append(file_handle)
        
        writer = csv.writer(file_handle, quoting = csv.QUOTE_ALL)
        writers.append(writer)
    
    try:
        with open(input_file, 'r', newline='', encoding='utf-8') as infile:
            reader = csv.reader(infile)
            
            # Read header row if it exists and write to all output files
            try:
                header = next(reader)
                for writer in writers:
                    writer.writerow(header)
                line_number = 1
            except StopIteration:
                line_number = 0
            
            for row in reader:
                file_index = line_number % n
                writers[file_index].writerow(row)
                line_number += 1
    
    finally:
        for file_handle in file_handles:
            file_handle.close()
    
    print(f"Successfully split {input_file} into {n} files:")
    for i, output_file in enumerate(output_files):
        print(f"  Part {i+1}: {output_file}")

def main():
    parser = argparse.ArgumentParser(
        description = "Split a CSV file into N separate files based on line number modulo N"
    )
    parser.add_argument(
        "input_file", 
        help = "Path to the input CSV file"
    )
    parser.add_argument(
        "n", 
        type = int, 
        help = "Number of output files to create; every nth line goes to the same file"
    )
    parser.add_argument(
        "-o", "--output-dir", 
        help = "Directory to save output files (default: same as input file)"
    )
    
    args = parser.parse_args()
    
    if args.n <= 0:
        print("Error: N must be a positive integer")
        return
    
    if not os.path.exists(args.input_file):
        print(f"Error: Input file '{args.input_file}' does not exist")
        return
    
    split_csv_by_modulo(args.input_file, args.n, args.output_dir)

if __name__ == "__main__":
    main()
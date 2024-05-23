import pandas as pd
import glob

def merge_csv_files(output_file, input_files_pattern):
    csv_files = glob.glob(input_files_pattern)
    df_list = []
    
    for file in csv_files:
        try:
            df = pd.read_csv(file, encoding='utf-8')
            df_list.append(df)
            print(f"Successfully read {file}")
        except UnicodeDecodeError:
            print(f"Encoding error in file {file}, trying with latin-1")
            try:
                df = pd.read_csv(file, encoding='latin-1')
                df_list.append(df)
                print(f"Successfully read {file} with latin-1 encoding")
            except Exception as e:
                print(f"Skipping file {file} due to read error: {e}")

    if df_list:
        merged_df = pd.concat(df_list, ignore_index=True)
        merged_df.to_csv(output_file, index=False)
        print(f"Saved merged CSV to {output_file}")
    else:
        print("No valid CSV files found to merge.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python merge_csvs.py <output_file> <input_files_pattern>")
    else:
        output_file = sys.argv[1]
        input_files_pattern = sys.argv[2]
        merge_csv_files(output_file, input_files_pattern)

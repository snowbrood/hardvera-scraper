import pandas as pd
import glob

def merge_csv_files(output_file, input_files_pattern):
    # Use glob to find all the input CSV files
    csv_files = glob.glob(input_files_pattern)
    # Read each CSV file and store it in a list
    df_list = [pd.read_csv(file) for file in csv_files]
    # Concatenate all dataframes
    merged_df = pd.concat(df_list, ignore_index=True)
    # Write the merged dataframe to the output file
    merged_df.to_csv(output_file, index=False)
    print(f"Saved merged CSV to {output_file}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python merge_csvs.py <output_file> <input_files_pattern>")
    else:
        output_file = sys.argv[1]
        input_files_pattern = sys.argv[2]
        merge_csv_files(output_file, input_files_pattern)

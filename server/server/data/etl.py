import csv
from utils import list_files_in_dir

INDUSTRIES = "industries"
SECTORS = "sectors"
STATES = "states"
SUMMARIES = "summaries"

def generate_master_data_file_for_type(data_type=""):
  if data_type not in [INDUSTRIES, SECTORS, STATES, SUMMARIES]:
    raise NotImplementedError(f"{data_type} is not valid for ETL")

  all_records = consolidate_records(data_type)

  write_final_csv(all_records, file_path=f"./data/{data_type}/ALL_CANDIDATES.csv")


def consolidate_records(data_type=""):
  """
  This script relies on all records already being pulled for all candidates
  which takes a few days based on OpenSecrets API limit
  """

  dir_to_read = f"./data/{data_type}"
  all_files = list_files_in_dir(dir_to_read)
  all_records = []

  print(f"Working on {len(all_files)} files in dir {dir_to_read}")

  for file_name in all_files:
    with open(f"./data/{data_type}/{file_name}", "r") as infile:
      reader = csv.DictReader(infile)
      data = [row for row in reader]

      if data_type == STATES:
        for cand in data:
          cand["state"] = cand["office"][:2]
      elif data_type != SUMMARIES:
        # Only the state / summary records contain a CID column, but we need it
        # to be able to uniquely identify candidates across datasets
        for record in data:
          record["cid"] = file_name.split(".")[0]  # N00003028.csv -> N00003028

      all_records.extend(data)

  return all_records

def write_final_csv(all_records, file_path=""):
  """
  Compiles the reps from all 50 state files into one master csv
  So I can seed a DB with it directly (and make updating easier)
  """
  headers = all_records[0].keys()
  with open(f"{file_path}", "w") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=headers)
    writer.writeheader()

    for rep in all_records:
      writer.writerow(rep)

  print(f"Saved {len(all_records)} records to {file_path}, Done.")

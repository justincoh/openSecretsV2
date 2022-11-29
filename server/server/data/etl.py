import csv
from utils import list_files_in_dir

def create_master_rep_list():
  all_reps = consolidate_all_candidates()
  write_final_csv(all_reps)


def consolidate_all_candidates():
  """
  It's easier to pull from OpenSecrets state by state
  So this script relies on having all 50 state files
  This function adds a 'state' key to each object and
  returns the full list
  """
  all_candidate_files = list_files_in_dir("./data/states/")
  all_candidates = []

  for file_name in all_candidate_files:
    with open(f"./data/states/{file_name}", "r") as infile:
      reader = csv.DictReader(infile)
      data = [row for row in reader]
      
      # There's no 'State' field on the candidate records
      # there is an 'office' e.g. NJS1 = NJSenator 1
      # this is for convenience later, I want a 'state' column
      for cand in data:
        cand["state"] = cand["office"][:2]
      
      all_candidates.extend(data)

  return all_candidates


def write_final_csv(all_candidates):
  """
  Compiles the reps from all 50 state files into one master csv
  So I can seed a DB with it directly (and make updating easier)
  """
  file_name = "ALL_CANDIDATES.CSV"
  headers = all_candidates[0].keys()
  with open(f"./data/states/{file_name}", "w") as outfile:
    writer = csv.DictWriter(outfile, fieldnames=headers)
    writer.writeheader()

    for rep in all_candidates:
      writer.writerow(rep)

  print(f"Saved {len(all_candidates)} reps to {file_name}, Done.")
  
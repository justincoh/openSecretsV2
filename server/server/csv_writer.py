import csv
import time
from pathlib import Path

from client import Client, RateLimitError, ClientError
from constants import STATES, INDUSTRY_FAILURES, SECTOR_FAILURES, API_KEY

# https://www.pythontutorial.net/python-basics/python-write-csv-file/
# do this but you have to parse into the @attributes
def fill_csv(state_code="", client=None):
    state_reps = client.get_legislators_for_state(state_code=state_code)
    headers = state_reps[0]["@attributes"].keys()

    file_name = f"data/{state_code}.csv"
    with open(file_name, "w") as outfile:
        writer = csv.DictWriter(outfile, fieldnames=headers)
        writer.writeheader()

        for rep in state_reps:
            writer.writerow(rep["@attributes"])

    print(f"{file_name} written with {len(state_reps)} entries")


def write_all_states(client=None):
    for state_code in STATES.keys():
        fill_csv(state_code=state_code, client=client)
        time.sleep(1)


class DataPuller(object):
    def __init__(self, client=None):
        self.client = client
        if client is None:
            self.client = Client(api_key=API_KEY)

        self.method_map = {
          "sectors": {
            "failures": SECTOR_FAILURES,
            "file_path": "./data/sectors/",
            "fetch_function": self.get_sector_summary_for_cid,
          },
          "industries": {
            "failures": INDUSTRY_FAILURES,
            "file_path": "./data/industries/",
            "fetch_function": self.get_top_ten_industries_for_cid,
          }
        }

    def pull_data_for_all_candidates(self, method=""):
        """
        Assumes getLegislators has already been run for all states
        and the data is saved in ./data/states/{state_code}.csv

        method must be one of 'industries' or 'sectors'
        """
        if method not in ["industries", "sectors"]:
          raise NotImplementedError(f"Cannot pull data for method: {method}")

        # so we don't go fetch things for candidates we already did, OS api has a small
        # daily call limit, don't want to do extra work
        existing_candidate_summaries = self.list_files_in_dir(self.method_map[method]["file_path"])

        # this relies on the files being saved in CID.csv format
        existing_cid_set = set(
            [name.split(".")[0] for name in existing_candidate_summaries]
        )
        
        # these are ones that failed mostly due to 404 cuz the data is missing
        existing_cid_set.update(self.method_map[method]["failures"])

        state_csvs = self.list_files_in_dir("./data/states/")

        failures = []
        # get all CIDs for a state
        for state_file_name in state_csvs:
            print(f"Working on file: {state_file_name}")
            state_cids = self.get_candidate_ids_from_state_file(
                f"./data/states/{state_file_name}"
            )

            for cid in state_cids:
                # make sure we're not doing duplicate work
                # we'll have to run this script over a number of days
                # to get around OpenSecrets API limit so we need to limit calls
                if cid in existing_cid_set:
                    print(f"CID {cid} already saved, skipping")
                    continue

                existing_cid_set.add(cid)
                try:
                    self.method_map[method]["fetch_function"](cid)
                except RateLimitError as e:
                    print(f"Rate limit exceeded. All failures: {failures}")
                    raise e
                except ClientError as e:
                    failures.append(f"{state_file_name}_{cid}")
                    print(f"Error getting data for CID: {cid}: {e}")
                    continue

            print(f"File {state_file_name} complete")

        print(f"All done. The following candidates failed to fetch: {failures}")

    def list_files_in_dir(self, dir):
        file_names = []
        for f in Path(dir).iterdir():
            file_names.append(f.name)

        return file_names

    def get_candidate_ids_from_state_file(self, file_path):
        candidate_ids = []
        with open(file_path) as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # CID is candidate ID
                candidate_ids.append(row["cid"])

        return candidate_ids


    def get_sector_summary_for_cid(self, cid):
        # wrap this in a try / except in the eventual caller to be safe
        # also handle the "does this file already exist? but in the caller"
        response = self.client.get_candidate_total_by_sector(cid=cid)

        # this needs to get the right keys now
        data = response["data"]

        # .keys() returns dict_keys class, turn it to a list
        headers = list(data[0]["@attributes"].keys())
        headers.extend(["last_updated", "cycle"])

        file_name = f"./data/sectors/{cid}.csv"
        with open(file_name, "w") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=headers)
            writer.writeheader()

            for row in data:
                obj = row["@attributes"]
                obj["last_updated"] = response["last_updated"]
                obj["cycle"] = response["cycle"]
                writer.writerow(obj)

        print(f"wrote file {file_name}")

    def get_top_ten_industries_for_cid(self, cid):
        response = self.client.get_candidate_top_ten_industries(cid=cid)

        # this needs to get the right keys now
        data = response["data"]

        # .keys() returns dict_keys class, turn it to a list
        headers = list(data[0]["@attributes"].keys())
        headers.extend(["last_updated", "cycle"])

        file_name = f"./data/industries/{cid}.csv"
        with open(file_name, "w") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=headers)
            writer.writeheader()

            for row in data:
                obj = row["@attributes"]
                obj["last_updated"] = response["last_updated"]
                obj["cycle"] = response["cycle"]
                writer.writerow(obj)

        print(f"wrote file {file_name}")

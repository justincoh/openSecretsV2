import csv
import time

from server.data.utils import list_files_in_dir
from client import Client, RateLimitError, ClientError
from server.constants import (
    API_KEY,
    FAILED_CONTRIBUTOR_CIDS,
    FAILED_INDUSTRY_CIDS,
    FAILED_SECTOR_CIDS,
    STATE_ABBREV_MAP,
)

def write_state_csv(state_code="", client=None):
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
    if client is None:
        client = Client(api_key=API_KEY)

    for state_code in STATE_ABBREV_MAP.keys():
        write_state_csv(state_code=state_code, client=client)
        time.sleep(1)


class DataPuller(object):
    def __init__(self, client=None):
        self.client = client
        if client is None:
            self.client = Client(api_key=API_KEY)

        self.method_map = {
            "sectors": {
                "failures": FAILED_SECTOR_CIDS,
                "file_path": "./data/sectors/",
                "fetch_function": self.get_sector_summary_for_cid,
            },
            "industries": {
                "failures": FAILED_INDUSTRY_CIDS,
                "file_path": "./data/industries/",
                "fetch_function": self.get_top_ten_industries_for_cid,
            },
            "summaries": {
                "failures": [],  # doesn't matter, rate limit is higher here, also rarely fails
                "file_path": "./data/summaries/",
                "fetch_function": self.get_candidate_overall_summary,
            },
            "contributors": {
                "failures": FAILED_CONTRIBUTOR_CIDS,
                "file_path": "./data/contributors/",
                "fetch_function": self.get_candidate_contributors,
            }
        }

    def pull_data_for_all_candidates(self, method=""):
        """
        Assumes getLegislators has already been run for all states
        and the data is saved in ./data/states/{state_code}.csv

        method must be in the known methods list
        """
        if method not in self.method_map.keys():
            raise NotImplementedError(f"Cannot pull data for method: {method}")

        # so we don't go fetch things for candidates we already did, OS api has a small
        # daily call limit, don't want to do extra work
        existing_candidate_summaries = list_files_in_dir(
            self.method_map[method]["file_path"]
        )

        # this relies on the files being saved in CID.csv format
        existing_cid_set = set(
            [name.split(".")[0] for name in existing_candidate_summaries]
        )

        # these are ones that failed mostly due to 404 cuz the data is missing
        existing_cid_set.update(self.method_map[method]["failures"])

        state_csvs = list_files_in_dir("./data/states/")

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
                # KeyError happens if returned data is empty
                except (ClientError, KeyError) as e:
                    failures.append(f"{state_file_name}_{cid}")
                    print(f"Error getting data for CID: {cid}: {e}")
                    continue

            print(f"File {state_file_name} complete")

        print(f"All done. The following candidates failed to fetch: {failures}")

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
        response = self.client.get_candidate_total_by_sector(cid=cid, cycle="2022")

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
        response = self.client.get_candidate_top_ten_industries(cid=cid, cycle="2022")

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

    def get_candidate_overall_summary(self, cid):
        # candidate overall summary is a much simpler endpoint
        response = self.client.get_candidate_summary(cid=cid, cycle="2022")
        file_name = f"./data/summaries/{cid}.csv"
        with open(file_name, "w") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=response.keys())
            writer.writeheader()
            writer.writerow(response)

        print(f"wrote file {file_name}")

    def get_candidate_contributors(self, cid):
        """
        Gets contributor organizations / individuals for a given candidate

        This notice must be present on displayed data, according to the docs
        ---
        The organizations themselves did not donate, rather the money
        came from the organization's PAC, its individual members or
        employees or owners, and those individuals' immediate families.
        ---
        """

        contributor_data = self.client.get_candidate_contributors(cid=cid, cycle="2022")
        contributor_list= [item["@attributes"] for item in contributor_data["contributors"]]
        file_name = f"./data/contributors/{cid}.csv"

        # org_name, total, pacs, indivs
        contributor_keys = contributor_list[0].keys()
        csv_headers = list(contributor_keys) + ["cycle", "source", "cid"]

        with open(file_name, "w") as outfile:
            writer = csv.DictWriter(outfile, fieldnames=csv_headers)
            writer.writeheader()

            for row in contributor_list:
                data = {
                    "cycle": contributor_data["cycle"],
                    "source": contributor_data["source"],
                    "cid": cid,
                    **row,
                }
                writer.writerow(data)

        print(f"wrote file {file_name}")

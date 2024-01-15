## Pulling the Data needed for this project

The first thing you need to do is pull the total list of all candidates / representatives from the OpenSecrets API. The only way to do that currently is to query by state using the [getLegislators](https://www.opensecrets.org/api/?method=getLegislators&output=doc) endpoint, so 50 individual calls. To do that, open an ipython shell from the same directory as `data_puller.py` and run the following:

### Fetching the data from [OpenSecrets API](https://www.opensecrets.org/open-data/api-documentation)
```py
from data_puller import write_all_states

write_all_states()
```

This will write individual files for each state, with each file containing one row per representative / candidate.

Once you have all 50 state files, you can run the commands to pull candidate data from the individual endpoints this project needs—[summaries](https://www.opensecrets.org/api/?method=candSummary&output=doc), [sectors](https://www.opensecrets.org/api/?method=candSector&output=doc), and [industries](https://www.opensecrets.org/api/?method=candIndustry&output=doc).

OpenSecrets API has a relatively low rate limit at 200 calls per endpoint per day. Given a total of ~550 total representatives, that means you'll have to run the code blocks below three times over three different days to obtain all needed data.

 Before running the code below, you should clear out the list in `failed_cids.py`, as the same candidate ids may not fail again in the future. Again, in an ipython shell in the same directory as `data_puller.py`:

```py
from data_puller import DataPuller

puller = DataPuller()

puller.pull_data_for_all_candidates(method="industries")
```

The `pull_data_for_all_candidates` will loop through individual candidates within individual state files present in e.g. /data/NJ.csv until it hits a rate limit error. When complete, it will print out a list of candidate IDs which failed to fetch, which you'll need to add to the failed_cids.py file so it knows to skip them next time you need to run this (and they don't add to your call count). When run in 11/2022, all of these failures were 404 errors for candidates that were too new to have data.

After running the above command, you should exit ipython, update the `failed_cids.py` file as described above, and then re-enter the shell.

```py
# Then again for sectors and summaries
from data_puller import DataPuller

puller = DataPuller()

# this uses the common failed_cids, as they fail the same across industries and
# sectors endpoints
puller.pull_data_for_all_candidates(method="sectors")

# This does not to care about failed_cids list, summaries are always present
puller.pull_data_for_all_candidates(method="summaries")
```

Once you've run all three data_puller commands, you'll be at your rate limit for all relevant endpoints for 24 hours, and you'll have to repeat this process over the another two days to complete the data pull. After three days of manual pulling, you can move on to the ETL section below

### Consolidating the generated CSVs
Now that you've patiently pulled data over three days, you can compile all the data into single spreadsheets per category using the command in `etl.py`. Again in a python shell:

```py
import etl

etl.generate_master_data_file_for_type(etl.INDUSTRIES)
etl.generate_master_data_file_for_type(etl.SECTORS)
etl.generate_master_data_file_for_type(etl.SUMMARIES)
etl.generate_master_data_file_for_type(etl.STATES)
```

This script will loop through all of the files we created when pulling data, and write one common master data file per data type within its directory.

The next step will be using these common data files as a seed for a database, but I'm not there yet so this README ends here for now.

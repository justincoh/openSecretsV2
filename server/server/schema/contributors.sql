CREATE TABLE contributors (
    org_name TEXT,
    total TEXT,
    pacs INTEGER,
    indivs INTEGER,
    total INTEGER,
    cycle INTEGER,
    source TEXT,
    candidate_id TEXT
);


--- \COPY contributors from '~/Projects/openSecretsV2/server/server/data/contributors/ALL_CANDIDATES_CONTRIBUTORS.csv' WITH CSV HEADER;
CREATE TABLE contributors (
    org_name TEXT,
    total INTEGER,
    pacs INTEGER,
    indivs INTEGER,
    cycle INTEGER,
    source TEXT,
    candidate_id TEXT
);


--- \COPY contributors from '~/Projects/openSecretsV2/server/server/data/seeds/ALL_CANDIDATES_CONTRIBUTORS.csv' WITH CSV HEADER;


--- select org_name, SUM(indivs) indivs, SUM(pacs) pacs, SUM(total)  total from contributors group by org_name order by 2 desc limit 10;
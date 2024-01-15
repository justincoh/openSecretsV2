CREATE TABLE sectors (
    sector_name TEXT,
    sector_id TEXT,
    indivs INTEGER,
    pacs INTEGER,
    total INTEGER,
    last_updated DATE,
    cycle INTEGER,
    candidate_id TEXT
);

--- \COPY sectors from '~/Projects/openSecretsV2/server/server/data/seeds/ALL_CANDIDATES_SECTORS.csv' WITH CSV HEADER;


--- select sector_name, SUM(indivs) indivs, SUM(pacs) pacs, SUM(total) total from sectors group by sector_name order by SUM(total) desc limit 10;
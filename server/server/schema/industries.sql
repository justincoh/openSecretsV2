CREATE TABLE industries (
    industry_code TEXT,
    industry_name TEXT,
    indivs INTEGER,
    pacs INTEGER,
    total INTEGER,
    last_updated DATE,
    cycle INTEGER,
    candidate_id TEXT
);


--- It looks like the FK referecne fails for former reps, they're no longer int he states list
--- verify the right number of candidates are there, do we have all 535?
--- \COPY industries from '~/Projects/openSecretsV2/server/server/data/seeds/ALL_CANDIDATES_INDUSTRIES.csv' WITH CSV HEADER;



--- select industry_name, SUM(indivs) indivs, SUM(pacs) pacs, SUM(total) total from industries group by industry_name order by SUM(total) desc limit 10;

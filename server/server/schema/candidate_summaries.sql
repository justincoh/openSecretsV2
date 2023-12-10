CREATE TABLE candidate_summaries (
    name TEXT,
    candidate_id TEXT PRIMARY KEY,
    cycle TEXT,
    state TEXT,
    party TEXT,
    chamber TEXT,
    first_elected INTEGER,
    next_election INTEGER,
    total double precision,
    spent double precision,
    cash_on_hand double precision,
    debt double precision,
    origin TEXT,
    source TEXT,
    last_updated DATE
);

--- ERROR:  invalid input syntax for type integer: "3153275.32"
--- CONTEXT:  COPY candidates, line 2, column total: "3153275.32"
--- \COPY candidate_summaries from '~/Projects/openSecretsV2/server/server/data/summaries/ALL_CANDIDATES_SUMMARIES.csv' WITH CSV HEADER;
--- COPY 628
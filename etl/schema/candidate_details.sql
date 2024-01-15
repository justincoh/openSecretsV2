CREATE TABLE candidate_details (
    candidate_id TEXT PRIMARY KEY,
    firstlast TEXT,
    lastname TEXT,
    party TEXT,
    office TEXT,
    gender TEXT,
    first_elected INTEGER,
    phone TEXT,
    website TEXT,
    congress_office TEXT,
    twitter_id TEXT,
    youtube_url TEXT,
    facebook_id TEXT,
    birthdate DATE,
    state TEXT
);

--- This file has a bunch of extra columns, might want to revisit the ETL file for this one
--- for now just manually delete the extras
--- \COPY candidate_details from '~/Projects/openSecretsV2/server/server/data/seeds/ALL_CANDIDATES_STATES.csv' WITH CSV HEADER;

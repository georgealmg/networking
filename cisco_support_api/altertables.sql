use ciscoapi;

alter table devices modify column IP varchar(15);
alter table devices modify column SerialNumber varchar(20);
alter table devices modify column osFamily varchar(5);
alter table devices modify column osVersion varchar(10);

alter table eox modify column EndOfSaleDate date;
alter table eox modify column LastDateOfSupport date;

alter table products modify column ProductReleaseDate date;

alter table software modify column SoftwareReleaseDate date;

CREATE TABLE IF NOT EXISTS bugs (
    product_id TEXT,
    os_version TEXT,
    bug_id TEXT,
    headline MEDIUMTEXT,
    severity INT,
    bug_status VARCHAR(9),
    last_modified_date DATE,
    known_fixed_releases TEXT
);

CREATE TABLE IF NOT EXISTS psirt (
    os_familiy VARCHAR(5),
    os_version TEXT,
    bug_id TEXT,
    advisoryTitle MEDIUMTEXT,
    cves MEDIUMTEXT,
    cwe TEXT,
    cve_version FLOAT(0),
    cve_status VARCHAR(9),
    firstPublished DATE,
    lastUpdated DATE,
    severity VARCHAR(9),
    affected_release TEXT,
    first_fixed TEXT,
    url MEDIUMTEXT
);

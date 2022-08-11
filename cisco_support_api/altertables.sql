use ciscoapi;

alter table devices modify column IP varchar(15);
alter table devices modify column SerialNumber varchar(20);
alter table devices modify column OSFamily varchar(5);
alter table devices modify column OSversion varchar(10);

alter table eox modify column EndOfSaleDate date;
alter table eox modify column LastDateOfSupport date;

alter table products modify column ProductReleaseDate date;

alter table software modify column SoftwareReleaseDate date;

CREATE TABLE IF NOT EXISTS bugs (
    ProductID TEXT,
    OSversion TEXT,
    BugID TEXT,
    headline MEDIUMTEXT,
    severity INT,
    status VARCHAR(9),
    LastModifiedDate DATE,
    KnownFixedReleases TEXT
);

CREATE TABLE IF NOT EXISTS psirt (
    OSfamily VARCHAR(5),
    OSversion TEXT,
    BugID TEXT,
    advisoryTitle MEDIUMTEXT,
    cves MEDIUMTEXT,
    cwe TEXT,
    status VARCHAR(9),
    firstPublished DATE,
    lastUpdated DATE,
    severity VARCHAR(9),
    first_fixed TEXT,
    url MEDIUMTEXT
);

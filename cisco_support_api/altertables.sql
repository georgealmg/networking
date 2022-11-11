use ciscoapi;

alter table devices modify Hostname not null;
alter table devices modify ProductID varchar(20) not null;
alter table devices modify SerialNumber varchar(20) not null;
alter table devices modify OSFamily varchar(5) not null;
alter table devices modify OSversion varchar(25) not null;


alter table eox modify ProductID varchar(20) not null;
alter table eox modify EndOfSaleDate date null;
alter table eox modify LastDateOfSupport date null;
alter table eox modify EOXMigrationDetails varchar(20) null;


alter table products modify ProductID varchar(20) not null;
alter table products modify ProductReleaseDate date not null;
alter table products modify ProductSeries not null;


alter table software modify ProductID varchar(20) not null;
alter table software modify RecommendedOSversion not null;
alter table software modify SoftwareReleaseDate date not null;
alter table software modify ImageName not null;


alter table serialnumbers modify ProductID varchar(20) not null;
alter table serialnumbers modify Customer not null;
alter table serialnumbers modify ContractEndDate date;
alter table serialnumbers modify IsCovered varchar(3) not null;



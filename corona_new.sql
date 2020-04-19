drop table if exists test;
drop table if exists locations;

create table locations (
	location_id int auto_increment primary key,
	admin0 varchar(256) default '',
	admin1 varchar(256) default '',
	admin2 varchar(256) default '',
	admin0_code varchar(2) default '',
	admin1_code varchar(2) default '',
	latitude float(10, 6),
	longitude float(10, 6),
	population float,
	area float,
	population_density float generated always as (population / area) stored,
	location_labelled boolean generated always as (latitude is not null and longitude is not null) stored
) collate utf8_bin;

create table test (
	entry_date date,
	location_id int,
	
	total int default 0,
	deaths int default 0,
	recoveries int default 0,
	active int generated always as (total - deaths - recoveries) stored,
	
	total_new int default 0,
	deaths_new int default 0,
	recoveries_new int default 0,
	active_new int generated always as (total_new - deaths_new - recoveries_new) stored,
	
	primary key(entry_date, location_id),
	foreign key(location_id) references locations(location_id) on delete cascade
);

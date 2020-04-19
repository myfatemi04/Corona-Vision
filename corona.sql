create database if not exists corona;
use corona;
drop table if exists datapoints;
create table datapoints (
	entry_date varchar(16),
	update_time datetime not null default CURRENT_TIMESTAMP,
	
	admin0 varchar(320) default '',
	admin1 varchar(320) default '',
	admin2 varchar(320) default '',
	`group` varchar(320) default '',
	
	latitude float(10, 6),
	longitude float(10, 6),
	
	is_first_day boolean default false,
	
	confirmed integer default 0,
	recovered integer default 0,
	deaths integer default 0,
	active integer default 0,
	serious integer default 0,

	dconfirmed integer default 0,
	drecovered integer default 0,
	ddeaths integer default 0,
	dactive integer default 0,
	dserious integer default 0,

	num_tests integer default 0,

	source_total TEXT,
	source_recovered TEXT,
	source_deaths TEXT,
	source_serious TEXT,
	source_num_tests TEXT,

	PRIMARY KEY(country, province, admin2, entry_date)
	COLLATE utf8_bin
);

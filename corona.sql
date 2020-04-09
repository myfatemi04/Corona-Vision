create database if not exists corona;
use corona;
drop table if exists datapoints;
create table datapoints (
	data_id integer not null auto_increment primary key,
	entry_date date,
	
	admin2 varchar(320),
	province varchar(320),
	country varchar(320),
	
	latitude float(10, 6) not null default 0,
	longitude float(10, 6) not null default 0,

	location_labelled boolean,
	location_accurate boolean,
	is_first_day boolean,
	is_primary boolean,
	
	confirmed int,
	recovered int,
	deaths int,
	active int,

	dconfirmed int,
	drecovered int,
	ddeaths int,
	dactive int
);

drop table if exists live;
create table live (
	data_id integer not null auto_increment primary key,
	
	update_time datetime not null default CURRENT_TIMESTAMP,

	admin2 varchar(320) default '',
	province varchar(320) default '',
	country varchar(320) default '',
	`group` varchar(320) default '',

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

	source_link TEXT
);

create database if not exists corona;
use corona;
create table locations (
	/* Administrative division location */
	country varchar(256) default '',
	province varchar(256) default '',
	county varchar(256) default '',

	population float,
	population_density float,

	latitude float(10, 6),
	longitude float(10, 6),

	start_cases date,

	primary key (country, province, county)

) collate utf8_bin;

create table datapoints (
	entry_date varchar(16),
	update_time datetime not null default CURRENT_TIMESTAMP,
	
	country varchar(320) default '',
	province varchar(320) default '',
	county varchar(320) default '',
	`group` varchar(320) default '',
	
	total integer default 0,
	recovered integer default 0,
	deaths integer default 0,
	serious integer default 0,
	tests integer default 0,
	hospitalized integer default 0,

	-- source_total TEXT,
	-- source_recovered TEXT,
	-- source_deaths TEXT,
	-- source_serious TEXT,
	-- source_tests TEXT,
	-- source_hospitalized TEXT,

	PRIMARY KEY(country, province, county, entry_date)
) COLLATE utf8_bin;

create table hospitals (
	hospital_id int auto_increment primary key,
	hospital_name varchar(256),
	hospital_type varchar(256),
	`address1` varchar(256),
	`address2` varchar(256),
	country varchar(256),
	province varchar(256),
	county varchar(256),
	licensed_beds int default 0,
	staffed_beds int default 0,
	icu_beds int default 0,
	adult_icu_beds int default 0,
	pediatric_icu_beds int default 0,
	potential_beds_increase int default 0,
	average_ventilator_usage int default 0
);

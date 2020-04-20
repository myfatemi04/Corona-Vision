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
	
	total integer default 0,
	recovered integer default 0,
	deaths integer default 0,
	active integer default 0,
	serious integer default 0,
	tests integer default 0,
	hospitalized integer default 0,

	dtotal integer default 0,
	drecovered integer default 0,
	ddeaths integer default 0,
	dactive integer default 0,
	dserious integer default 0,
	dtests integer default 0,
	dhospitalized integer default 0,

	source_total TEXT,
	source_recovered TEXT,
	source_deaths TEXT,
	source_serious TEXT,
	source_tests TEXT,
	source_hospitalized TEXT,

	PRIMARY KEY(admin0, admin1, admin2, entry_date)
) COLLATE utf8_bin;


create table locations (
	location_id int auto_increment primary key,
	/* Administrative division location */
	admin0 varchar(256) default '',
	admin1 varchar(256) default '',
	admin2 varchar(256) default '',

	/* Administrative division ISO codes */
	admin0_code varchar(2) default '',
	admin1_code varchar(2) default '',
	admin2_code varchar(10) default '',

	/* Specificity of location */
	admin_level enum("world", "admin0", "admin1", "admin2"),

	/* Geographic location */
	latitude float(10, 6),
	longitude float(10, 6),

	/* Demographics */
	population float,
	population_density float,
	
	/* Weather
	   Relative humidity, temperature in C */
	humidity float,
	temperature float,

	/* Virus lockdown info */
	start_cases date,
	start_socdist date,
	start_lockdown date,

	`geometry` json

) collate utf8_bin;

create table test_locations (
	location_id int auto_increment primary key,
	/* Administrative division location */
	admin0 varchar(256) default '',
	admin1 varchar(256) default '',
	admin2 varchar(256) default '',

	/* Administrative division ISO codes */
	admin0_code varchar(2) default '',
	admin1_code varchar(2) default '',
	admin2_code varchar(10) default '',

	/* Specificity of location */
	admin_level enum("world", "admin0", "admin1", "admin2"),

	/* Demographics */
	population float,
	population_density float,

	latitude float(10, 6),
	longitude float(10, 6),
	
	/* Weather
	   Relative humidity, temperature in C */
	humidity float,
	temperature float,

	/* Virus lockdown info */
	start_cases date,
	start_socdist date,
	start_lockdown date,

	`geometry` json

) collate utf8_bin;

create table test_datapoints (
	entry_date varchar(16),
	update_time datetime not null default CURRENT_TIMESTAMP,
	
	admin0 varchar(320) default '',
	admin1 varchar(320) default '',
	admin2 varchar(320) default '',
	`group` varchar(320) default '',
	
	total integer default 0,
	recovered integer default 0,
	deaths integer default 0,
	active integer default 0,
	serious integer default 0,
	tests integer default 0,
	hospitalized integer default 0,

	dtotal integer default 0,
	drecovered integer default 0,
	ddeaths integer default 0,
	dactive integer default 0,
	dserious integer default 0,
	dtests integer default 0,
	dhospitalized integer default 0,

	source_total TEXT,
	source_recovered TEXT,
	source_deaths TEXT,
	source_serious TEXT,
	source_tests TEXT,
	source_hospitalized TEXT,

	PRIMARY KEY(admin0, admin1, admin2, entry_date)
) COLLATE utf8_bin;

create table hospitals (
	hospital_id int auto_increment primary key,
	hospital_name varchar(256),
	hospital_type varchar(256),
	`address1` varchar(256),
	`address2` varchar(256),
	admin0 varchar(256),
	admin1 varchar(256),
	admin2 varchar(256),
	licensed_beds int default 0,
	staffed_beds int default 0,
	icu_beds int default 0,
	adult_icu_beds int default 0,
	pediatric_icu_beds int default 0,
	potential_beds_increase int default 0,
	average_ventilator_usage int default 0
);

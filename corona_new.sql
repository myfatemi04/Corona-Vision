drop table if exists test;
drop table if exists locations;

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
	start_lockdown date

) collate utf8_bin;

create table test (
	entry_date date,
	update_time datetime default current_timestamp,

	admin0 varchar(256),
	admin1 varchar(256),
	admin2 varchar(256),
	
	total int,
	deaths int,
	recoveries int,
	tests int,
	serious int,
	hospitalized int,
	
	total_new int,
	deaths_new int,
	recoveries_new int,
	tests_new int,
	serious_new int,
	hospitalized_new int,

	source_total text,
	source_deaths text,
	source_recoveries text,
	source_tests text,
	source_serious text,
	source_hospitalized text,
	
	primary key(entry_date, admin0, admin1, admin2)
);

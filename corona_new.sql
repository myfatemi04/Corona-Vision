drop table if exists test;
drop table if exists locations;

create table locations (
	location_id int auto_increment primary key,
	/* Administrative division location */
	country varchar(256) default '',
	province varchar(256) default '',
	county varchar(256) default '',

	/* Administrative division ISO codes */
	country_code varchar(2) default '',
	province_code varchar(2) default '',
	county_code varchar(10) default '',

	/* Specificity of location */
	admin_level enum("world", "country", "province", "county"),

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

	country varchar(256),
	province varchar(256),
	county varchar(256),
	
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
	
	primary key(entry_date, country, province, county)
);

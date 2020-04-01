create database if not exists corona;
use corona;
drop table if exists datapoints;
create table datapoints (
	data_id int not null auto_increment primary key,
	entry_date date,
	
	admin2 varchar(320),
	province varchar(320),
	country varchar(320),
	
	latitude float(10, 6) not null,
	longitude float(10, 6) not null,
	
	confirmed int,
	recovered int,
	dead int,
	active int
);
drop table if exists data_entries;
create table data_entries (
	entry_date date primary key,
	total_confirmed int,
	total_recovered int,
	total_dead int,
	total_active int
);

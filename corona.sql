create database if not exists corona;
use corona;
drop table if exists datapoints;
create table datapoints (
	data_id int not null auto_increment primary key,
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
	dead int,
	active int,

	dconfirmed int,
	drecovered int,
	ddead int,
	dactive int
);

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

	location_labelled boolean,
	is_first_day boolean,
	
	confirmed int,
	recovered int,
	dead int,
	active int,

	dconfirmed int,
	drecovered int,
	ddead int,
	dactive int
);

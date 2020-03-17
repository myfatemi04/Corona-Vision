drop table if exists users;
create table users (
	user_id int not null auto_increment primary key,
	email varchar(320),
	firstname varchar(32),
	lastname varchar(32),
	password_encrypt varchar(256),
	has_corona BOOLEAN
);
drop table if exists datapoints;
create table datapoints (
	data_id int not null auto_increment primary key,
	location varchar(320),
	latitude float(10, 6) not null,
	longitude float(10, 6) not null,
	confirmed int,
	recovered int,
	dead int,
	email varchar(320),
	status int
);

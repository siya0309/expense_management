create database expense_management;
use expense_management;
create table users(user_id int auto_increment primary key,
	name varchar(100),
    email varchar(100) unique,
    password varchar(200)
    );
create table income(income_id int auto_increment primary key,
	user_id int,
    amount decimal(10,2),
    source varchar(100),
    date date,
    foreign key(user_id) references users(user_id)
    );
    
create table expense(expensw_id int auto_increment primary key,
	user_id int,
    amount decimal(10,2),
    category varchar(200),
    date date,
    description text,
    foreign key(user_id) references users(user_id)
    );
desc expense;
desc users;
desc income;
select * from users;

    

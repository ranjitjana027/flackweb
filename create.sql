create table users
(
  username varchar(50) primary key,
  password varchar(30) not null
);

create table display
  (
    username varchar(50) references users(username) on delete cascade,
    display_name varchar(30) not null
  );

create table channels
  (
    username varchar(50) references users(username) on delete cascade,
    channel varchar(30) not null
  );

create table messages
  (
    channel varchar(30) not null,
    username varchar(50) references users(username) on delete cascade,
    message varchar(200) not null
  );

create table channels(
  id primary key,
  name varchar(255),
  count_user integer,
  signing text,
  link text,
  confirm_public boolean,
  empty_string boolean
);

create table users(
    id primary key,
    message_id int
);
select * from users;
drop table channels;


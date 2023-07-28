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

create table posts(
    id primary key,
    text text,
    under_the_text boolean,
    media boolean,
    button boolean
);

create table buttons(
    id primary key,
    name text,
    type text,
    number integer,
    message_id int,
    foreign key (id) references posts(id)
);

create table url_buttons(
    id primary key,
    url text,
    id_button integer,
    foreign key (id_button) references buttons(id)
);

create table hidden_buttons(
    id primary key,
    text_by_subscriber text,
    text_bu_not_subscriber text,
    id_button integer,
    foreign key (id_button) references buttons(id)
);

create table media(
    id primary key,
    path_to_file text,
    type text,
    number integer,
    id_post integer,
    foreign key (id_post) references posts(id)
);

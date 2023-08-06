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
    media boolean,
    button boolean,
    protect boolean,
    time integer,
    duration integer,
    delayed text,
    send_time integer,
    end_posting integer
);


-- create table buttons(
--     id primary key,
--     name text,
--     type text,
--     post_id int,
--     foreign key (post_id) references posts(id)
-- );

create table url_buttons(
    id primary key,
    name text,
    url text,
    sizes text,
    id_post integer,
    foreign key (id_post) references posts(id)
);

create table hidden_buttons(
    id primary key,
    name text,
    text_by_subscriber text,
    text_by_not_subscriber text,
    id_post integer,
    foreign key (id_post) references posts(id)
);

create table media(
    id primary key,
    path_to_file text,
    type integer,
    location boolean,
    id_post integer,
    foreign key (id_post) references posts(id)
);

create table post_channel(
    id primary key,
    id_post integer,
    id_channel integer,
    foreign key (id_post) references posts(id),
    foreign key (id_channel) references channels(id)
);
drop table users;
drop table media;
drop table posts;
drop table hidden_buttons;
drop table url_buttons;
drop table post_channel;

create table registered_emails(id int serial primary key,emails varchar(max) unique)



docker run -d   --name my_postgres_db   -e POSTGRES_USER=myuser   -e POSTGRES_PASSWORD=mypassword   -e POSTGRES_DB=user_activity   -v pg_user_data:/var/lib/postgresql   -p 5432:5432   postgres:alpine
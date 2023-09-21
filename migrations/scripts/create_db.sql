select 'create database dataops' where not exists (select from pg_database where datname = 'dataops')\gexec
\c dataops

CREATE TABLE "results" (
  "id" bigint PRIMARY KEY NOT NULL,
  "vacancy_name" char(120) NOT NULL,
  "url" char(120) NOT NULL,
  "company" char(120),
  "salary" bigint,
  "currency" char(4),
  "location" char(120),
  "metro" char(120)
);



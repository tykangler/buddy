CREATE TABLE transaction_days (
   id INTEGER PRIMARY KEY,
   day_of_month INTEGER,
   recurring_id INTEGER,
   FOREIGN KEY (recurring_id) REFERENCES recurring(id)
);
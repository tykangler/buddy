CREATE TABLE recurring (
   id INTEGER PRIMARY KEY,
   name TEXT NOT NULL UNIQUE,
   type TEXT NOT NULL,
   frequency INTEGER NOT NULL,
   unit TEXT NOT NULL,
   amount NUMERIC NOT NULL,
   begin TEXT,
   end TEXT
);
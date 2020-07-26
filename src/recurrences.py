from dto.recurring import recurring_dto
import sqlite3

class recurrences:
   def __init__(self, db_info):
      if len(db_info) != 2:
         raise ValueError("invalid database information")
      (self.db_path, self.table_name) = db_info

   def enter(self, name, type, frequency, unit, amount, begin, end):
      with sqlite3.connect(self.db_path) as conn:
         cursor = conn.cursor()
         cursor.execute(f"""
                        INSERT INTO [{self.table_name}] 
                        ([name], [type], [frequency], [unit], [amount], [begin], [end])
                        VALUES
                        (?, ?, ?, ?, ?, ?)
                        """, (name, type, frequency, unit, amount, begin, end))
from decimal import Decimal
from itertools import chain
import datetime

class Entry:
   def __init__(self, name, expected):
      self.name = name
      self._expected = Decimal(expected)

   @classmethod
   def from_json(cls, obj):
      new_section = cls(obj["name"], obj["expected"])
      return new_section

   def to_json(self):
      return dict(name=self.name, expected=float(self._expected))

   @property
   def expected(self):
      return self._expected

   @expected.setter
   def expected(self, new_val):
      self._expected = Decimal(new_val)

class Section:
   """
   tracks expected dollar amounts
   """
   def __init__(self, name):
      self.name = name
      self._entries = {}
      self._total = Decimal(0)

   @classmethod
   def from_json(cls, obj):
      new_section = cls(obj["name"])
      entries = obj["entries"]
      new_section._entries = {entry_id: Entry.from_json(entries[entry_id]) 
                              for entry_id in entries}
      new_section._total = Decimal(obj["total"])
      return new_section

   def to_json(self):
      return dict(name=self.name,
                  entries={entry_id: self._entries[entry_id].to_json() for entry_id in self._entries},
                  total=float(self._total))

   def plan(self, entry_id, name, expected):
      self._entries[entry_id] = Entry(name, expected)
      self._total += expected
   
   def remove(self, entry_id):
      amt = self._entries[entry_id].expected
      del self._entries[entry_id]
      self._total -= amt

   def __iter__(self):
      return iter(self._entries)

   def __getitem__(self, entry_id):
      return self._entries[entry_id]

   def __contains__(self, entry_id):
      return entry_id in self._entries

   def __len__(self):
      return len(self._entries)

   def __eq__(self, other):
      return self.name == other.name

   @property
   def total(self):
      return self._total

class Budget:
   """
   Used to plan transactions and exchanges. Entries are organized into two sections:
   income, and expense.
   args:
      name (str): The name of the budget
      start (str, datetime.date): Beginning of the date range, Must be less than end
      end (str, datetime.date): End of the date range, Must be greater than start
   """

   SECTIONS = ["income", "expense"]
   INCOME, EXPENSE = 0, 1
   
   def __init__(self, name, start, end):
      self.name = name
      self._start = datetime.date(start)
      self._end = datetime.date(end)
      self._sections = [Section(sect_name) for sect_name in self.SECTIONS]

   @classmethod
   def from_json(cls, obj):
      new_budget = cls(name=obj["name"], start=obj["start"], end=obj["end"])
      sections = obj["sections"]
      new_budget._sections = [Section.from_json(sect_name) for sect_name in sections]
      return new_budget

   def to_json(self):
      return dict(name=self.name,
                  start=self._start, end=self._end, 
                  sections=[section.to_json() for section in self._sections])
   
   @property
   def start(self):
      "return the beginning of the date range for budget"
      return self._start

   @start.setter
   def start(self, new_date):
      "set the beginning of date range for budget. new date must be less than end of date range."
      if new_date >= self._end:
         raise ValueError(f"{new_date} not less than end of date range {self._end}")
      self._start = datetime.date(new_date)
   
   @property
   def end(self):
      """return the end of the date range for budget. new date must be greater than beginning 
      of date range."""
      return self._end

   @end.setter
   def end(self, new_date):
      """set the end of the date range for budget. new date must be greater than beginning 
      of the date range."""
      if new_date <= self._start:
         raise ValueError(f"{new_date} not greater than start of date range {self._start}")
      self._end = datetime.date(new_date)

   @property
   def balance(self):
      "returns total income minus total expenses"
      return self._sections[self.INCOME].total - self._sections[self.EXPENSE].total

   def income(self):
      "return the income section of this budget"
      return self._sections[self.INCOME]

   def expense(self):
      "return the expense section of this budget"
      return self._sections[self.EXPENSE]

   def __iter__(self):
      "iterate over all id values in the budget"
      return chain(*(iter(sect) for sect in self._sections))

   def __getitem__(self, entry_id):
      """retrieves the entry associated with entry_id. returns a tuple with
      the first element being the section name and the second being the entry
      object - (section_name, entry)"""
      sect = entry_id in self
      if not sect:
         raise KeyError("entry not found")
      return sect.name, sect[entry_id]

   def __contains__(self, entry_id):
      """if entry_id is found within any section, then the section it was found in is
      returned. else, returns None."""
      for sect in self._sections:
         if entry_id in sect:
            return sect
      return None
         
   def __str__(self):
      return self.name
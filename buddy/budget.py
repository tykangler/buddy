from decimal import Decimal
from itertools import chain
import datetime

class Entry:
   def __init__(self, name, expected):
      self.name = name
      self.expected = Decimal(expected)

   @classmethod
   def from_json(cls, obj):
      new_section = cls(obj["name"], obj["expected"])
      return new_section

   def to_json(self):
      return dict(name=self.name, expected=float(self.expected))

class Section:
   """
   tracks expected dollar amounts
   """
   def __init__(self, name):
      self._name = name
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
      return dict(name=self._name,
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
      return self._name == other._name

   def name(self):
      return self._name

   def total(self):
      return self._total

class Budget:
   """
   Used to plan transactions and exchanges. Entries are organized into two sections:
   income, and expense.
   Args:
      name (str): The name of the budget
      from_date (str, datetime.date): Beginning of the date range
      to_date (str, datetime.date): End of the date range
   """

   SECTIONS = ["income", "expense"]
   INCOME, EXPENSE = 0, 1
   
   def __init__(self, name, from_date, to_date):
      self._name = name
      self._from = datetime.date(from_date)
      self._to = datetime.date(to_date)
      self._sections = [Section(sect_name) for sect_name in self.SECTIONS]

   @classmethod
   def from_json(cls, obj):
      new_budget = cls(name=obj["name"], from_date=obj["from_date"], to_date=obj["to_date"])
      sections = obj["sections"]
      new_budget._sections = [Section.from_json(sect_name) for sect_name in sections]
      return new_budget

   def to_json(self):
      return dict(name=self._name,
                  from_date=self._from, to_date=self._to, 
                  sections=[section.to_json() for section in self._sections])

   def name(self):
      return self._name

   def start_date(self):
      return self._from
   
   def end_date(self):
      return self._to

   def balance(self):
      "returns total income minus total expenses"
      return self._sections[self.INCOME].total() - self._sections[self.EXPENSE].total()

   def income(self):
      return self._sections[self.INCOME]

   def expense(self):
      return self._sections[self.EXPENSE]

   def __iter__(self):
      return chain(*(iter(sect) for sect in self._sections))

   def __getitem__(self, entry_id):
      sect = entry_id in self
      if not sect:
         raise KeyError("entry not found")
      return sect.name, sect[entry_id]

   def __contains__(self, entry_id):
      for sect in self._sections:
         if entry_id in sect:
            return sect
      return None
         
   def __str__(self):
      return self._name
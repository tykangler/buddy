import copy
from decimal import Decimal

class AccountError(Exception):
   pass

class Section:
   BALANCE = 0
   DESC = 1

   class AccountIterator:
      def __init__(self, section):
         self._header = section.header
         self._entry_iterator = iter(section._entries)

      def __next__(self):
         return self._header, next(self._entry_iterator)

   def __init__(self, header):
      self._header = header
      self._entries = {}
      self._total = Decimal(0)

   @property
   def header(self):
      return self._header

   def enter(self, name, balance, description):
      if name in self._entries:
         self._total += balance - self._entries[name][self.BALANCE]
      else:
         self._total += balance  
      self._entries[name] = [balance, description]

   def remove(self, name):
      if name not in self._entries:
         raise AccountError(f"{name} not an added entry")
      self._total -= self._entries.pop(name)[self.BALANCE]

   @property
   def total(self):
      return self._total

   def __getitem__(self, name):
      return tuple(self._entries[name])
      
   def __contains__(self, name):
      return name in self._entries

   def __iter__(self):
      return self.AccountIterator(self)

def create_statement(header1, header2):
   return {header1: Section(header1), header2: Section(header2)}

def balance(statement):
   if len(statement) > 2:
      raise ValueError(f"statement has {len(statement)} sections, but only two allowed")
   value_in, value_out = statement
   return value_in - value_out

def create_budget(start, end, *, roll=False, clone=None):
   budget = dict(start=start, end=end, roll=roll)
   if clone:
      budget["income"] = copy.deepcopy(clone["income"])
      budget["expense"] = copy.deepcopy(clone["expense"])
   else:
      budget.update(create_statement("income", "expense"))
   return budget

def create_snapshot(start, end):
   return dict(start=start, end=end, 
               balance=create_statement("assets", "liabilities"),
               profit=create_statement("income", "expenses"), 
               cash=create_statement("inflow", "outflow"))

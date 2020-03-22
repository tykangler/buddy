import numbers
from decimal import Decimal
import datetime

class Transaction:
   """
   a single line item in a financial statement. Contains fields for name, date, and 
   amount earned in transaction
   """
   def __init__(self, name, amount, date):
      self.name = name
      self._amount = Decimal(amount)
      self._date = datetime.date(date)

   @property
   def amount(self):
      return self._amount
   
   @amount.setter
   def amount(self, new_val):
      self._amount = Decimal(new_val)

   @property
   def date(self):
      return self._date

   @date.setter
   def date(self, new_val):
      self._date = datetime.date(new_val)

   @classmethod
   def from_json(cls, obj):
      return cls(obj["name"], obj["amount"], obj["date"])

   def to_json(self):
      return dict(name=self.name, amount=float(self.amount), date=str(self.date))

   def __repr__(self):
      return f"Transaction({self.name}, {self.amount}, {self.date})"

   def __str__(self):
      return self.name

class Ledger:
   "tracks dollar amounts"
   def __init__(self, name, start, end):
      self.name = name
      self._total = Decimal(0)
      self._transactions = {}
      self._start = datetime.date(start)
      self._end = datetime.date(end)

   @classmethod
   def from_json(cls, obj):
      new_ledger = cls(obj["name"], obj["start"], obj["end"])
      new_ledger._total = obj["total"]
      trans = obj["transactions"]
      new_ledger._transactions = {entry_id: Transaction.from_json(trans[entry_id]) 
                                  for entry_id in trans}
      return new_ledger

   def to_json(self):
      return dict(total=float(self._total), 
                  transactions={entry_id: self._transactions[entry_id].to_json() 
                                for entry_id in self._transactions})

   def enter(self, entry_id, *, name, amount, date):
      self._transactions[entry_id] = Transaction(name=name, amount=amount, date=date)
      self._total += amount

   def remove(self, entry_id):
      amount_to_remove = self._transactions[entry_id].amount
      del self._transactions[entry_id]
      self._total -= amount_to_remove

   def __iter__(self):
      return iter(self._transactions)

   def __getitem__(self, entry_id):
      return self._transactions[entry_id]

   def __setitem__(self, entry_id, new_val):
      self._transactions[entry_id] = new_val

   def __contains__(self, entry_id):
      return entry_id in self._transactions

   def __len__(self):
      return len(self._transactions)

   def __str__(self):
      return self.name

   @property
   def total(self):
      return self._total

   @property
   def start(self):
      return self._start

   @start.setter
   def start(self, new_date):
      if new_date >= self._end:
         raise ValueError(f"{new_date} not less than end of date range {self._end}")
      self._start = datetime.date(new_date)

   @property
   def end(self):
      return self._end

   @end.setter
   def end(self, new_date):
      if new_date <= self._start:
         raise ValueError(f"{new_date} not greater than start of date range {self._start}")
      self._end = datetime.date(new_date)


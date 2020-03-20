import numbers
from decimal import Decimal
import datetime

class Transaction:
   """
   a single line item in a financial statement. Contains fields for name, date, and 
   amount earned in transaction
   """
   def __init__(self, name, amount, date):
      self._name = name
      self._amount = Decimal(amount)
      self._date = datetime.date(date)

   def name(self):
      return self._name

   def amount(self):
      return self._amount

   def date(self):
      return self._date

   @classmethod
   def from_json(cls, obj):
      return cls(obj["name"], obj["amount"], obj["date"])

   def to_json(self):
      return dict(name=self._name, amount=float(self._amount), date=str(self._date))

   def __repr__(self):
      return f"Transaction({self._name}, {self._amount}, {self._date})"

   def __str__(self):
      return self._name

class Ledger:
   "tracks dollar amounts"
   def __init__(self, name, from_date, to_date):
      self._name = name
      self._total = Decimal(0)
      self._transactions = {}
      self._from_date = datetime.date(from_date)
      self._to_date = datetime.date(to_date)

   @classmethod
   def from_json(cls, obj):
      new_ledger = cls(obj["name"], obj["from_date"], obj["to_date"])
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
      return self._name

   def name(self):
      return self._name

   def total(self):
      return self._total

   def start(self):
      return self._from_date

   def end(self):
      return self._to_date


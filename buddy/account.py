from decimal import Decimal

import tag

class AccountError(Exception):
   pass

class Account(tag.Taggable):
   """
      A financial account. Stores an account name, account balance, and description
   """
   def __init__(self, name, balance, description=""):
      self._name = name
      self._balance = balance
      self._description = description
      super().__init__()

   @property
   def name(self):
      return self._name

   @property
   def balance(self):
      return self._balance

   @balance.setter
   def balance(self, val):
      self._balance = val

   @property
   def description(self):
      return self._description

   @description.setter
   def description(self, new_desc):
      self._description = new_desc

class Statement(tag.Taggable):
   def __init__(self):
      self._entries = {}
      self._total = Decimal(0)
      super().__init__()

   def enter(self, name, account):
      if name in self._entries:
         self._total += account.balance - self._entries[name]
      else:
         self._total += account.balance
      self._entries[name] = name

   def remove(self, name):
      if name not in self._entries:
         raise AccountError(f"{name} not an added entry")
      self._total -= self._entries.pop(name).balance

   @property
   def total(self):
      return self._total

   def __getitem__(self, name):
      return self._entries[name]
      
   def __iter__(self):
      return iter(self._entries)
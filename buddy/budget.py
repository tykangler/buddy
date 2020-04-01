import copy

import account
import tag

class BudgetError(Exception):
   pass

class Budget(tag.Taggable):
   def __init__(self, start, end, *, roll=False):
      self._start = start
      self._end = end
      self.roll = roll
      self._income = account.Statement()
      self._expense = account.Statement()

   @classmethod
   def clone(cls, other_budget, start, end, *, roll=False):
      new_budget = cls(start, end, roll=roll)
      new_budget._income = copy.deepcopy(other_budget._income)
      new_budget._expense = copy.deepcopy(other_budget._expense)
      return new_budget

   @property
   def start(self):
      return self._start

   @start.setter
   def start(self, new_date):
      if new_date >= self._end:
         raise BudgetError(f"start date {new_date} must be less than end date {self._end}")
      self._start = new_date

   @property
   def end(self):
      return self._end

   @end.setter
   def end(self, new_date):
      if new_date <= self._start:
         raise BudgetError(f"end date {new_date} must be greater than start date {self._start}")
      self._end = new_date

   @property
   def income(self):
      return self._income

   @property
   def expense(self):
      return self._expense

   
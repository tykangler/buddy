class Account:
   """
      A financial account. Stores an account name and an account balance
   """
   def __init__(self, name, balance):
      self._name = name
      self._balance = balance

   @property
   def name(self):
      return self._name

   @property
   def balance(self):
      return self._balance

   @balance.setter
   def balance(self, val):
      self._balance = val
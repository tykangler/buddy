from decimal import Decimal
import datetime as dt

import tag

class TransactionError(Exception):
   pass

class Transaction(tag.Taggable):
   MAX_NOTE_LEN = 50
   def __init__(self, debits: dict, credits: dict, note):
      amts_to_dec = lambda entry: {account: Decimal(entry[account]) for account in entry} 
      if len(note) > self.MAX_NOTE_LEN:
         raise TransactionError(f"length of note is greater than {self.MAX_NOTE_LEN}")
      elif not isinstance(note, str):
         raise TransactionError(f"attempted to set non-str value to note")
      
      self._note = note
      self._debits = amts_to_dec(debits)
      self._credits = amts_to_dec(credits)

      debits_sum = sum(self._debits.values())
      credits_sum = sum(self._credits.values())
      if debits_sum != credits_sum:
         raise TransactionError(f"debit of {debits_sum} doesn't match credit of {credits_sum}")
      self._total = debits_sum
      super().__init__()

   @property
   def note(self):
      return self._note

   @note.setter
   def note(self, new_note):
      if len(new_note) > self.MAX_NOTE_LEN:
         raise ValueError(f"length of note is greater than {self.MAX_NOTE_LEN}")
      elif not isinstance(new_note, str):
         raise TypeError(f"attempted to set non-str value to note")
      self._note = new_note

   @property
   def total(self) -> int:
      return self._total

   def debit_accounts(self):
      return self._debits.keys()

   def credit_accounts(self):
      return self._credits.keys()

   def debit_value(self, account) -> Decimal:
      if account not in self._debits:
         raise KeyError(f"{account} not a debited account in this transaction")
      return self._debits[account]

   def credit_value(self, account) -> Decimal:
      if account not in self._credits:
         raise KeyError(f"{account} not a credited account in this transaction")
      return self._credits[account]

class Journal(tag.Taggable):
   def __init__(self):
      self._entries = dict()
      self._total = Decimal(0)
      super().__init__()

   def __getitem__(self, val):
      "retrieve a transaction at a date or within a range of dates if val is a slice"
      if isinstance(val, slice):
         new_journal = Journal()
         date_from = val.start if val.start else dt.date.min
         date_to = val.stop if val.stop else dt.date.max
         new_journal._entries = {date: trans for date, trans in self._entries.items() 
                                 if date < date_to and date >= date_from}
         new_journal._total = sum(tran.total for tran in new_journal._entries.values())
         return new_journal
      else:
         return self._entries[val]

   def __setitem__(self, val, transaction: Transaction):
      self._entries[val] = transaction
      self._total += transaction.total

   def __iter__(self):
      return iter(self._entries)

   def __len__(self):
      return len(self._entries)

   @property
   def total(self):
      return self._total
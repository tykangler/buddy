class TagError(Exception):
   pass

class Taggable:
   def __init__(self):
      self._tags = set()

   @property
   def tags(self):
      return self._tags

   def add_tag(self, tag):
      self._tags.add(tag)

   def remove_tag(self, tag):
      if tag in self._tags:
         self._tags.remove(tag)
      else:
         raise TagError(f"{tag} not present")
   
   def has_tag(self, val):
      return val in self._tags

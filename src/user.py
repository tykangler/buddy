import json
import os

class ConfigError(Exception):
   pass

class Configuration:
   def __init__(self, settings):
      self._settings = settings

   def __getitem__(self, option):
      if option not in self._settings:
         raise ConfigError(f"{option} is not an option")
      return self._settings[option]

   def __contains__(self, option):
      return option in self._settings

   def __setitem__(self, option, setting):
      if option not in self._settings:
         raise ConfigError(f"{option} is not an option")
      self._settings[option] = setting

def read(path, *, read_hook, default):
   if os.path.isfile(path):
      with open(path) as inp:
         obj = json.load(inp, object_hook=read_hook)
      return obj
   else:
      return default()

def write(obj, path, *, write_hook):
   with open(path, "w") as out:
      json.dump(obj, out, default=write_hook)
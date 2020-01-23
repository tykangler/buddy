class Dispatch:
   def __init__(self, command_dispatch):
      self.command_dispatch = command_dispatch
   
   def add_handler(self, command, handler):
      self.command_dispatch[command] = handler

   def execute(self, request):
      try:
         self.command_dispatch[request.command](*request.command_args)
      except TypeError:
         pass
      
class Request:
   def __init__(self, command, command_args):
      self.command = command
      self.command_args = command_args

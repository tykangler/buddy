import json

# Main Dash

INTRO = "Hi I'm Buddy!"
INPUT_ARRROW = "> "
COMMAND_ARROW = ">>> "
MIN_DESC_START = 12
MIN_SPACE_COMM_DESC = 3

def print_dashboard(command_to_desc):
   print(INTRO)
   start_description = max([len(command) for command in command_to_desc]) + MIN_SPACE_COMM_DESC
   start_description = max(start_description, MIN_DESC_START)
   for command in command_to_desc:
      print(command + 
            " " * (start_description - len(command)) + 
            command_to_desc[command])

def eofinput(prompt):
   try:
      return input(prompt)
   except EOFError:
      return ""

def collect_input(*, arrow):
   read = eofinput(arrow)
   while read != "":
      yield read.split()
      read = eofinput(arrow)
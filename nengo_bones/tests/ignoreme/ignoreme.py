# this will trigger a pylint unused-import error
import nengo_bones

# this will trigger a flake8 whitespace end of line error
str = """
abc 
de
"""

# this would be changed if black formatting were applied
not_black_formatted = ["a", "b",
                       "c"]

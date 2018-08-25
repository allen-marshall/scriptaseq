"""Utilities related to handling user-supplied scripts."""

# Name of the Python function that user-supplied scripts are expected to define in order to specify their functionality.
USER_SCRIPT_FUNC_NAME = 'script'

class UserScriptError(Exception):
  """Exception indicating that a user-supplied script failed in some way."""
  pass

def invoke_user_script(user_script, *args, **kwargs):
  """Invokes the specified user script, and returns its return value.
  Raises UserScriptError if the script fails.
  WARNING: Any string passed as the user_script parameter will be executed as a Python script. Avoid passing untrusted
    code in user_script.
  user_script -- String containing the user script to execute.
  args -- Positional arguments to pass to the script.
  kwargs -- Keyword arguments to pass to the script.
  """
  # Try to execute the script string.
  env = {}
  try:
    exec(user_script, env)
  except BaseException as e:
    raise UserScriptError('User script failed: {}'.format(e.message)) from e
  
  # Make sure the script defined a function as expected.
  if not USER_SCRIPT_FUNC_NAME in env:
    raise UserScriptError('User script failed to define function \'{}\''.format(USER_SCRIPT_FUNC_NAME))
  
  # Try to execute the function that was defined by the script string, and return its result.
  try:
    return env[USER_SCRIPT_FUNC_NAME](*args, **kwargs)
  except BaseException as e:
    raise UserScriptError('User script failed: {}'.format(e.message)) from e
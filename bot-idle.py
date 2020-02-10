"""
Idle bot that allows to control the OpenWPM browser by hand (in HF version).
"""

from automation import CommandSequence, TaskManager

NUM_BROWSERS = 1
sites = ['http://localhost:8080']

manager_params, browser_params = TaskManager.load_default_params(NUM_BROWSERS) # Load default parameters
manager_params['data_directory'] = '~/Desktop/idle/'
manager_params['log_directory'] = '~/Desktop/idle/'

instrumentation = True
for i in range(NUM_BROWSERS):
    browser_params[i]['http_instrument'] = instrumentation # Record HTTP Requests and Responses
    browser_params[i]['cookie_instrument'] = instrumentation # Record cookie changes
    browser_params[i]['navigation_instrument'] = instrumentation # Record navigations
    browser_params[i]['js_instrument'] = instrumentation # Record JS Web API calls
    browser_params[i]['save_content'] = instrumentation # Save all content of the response body
    browser_params[i]['headless'] = False # Use headless or headfull browser

manager = TaskManager.TaskManager(manager_params, browser_params)

for site in sites:
    command_sequence = CommandSequence.CommandSequence(site, reset=True)
    command_sequence.get(sleep=3600,timeout=3600)
    manager.execute_command_sequence(command_sequence)#, index='**') # (To have all browsers go to the same sites, add `index='**'`)
manager.close()

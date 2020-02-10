"""
Bot for automated measurement using `BrowserBasedBotFP` and JavaScript template attacks.
"""

from automation import CommandSequence, TaskManager
from selenium.webdriver.common.action_chains import ActionChains
import time

PORT_BR_BASED_BOT_FP = "8080"
PORT_TEMPLATE_ATTACK = "8000"

class Config:
    """
    Class representing one measurement configuration.
    """
    def __init__(self):
        self.framework = None # Either `'B'` for BrowserBasedBotFP or `'T'` for template attack
        self.http_instrument = None
        self.cookie_instrument = None
        self.navigation_instrument = None
        self.js_instrument = None
        self.save_content = None
        self.headless = None
    
    def description(self):
    """
    Get a comparatively short string containing the exact options of the configuration.
    """
        browForm = ""
        if self.headless:
            browForm = "HL"
        else:
            browForm = "HF"
        return "OWPMNightly70.0_gecko0.24.0_{0}_HTTP={1:d}_Cookie={2:d}_Navig={3:d}_JS={4:d}_SaveContent={5:d}".format(browForm, self.http_instrument, self.cookie_instrument, self.navigation_instrument, self.js_instrument, self.save_content)

config = []
for i in range(12):
    config.append(Config())
    if i in range(6):
        config[i].framework = 'B'
    else:
        config[i].framework = 'T'
    if i in [0, 2, 4, 6, 8, 10]:
        config[i].headless = False # Headful
    else:
        config[i].headless = True # Headless
for i in [0, 1, 6, 7]: # Without instrumentation
    config[i].http_instrument = False
    config[i].cookie_instrument = False
    config[i].navigation_instrument = False
    config[i].js_instrument = False
    config[i].save_content = False
for i in [2, 3, 8, 9]: # With JavaScript instrumentation
    config[i].http_instrument = False
    config[i].cookie_instrument = False
    config[i].navigation_instrument = False
    config[i].js_instrument = True
    config[i].save_content = False
for i in [4, 5, 10, 11]: # With full instrumentation
    config[i].http_instrument = True
    config[i].cookie_instrument = True
    config[i].navigation_instrument = True
    config[i].js_instrument = True
    config[i].save_content = True

# Custom functions
def fill_config(text, **kwargs): # Thanks to Benjamin Krumnow, see https://github.com/bkrumnow/StealthBot/blob/5f125c16ec9b9b17cefb1e90552fb49e88d658f1/automation/Commands/browser_commands.py#L377-L389
    """ types the name into the input field """
    webdriver = kwargs['driver']
    SELECTOR_FOR_FINGERPRINT_INPUT = "#txtConfDesc"
    ele = webdriver.find_element_by_css_selector(SELECTOR_FOR_FINGERPRINT_INPUT)
    SELECTOR_FOR_FINGERPRINT_BUTTON = "#btnFP"
    ele2 = webdriver.find_element_by_css_selector(SELECTOR_FOR_FINGERPRINT_BUTTON)
    action = ActionChains(webdriver)
    action.move_to_element(ele).click(ele).send_keys(text).move_to_element(ele2).click(ele2).perform()
    time.sleep(1)
    alert = webdriver.switch_to_alert()
    alert.dismiss()
    time.sleep(1)
    return

def take_fingerprint(**kwargs): # Thanks to Benjamin Krumnow, see https://github.com/bkrumnow/StealthBot/blob/5f125c16ec9b9b17cefb1e90552fb49e88d658f1/automation/Commands/browser_commands.py#L391-L399
    """ clicks the button in order to start fingerprinting """
    webdriver = kwargs['driver']
    print("Starting clicking")
    SELECTOR_FOR_FINGERPRINT_BUTTON = "#btnFP"
    ele = webdriver.find_element_by_css_selector(SELECTOR_FOR_FINGERPRINT_BUTTON)
    print(ele)
    action = ActionChains(webdriver)
    action.move_to_element(ele).click(ele).perform()
    print("done with clicking")

def execute_template_dialog(text, **kwargs): # Thanks to Benjamin Krumnow, see https://github.com/bkrumnow/StealthBot/blob/5f125c16ec9b9b17cefb1e90552fb49e88d658f1/automation/Commands/browser_commands.py#L401-L413
    """ clicks the button in order to start fingerprinting """
    webdriver = kwargs['driver']
    el = webdriver.find_element_by_css_selector("input")
    action = ActionChains(webdriver)
    action.move_to_element(el).click(el).perform()
    time.sleep(2)
    alert = webdriver.switch_to_alert()
    print("perform send keys")
    alert.send_keys(text)
    time.sleep(2)
    print("start")
    alert.accept()
    time.sleep(1500) # The timeout when this function is called triggers earlier so this ensures we wait until then
# End custom functions

for i in range(len(config)): # Measure each browser configuration after each other
    thisConfig = config[i]
    NUM_BROWSERS = 1
    manager_params, browser_params = TaskManager.load_default_params(NUM_BROWSERS) # Load default parameters
    manager_params['data_directory'] = '~/Desktop/measurement/'
    manager_params['log_directory'] = '~/Desktop/measurement/'
    site = "http://localhost:"
    if thisConfig.framework == 'B':
        site += PORT_BR_BASED_BOT_FP
    elif thisConfig.framework == 'T':
        site += PORT_TEMPLATE_ATTACK
    else:
        raise ValueError("Unknown framework option:", thisConfig.framework)
    browser_params[0]['http_instrument'] = thisConfig.http_instrument
    browser_params[0]['cookie_instrument'] = thisConfig.cookie_instrument
    browser_params[0]['navigation_instrument'] = thisConfig.navigation_instrument
    browser_params[0]['js_instrument'] = thisConfig.js_instrument
    browser_params[0]['save_content'] = thisConfig.save_content
    browser_params[0]['headless'] = thisConfig.headless
    manager = TaskManager.TaskManager(manager_params, browser_params)
    command_sequence = CommandSequence.CommandSequence(site, reset=True)
    confDescr = thisConfig.description()
    if thisConfig.framework == 'B':
        command_sequence.get(sleep=10, timeout=60)
        command_sequence.run_custom_function(fill_config, (confDescr,), timeout=5)
        command_sequence.run_custom_function(take_fingerprint, timeout=15)
    elif thisConfig.framework == 'T':
        command_sequence.get(sleep=10, timeout=170) # Higher timeouts because template attacks take longer
        command_sequence.run_custom_function(execute_template_dialog, (confDescr,), timeout=150) # Higher timeouts because template attacks take longer
    else:
        raise ValueError("Unknown framework option:", thisConfig.framework)
    manager.execute_command_sequence(command_sequence)
    manager.close()
    print("Iteration {} finished.".format(i))

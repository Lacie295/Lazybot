# created by Sami Bosch on Wednesday, 31 October 2018

# This script launches the necessary functions for the test bot

import json
from run import runbot


with open('config.json') as f:
    data = json.load(f)
runbot(data["TestToken"])
import os
import logging
import re

logger = logging.getLogger()
logger.setLevel(logging.INFO)


class LexHandler:
    """handles incoming and outgoing params to Lex and validates slots"""

    def __init__(self, event):
        self.event = event
        self.slots = event['currentIntent']['slots']
        self.intent = event['currentIntent']['name']
        self.input_text = event['inputTranscript']
        self.sess_attr = event['sessionAttributes']
        self.invocation = event['invocationSource']


    ### Helpers to control state of the conversation

    def delegate(self, intent=None):
        return {
            'sessionAttributes': self.sess_attr,
            'dialogAction': {
                'type': 'Delegate',
                'slots': self.slots
            }
        }

    def fulfill(self, msg="Your document is complete."):
        return {
            'sessionAttributes': self.sess_attr,
            'dialogAction': {
                'type': 'Close',
                'fulfillmentState': 'Fulfilled',
                "message": {
                  "contentType": "PlainText",
                  "content": msg
                }
            }
        }



    def elicit_slot(self, err):
        return {
            'sessionAttributes': self.sess_attr,
            'dialogAction': {
                'type': 'ElicitSlot',
                'intentName': self.intent,
                'slots': self.slots,
                'slotToElicit': err['violatedSlot'],
                'message': {'contentType': 'PlainText', 'content': err['message'] }
            }
        }

    def elicit_intent(self, msg="How can I help you?"):
        return {
             "sessionAttributes": self.sess_attr,
             "dialogAction": {
                "type": "ElicitIntent",
                "message": {
                  "contentType": "PlainText",
                  "content": msg
            }
        }
    }

    #### Slot Validators

    def val_error(self, slot, msg):
        res = {"isValid": False, "violatedSlot": slot, 'message': msg }
        return res

    def validates_presence(self, slot, msg=None):
        if not self.slots[slot]: # raise val_error
            if not msg:
                msg = "What is the {}?".format(slot)
            err = self.val_error(slot, msg)
            return self.elicit_slot(err)

    def validates_in(self, iterable, slot, msg=None):
        if self.slots[slot] not in iterable:
            if not msg:
                iter_list = ", ".join([str(x) for x in iterable])
                msg = "Your {0} must be one of the following: {1}".format(slot, iter_list)
            err = self.val_error(slot, msg)
            return self.elicit_slot(err)

    def validates_length(self, rng, slot, msg=None):
        if not self.slots[slot]: return
        # rng = (min, max)
        if len(self.slots[slot]) > rng[1]:
            if not msg:
                msg = "Your {0} is too large. I can handle {1} characters max.".format(slot, rng[1])
            err = self.val_error(slot, msg)
            return self.elicit_slot(err)

        if len(self.slots[slot]) < rng[0]:
            if not msg:
                msg = "Your {0} is too small. I need at least {1} characters.".format(slot, rng[0])
            err = self.val_error(slot, msg)
            return self.elicit_slot(err)


    def validates_pattern(self, regex, slot, msg=None):
        if not self.slots[slot]: return

        pattern = re.compile(regex)
        if not pattern.match(self.slots[slot]):
            if not msg:
                msg = "Your {0} seems to have an invalid format".format(slot)
            err = self.val_error(slot, msg)
            return self.elicit_slot(err)


    def run_validation(self, validators):
        for error in validators:
            if error:
                return error

        return lex.delegate()

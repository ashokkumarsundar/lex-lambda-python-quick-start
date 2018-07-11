import logging
import LexHandler from LexHandler

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def help_user(lex):
    return lex.fulfill("Start by telling me what type of legal document you need? Such as 'bill of sale', 'promissory note', 'pool service contract', etc. Or you can say 'show all'")

def not_understood(lex):
    return lex.fulfill("I did not understand that... Can you rephrase your message?")

def dispatch(lex):
    """Routes conversation based on incoming intent"""

    if lex.intent == "BasicHelp":
        return help_user(lex)
    else:
        return not_understood(lex)


def lambda_handler(event, context=None):
    lex = LexHandler(event)
    logger.info(('IN', event))

    try:
        res = dispatch(lex)
        logger.info(('OUT', res))
        return res
    except Exception as e:
        logger.error(e)

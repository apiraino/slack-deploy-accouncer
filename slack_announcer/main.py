# coding: utf-8

import logging
import json
from json import JSONEncoder
from urllib.parse import parse_qs
from urllib.error import URLError
from urllib.request import Request, urlopen
from slack_announcer.utils import get_slack_key

logger = logging.getLogger('slack_announcer.aws_lambda')
logger.setLevel(logging.DEBUG)

# cmd param validation
WORLDS = ['duedot', 'quokky']
COMPONENTS = ['platform', 'backend', 'webapp']
ENVS = ['master', 'develop', 'staging', 'production']
# where to post the message
DEST_CHANNEL = 'deployments'

SLACK_URL = 'https://slack.com/api/chat.postMessage'
# token Slack is using to call me
SLACK_TOKEN = get_slack_key('slack_token')
# token to post a message on slack
APP_TOKEN = get_slack_key('app_token')

CMD_HELP = {
   'response_type': 'ephemeral',
   'text': 'How to use /deploy',
   'attachments': [
       {
           'text': '/deploy <world> <component> <environment> <branch>\nex. /deploy quokky webapp staging release/develop\n* world: required\n* component: required\n* environment: required\n* branch: optional\n'
       }
   ]
}


class ValidationError(Exception):

    def __init__(self, message, *args, **kwargs):
        self.message = message
    pass


class SlackPostError(ValidationError):

    pass


def validate_input(user_params):
    items = user_params.split()
    if len(items) < 3:
        raise ValidationError('Please at least 3 params (type `/deploy help`)')
    world, component, env = items[0], items[1], items[2]
    try:
        branch = items[3]
    except IndexError:
        branch = '-'
    if world not in WORLDS:
        raise ValidationError(
            'Allowed worlds: {} (type `/deploy help`)'.format(
                ', '.join(WORLDS)))
    if component not in COMPONENTS:
        raise ValidationError(
            'Allowed components: {} (type `/deploy help`)'.format(
                ', '.join(COMPONENTS)))
    if env not in ENVS:
        raise ValidationError(
            'Allowed environment: {} (type `/deploy help`)'.format(
                ', '.join(ENVS)))
    return world, component, env, branch


def call_slack(url, channels, author_name, **kwargs):
        payload = {
            'channel': DEST_CHANNEL,
            'text': '{} is performing a deploy'.format(author_name),
            'attachments': [{
                'fields': [
                    {
                        'title': 'World',
                        'value': kwargs['world'],
                        'short': True
                    },
                    {
                        'title': 'Component',
                        'value': kwargs['component'],
                        'short': True
                    },
                    {
                        'title': 'Environment',
                        'value': kwargs['env'],
                        'short': True
                    },
                    {
                        'title': 'Branch',
                        'value': kwargs['branch'],
                        'short': True
                    }
                ],
                'color': '#00ff00'
            }],
        }
        payload = bytes(json.dumps(payload, cls=JSONEncoder), encoding='utf-8')
        req = Request(SLACK_URL)
        req.add_header('Authorization', 'Bearer {}'.format(APP_TOKEN))
        req.add_header('Content-Type', 'application/json')
        resp_data = ''
        try:
            resp = urlopen(req, data=payload).read()
            resp_data = json.loads(resp)
        except URLError as exc:
            raise SlackPostError(exc)
        if resp_data['ok'] is not True:
            raise SlackPostError("Error posting message: {}".format(resp_data))


def lambda_handler(event, context):
    params = parse_qs(event['body-json'])
    resp = 'Broadcasting announcement! :antonio_happy: :gun:'
    if params['token'][0] != SLACK_TOKEN:
        resp = 'Invalid token'
    else:
        try:
            text = params['text'][0]
        except KeyError:
            return 'Unsure on what to do? Type `/deploy help`'
        logging.info(text)
        if text == 'help':
            return CMD_HELP
        try:
            world, component, env, branch = validate_input(params['text'][0])
        except ValidationError as exc:
            return exc.message
        try:
            slack_url = params['response_url'][0]
            call_slack(slack_url, DEST_CHANNEL, params['user_name'][0],
                       world=world, component=component, env=env, branch=branch)
        except SlackPostError as exc:
            return 'Error posting message: {}'.format(exc.message)
    return resp

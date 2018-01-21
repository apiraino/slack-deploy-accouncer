# Slack deploy announcer
A Python3 script implementing a `/deploy` Slack custom slash command.

This replaces shouting at your teammates ("hey people deployyyyy on production", "WAT?!?!" "LOL")

Also useful to know which branch will be deployed.

## Requirements
- `boto3` library
- tested with Python 3.6.3 (Python 2.x not supported - about time)

## Install
__This script code has been factored to be deployed on AWS Lambda__

- Configure the AWS Lambda
- Create the credentials to access credentials (EC2 > AWS Parameter Store)

  `/slack_deployer/app_token`

  `/slack_deployer/slack_token`
- Create a zip of this package

  `zip -r slack_announcer.zip slack_announcer`
- upload the zip on AWS Lambda

## Slack command usage

`/deploy help` for a quick syntax help

`/deploy <world> <component> <environment> <branch>` full command

## Notes
This repo __can't__ be simply copied and pasted for your use case, it needs to be adapted. 'Twas just a toy project for a NonStopHacking [@Mittelab](https://www.mittelab.org). But it should get you started.

## References

* [Slack chat.postMessage API](https://api.slack.com/methods/chat.postMessage)

* [Slack chat post message tester](https://api.slack.com/methods/chat.postMessage/test)

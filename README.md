# Twitlib

Twitlib is a python library that helps automate the management of a
Twitter account. It was specifically designed to receive and
manipulate tweets from Twitter's streaming API using a thread pool
design pattern.

Some of the current features include:
* Dumping streamed tweets to JSON files
* Downloading media from streamed tweets
* Mirroring of streamed tweets to another account
* Scalability thanks to a thread pool design pattern
* Extensible through user defined thread subclasses

## Documentation

Please see TODO for API documentation. An [example](example/) script
is provided.

## Planned Features

### DM Control

In order to facilitate control of bot accounts without programming
or command line knowledge, modules are provided to allow for bot
control via direct messages. This control system will authenticate DMs
from the bot's owner using the owner's twitter ID. When the bot
receives a direct message from the owner it will parse the message
content and take a predefined action based on message content.

Ideally, the module would follow functional programming practices as
follows

1. The parser is constructed with a list of functions that map tweet
	 text content to either function calls that perform a desired
	 response action (if tweet matches some regex) or a noop/None
	 function (if there is no match).

This system could also be used to provide automated responses to users
who DM the bot, perhaps directing them to the owner's real account.

### Watermarking

Through DM control the bot can perform actions with the full power of
a command line, using DMs as a way to exchange input and output data
over Twitter. One potential use case is the watermarking of images.
Suppose that the bot's host machine has a script that can watermark
an image. The bot owner could DM the bot with an image and some
trigger phrase ('watermark'), at which point the bot would watermark
the image and send the result back to the owner via twitter DM.

### Scheduling

Scheduling of account actions can easily be added.

* Tweets could be pre-written and scheduled for release at a later time.
* An account could be set to private or public on a scheduled
	interval, with additional logic that accounts for when the user last
	tweeted.

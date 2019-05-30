#!python
import os
from absl import app
from absl import flags

FLAGS = flags.FLAGS

flags.DEFINE_bool(
    'auth',
    False,
    'Carry out authentication flow and exit'
)

DEFAULT_ID = os.environ.get('TWITTER_ID', [])
flags.DEFINE_list(
    'follow',
    [],
    'List of screen names to follow'
)

flags.DEFINE_list(
    'track',
    [],
    'List of hashtags to follow'
)

flags.DEFINE_bool(
    'mirror',
    False,
    'Mirror tweets'
)

flags.DEFINE_bool(
    'download',
    False,
    'Download tweets'
)

flags.DEFINE_bool(
    'media',
    False,
    'Download tweet media'
)

flags.DEFINE_bool(
    'dry_run',
    False,
    'Only print actions to be taken'
)

flags.DEFINE_bool(
    'mock_posts',
    False,
    'Patches tweepy API upload functions with logging mocks'
)

flags.DEFINE_string(
    'temp_dir',
    'tmp',
    'Directory to hold temporarily downloaded media'
)

flags.DEFINE_string(
    'dir',
    os.environ.get('TWITLIB_DIR', './'),
    'Directory to downloaded tweets and media to'
)

flags.DEFINE_string(
    'write_format',
    os.environ.get('TWITLIB_WRITE_FMT', 'status_{id}.json'),
    'Filename format for downloaded tweets'
)

flags.DEFINE_string(
    'media_format',
    os.environ.get('TWITLIB_MEDIA_FMT', 'media_{id}'),
    'Directory format for downloaded media'
)

flags.DEFINE_integer(
    'workers',
    os.environ.get('TWITLIB_NUM_WORKERS', 2),
    'Number of worker threads for each type of operation'
)

flags.register_validator(
    'dir',
    lambda v : os.path.isdir(v),
    message='--dir must point to an existing directory'
)

flags.register_validator(
    'temp_dir',
    lambda v : os.path.isdir( os.path.dirname(os.path.abspath(v)) ),
    message='--temp-dir must exist.'
)

flags.register_validator(
    'workers',
    lambda v : v > 0 and v < 10,
    message='--workers must be a positive integer < 10.'
)

flags.register_validator(
    'follow',
    lambda ids : all([int(t) for t in ids]),
    message='--follow must be one or more integer twitter ids.'
)

flags.register_validator(
    'track',
    lambda tags : all([isinstance(t, str) for t in tags]),
    message='--track must be one or more strings'
)

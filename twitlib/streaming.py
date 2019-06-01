"""
Producers and consumers for a thread pool pattern of receiving
objects from Twitter's streaming API and acting on those objects
in some way.
"""
import logging
import requests
import json
import os

from threading import Thread
from queue import Queue
from typing import Callable, List, NoReturn, ClassVar, Union, Type

import twitter
from twitter import Api
from twitter.models import Status, Media, User

import twitlib.util as util

FilterFunc = Callable[[Status], bool]

log = logging.getLogger('twitlib')

class WorkerThread(Thread):
    """
    Abstract worker thread to process jobs from the dispatcher. Derived
    classes must override process_status() and may override default_filter()
    if desired. Inherits from threading.Thread class.
    """

    QUEUE: ClassVar[Queue] = Queue()

    def __init__(self, loops=None, dry_run=False, **kwargs):
        """
        Worker thread base class constructor. Follows the `threading.Thread`
        paradigm of accepting only keyword arguments.

        Keyword Args
        ===
        loops : int > 0 or None
            Maximum iterations of the run() loop. After `loops` items have been
            dequeued, the thread will die. Defaults to no iteration limit.

        filters : function, list(function),
            Maximum iterations of the run() loop. After `loops` items have been
            dequeued, the thread will die. Defaults to no iteration limit.

        **kwargs :
            Forwarded to threading.Thread constructor
        """
        self.loops = loops
        self.dry_run = dry_run
        self.filters = kwargs.pop('filters', [self.default_filter])

        # Default to daemon thread for worker
        daemon = kwargs.pop('daemon', True)
        super().__init__(daemon=daemon, **kwargs)

    @property
    def filters(self) -> List[FilterFunc]: return self._filters

    @filters.setter
    def filters(self, funcs: List[FilterFunc]) -> None: self._filters = funcs

    @property
    def loops(self) -> int: return self._loops

    @loops.setter
    def loops(self, val: Union[int, None]) -> None:
        if val == None or val > 0:
            self._loops = val
        else:
            raise ValueError('loops must be an int > 0')

    @property
    def dry_run(self) -> bool: return self._dry_run

    @dry_run.setter
    def dry_run(self, val: bool) -> None: self._dry_run = val

    def run(self) -> None:
        """
        Looping method that consumes from the class job queue and runs
        process_status() on dequeued objects. Thread can be killed by
        enqueueing None; when None is dequeued by the thread, looping
        will end
        """

        cls = self.__class__.__name__
        log.debug('{cls} started', cls=cls)
        loop_count = 0

        while self.loops == None or loop_count < self.loops:

            # Block waiting for incoming status
            status = self.__class__.dequeue()
            if status is None:
                log.debug('Stopping %s', cls)
                self.__class__.QUEUE.task_done()
                break

            try:
                self.process_status(status)
                log.debug('%s finished job', cls)

            except Exception:
                log.exception('Exception on status: %s', status.__repr__())
                raise

            finally:
                self.__class__.QUEUE.task_done()
                loop_count += 1

    @classmethod
    def dequeue(cls, **kwargs) -> Union[Status, None]:
        """
        Dequeue a job from the class job queue. Will block indefinitely by default.
        Keyword args are forwarded to Queue.get(), can be used to override blocking.

        Return
        ===
            Status or None:
        The next Status object or None instance in queue. Dequeueing None is a signal
        for the WorkerThread to end its run() loop.
        """
        return cls.QUEUE.get(block=True, timeout=None, **kwargs)

    @classmethod
    def enqueue(cls, status: Union[Status, None], **kwargs) -> None:
        """
        Enqueue a job to the class job queue. Will block indefinitely by default.
        Keyword args are forwarded to Queue.get(), can be used to override blocking.

        Args
        ===
            status : twitter.Status or None
        The status to enqueue, or None to kill the dequeueing thread.

        Return: None
        """
        cls.QUEUE.put(status, block=True, timeout=None, **kwargs)

    def process_status(self, status: Status) -> NoReturn:
        """
        Called whenever a job is pulled from the class job queue. Override this in
        subclasses to specify how dequeued items are processed
        """
        # Call to simplify testing TODO remove?
        WorkerThread.validate_status(status, self.filters)
        raise NotImplementedError('Please override WorkerThread.process_status()')

    @staticmethod
    def default_filter(status: Status) -> bool:
        """
        Provides a set of default filters to be used if if no argument is given
        for `filters`. Override this in subclasses as needed
        """
        return True

    @staticmethod
    def validate_status(status: Status, funcs: List[FilterFunc]) -> bool:
        """
        Pass a status through a list of validation functions.
        Return: all( [ f(status) for f in funcs ] )
        """
        failures = [ f for f in funcs if not f(status) ]
        if failures:
            log.debug('Tweet %i failed %i filter criteria: %s',
                status.id,
                len(failures),
                failures
            )
            return False
        else:
            log.debug('Tweet %i passed validation', status.id)
            return True

    @staticmethod
    def format_filename(status: Status, fmt: str, dirname:str = None) -> str:
        """
        Helper method to apply a given format to a status object.
        forwarded to json.dump(). Optionally specify a directory path that
        will be prepended to the generated filename.
        """
        kwargs = status.AsDict()
        name = fmt.format(**kwargs)
        return os.path.join(dirname, name) if dirname else name

class WriterThread(WorkerThread):
    """
    Worker thread for writing content received by a tweepy stream to a file.
    For now, writing is only defined for Status objects. Direct message
    writing may be enabled in the future.
    """

    QUEUE: ClassVar[Queue] = Queue()

    def __init__(self, dirname='', format='status_{id}.json', **kwargs):
        self.dirname = dirname
        self.format = format
        super().__init__(**kwargs)

    @property
    def dirname(self) -> str: return self._dirname

    @dirname.setter
    def dirname(self, val: str) -> None: self._dirname = val

    @property
    def format(self) -> str: return self._format

    @format.setter
    def format(self, val: str) -> None: self._format = val

    def process_status(self, status: Status) -> str:
        """
        Override for WorkerThread.process_status(). Performs the following actions:

            1.  Applies the filter functions in self.filter to the incoming status.
                If any filter returns False, processing will abort.

            2.  Writes the status as a JSON to a file formatted with self.tweet_fmt
                located in the directory given in self.dirname

        Return: Name of written file, or None if error
        """
        if not WorkerThread.validate_status(status, self.filters):
            log.info('Tweet %i failed filter %s filter criteria', status.id, self.__class__.__name__)
            return None

        name = WorkerThread.format_filename(status, self.format, self.dirname)
        if self.dry_run:
            log.info('[DRY RUN] Wrote status %i to %s', status.id, name)
            return None
        else:
            result = self.write_status(status, name)
            log.info('Wrote status %i to %s', status.id, name)
            return result


    @staticmethod
    def write_status(status: Status, filename: str) -> str:
        """
        Write a status as a JSON object to a given file. Keyword args are
        forwarded to json.dump()
        """
        with open(filename, 'w', encoding='utf-32') as f:
            json.dump(status.AsDict(), f, indent=2, sort_keys=True)

        log.debug('Wrote status to %s', filename)
        return filename

    @staticmethod
    def default_filter(status: Status) -> bool:
        """
        Provides general filtering of a tweets to determine which should
        be saved.

        Criteria is as follows:
            1. Ignores statuses that are retweets

        Returns true if all criteria are met, false otherwise
        """
        return not status.retweeted_status


class MirrorThread(WorkerThread):
    """
    Worker thread for mirroring tweets received by a tweepy stream.
    Mirroring is only defined for Status objects (tweepy tweets).
    """

    QUEUE: ClassVar[Queue] = Queue()

    def __init__(self, **kwargs):

        default_args = {
                'api': Api(),
                'temp_dir': '',
        }
        for attr, default in default_args.items():
            val = kwargs.pop(attr, default)
            setattr(self, attr, val)

        super().__init__(**kwargs)

    @property
    def temp_dir(self) -> str: return self._temp_dir

    @temp_dir.setter
    def temp_dir(self, val: str) -> None: self._temp_dir = val

    @property
    def api(self) -> str: return self._api

    @api.setter
    def api(self, val: Api) -> None: self._api = val

    def process_status(self, status: Status) -> Status:
        """
        Override for WorkerThread.process_status(). Performs the following actions:

            1.  Applies the filter functions in self.filter to the incoming status.
                If any filter returns False, processing will abort.

            2.  Writes the status as a JSON to a file formatted with self.tweet_fmt
                located in the directory given in self.dirname

        Returns the newly tweeted Status, or None if validation failed or dry_run=True
        """
        if not WorkerThread.validate_status(status, self.filters):
            log.info('Tweet %i failed filter %s filter criteria', status.id, self.__class__.__name__)
            return None

        if self.dry_run:
            log.info('[DRY RUN] Mirroring tweet %i', status.id)
            return None
        else:
            log.info('Mirroring tweet %i', status.id)
            return MirrorThread.mirror(self.api, status, self.temp_dir)

    @staticmethod
    def mirror(api: Api, status: Status, temp_dir: str = '') -> Status:
        """Mirror a status. Returns a Status object with the newly posted tweet"""
        text = status.full_text if status.full_text else status.text
        text = util.remove_urls(text)
        media = MediaDownloaderThread.download_media(status, temp_dir)
        return api.PostUpdate(status=text, media=media)

    @staticmethod
    def default_filter(status: Status):
        """
        Provides general validation of a tweet to determine if it is a
        dandidate for mirroring.

        Criteria is as follows:
            1. Not tweeted in reply to or mentioning another user
            2. User ID of tweet poster matches user ID of this API

        Returns true if all criteria are met, false otherwise
        """
        failures = [
            status.in_reply_to_status_id,
            status.user_mentions,
            status.retweeted
        ]
        return False if any(failures) else True

class MediaDownloaderThread(WorkerThread):
    """
    Worker thread for writing content received by a tweepy stream to a file.
    For now, writing is only defined for Status objects. Direct message
    writing may be enabled in the future.
    """

    QUEUE: ClassVar[Queue] = Queue()

    def __init__(self, dirname='', format='media_{id}.json', **kwargs):
        self.dirname=dirname
        self.format=format
        super().__init__(**kwargs)

    @property
    def dirname(self) -> str: return self._dirname

    @dirname.setter
    def dirname(self, val: str) -> None: self._dirname = val

    @property
    def format(self) -> str: return self._format

    @format.setter
    def format(self, val: str) -> None: self._format = val

    def process_status(self, status: Status):
        """
        Override for WorkerThread.process_status(). Performs the following actions:

            1.  Applies the filter functions in self.filter to the incoming status.
                If any filter returns False, processing will abort.

            2.  Writes the status as a JSON to a file formatted with self.tweet_fmt
                located in the directory given in self.dirname

        """
        if not WorkerThread.validate_status(status, self.filters):
            log.info('Tweet %i failed filter %s filter criteria', status.id, self.__class__.__name__)
            return []

        media_list = status.media
        url_list = util.list_media(status)
        status_dir = WorkerThread.format_filename(status, self.format, self.dirname)

        if not self.dry_run:
            log.info('Downloading media urls:%s', url_list)
            out_files = MediaDownloaderThread.download_media(status, status_dir)
            log.info('Downloaded media to files: %s', out_files)
            return out_files
        else:
            out_files = [
                    MediaDownloaderThread.url_to_file(url, self.dirname)
                    for url in url_list
            ]
            log.info('[DRY RUN] downloading media urls:%s', url_list)
            return None


    @staticmethod
    def download_media(status: Status, dirname: str):
        """
        Download media from a Status into a given directory. Returns a list of
        filepaths that were downloaded.
        """
        # Check if status has media
        media_list = status.media
        if not media_list:
            log.debug('Status %i had no media, skipping download', status.id)
            return []

        # Create subdirectory for downloads
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        # Download each media element into subdirectory
        result = []
        for i, media in enumerate(media_list):
            log.debug('Downloading media item %i', i+1)
            url = media.media_url_https

            # TODO validate response code
            r = requests.get(url)
            log.debug('Request got URL %s', url)

            filepath = MediaDownloaderThread.url_to_file(url, dirname)
            with open(filepath, 'wb') as f:
                f.write(r.content)
            log.debug('Wrote %s', filepath)

            result.append(filepath)

        return result

    @staticmethod
    def url_to_file(url: str, dirname: str ='') -> str:
        """
        Helper method to generate a filename from an image URL.

        Args
        ===
            url: str
        The image URL. Must be of the form "host/file.ext".

            dirname: str
        A directory path to prepend to the output filename.
        Defaults to ''.

        Return: str
        ===
        Filename part of the given URL, relative to a given
        directory path if specified.

        Examples
        ---
        Input: url='host/file.ext', dirname='dir'
        Output: 'dir/file.ext'
        """
        filename = os.path.basename(url)
        return os.path.join(dirname, filename)

    @staticmethod
    def default_filter(status: Status):
        """
        Provides general filtering of a tweets to determine which should
        be saved.

        Criteria is as follows:
            1. Right now, mimick WriterThread

        Returns true if all criteria are met, false otherwise
        """
        return WriterThread.default_filter(status)

class BaseListener():
    """
    Abstract listener with logging functions. Designed to be
    compatible with tweepy StreamListener objects.
    """

    def on_connect(self, *args, **kwargs):
        log.info('Listener connected')

    def on_status(self, status: Status) -> None:
        log.info('Got status: %s', status.__repr__())

    def on_direct_message(self, status) -> None:
        log.info('Got direct message')

    def on_limit(self, status: Status) -> None:
        log.warning('Got limit message')

    def on_timeout(self, status: Status) -> None:
        log.warning('Stream timeout')

    def on_error(self, status_code: int) -> Union[bool, None]:
        log.error('Got error code %i', status_code)
        if status_code == 429:
            return False
        return None

class Dispatcher(BaseListener):
    """
    Listener that dispatches threads on action. Inherits logging
    calls and on_error handling from BaseListener.
    """

    def __init__(self, threads: List[WorkerThread] = []):
        """
        When a status is received and pushed to on_status(), the
        dispatcher will call thread.enqueue(status) for each
        thread class given in the `threads` arg.
        """
        self._threads = threads
        super().__init__()

    @property
    def threads(self) -> List[WorkerThread]: return self._threads

    @threads.setter
    def threads(self, val: List[WorkerThread]): self._threads = val

    def on_status(self, status: Type[Status]) -> None:
        """Adds status to queue of listening WorkerThreads"""
        super().on_status(status)

        for thread_cls in self.threads:
            thread_cls.enqueue(status)

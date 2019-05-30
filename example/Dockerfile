FROM twitlib

ADD flags.py /
ADD main.py /
ADD get_access_token.py /

RUN mkdir -p /mnt /mnt/log

ENTRYPOINT [ "python", "./main.py", "--dir=/mnt" ]
CMD [ "--mirror", "--log_dir=/mnt/log", "--alsologtostderr"]

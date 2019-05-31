FROM tidalpaladin/twitlib:stable

ADD flags.py /
ADD main.py /
ADD get_access_token.py /

RUN mkdir -p /mnt /mnt/log
RUN pip install ipython absl-py

ENTRYPOINT [ "python", "./main.py", "--dir=/mnt" ]
CMD [ "--mirror", "--log_dir=/mnt/log", "--alsologtostderr"]

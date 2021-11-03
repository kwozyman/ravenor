FROM alpine
RUN apk add python3
RUN python3 -m ensurepip
RUN python3 -m pip install praw pyyaml
ADD ravenor.py /ravenor/ravenor
ADD db/* /ravenor/db/
WORKDIR /ravenor
CMD python3 /ravenor/ravenor --config-file /ravenor/db/config.yml

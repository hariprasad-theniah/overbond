FROM python:3
WORKDIR submission
ADD overbond.py /
ENTRYPOINT [ "python", "./overbond.py"]

# This is my test


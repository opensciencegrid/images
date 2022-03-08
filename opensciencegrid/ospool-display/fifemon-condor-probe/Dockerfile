FROM python:2.7

WORKDIR /fifemon
COPY . .
RUN python setup.py install

CMD [ "fifemon", "/fifemon/fifemon.cfg" ]
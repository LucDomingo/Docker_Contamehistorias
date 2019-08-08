FROM library/python:3.7.1-alpine

RUN apk update && apk upgrade && \
    apk add --no-cache bash git openssh && \
    apk add build-base

RUN pip install --upgrade pip
RUN pip install flask
RUN pip install flasgger


RUN apk --update add --virtual scipy-runtime python py-pip \
    && apk add --virtual scipy-build \
        build-base python-dev openblas-dev freetype-dev pkgconfig gfortran \
    && ln -s /usr/include/locale.h /usr/include/xlocale.h \
    && pip install --no-cache-dir numpy \ 
    && pip install --no-cache-dir matplotlib \
    && pip install --no-cache-dir scipy \
    && apk del scipy-build \
    && apk add --virtual scipy-runtime \
        freetype libgfortran libgcc libpng  libstdc++ musl openblas tcl tk \
    && rm -rf /var/cache/apk/*


ENV PYTHON_PACKAGES="\
    pandas \
    nltk \
    jellyfish \
    networkx \
    segtok \
    elasticsearch \
    recordclass \
    requests \
    Click>=6.0 \
    click_datetime==0.2 \
    stop-words \
    mediacloud \
    werkzeug \
" 

RUN pip install --no-cache-dir $PYTHON_PACKAGES 
RUN pip install git+https://github.com/LIAAD/TemporalSummarizationFramework
RUN pip install gunicorn

ADD ./webapp /opt/webapp/
WORKDIR /opt/webapp

EXPOSE 80
CMD gunicorn --bind 0.0.0.0:80 wsgi 

FROM alpine:3.7

RUN apk update \
&& apk upgrade \
&& apk add --no-cache bash \
&& apk add --no-cache --virtual=build-dependencies unzip \
&& apk add --no-cache curl \
&& apk add --no-cache openjdk8-jre

RUN apk add --no-cache python3 \
&& python3 -m ensurepip \
&& pip3 install --upgrade pip setuptools \
&& rm -r /usr/lib/python*/ensurepip && \
if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
rm -r /root/.cache

ADD requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir -p /etc/spark/

ADD log4j.properties /etc/spark/

ENV SPARK_CONF_DIR=/etc/spark/

ENV JAVA_HOME="/usr/lib/jvm/java-1.8-openjdk"

RUN mkdir /joboutput

EXPOSE 4040

ENTRYPOINT ["/usr/bin/spark-submit"] 
CMD ["--help"]

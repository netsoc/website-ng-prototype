FROM python:3-alpine

COPY requirements.txt /opt/
RUN pip install -r /opt/requirements.txt && \
	mkdir /opt/app

COPY app.sh /opt/

USER nobody:nogroup
ENV GUNICORN_WORKERS=4
EXPOSE 8080/tcp
HEALTHCHECK --start-period=1s --interval=10s --retries=3 \
	CMD curl -f http://localhost:8080 -H "Host: $PUBLIC_HOST" || exit 1
CMD [ "/opt/app.sh" ]
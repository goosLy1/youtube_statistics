FROM python
WORKDIR /opt
VOLUME [ "C:\Program Files\fastapi_yt:/opt" ]
RUN pip install -r requirements.txt
EXPOSE 8000
# CMD while true; do sleep 10;done
CMD uvicorn main:app --host 0.0.0.0
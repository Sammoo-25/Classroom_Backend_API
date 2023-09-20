FROM python:3.10-alpine3.14

WORKDIR /app

COPY requirements.txt .

RUN apk add --no-cache gcc musl-dev linux-headers
RUN apk add --no-cache sqlite
RUN apk add --no-cache gcc musl-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY . .

ENV FLASK_APP=app.py
ENV FLASK_ENV=development
RUN chmod +x start.sh
#RUN source start.sh
EXPOSE 5000
CMD ["sh", "start.sh"]
#CMD ["flask", "run"]

FROM python:3.7-slim-buster

ADD . /app
WORKDIR /app
COPY requirements.txt /
RUN pip3 install -r requirements.txt

# STEP 5: Declare environment variables
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# STEP 6: Expose the port that Flask is running on
EXPOSE 5000

# STEP 7: Run Flask!
CMD ["flask", "run", "--host=0.0.0.0"]
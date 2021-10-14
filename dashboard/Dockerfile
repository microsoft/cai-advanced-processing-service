FROM python:3.7-slim
COPY . /app
WORKDIR /app
RUN apt-get update
RUN apt-get install -y libssl1.1 libasound2
RUN pip install -r requirements.txt
EXPOSE 80
RUN mkdir ~/.streamlit
RUN cp config.toml ~/.streamlit/config.toml
WORKDIR /app
ENTRYPOINT ["streamlit", "run"]
CMD ["main.py"]
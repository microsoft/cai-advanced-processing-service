import os
from azure.storage.blob import ContainerClient
from azure.cosmosdb.table import TableService, Entity
import pandas as pd
import streamlit as st

@st.cache
def get_audio_stream(connection_data, language, audio_file):
    container_client = ContainerClient.from_connection_string(connection_data['connection_string'], container_name=connection_data['container'])
    audio = container_client.download_blob(f'{language}_{audio_file}.wav').readall()
    return audio

@st.cache
def get_audio_files(connection_data):
    container_client = ContainerClient.from_connection_string(connection_data['connection_string'], container_name=connection_data['container'])
    blob_list = container_client.list_blobs()
    file_iterator = blob_list
    file_dict = dict()
    for index, value in enumerate(file_iterator):
        _name = value.name
        try:
            lang = _name.split("_")[0]
            file = _name.split("_")[1].replace('.wav', '')
            if lang not in file_dict.keys():
                file_dict[lang] = [file]
            else:
                file_dict[lang].append(file)
        except Exception as e:
            logging.warning(f'{e}')
    return file_dict

def get_data_from_table(connection_data):
    table_service = TableService(connection_string = connection_data['connection_string'])
    tasks = table_service.query_entities(connection_data['table_name'])
    return tasks

def push_data_to_table(connection_data, data):
    # Insert a new entity
    table_service = TableService(connection_string=connection_data['connection_string'])
    table_service.insert_or_replace_entity(connection_data['table_name'], data)

def main():
    file_dict = get_audio_files()
    tasks = get_data_from_table()
    return file_dict, tasks

if __name__ == "__main__":
    file_dict, tasks = main()
    print(file_dict)
    for _ in tasks:
        print(_)
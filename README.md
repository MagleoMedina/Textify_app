# Textify
# Proyecto de Grabación y Transcripción de Audio

Este proyecto permite grabar audio, transcribirlo y guardar la transcripción junto con metadatos en una base de datos.

## Requisitos

Para ejecutar este proyecto, necesitas tener instaladas las siguientes librerías:

- `customtkinter`
- `pyaudio`
- `speech_recognition`
- `numpy`
- `tkcalendar`
- `tkinter`
- `sqlite3`
- `re`
- `wave`
- `audiofile`


## Instalación

Puedes instalar las librerías necesarias utilizando `pip`. A continuación se muestra cómo instalar cada una de ellas:

```sh
pip install -r requeriments.txt
```
# Diagrama de la base de datos
![image](https://github.com/user-attachments/assets/c7e250f1-57b5-47fa-923d-e50be3f0c54b)

## Archivo ejecutable (Utiliza pyinstaller)
pyinstaller --windowed --onefile --add-data "logoAudio.ico;." --add-data "logoAudio.png;." --icon=logoAudio.ico --add-data "database_tendencias.db;." --name "Textify" main.py

import customtkinter as ctk
import os
import threading
import speech_recognition as sr
import tkinter.messagebox as messagebox
from tkcalendar import DateEntry  
from tkinter import ttk, filedialog  
import db_manager 
import time
import audiofile as af
from modulo_1 import AudioRecorderApp  # Importar la clase del módulo 1

class AudioFileRecorderApp(ctk.CTkFrame):  # Cambiar la herencia a CTkFrame
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        #self.geometry("1280x720")  
        #self.resizable(False, False)

        # Variables
        self.filename = "transcription.txt"
        self.processing = False
        
        #Base de datos
        self.db_manager = db_manager.DBManager("database_tendencias.db")

        # Registra una función de validación para el ingreso de cédulas
        self.cedula_validation = self.register(self.validate_cedula)

        # Crear la interfaz
        self.main_frame = ctk.CTkFrame(self, corner_radius=10)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)

        # Seccion 1: botones de control
        self.controls_frame = ctk.CTkFrame(self.main_frame)
        self.controls_frame.grid(row=0, column=0, columnspan=2, pady=10)

        self.load_button = ctk.CTkButton(self.controls_frame, text="Cargar Archivo de Audio", command=self.load_audio_file)
        self.load_button.grid(row=0, column=0, padx=10, pady=10)

        self.save_button = ctk.CTkButton(self.controls_frame, text="Guardar Transcripcion", command=self.save_transcription, state="disabled")
        self.save_button.grid(row=0, column=2, padx=10, pady=10)

        # Seccion 2: Status de las etiquetas
        self.status_frame = ctk.CTkFrame(self.main_frame)
        self.status_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="", font=("Arial", 16))
        self.status_label.grid(row=0, column=0, pady=10)

        # Secccion 3: Area de texto de la transcripción
        self.text_area = ctk.CTkTextbox(self.main_frame, width=600, height=150)
        self.text_area.grid(row=2, column=0, columnspan=2, pady=10)

        # Seccion 4: Metadata (Tema, Título, Fecha, Número de Autores)
        self.metadata_frame = ctk.CTkFrame(self.main_frame)
        self.metadata_frame.grid(row=3, column=0, columnspan=2, pady=10)

        # Tema
        self.tema_label = ctk.CTkLabel(self.metadata_frame, text="Tema:")
        self.tema_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.tema_combobox = ctk.CTkComboBox(self.metadata_frame, state="readonly")
        self.tema_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        self.populate_tema_combobox()

        # Título
        self.titulo_label = ctk.CTkLabel(self.metadata_frame, text="Título:")
        self.titulo_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.titulo_entry = ctk.CTkEntry(self.metadata_frame, width=250)
        self.titulo_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.titulo_entry.bind("<KeyRelease>", self.check_titulo)

        # Fecha
        self.fecha_label = ctk.CTkLabel(self.metadata_frame, text="Fecha:")
        self.fecha_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.fecha_entry = DateEntry(self.metadata_frame, width=18, background="darkblue",
                                     foreground="white", borderwidth=2, date_pattern="dd-mm-y")
        self.fecha_entry.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        # ¿Nuevo Usuario?
        self.nuevo_usuario_label = ctk.CTkLabel(self.metadata_frame, text="Nuevo Usuario?")
        self.nuevo_usuario_label.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.nuevo_usuario_var = ctk.StringVar(value="")  # Initially no selection
        self.nuevo_usuario_si = ctk.CTkRadioButton(self.metadata_frame, text="Si", variable=self.nuevo_usuario_var, value="si", command=self.toggle_autores_fields)
        self.nuevo_usuario_si.grid(row=3, column=1, padx=10, pady=5, sticky="w")
        self.nuevo_usuario_no = ctk.CTkRadioButton(self.metadata_frame, text="No", variable=self.nuevo_usuario_var, value="no", command=self.toggle_autores_fields)
        self.nuevo_usuario_no.grid(row=3, column=2, padx=10, pady=5, sticky="w")

        # Crear un estilo personalizado para el Combobox
        style = ttk.Style()
        style.theme_use('default')
        style.configure("TCombobox",
                        fieldbackground="lightgray",  # Fondo del campo de entrada
                        background="white",           # Fondo del desplegable
                        foreground="blue",            # Color del texto
                        borderwidth=2,                # Ancho del borde
                        relief="solid",               # Estilo del borde
                        font=("Helvetica", 12))       # Fuente y tamaño del texto
        # Número de Autores
        self.num_autores_label = ctk.CTkLabel(self.metadata_frame, text="Número de Autor/Autores:")
        self.num_autores_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.num_autores_combobox = ttk.Combobox(self.metadata_frame, values=list(range(1, 11)), state="readonly", style="TCombobox")
        self.num_autores_combobox.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        self.num_autores_combobox.bind("<<ComboboxSelected>>", self.update_autores_fields)

        # Número de Autores para "No" 
        self.num_autores_label_no = ctk.CTkLabel(self.metadata_frame, text="Número de Autor/Autores:")
        self.num_autores_combobox_no = ttk.Combobox(self.metadata_frame, values=list(range(1, 11)), state="readonly")
        self.num_autores_combobox_no.bind("<<ComboboxSelected>>", self.update_cedula_fields)

        # Cédula Entry para "No"
        self.cedula_entries_no = []

        # Seccion 5: Autores campos dinamicos
        self.autores_frame = ctk.CTkFrame(self.main_frame)
        self.autores_frame.grid(row=4, column=0, columnspan=2, pady=10)

        # Cédula Entry para "No" 
        self.cedula_label_no = ctk.CTkLabel(self.metadata_frame, text="Ingrese Cédula:")
        self.cedula_entry_no = ctk.CTkEntry(self.metadata_frame, width=250, validate="key", validatecommand=(self.cedula_validation, '%P'))
        self.buscar_button_no = ctk.CTkButton(self.metadata_frame, text="buscar", command=self.buscar_cedula)
        self.nombre_entry_no = ctk.CTkEntry(self.metadata_frame, width=250, state="readonly")
        self.apellido_entry_no = ctk.CTkEntry(self.metadata_frame, width=250, state="readonly")
        self.nombre_entry_no.grid_remove()
        self.apellido_entry_no.grid_remove()

        # Initially hide the authors section and cédula entry
        self.toggle_autores_fields()

    def check_titulo(self, event):
        titulo = self.titulo_entry.get()
        if self.db_manager.titulo_existe(titulo):
            self.status_label.configure(text="Título ocupado. Por favor, elija otro título.", text_color="red")
        else:
            self.status_label.configure(text="", text_color="black")  # Set a valid color name

    def load_audio_file(self):
        self.clear_inputs()
        self.status_label.configure(text="")
        # Abrir un cuadro de diálogo para seleccionar el archivo
        self.filepath = filedialog.askopenfilename(filetypes=[("Archivos de audio", "*.wav *.mp3 *.flac *.ogg")])
        
        if self.filepath:
            # Verificar si el archivo no es un WAV y convertirlo
            if not self.filepath.lower().endswith('.wav'):
                # Crear la ruta para el archivo WAV
                wav_filepath = self.filepath.rsplit('.', 1)[0] + '.wav'
                # Lee el archivo de entrada
                data, samplerate = af.read(self.filepath)
                # Escribe el archivo en formato WAV
                af.write(wav_filepath, data, samplerate)
                self.filepath = wav_filepath  # Actualizamos la ruta del archivo a la versión WAV
            
            # Mostrar mensaje de éxito
            messagebox.showinfo("Archivo Cargado", f"Archivo cargado: {os.path.basename(self.filepath)}")
            # transcripción
            self.start_transcription_thread()

    def update_progress_bar(self, duration):
        #Actualizar barra de progreso en el hilo principal
        steps = 20
        for i in range(steps):
            if not self.processing:
                break  # Si se detiene el procesamiento, salir
            percentage = ((i + 1) / steps) * 100
            self.status_label.configure(text=f"Procesando grabación... {percentage:.0f}%", text_color="orange")
            self.update_idletasks()
            time.sleep(duration / steps)

    def transcribe_audio(self):
        #Procesar el audio en un hilo separado
        self.processing = True
        recognizer = sr.Recognizer()

        try:
            with sr.AudioFile(self.filepath) as source:
                audio_data = recognizer.record(source)
                duration = source.DURATION

                # Inicia la barra de progreso
                threading.Thread(target=self.update_progress_bar, args=(duration,), daemon=True).start()

                # Procesar la transcripción
                self.transcription = recognizer.recognize_google(audio_data, language="es-ES")
                self.text_area.insert("0.0", self.transcription)
                self.status_label.configure(text="Grabación transcrita exitosamente", text_color="green")
                self.save_button.configure(state="normal")
        except Exception as e:
            self.text_area.insert("0.0", f"No se pudo transcribir el audio: {e}")
            self.status_label.configure(text="Transcripción fallida", text_color="red")
        finally:
            self.processing = False  # Indicar que el procesamiento ha finalizado

    def start_transcription_thread(self):
        #Iniciar hilo de procesamiento
        if not self.filepath:
            messagebox.showerror("Error", "Primero debe cargar un archivo de audio.")
            return

        if self.processing:
            messagebox.showwarning("Aviso", "Ya se está procesando un archivo.")
            return

        threading.Thread(target=self.transcribe_audio, daemon=True).start()

    
    def clear_inputs(self):
        AudioRecorderApp.clear_inputs(self)

    def save_transcription(self):
        AudioRecorderApp.save_transcription(self)

    def update_autores_fields(self, event):
        AudioRecorderApp.update_autores_fields(self, event)

    def toggle_autores_fields(self):
        AudioRecorderApp.toggle_autores_fields(self)

    def update_cedula_fields(self, event):
        AudioRecorderApp.update_cedula_fields(self, event)

    def buscar_cedula(self):
        AudioRecorderApp.buscar_cedula(self)

    def populate_tema_combobox(self):
       AudioRecorderApp.populate_tema_combobox(self)

    def validate_cedula(self, value_if_allowed):
        if value_if_allowed.isdigit() or value_if_allowed == "":
            return True
        else:
            return False
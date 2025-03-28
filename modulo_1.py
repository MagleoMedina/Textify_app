import customtkinter as ctk
import threading
import os
import wave
import pyaudio
import speech_recognition as sr
import numpy as np
import tkinter.messagebox as messagebox
from tkcalendar import DateEntry  
from tkinter import ttk  
import db_manager 
import time


class AudioRecorderApp(ctk.CTkFrame):  # Cambiar la herencia a CTkFrame
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)
        #self.geometry("1280x720")  
        #self.resizable(False, False)

        # Variables
        self.is_recording = False
        self.audio_frames = []
        self.filename = "transcription.txt"
        self.audio_thread = None
        self.no_audio_detected = False
        self.processing = False

        #Base de datos
        database_path = db_manager.DBManager.get_database_path()
        self.db_manager = db_manager.DBManager(database_path)

        # Registra una función de validación para el ingreso de cédulas
        self.cedula_validation = self.register(self.validate_cedula)

        # Crear la interfaz
        self.main_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#1E3A5F")
        self.main_frame.pack(padx=0, pady=0, fill="both", expand=True)

        # Seccion 1: botones de control
        self.controls_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E3A5F" )
        self.controls_frame.grid(row=0, column=0, columnspan=3, pady=10)

        # Modificación de los botones
        self.start_button = ctk.CTkButton(self.controls_frame, text="Empezar Grabación", command=self.start_recording, fg_color="#4CAF50", text_color="white")  # Cambia el color a un verde que combine
        self.start_button.grid(row=0, column=0, padx=10, pady=10)

        self.stop_button = ctk.CTkButton(self.controls_frame, text="Detener Grabación", command=self.stop_recording, state="disabled", fg_color="#F44336", text_color="white")  # Rojo para detener
        self.stop_button.grid(row=0, column=1, padx=10, pady=10)

        self.save_button = ctk.CTkButton(self.controls_frame, text="Guardar Transcripción", command=self.save_transcription, state="disabled", fg_color="#2196F3", text_color="white")  # Azul para guardar
        self.save_button.grid(row=0, column=2, padx=10, pady=10)


        # Seccion 2: Status de las etiquetas
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E3A5F")
        self.status_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        self.status_label = ctk.CTkLabel(self.status_frame, text="", font=("Arial", 16))
        self.status_label.grid(row=0, column=0, pady=10)

        # Secccion 3: Area de texto de la transcripción
        placeholder_text = "Esperando Archivo para editar..."
        
        self.text_area = ctk.CTkTextbox(self.main_frame, border_width=2, width=455, height=70, fg_color="#1E3A5F", border_color="white")  # Cambiar el tamaño
        self.text_area.grid(row=2, column=0, columnspan=2, padx=20, pady=20)  # Cambiar la posición y los márgenes

        self.text_area.insert("1.0", placeholder_text)
        self.text_area.bind("<FocusIn>", lambda event: self.text_area.delete("1.0", "end") if self.text_area.get("1.0", "end-1c") == placeholder_text else None)
        self.text_area.bind("<FocusOut>", lambda event: self.text_area.insert("1.0", placeholder_text) if not self.text_area.get("1.0", "end-1c") else None)


        # Seccion 4: Metadata (Tema, Título, Fecha, Número de Autores)
        self.metadata_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E3A5F")
        self.metadata_frame.grid(row=3, column=0, columnspan=2, pady=10)

        # Tema
        self.tema_label = ctk.CTkLabel(self.metadata_frame, text="Tema:")
        self.tema_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
       
        self.tema_combobox = ttk.Combobox(self.metadata_frame, state="readonly")
        self.tema_combobox.grid(row=0, column=1, padx=10, pady=5, sticky="w")
        style = ttk.Style()
        style.theme_use("clam")

        # Configurar el estilo del FECHA ESTO ES GLOBAL
        style.configure("TCombobox",
                        background="#1f6aa5",  # Color de fondo de la flechita
                        fieldbackground="#1E3A5F",  # Color de fondo del campo de texto
                        foreground="white",  # Color del texto
                        bordercolor="white",  # Color del borde
                        lightcolor="#1E3A5F",  # Color claro del borde
                        darkcolor="#1E3A5F",  # Color oscuro del borde
                        arrowcolor="white")  # Color de la flecha del combobox
        # SELECCION TEMA ESTO ES GLOBAL
        style.map("TCombobox",
                  fieldbackground=[("readonly", "#1E3A5F")],
                  background=[("readonly", "#1f6aa5")], #color de la flechida de fondo
                  foreground=[("readonly", "white")],
                  selectforeground=[("readonly", "white")],
                  bordercolor=[("readonly", "white")],
                  lightcolor=[("readonly", "#1E3A5F")],
                  darkcolor=[("readonly", "#1E3A5F")],
                  arrowcolor=[("readonly", "white")]) #color de la flechita

        # Aplicar el estilo al Combobox
        self.tema_combobox.configure(style="TCombobox")
        self.populate_tema_combobox()

        # Título
        self.titulo_label = ctk.CTkLabel(self.metadata_frame, text="Título:")
        self.titulo_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.titulo_entry = ctk.CTkEntry(self.metadata_frame, width=250, corner_radius=0, border_color="white", fg_color="#1E3A5F" )
        self.titulo_entry.grid(row=1, column=1, padx=10, pady=5, sticky="w")
        self.titulo_entry.bind("<KeyRelease>", self.check_titulo)

        # Fecha
        self.fecha_label = ctk.CTkLabel(self.metadata_frame, text="Fecha:")
        self.fecha_label.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.fecha_entry = DateEntry(self.metadata_frame, width=18, background="#1f6aa5",
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

        # Número de Autores
        self.num_autores_label = ctk.CTkLabel(self.metadata_frame, text="Número de Autor/Autores:")
        self.num_autores_label.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        self.num_autores_combobox = ttk.Combobox(self.metadata_frame, values=list(range(1, 6)), state="readonly")
        self.num_autores_combobox.grid(row=4, column=1, padx=10, pady=5, sticky="w")
        self.num_autores_combobox.bind("<<ComboboxSelected>>", self.update_autores_fields)

        # Número de Autores para "No" 
        self.num_autores_label_no = ctk.CTkLabel(self.metadata_frame, text="Número de Autor/Autores:")
        self.num_autores_combobox_no = ttk.Combobox(self.metadata_frame, values=list(range(1, 6)), state="readonly")
        self.num_autores_combobox_no.bind("<<ComboboxSelected>>", self.update_cedula_fields)

        # Cédula Entry para "No"
        self.cedula_entries_no = []

        # Seccion 5: Autores campos dinamicos
        self.autores_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E3A5F")  #aqui se debe hacer responsive 
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

        self.check_microphone()
        
    def check_titulo(self, event):
        titulo = self.titulo_entry.get()
        if self.db_manager.titulo_existe(titulo):
            self.status_label.configure(text="Título ocupado. Por favor, elija otro título.", text_color="red")
        else:
            self.status_label.configure(text="", text_color="black")  # Set a valid color name

    def check_microphone(self):
        p = pyaudio.PyAudio()
        if p.get_device_count() == 0:
            self.status_label.configure(text="No se detecta un micrófono. Conecte un micrófono para grabar.", text_color="red")
            self.start_button.configure(state="disabled")
        p.terminate()

    def start_recording(self):
        self.clear_inputs()  # Clear all input fields
        self.is_recording = True
        self.audio_frames = []
        self.start_button.configure(state="disabled")
        self.stop_button.configure(state="normal")
        self.status_label.configure(text="Grabando...", text_color="red")
        self.audio_thread = threading.Thread(target=self.record_audio)
        self.audio_thread.start()

    def clear_inputs(self):
        self.tema_combobox.set("")
        self.titulo_entry.delete(0, "end")
        #self.fecha_entry.set_date("")
        self.nuevo_usuario_var.set("")
        self.num_autores_combobox.set("")
        self.num_autores_combobox_no.set("")
        self.text_area.delete("1.0", "end")
        self.toggle_autores_fields()

    def stop_recording(self):
        self.is_recording = False
        self.start_button.configure(state="normal")
        self.stop_button.configure(state="disabled")
        self.status_label.configure(text="Procesando grabación...", text_color="lightblue")

        # Procesar en un hilo separado para evitar congelar la UI
        threading.Thread(target=self.process_recording).start()

    def process_recording(self):
        self.audio_thread.join()  # Asegurarse de que la grabación ha terminado
        self.transcribe_audio()

        # Indicar que el proceso ha finalizado
        #self.status_label.configure(text="Grabación transcrita exitosamente", text_color="green")

    def record_audio(self):
        chunk = 1024
        format = pyaudio.paInt16
        channels = 1
        rate = 44100
        silence_threshold = 50  # Umbral para detectar silencio

        p = pyaudio.PyAudio()
        stream = p.open(format=format, channels=channels, rate=rate, input=True, frames_per_buffer=chunk)

        while self.is_recording:
            data = stream.read(chunk)
            self.audio_frames.append(data)

            # Convierte datos de audio en una matriz numpy para su análisis
            audio_data = np.frombuffer(data, dtype=np.int16)
            amplitude = np.max(np.abs(audio_data))

            # Detecta si el audio está presente o no
            if amplitude < silence_threshold:
                if not self.no_audio_detected:
                    self.status_label.configure(text="No se detecta audio...", text_color="orange")
                    self.no_audio_detected = True
            else:
                if self.no_audio_detected:
                    self.status_label.configure(text="Grabando...", text_color="red")
                    self.no_audio_detected = False
        stream.stop_stream()
        stream.close()
        p.terminate()

        # Guardar el audio en un archivo WAV
        wf = wave.open("Audio.wav", 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(p.get_sample_size(format))
        wf.setframerate(rate)
        wf.writeframes(b''.join(self.audio_frames))
        wf.close()

    def update_progress_bar(self, duration):
       from modulo_2 import AudioFileRecorderApp
       AudioFileRecorderApp.update_progress_bar(self, duration)

    def transcribe_audio(self):
        self.processing = True
        recognizer = sr.Recognizer()
        with sr.AudioFile("Audio.wav") as source:
            audio_data = recognizer.record(source)
            duration = source.DURATION
            start_time = time.time()  # Start time for processing
            try:

                # Inicia la barra de progreso
                threading.Thread(target=self.update_progress_bar, args=(duration,), daemon=True).start()

                transcription = recognizer.recognize_google(audio_data, language="es-ES")
                self.text_area.insert("0.0", transcription)
                self.save_button.configure(state="normal")
                self.status_label.configure(text="Grabación transcrita exitosamente", text_color="green")
            except sr.UnknownValueError:
                self.text_area.insert("0.0", "No se pudo transcribir el audio.")
                self.status_label.configure(text="Ocurrió un error en la transcripción", text_color="lightcoral")
            except sr.RequestError as e:
                self.text_area.insert("0.0", f"Error con el servicio de transcripción: {e}")
                self.status_label.configure(text="Ocurrió un error en la transcripción", text_color="lightcoral")
            finally:
                elapsed_time = time.time() - start_time  # Calculate elapsed time
                print(f"Tiempo de procesamiento: {elapsed_time:.2f} segundos")  # Print elapsed time
                self.processing = False

    def save_transcription(self):
        # Validar que los campos no estén vacíos
        if not self.tema_combobox.get():
            messagebox.showerror("Error", "El campo 'Tema' no puede estar vacío.")
            return
        if not self.titulo_entry.get():
            messagebox.showerror("Error", "El campo 'Título' no puede estar vacío.")
            return
        if not self.text_area.get("1.0", "end-1c").strip():
            messagebox.showerror("Error", "El campo 'Transcripción' no puede estar vacío.")
            return
        if not self.nuevo_usuario_var.get():
            messagebox.showerror("Error", "Debe seleccionar una opción para 'Nuevo Usuario?'.")
            return
        if self.nuevo_usuario_var.get() == "si" and not self.num_autores_combobox.get():
            messagebox.showerror("Error", "El campo 'Número de Autor/Autores' no puede estar vacío.")
            return
        if self.nuevo_usuario_var.get() == "no" and not self.num_autores_combobox_no.get():
            messagebox.showerror("Error", "El campo 'Número de Autor/Autores' no puede estar vacío.")
            return

        # Validar que los campos de cédula, nombre y apellido no estén vacíos
        if self.nuevo_usuario_var.get() == "si":
            for i in range(1, int(self.num_autores_combobox.get()) + 1):
                nombre = self.autores_frame.grid_slaves(row=i, column=1)[0].get()
                apellido = self.autores_frame.grid_slaves(row=i, column=3)[0].get()
                cedula = self.autores_frame.grid_slaves(row=i, column=5)[0].get()
                if not nombre:
                    messagebox.showerror("Error", f"El campo 'Nombre Autor {i}' no puede estar vacío.")
                    return
                if not apellido:
                    messagebox.showerror("Error", f"El campo 'Apellido Autor {i}' no puede estar vacío.")
                    return
                if not cedula:
                    messagebox.showerror("Error", f"El campo 'Cédula Autor {i}' no puede estar vacío.")
                    return
                if self.db_manager.obtener_autor_id(cedula):
                    messagebox.showerror("Error", f"La cédula {cedula} ya se encuentra registrada.")
                    return
        elif self.nuevo_usuario_var.get() == "no":
            for entry in self.cedula_entries_no:
                cedula = entry[1].get()
                if not cedula:
                    messagebox.showerror("Error", "El campo 'Cédula' no puede estar vacío.")
                    return

        # Guardar la transcripción en un archivo
        with open(self.filename, "w") as file:
            file.write(self.text_area.get("1.0", "end-1c"))
        messagebox.showinfo(title="Guardado", message=f"Transcripción guardada como {self.filename} en su carpeta local")

        # Obtener los datos de la interfaz
        tema = self.tema_combobox.get()
        titulo = self.titulo_entry.get()
        fecha = self.fecha_entry.get_date().strftime("%d-%m-%Y")
        texto = self.text_area.get("1.0", "end-1c")
        nuevo_usuario = self.nuevo_usuario_var.get()
        autores = []

        if nuevo_usuario == "si":
            num_autores = int(self.num_autores_combobox.get())
            for i in range(1, num_autores + 1):
                nombre = self.autores_frame.grid_slaves(row=i, column=1)[0].get()
                apellido = self.autores_frame.grid_slaves(row=i, column=3)[0].get()
                cedula = self.autores_frame.grid_slaves(row=i, column=5)[0].get()
                autores.append((nombre, apellido, cedula))
        elif nuevo_usuario == "no":
            for entry in self.cedula_entries_no:
                cedula = entry[1].get()
                nombre = entry[2].get()
                apellido = entry[3].get()
                autores.append((nombre, apellido, cedula))

        # Guardar los datos en la base de datos
        tema_id = self.db_manager.obtener_tema_id(tema)
        self.db_manager.insertar_presentacion(tema_id, titulo, fecha, texto)
        presentacion_id = self.db_manager.obtener_presentacion_id(titulo)

        for autor in autores:
            nombre, apellido, cedula = autor
            autor_id = self.db_manager.obtener_autor_id(cedula)
            if not autor_id:
                self.db_manager.insertar_autor(nombre, apellido, cedula)
                autor_id = self.db_manager.obtener_autor_id(cedula)
            self.db_manager.relacionar_presentacion_autor(presentacion_id, autor_id)

        # Limpiar todos las entradas 
        self.clear_inputs()

    def update_autores_fields(self, event):
        # Limpiar los campos existentes
        for widget in self.autores_frame.winfo_children():
            widget.destroy()

        num_autores = int(self.num_autores_combobox.get())
        for i in range(1, num_autores + 1):
            nombre_label = ctk.CTkLabel(self.autores_frame, text=f"Nombre Autor {i}:")
            nombre_label.grid(row=i, column=0, padx=5, pady=2, sticky="w")
            nombre_entry = ctk.CTkEntry(self.autores_frame, width=200, fg_color="#1E3A5F", border_color="white", border_width=2,   )
            nombre_entry.grid(row=i, column=1, padx=5, pady=2)

            apellido_label = ctk.CTkLabel(self.autores_frame, text=f"Apellido Autor {i}:")
            apellido_label.grid(row=i, column=2, padx=5, pady=2, sticky="w")
            apellido_entry = ctk.CTkEntry(self.autores_frame, width=200, fg_color="#1E3A5F", border_color="white", border_width=2,)
            apellido_entry.grid(row=i, column=3, padx=5, pady=2)

            cedula_label = ctk.CTkLabel(self.autores_frame, text=f"Cédula Autor {i}:")
            cedula_label.grid(row=i, column=4, padx=5, pady=2, sticky="w")
            cedula_entry = ctk.CTkEntry(self.autores_frame, width=200, validate="key", validatecommand=(self.cedula_validation, '%P'), fg_color="#1E3A5F",  border_color="white", border_width=2,)
            cedula_entry.grid(row=i, column=5, padx=5, pady=2)

    def toggle_autores_fields(self):
        # Clear previous fields and labels
        for widget in self.autores_frame.winfo_children():
            widget.destroy()
        for entry in self.cedula_entries_no:
            entry[0].destroy()
            entry[1].destroy()
            entry[2].destroy()
            entry[3].destroy()
        self.cedula_entries_no.clear()

        if self.nuevo_usuario_var.get() == "si":
            self.num_autores_label.grid()
            self.num_autores_combobox.grid()
            self.autores_frame.grid()
            self.cedula_label_no.grid_remove()
            self.cedula_entry_no.grid_remove()
            self.buscar_button_no.grid_remove()
            self.nombre_entry_no.grid_remove()
            self.apellido_entry_no.grid_remove()
            self.num_autores_label_no.grid_remove()
            self.num_autores_combobox_no.grid_remove()
            # Establecer el valor del combobox y llamar a update_autores_fields
            self.num_autores_combobox.set("1") # ESTABLECER POR DEFECTO EL NUMERO DE LISTA A 1
            self.update_autores_fields(None) # LLAMANDO FUNCION
        elif self.nuevo_usuario_var.get() == "no":
          
            self.num_autores_label.grid_remove()
            self.num_autores_combobox.grid_remove()
            self.autores_frame.grid_remove()
            self.num_autores_label_no.grid(row=4, column=0, padx=10, pady=5, sticky="w")
            self.num_autores_combobox_no.grid(row=4, column=1, padx=10, pady=5, sticky="w")
            self.cedula_label_no.grid_remove()
            self.cedula_entry_no.grid_remove()
            self.buscar_button_no.grid_remove()
            self.nombre_entry_no.grid_remove()
            self.apellido_entry_no.grid_remove()
            self.num_autores_combobox_no.set("1")  # Establecer valor predeterminado de 1
            self.update_cedula_fields(None) # LLAMANDO
    
        else:
            self.num_autores_label.grid_remove()
            self.num_autores_combobox.grid_remove()
            self.autores_frame.grid_remove()
            self.cedula_label_no.grid_remove()
            self.cedula_entry_no.grid_remove()
            self.buscar_button_no.grid_remove()
            self.nombre_entry_no.grid_remove()
            self.apellido_entry_no.grid_remove()
            self.num_autores_label_no.grid_remove()
            self.num_autores_combobox_no.grid_remove()

    def update_cedula_fields(self, event):
        # limpiar los campos existentes
        for entry in self.cedula_entries_no:
            entry[0].destroy()
            entry[1].destroy()
            entry[2].destroy()
            entry[3].destroy()
        self.cedula_entries_no.clear()

        num_autores = int(self.num_autores_combobox_no.get())
        for i in range(num_autores):
            cedula_label = ctk.CTkLabel(self.metadata_frame, text=f"Ingrese Cédula {i + 1}:")
            cedula_label.grid(row=5 + i, column=0, padx=10, pady=5, sticky="w")
            cedula_entry = ctk.CTkEntry(self.metadata_frame, width=250, validate="key", validatecommand=(self.cedula_validation, '%P'), fg_color="#1E3A5F", border_color="white", border_width=2,)
            cedula_entry.grid(row=5 + i, column=1, padx=10, pady=5, sticky="w")
            nombre_entry = ctk.CTkEntry(self.metadata_frame, width=250, state="readonly")
            apellido_entry = ctk.CTkEntry(self.metadata_frame, width=250, state="readonly")
            self.cedula_entries_no.append((cedula_label, cedula_entry, nombre_entry, apellido_entry))

        self.buscar_button_no.grid(row=5 + num_autores, column=2, padx=10, pady=5, sticky="w")

    def buscar_cedula(self):
        for entry in self.cedula_entries_no:
            cedula = entry[1].get()
            autor = self.db_manager.obtener_autor_por_cedula(cedula)
            if autor:
                nombre, apellido = autor
                entry[2].configure(state="normal")
                entry[3].configure(state="normal")
                entry[2].delete(0, "end")
                entry[3].delete(0, "end")
                entry[2].insert(0, nombre)
                entry[3].insert(0, apellido)
                entry[2].configure(state="readonly")
                entry[3].configure(state="readonly")
                entry[2].grid(row=5 + self.cedula_entries_no.index(entry), column=2, padx=10, pady=5, sticky="w")
                entry[3].grid(row=5 + self.cedula_entries_no.index(entry), column=3, padx=10, pady=5, sticky="w")
            else:
                messagebox.showinfo(title="No encontrado", message=f"No se encontró un autor con la cédula {cedula}.")

    def populate_tema_combobox(self):
        temas = self.db_manager.obtener_todos_los_temas()
        self.tema_combobox['values'] = temas

    def validate_cedula(self, value_if_allowed):
        if value_if_allowed.isdigit() or value_if_allowed == "":
            return True
        else:
            return False




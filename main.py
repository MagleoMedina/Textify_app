import customtkinter as ctk
from modulo_1 import AudioRecorderApp  # Importar la clase del módulo 1
from modulo_2 import AudioFileRecorderApp  # Importar la clase del módulo 2
from modulo_3 import App

class VentanaMain:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Textify")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)

        # Crear frame principal que ocupe toda la ventana y tenga fondo blanco
        self.frame_principal = ctk.CTkFrame(self.root, fg_color="white", corner_radius=0)
        self.frame_principal.pack(fill="both", expand=True)

        # Crear frame para botones dentro del frame principal
        self.frame_botones = ctk.CTkFrame(self.frame_principal, fg_color="#1E3A5F", corner_radius=0)
        self.frame_botones.pack(side="left", fill="y")
        # Establecer el icono de la ventana
        self.root.iconbitmap("logoAudio.ico")  # Para .ico
        
        self.title = ctk.CTkLabel(self.frame_botones, text="Textify", fg_color="#1E3A5F")
        self.title.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        # Crear enlaces
        self.boton_modulo1 = ctk.CTkLabel(self.frame_botones, text="Grabar archivos de audio", fg_color="#1E3A5F", cursor="hand2")
        self.boton_modulo1.bind("<Button-1>", lambda e: self.mostrar_modulo_1())
        self.boton_modulo1.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.boton_modulo2 = ctk.CTkLabel(self.frame_botones, text="Subir archivos de audio", fg_color="#1E3A5F", cursor="hand2")
        self.boton_modulo2.bind("<Button-1>", lambda e: self.mostrar_modulo_2())
        self.boton_modulo2.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.boton_modulo3 = ctk.CTkLabel(self.frame_botones, text="Buscar archivos subidos", fg_color="#1E3A5F", cursor="hand2")
        self.boton_modulo3.bind("<Button-1>", lambda e: self.mostrar_modulo_3())
        self.boton_modulo3.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.boton_cerrar = ctk.CTkLabel(self.frame_botones, text="Cerrar aplicacion", fg_color="#1E3A5F", cursor="hand2")
        self.boton_cerrar.bind("<Button-1>", lambda e: self.cerrar_aplicacion())
        self.boton_cerrar.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        # Colocar botones usando grid
        self.title.grid(row=0, column=0, padx=55, pady=5, sticky="w")
        self.boton_modulo1.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.boton_modulo2.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.boton_modulo3.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.boton_cerrar.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        # Frames para los modulos dentro del frame principal
        self.frame_modulo = ctk.CTkFrame(self.frame_principal)
        self.frame_modulo.place(relx=0.5, rely=0.43, anchor="center", )
        
        

    def limpiar_frame_modulo(self):
        for widget in self.frame_modulo.winfo_children():
            widget.destroy()

    def mostrar_modulo_1(self):
        # Limpiar el frame antes de mostrar el contenido del módulo 1
        self.limpiar_frame_modulo()
        
        # Crear una instancia de AudioRecorderApp dentro del frame_modulo
        modulo_1_app = AudioRecorderApp(self.frame_modulo)
        modulo_1_app.pack(fill="both", expand=True)

    def mostrar_modulo_2(self):
        # Limpiar el frame antes de mostrar el contenido del módulo 2
        self.limpiar_frame_modulo()
        
        # Crear una instancia de AudioFileRecorderApp dentro del frame_modulo
        modulo_2_app = AudioFileRecorderApp(self.frame_modulo)
        modulo_2_app.pack(fill="both", expand=True)
        
    def mostrar_modulo_3(self):
        # Limpiar el frame antes de mostrar el contenido del módulo 3
        self.limpiar_frame_modulo()
        
        # Aqui implementar el contenido del módulo 3
        modulo_3_app = App(self.frame_modulo)
        modulo_3_app.pack(fill="both", expand=True)
        
    def cerrar_aplicacion(self):
        self.root.quit()  # O usa self.root.destroy()
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    ventana = VentanaMain()
    ventana.run()

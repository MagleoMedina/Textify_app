import customtkinter as ctk
from modulo_1 import AudioRecorderApp  # Importar la clase del módulo 1

class VentanaMain:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Ventana Principal")
        self.root.geometry("1280x720")
        
        # Crear frame para botones
        self.frame_botones = ctk.CTkFrame(self.root)
        self.frame_botones.place(relx=0.0, rely=0.5, anchor="w")
        
        # Crear botones
        self.boton_modulo1 = ctk.CTkButton(self.frame_botones, text="Módulo 1", command=self.mostrar_modulo_1)
        self.boton_modulo2 = ctk.CTkButton(self.frame_botones, text="Módulo 2", command=self.mostrar_modulo_2)
        self.boton_modulo3 = ctk.CTkButton(self.frame_botones, text="Módulo 3", command=self.mostrar_modulo_3)
        
        # Colocar botones usando grid
        self.boton_modulo1.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.boton_modulo2.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.boton_modulo3.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        # Frames para los modulos
        self.frame_modulo = ctk.CTkFrame(self.root)
        self.frame_modulo.place(relx=0.5, rely=0.5, anchor="center")
        

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
        
        # Aqui implementar el contenido del módulo 2
        etiqueta = ctk.CTkLabel(self.frame_modulo, text="Módulo 2")
        etiqueta.pack()    
        
    def mostrar_modulo_3(self):
        # Limpiar el frame antes de mostrar el contenido del módulo 3
        self.limpiar_frame_modulo()
        
        # Aqui implementar el contenido del módulo 3
        etiqueta = ctk.CTkLabel(self.frame_modulo, text="Módulo 3") 
        etiqueta.pack()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    ventana = VentanaMain()
    ventana.run()

import ctypes
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import sys
from modulo_1 import AudioRecorderApp  # Importar la clase del módulo 1
from modulo_2 import AudioFileRecorderApp  # Importar la clase del módulo 2
from modulo_3 import App

class SplashScreen:
    def __init__(self, root):
        ctk.set_appearance_mode("dark") 
        self.root = root
        self.root.overrideredirect(True)  
        
        # Obtener el tamaño de la pantalla
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        # Definir el tamaño de la ventana del splash screen
        window_width = 400
        window_height = 300
        
        # Calcular la posición para centrar la ventana
        position_right = int(screen_width / 2 - window_width / 2)
        position_down = int(screen_height / 2 - window_height / 2)
        
        # Establecer la geometría de la ventana
        self.root.geometry(f"{window_width}x{window_height}+{position_right}+{position_down}")
        
        # Hacer la ventana transparente
        self.root.attributes("-transparentcolor", "#92d050")

        # Cargar y ajustar la imagen al tamaño de la ventana
        image_path = self.get_resource_path("logoAudio.png")
        self.image = Image.open(image_path)
        self.image = self.image.resize((window_width, window_height), Image.LANCZOS)
        
        # Convertir la imagen a un formato compatible con transparencia
        self.photo = ImageTk.PhotoImage(self.image)
        
        # Crear un label para mostrar la imagen
        self.label = tk.Label(self.root, image=self.photo, bg="white", bd=0, highlightthickness=0)
        self.label.pack(expand=True)

        # Iniciar la opacidad en 0 (transparente)
        self.alpha = 0
        self.fade_in()

        # Hacer la ventana clickeable y con transparencia
        self.make_window_clickthrough()

    def fade_in(self):
        """Aplicar efecto fade-in a la imagen."""
        if self.alpha < 1.0:
            self.alpha += 0.01
            self.root.attributes("-alpha", self.alpha)
            self.root.after(10, self.fade_in)

    def make_window_clickthrough(self):
        """Hacer la ventana transparente y clickeable."""
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        # WS_EX_LAYERED y WS_EX_TRANSPARENT hacen que sea transparente al clic
        ctypes.windll.user32.SetWindowLongW(hwnd, -20, 
                                            ctypes.windll.user32.GetWindowLongW(hwnd, -20) | 0x20)
        # Actualizar para manejar la transparencia
        ctypes.windll.user32.SetLayeredWindowAttributes(hwnd, 0, 255, 0x2)

    def get_resource_path(self, relative_path):
        """Obtiene la ruta del archivo, considerando si el programa está empaquetado."""
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def show(self):
        self.root.after(5000, self.root.destroy)  # Cerrar la ventana después de 10 segundos


class VentanaMain:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("Textify")
        self.root.geometry("1280x720")
        self.root.resizable(False, False)

        # Crear frame principal que ocupe toda la ventana y tenga fondo blanco
        self.frame_principal = ctk.CTkFrame(self.root, fg_color="#1E3A5F", corner_radius=0)
        self.frame_principal.pack(fill="both", expand=True)

        # Crear frame para botones dentro del frame principal
        self.frame_botones = ctk.CTkFrame(self.frame_principal, fg_color="#1E3A9F", corner_radius=0)
        self.frame_botones.pack(side="left", fill="y")
        
        # Establecer el icono de la ventana
        icon_path = self.get_resource_path("logoAudio.ico")
        self.root.iconbitmap(icon_path)  # Para .ico
        
        self.title = ctk.CTkLabel(self.frame_botones, text="Textify", fg_color="#1E3A9F")
        self.title.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        # Crear enlaces
        self.boton_modulo1 = ctk.CTkLabel(self.frame_botones, text="Grabar archivos de audio", fg_color="#1E3A9F", cursor="hand2")
        self.boton_modulo1.bind("<Button-1>", lambda e: self.mostrar_modulo_1())
        self.boton_modulo1.grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.boton_modulo2 = ctk.CTkLabel(self.frame_botones, text="Subir archivos de audio", fg_color="#1E3A9F", cursor="hand2")
        self.boton_modulo2.bind("<Button-1>", lambda e: self.mostrar_modulo_2())
        self.boton_modulo2.grid(row=1, column=0, padx=10, pady=5, sticky="w")

        self.boton_modulo3 = ctk.CTkLabel(self.frame_botones, text="Buscar archivos subidos", fg_color="#1E3A9F", cursor="hand2")
        self.boton_modulo3.bind("<Button-1>", lambda e: self.mostrar_modulo_3())
        self.boton_modulo3.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        
        self.boton_cerrar = ctk.CTkLabel(self.frame_botones, text="Cerrar aplicacion", fg_color="#1E3A9F", cursor="hand2")
        self.boton_cerrar.bind("<Button-1>", lambda e: self.cerrar_aplicacion())
        self.boton_cerrar.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        
        # Colocar botones usando grid
        self.title.grid(row=0, column=0, padx=55, pady=5, sticky="w")
        self.boton_modulo1.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.boton_modulo2.grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.boton_modulo3.grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.boton_cerrar.grid(row=4, column=0, padx=10, pady=5, sticky="w")
        
        # Frames para los modulos dentro del frame principal
        self.frame_modulo = ctk.CTkFrame(self.frame_principal, fg_color="#1E3A5F")
        self.frame_modulo.place(relx=0.5, rely=0.43, anchor="center")
        
        # Cargar y mostrar la imagen en el frame_modulo
        self.logo_image = Image.open("logoAudio.ico")
        self.logo_image = self.logo_image.resize((260, 250), Image.LANCZOS)  # Ajustar el tamaño de la imagen
        self.logo_photo = ImageTk.PhotoImage(self.logo_image)
        self.logo_label = ctk.CTkLabel(self.frame_modulo, image=self.logo_photo, text="")
        self.logo_label.pack(pady=40, padx=20, anchor="center", expand=True)  # Ajustar el padding y centrar          
    
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
        self.limpiar_frame_modulo()
        # Aqui implementar el contenido del módulo 3
        modulo_3_app = App(self.frame_modulo)
        modulo_3_app.pack(fill="both", expand=True)
   
    def cerrar_aplicacion(self):
        self.root.quit()  

    def get_resource_path(self, relative_path):
        """Obtiene la ruta del archivo, considerando si el programa está empaquetado."""
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    #splash_root = tk.Tk()
    #splash = SplashScreen(splash_root)
    #splash.show()
    #splash_root.mainloop()
    
    ventana = VentanaMain()
    ventana.frame_modulo.place(relx=0.58, rely=0.50, anchor="center")  # Ajustar relx para mover a la derecha 
    ventana.run()
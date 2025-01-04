import customtkinter as ctk
import tkinter.messagebox as messagebox
import db_manager


class App(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.pack(fill="both", expand=True)

        # Base de datos
        self.db_manager = db_manager.DBManager("database_tendencias.db")

        # Variables
        temas = self.db_manager.obtener_todos_los_temas()
        temas.insert(0, "BUSCAR POR TEMA")  # Opción inicial

        # Agregar el Entry principal
        self.entry = ctk.CTkEntry(self, placeholder_text="Escribe para buscar...",
                                  width=850, height=45, corner_radius=10)
        self.entry.grid(row=0, column=0, columnspan=3, padx=20, pady=20, sticky="nsew")

        # Configurar widgets distribuidos horizontalmente
        self.botton1 = ctk.CTkButton(self, text="BUSCAR POR TÍTULO",
                                     corner_radius=10, width=240,
                                     command=self.buscar_por_titulo)
        self.botton1.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        self.combobox = ctk.CTkComboBox(self, values=temas,
                                        corner_radius=10, width=240, fg_color="#1f6aa5", border_width=0,
                                        command=self.buscar_por_tema)
        self.combobox.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        self.botton3 = ctk.CTkButton(self, text="BUSCAR POR PALABRA CLAVE",
                                     corner_radius=10, width=240,
                                     command=self.buscar_por_palabra_clave)
        self.botton3.grid(row=1, column=2, padx=10, pady=10, sticky="ew")

        self.resultados = ctk.CTkLabel(self, text="Resultados:")
        self.resultados.grid(row=2, column=0, sticky="w", padx=10)

        # Widgets para mostrar los resultados
        self.frame = ctk.CTkFrame(self, width=850, height=280)
        self.frame.grid(row=3, columnspan=3, padx=10, pady=10, sticky="ew")

    def limpiar_frame(self):
        """Elimina todos los widgets del frame."""
        for widget in self.frame.winfo_children():
            widget.destroy()

    def mostrar_resultados(self, resultados):
        """Muestra los resultados con botones para ver y descargar texto."""
        if resultados:
            for idx, (id_, titulo, _, texto) in enumerate(resultados):
                # Mostrar el título
                label = ctk.CTkLabel(self.frame, text=f"{idx + 1}. {titulo}")
                label.grid(row=idx, column=0, padx=10, pady=5, sticky="w")

                # Botón para ver el texto
                ver_btn = ctk.CTkButton(self.frame, text="Ver", width=100,
                                        command=lambda t=texto: self.ver_texto(t))
                ver_btn.grid(row=idx, column=1, padx=5, pady=5)

                # Botón para descargar el texto
                descargar_btn = ctk.CTkButton(self.frame, text="Descargar", width=100,
                                              command=lambda t=texto, title=titulo: self.descargar_texto(t, title))
                descargar_btn.grid(row=idx, column=2, padx=5, pady=5)
        else:
            no_result_label = ctk.CTkLabel(self.frame, text="No hay resultados.")
            no_result_label.pack(anchor="center", padx=10, pady=10)

    def ver_texto(self, texto):
        """Muestra el texto en una ventana de solo lectura."""
        ventana = ctk.CTkToplevel(self)
        ventana.title("Texto")
        ventana.geometry("600x400")

        texto_widget = ctk.CTkTextbox(ventana, width=580, height=380)
        texto_widget.insert("1.0", texto)
        texto_widget.configure(state="disabled")
        texto_widget.pack(padx=10, pady=10)

    def descargar_texto(self, texto, titulo):
        """Descarga el texto como un archivo TXT."""
        filename = f"{titulo}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            file.write(texto)
        messagebox.showinfo("Descarga completada", f"El archivo se guardó como:\n{filename}")

    def buscar_por_titulo(self):
        """Busca presentaciones por título y muestra los resultados."""
        keyword = self.entry.get().strip()
        resultados = self.db_manager.buscar_por_titulo(keyword)

        self.limpiar_frame()  # Limpiar el frame antes de mostrar los resultados
        self.mostrar_resultados(resultados)

    def buscar_por_palabra_clave(self):
        """Busca presentaciones por palabra clave y muestra los resultados."""
        keyword = self.entry.get().strip()
        resultados = self.db_manager.buscar_por_palabra_clave(keyword)

        self.limpiar_frame()  # Limpiar el frame antes de mostrar los resultados
        self.mostrar_resultados(resultados)

    def buscar_por_tema(self, event=None):
        """Busca presentaciones por tema y muestra los resultados."""
        tema_seleccionado = self.combobox.get()

        if tema_seleccionado == "BUSCAR POR TEMA":
            return

        resultados = self.db_manager.obtener_presentaciones_por_nombre_tema(tema_seleccionado)

        self.limpiar_frame()  # Limpiar el frame antes de mostrar los resultados
        self.mostrar_resultados(resultados)


# # Crear la app
# if __name__ == "__main__":
#     root = ctk.CTk()
#     root.geometry("900x600")
#     app = App(root)
#     root.mainloop()

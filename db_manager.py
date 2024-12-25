import sqlite3

class DBManager:
    def __init__(self, db_name):
        """
        Inicializa la conexión con la base de datos.
        """
        self.db_name = db_name
        self.connection = None
        self.cursor = None
        self.connect()
        self.setup_database()  # Ensure the database schema is set up

    def connect(self):
        """
        Establece una conexión con la base de datos.
        """
        try:
            self.connection = sqlite3.connect(self.db_name)
            self.cursor = self.connection.cursor()
            print("Conexión establecida con la base de datos.")
        except sqlite3.Error as e:
            print(f"Error al conectar con la base de datos: {e}")

    def disconnect(self):
        """
        Cierra la conexión con la base de datos.
        """
        if self.connection:
            self.connection.close()
            print("Conexión cerrada.")

    def execute_query(self, query, params=None):
        """
        Ejecuta una consulta SQL.
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            self.connection.commit()
            #print("Consulta ejecutada con éxito.")
        except sqlite3.Error as e:
            print(f"Error al ejecutar la consulta: {e}")

    def fetch_all(self, query, params=None):
        """
        Ejecuta una consulta SQL y devuelve todos los resultados.
        """
        try:
            if params:
                self.cursor.execute(query, params)
            else:
                self.cursor.execute(query)
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error al realizar la consulta: {e}")
            return []

    def setup_database(self):
        """
        Configura las tablas según el esquema proporcionado.
        """
        schemas = [
            """
            CREATE TABLE IF NOT EXISTS Tema (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                Nombre TEXT NOT NULL
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Presentacion_autor (
                ID INTEGER NOT NULL,
                Presentacion INTEGER NOT NULL,
                Autor INTEGER NOT NULL,
                PRIMARY KEY(ID AUTOINCREMENT),
                FOREIGN KEY(Presentacion) REFERENCES Presentacion(ID),
                FOREIGN KEY(Autor) REFERENCES Autor(ID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Presentacion (
                ID INTEGER NOT NULL,
                Tema INTEGER NOT NULL,
                Titulo TEXT NOT NULL UNIQUE,
                Fecha TEXT NOT NULL,
                Texto TEXT NOT NULL,
                PRIMARY KEY(ID AUTOINCREMENT),
                FOREIGN KEY(Tema) REFERENCES Tema(ID)
            );
            """,
            """
            CREATE TABLE IF NOT EXISTS Autor (
                ID INTEGER NOT NULL,
                Nombre TEXT NOT NULL,
                Apellido TEXT NOT NULL,
                Cedula INTEGER UNIQUE,
                PRIMARY KEY(ID)
            );
            """
        ]
        for schema in schemas:
            self.execute_query(schema)

    # Métodos específicos para las tablas
    def insertar_tema(self, nombre):
        """
        Inserta un nuevo tema.
        """
        query = "INSERT INTO Tema (Nombre) VALUES (?);"
        self.execute_query(query, (nombre,))

    def insertar_autor(self, nombre, apellido, cedula):
        """
        Inserta un nuevo autor.
        """
        query = "INSERT INTO Autor (Nombre, Apellido, Cedula) VALUES (?, ?, ?);"
        self.execute_query(query, (nombre, apellido, cedula))

    def insertar_presentacion(self, tema_id, titulo, fecha, texto):
        """
        Inserta una nueva presentación.
        """
        query = "INSERT INTO Presentacion (Tema, Titulo, Fecha, Texto) VALUES (?, ?, ?, ?);"
        self.execute_query(query, (tema_id, titulo, fecha, texto))

    def relacionar_presentacion_autor(self, presentacion_id, autor_id):
        """
        Crea una relación entre una presentación y un autor.
        """
        query = "INSERT INTO Presentacion_autor (Presentacion, Autor) VALUES (?, ?);"
        self.execute_query(query, (presentacion_id, autor_id))

    def obtener_presentaciones_por_tema(self, tema_id):
        """
        Obtiene todas las presentaciones de un tema específico.
        """
        query = """
        SELECT Presentacion.ID, Presentacion.Titulo, Presentacion.Fecha, Presentacion.Texto
        FROM Presentacion
        WHERE Tema = ?;
        """
        return self.fetch_all(query, (tema_id,))

    def obtener_autores_de_presentacion(self, presentacion_id):
        """
        Obtiene los autores de una presentación específica.
        """
        query = """
        SELECT Autor.Nombre, Autor.Apellido
        FROM Presentacion_autor
        INNER JOIN Autor ON Presentacion_autor.Autor = Autor.ID
        WHERE Presentacion_autor.Presentacion = ?;
        """
        return self.fetch_all(query, (presentacion_id,))

    def obtener_todos_los_temas(self):
        """
        Devuelve todos los nombres de los temas.
        """
        query = "SELECT Nombre FROM Tema;"
        return [tema[0] for tema in self.fetch_all(query)]

    def titulo_existe(self, titulo):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM Presentacion WHERE Titulo = ?", (titulo,))
        result = cursor.fetchone()[0]
        conn.close()
        return result > 0

    def obtener_autor_por_cedula(self, cedula):
        """
        Obtiene el autor por su cedula.
        """
        query = "SELECT Nombre, Apellido FROM Autor WHERE Cedula = ?;"
        result = self.fetch_all(query, (cedula,))
        return result[0] if result else None

    def obtener_tema_id(self, nombre):
        """
        Obtiene el ID de un tema por su nombre.
        """
        query = "SELECT ID FROM Tema WHERE Nombre = ?;"
        result = self.fetch_all(query, (nombre,))
        return result[0][0] if result else None

    def obtener_presentacion_id(self, titulo):
        """
        Obtiene el ID de una presentación por su título.
        """
        query = "SELECT ID FROM Presentacion WHERE Titulo = ?;"
        result = self.fetch_all(query, (titulo,))
        return result[0][0] if result else None

    def obtener_autor_id(self, cedula):
        """
        Obtiene el ID de un autor por su cédula.
        """
        query = "SELECT ID FROM Autor WHERE Cedula = ?;"
        result = self.fetch_all(query, (cedula,))
        return result[0][0] if result else None

# Ejemplo de uso
if __name__ == "__main__":
    db = DBManager("database_tendencias.db")

    # Crear las tablas desde el esquema
    # db.setup_database()  # This is now called in the constructor

    temas = db.obtener_todos_los_temas()
    print("Temas registrados:", temas)

    # Cerrar conexión
    db.disconnect()
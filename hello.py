import streamlit as st
import sqlite3
from PIL import Image
import io

# Función para verificar acceso de usuario y contraseña
def verificar_acceso(usuario, contraseña):
    """
    Verifica si el usuario y la contraseña son válidos.
    """
    USUARIOS_VALIDOS = {
        "personal1": "personalcontra",
        "especialista1": "especialistacontra",
        "flavio": "avendano",
        "axel" : "balboa"
    }
    return USUARIOS_VALIDOS.get(usuario) == contraseña

# Conectar o crear una base de datos
def conectar_db():
    conn = sqlite3.connect('pacientes.db')
    return conn

# Crear una tabla para almacenar la información de los pacientes y sus imágenes
def crear_tabla():
    conn = conectar_db()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        edad TEXT,
        sexo TEXT,
        sintomas_previos TEXT,
        foto_ojo_derecho BLOB,
        foto_ojo_izquierdo BLOB
    )
    ''')
    conn.close()

# Insertar o actualizar la información de un paciente en la base de datos
def guardar_datos_paciente(nombre, edad, sexo, sintomas_previos, foto_ojo_derecho, foto_ojo_izquierdo, id_paciente=None):
    conn = conectar_db()
    cursor = conn.cursor()
    if id_paciente:  # Si ya existe el paciente, actualizar
        cursor.execute('''
        UPDATE pacientes
        SET nombre=?, edad=?, sexo=?, sintomas_previos=?, foto_ojo_derecho=?, foto_ojo_izquierdo=?
        WHERE id=?
        ''', (nombre, edad, sexo, sintomas_previos, foto_ojo_derecho, foto_ojo_izquierdo, id_paciente))
    else:  # Si no existe, insertar un nuevo paciente
        cursor.execute('''
        INSERT INTO pacientes (nombre, edad, sexo, sintomas_previos, foto_ojo_derecho, foto_ojo_izquierdo)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (nombre, edad, sexo, sintomas_previos, foto_ojo_derecho, foto_ojo_izquierdo))
    conn.commit()
    conn.close()

# Eliminar un paciente de la base de datos
def eliminar_paciente(id_paciente):
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM pacientes WHERE id=?', (id_paciente,))
    conn.commit()
    conn.close()

# Cargar los datos de todos los pacientes desde la base de datos
def cargar_datos_pacientes():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pacientes")
    datos = cursor.fetchall()
    conn.close()
    return datos

# Convertir imagen a binario para almacenar en la base de datos
def convertir_a_binario(imagen):
    if imagen is not None:
        return imagen.read()
    return None

# Convertir binario a imagen para visualizar
def convertir_a_imagen(binario):
    if binario:
        return Image.open(io.BytesIO(binario))
    return None

# Inicializar la base de datos y tabla al inicio
crear_tabla()

# Estado de la sesión para saber si el usuario está logueado y su tipo
if "acceso_concedido" not in st.session_state:
    st.session_state.acceso_concedido = False
    st.session_state.tipo_usuario = None
    st.session_state.paciente_seleccionado = None

# Si el usuario aún no está autenticado, mostrar el formulario de inicio de sesión
if not st.session_state.acceso_concedido:
    st.markdown("<h1 style='color: #4B8BBE;'>Iniciar Sesión</h1>", unsafe_allow_html=True)
    with st.form("form_login"):
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")
        submit_login = st.form_submit_button("Ingresar")

    if submit_login:
        if verificar_acceso(usuario, contraseña):
            st.success("Acceso concedido.")
            st.session_state.acceso_concedido = True
            st.session_state.tipo_usuario = usuario  # Guardamos el tipo de usuario
            st.experimental_set_query_params(refresh=True)
        else:
            st.error("Usuario o contraseña incorrectos.")
else:
    # Página de selección de pacientes
    st.markdown(f"<h1 style='color: #4B8BBE;'>Historial Médico</h1>", unsafe_allow_html=True)
    st.markdown(f"<h2 style='color: #306998;'>Bienvenido {st.session_state.tipo_usuario}</h2>", unsafe_allow_html=True)

    # Cargar los datos de todos los pacientes
    pacientes_db = cargar_datos_pacientes()

    # Mostrar los datos de los pacientes cargados desde la base de datos
    st.markdown("<h3 style='color: #306998;'>Pacientes:</h3>", unsafe_allow_html=True)
    if len(pacientes_db) == 0:
        st.warning("No hay pacientes cargados.")
    else:
        for i, paciente in enumerate(pacientes_db):
            id_paciente, nombre, edad, sexo, sintomas_previos, _, _ = paciente
            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                if st.button(f"Paciente {i+1} ({nombre})", key=f"btn_paciente_{id_paciente}"):
                    st.session_state.paciente_seleccionado = paciente

            with col2:
                if st.button("Eliminar", key=f"eliminar_{id_paciente}"):
                    eliminar_paciente(id_paciente)
                    st.experimental_rerun()  # Recargar la página para ver los cambios

    # Formulario para agregar un nuevo paciente
    st.markdown("<h3 style='color: #4B8BBE;'>Agregar nuevo paciente:</h3>", unsafe_allow_html=True)
    with st.form("form_agregar_paciente"):
        nuevo_nombre = st.text_input("Nombre y Apellidos", key="nuevo_nombre")
        nueva_edad = st.text_input("Edad", key="nueva_edad")
        nuevo_sexo = st.text_input("Sexo", key="nuevo_sexo")
        nuevo_sintomas = st.text_area("Síntomas previos", key="nuevo_sintomas")
        submit_nuevo_paciente = st.form_submit_button("Agregar Paciente")

    # Guardar el nuevo paciente en la base de datos
    if submit_nuevo_paciente:
        if not (nuevo_nombre and nueva_edad and nuevo_sexo):
            st.error("Nombre, Edad y Sexo son obligatorios.")
        else:
            guardar_datos_paciente(nuevo_nombre, nueva_edad, nuevo_sexo, nuevo_sintomas, None, None)
            st.success("Paciente agregado correctamente.")
            st.experimental_rerun()  # Recargar la página para ver el nuevo paciente

    # Si un paciente es seleccionado, mostrar las opciones de Historial Médico o Reporte
    if st.session_state.paciente_seleccionado:
        paciente = st.session_state.paciente_seleccionado
        st.markdown(f"<h3 style='color: #306998;'>Paciente: {paciente[1]}</h3>", unsafe_allow_html=True)
        seleccion = st.radio("Selecciona una opción", ("Historial Médico", "Reporte"))

        if seleccion == "Historial Médico":
            # Formulario de historial médico específico para cada paciente
            with st.form("form_historial"):
                nombre = st.text_input("Nombre y Apellidos", key="nombre", value=paciente[1])
                edad = st.text_input("Edad", key="edad", value=paciente[2])
                sexo = st.text_input("Sexo", key="sexo", value=paciente[3])
                sintomas_previos = st.text_area("Síntomas previos", key="sintomas_previos", value=paciente[4])
                camara = st.camera_input(" Tomar foto")

                # Campos para adjuntar fotos de los ojos
                foto_ojo_derecho = st.file_uploader("Foto ojo derecho", type=["png", "jpg", "jpeg"], key="foto_derecho")
                foto_ojo_izquierdo = st.file_uploader("Foto ojo izquierdo", type=["png", "jpg", "jpeg"], key="foto_izquierdo")

                # Visualizar imágenes actuales
                imagen_derecha = convertir_a_imagen(paciente[5])  # Convertir binario a imagen
                if imagen_derecha:
                    st.image(imagen_derecha, caption="Foto ojo derecho", use_column_width=True)

                imagen_izquierda = convertir_a_imagen(paciente[6])  # Convertir binario a imagen
                if imagen_izquierda:
                    st.image(imagen_izquierda, caption="Foto ojo izquierdo", use_column_width=True)

                submit_historial = st.form_submit_button("Guardar Historial")

            # Verificar si los campos obligatorios están completos y guardarlos en la base de datos
            if submit_historial:
                if not (nombre and edad and sexo):
                    st.error("Nombre, Edad y Sexo son obligatorios.")
                else:
                    # Convertir imágenes a binario y guardarlas en la base de datos
                    binario_ojo_derecho = convertir_a_binario(foto_ojo_derecho)
                    binario_ojo_izquierdo = convertir_a_binario(foto_ojo_izquierdo)

                    guardar_datos_paciente(nombre, edad, sexo, sintomas_previos, binario_ojo_derecho, binario_ojo_izquierdo, id_paciente=paciente[0])
                    st.success("Historial médico guardado correctamente.")
                    st.experimental_rerun()  # Refrescar para ver cambios

    # Botón para cerrar sesión
    if st.button("Cerrar sesión", key="cerrar_sesion"):
        st.session_state.acceso_concedido = False
        st.session_state.tipo_usuario = None
        st.session_state.paciente_seleccionado = None
        st.experimental_set_query_params(refresh=True)

import streamlit as st
import sqlite3
from PIL import Image
import io
from fpdf import FPDF

# Función para verificar acceso de usuario y contraseña
def verificar_acceso(usuario, contraseña):
    USUARIOS_VALIDOS = {
        "personal1": "personalcontra",
        "especialista1": "especialistacontra"
    }
    return USUARIOS_VALIDOS.get(usuario) == contraseña

# Conectar o crear una base de datos
def conectar_db():
    conn = sqlite3.connect('pacientes.db')
    return conn

# Crear una tabla para almacenar la información de los pacientes y sus imágenes
def crear_tabla():
    conn = conectar_db()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS pacientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT,
        edad TEXT,
        sexo TEXT,
        direccion TEXT,
        dni TEXT,
        telefono TEXT,
        sintomas_previos TEXT,
        foto_ojo_derecho BLOB,
        foto_ojo_izquierdo BLOB,
        reporte TEXT
    )
    ''')
    conn.commit()
    conn.close()

# Insertar o actualizar la información de un paciente en la base de datos
def guardar_datos_paciente(nombre, edad, sexo, direccion, dni, telefono, sintomas_previos, foto_ojo_derecho, foto_ojo_izquierdo, reporte, id_paciente=None):
    conn = conectar_db()
    cursor = conn.cursor()
    if id_paciente:
        cursor.execute('''
        UPDATE pacientes
        SET nombre=?, edad=?, sexo=?, direccion=?, dni=?, telefono=?, sintomas_previos=?, foto_ojo_derecho=?, foto_ojo_izquierdo=?, reporte=?
        WHERE id=?
        ''', (nombre, edad, sexo, direccion, dni, telefono, sintomas_previos, foto_ojo_derecho, foto_ojo_izquierdo, reporte, id_paciente))
    else:
        cursor.execute('''
        INSERT INTO pacientes (nombre, edad, sexo, direccion, dni, telefono, sintomas_previos, foto_ojo_derecho, foto_ojo_izquierdo, reporte)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nombre, edad, sexo, direccion, dni, telefono, sintomas_previos, foto_ojo_derecho, foto_ojo_izquierdo, reporte))
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

# Función para generar PDF del reporte del paciente
def generar_pdf(nombre, edad, sexo, direccion, dni, telefono, sintomas, reporte, imagen_derecho, imagen_izquierdo):
    pdf = FPDF()
    pdf.add_page()

    # Título del reporte
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Reporte Médico del Paciente", ln=True, align="C")
    pdf.ln(10)

    # Información del paciente
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Datos del Paciente", ln=True)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Nombre: {nombre}", ln=True)
    pdf.cell(0, 10, f"Edad: {edad}", ln=True)
    pdf.cell(0, 10, f"Sexo: {sexo}", ln=True)
    pdf.cell(0, 10, f"Dirección: {direccion}", ln=True)
    pdf.cell(0, 10, f"DNI: {dni}", ln=True)
    pdf.cell(0, 10, f"Teléfono: {telefono}", ln=True)

    # Dibujar un rectángulo para las secciones
    pdf.ln(10)
    pdf.set_fill_color(230, 230, 230)  # Color de relleno
    pdf.cell(0, 10, "Síntomas Previos", border=1, ln=True, fill=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=sintomas, border=1)
    
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Reporte Médico", border=1, ln=True, fill=True)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, txt=reporte, border=1)

    # Dibujar una sección para las imágenes
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Imágenes de los Ojos", ln=True, fill=True)
    pdf.ln(5)

    if imagen_derecho:
        img_path = "ojo_derecho_temp.png"
        imagen_derecho.save(img_path)
        pdf.cell(0, 10, "Imagen Ojo Derecho:", ln=True)
        pdf.image(img_path, x=10, y=None, w=90)
    
    if imagen_izquierdo:
        img_path = "ojo_izquierdo_temp.png"
        imagen_izquierdo.save(img_path)
        pdf.cell(0, 10, "Imagen Ojo Izquierdo:", ln=True)
        pdf.image(img_path, x=110, y=None, w=90)

    # Espacio para firma y nombre del especialista
    pdf.ln(20)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 10, "Especialista: ________", ln=True, align="L")
    pdf.cell(0, 10, "Firma: ________", ln=True, align="L")

    # Guardar PDF en un archivo temporal
    pdf_output = f"Reporte_{nombre}.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Inicializar la base de datos y tabla al inicio
crear_tabla()

# Estilo de la página con fondo de color pastel
st.markdown(
    """
    <style>
    .main {
        background-color: #f0f8ff; /* Color pastel para el fondo */
    }
    </style>
    """, unsafe_allow_html=True
)

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
            st.session_state.tipo_usuario = usuario
            st.experimental_set_query_params(refresh=True)
        else:
            st.error("Usuario o contraseña incorrectos.")
else:
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
            id_paciente, nombre, edad, sexo, direccion, dni, telefono, sintomas_previos, foto_derecho, foto_izquierdo, reporte = paciente
            col1, col2, col3 = st.columns([5, 1, 1])
            with col1:
                if st.button(f"Paciente {i+1} ({nombre})", key=f"btn_paciente_{id_paciente}"):
                    st.session_state.paciente_seleccionado = paciente

            with col2:
                if st.button("Eliminar", key=f"eliminar_{id_paciente}"):
                    eliminar_paciente(id_paciente)
                    st.experimental_set_query_params(refresh=True)

    # Agregar un nuevo paciente con opción desplegable
    with st.expander("Agregar nuevo paciente"):
        st.markdown("<h3 style='color: #4B8BBE;'>Ingrese los datos del nuevo paciente:</h3>", unsafe_allow_html=True)
        with st.form("form_agregar_paciente"):
            nuevo_nombre = st.text_input("Nombre y Apellidos", key="nuevo_nombre")
            nueva_edad = st.text_input("Edad", key="nueva_edad")
            nuevo_sexo = st.selectbox("Sexo", options=["Masculino", "Femenino"], key="nuevo_sexo")
            nueva_direccion = st.text_input("Dirección", key="nueva_direccion")
            nuevo_dni = st.text_input("DNI", key="nuevo_dni")
            nuevo_telefono = st.text_input("Teléfono", key="nuevo_telefono")
            nuevo_sintomas = st.text_area("Síntomas previos", key="nuevo_sintomas")
            submit_nuevo_paciente = st.form_submit_button("Agregar Paciente")

        # Guardar el nuevo paciente en la base de datos
        if submit_nuevo_paciente:
            if not (nuevo_nombre and nueva_edad and nuevo_sexo and nueva_direccion and nuevo_dni and nuevo_telefono):
                st.error("Nombre, Edad, Sexo, Dirección, DNI y Teléfono son obligatorios.")
            else:
                # Guardar el nuevo paciente
                guardar_datos_paciente(nuevo_nombre, nueva_edad, nuevo_sexo, nueva_direccion, nuevo_dni, nuevo_telefono, nuevo_sintomas, None, None, None)
                st.success("Paciente agregado correctamente.")
                st.experimental_set_query_params(refresh=True)

    # Si un paciente es seleccionado, mostrar las opciones de Historial Médico o Reporte
    if st.session_state.paciente_seleccionado:
        paciente = st.session_state.paciente_seleccionado
        st.markdown(f"<h3 style='color: #306998;'>Paciente: {paciente[1]}</h3>", unsafe_allow_html=True)
        seleccion = st.radio("Selecciona una opción", ("Historial Médico", "Reporte"))

        if seleccion == "Historial Médico":
            # Mostrar el formulario de Historial Médico
            with st.form("form_historial"):
                nombre = st.text_input("Nombre y Apellidos", value=paciente[1])
                edad = st.text_input("Edad", value=paciente[2])
                sexo = st.selectbox("Sexo", options=["Masculino", "Femenino"], index=0 if paciente[3] == "Masculino" else 1)
                direccion = st.text_input("Dirección", value=paciente[4])
                dni = st.text_input("DNI", value=paciente[5])
                telefono = st.text_input("Teléfono", value=paciente[6])
                sintomas_previos = st.text_area("Síntomas previos", value=paciente[7])

                # Campos para adjuntar fotos de los ojos
                foto_ojo_derecho = st.file_uploader("Foto ojo derecho", type=["png", "jpg", "jpeg"], key="foto_derecho")
                foto_ojo_izquierdo = st.file_uploader("Foto ojo izquierdo", type=["png", "jpg", "jpeg"], key="foto_izquierdo")

                # Visualizar imágenes actuales
                imagen_derecha = convertir_a_imagen(paciente[8])
                if imagen_derecha:
                    st.image(imagen_derecha, caption="Foto ojo derecho", use_column_width=True)

                imagen_izquierda = convertir_a_imagen(paciente[9])
                if imagen_izquierda:
                    st.image(imagen_izquierda, caption="Foto ojo izquierdo", use_column_width=True)

                submit_historial = st.form_submit_button("Guardar Historial")

            # Guardar los datos de historial médico en la base de datos
            if submit_historial:
                if not (nombre and edad and sexo and direccion and dni and telefono):
                    st.error("Nombre, Edad, Sexo, Dirección, DNI y Teléfono son obligatorios.")
                else:
                    binario_ojo_derecho = convertir_a_binario(foto_ojo_derecho)
                    binario_ojo_izquierdo = convertir_a_binario(foto_ojo_izquierdo)
                    guardar_datos_paciente(nombre, edad, sexo, direccion, dni, telefono, sintomas_previos, binario_ojo_derecho, binario_ojo_izquierdo, paciente[10], id_paciente=paciente[0])
                    st.success("Historial médico guardado correctamente.")
                    st.experimental_set_query_params(refresh=True)

        elif seleccion == "Reporte":
            st.markdown("<h3 style='color: #306998;'>Reporte del paciente</h3>", unsafe_allow_html=True)
            with st.form("form_reporte"):
                reporte = st.text_area("Escribe el reporte aquí:", value=paciente[10] if paciente[10] else "", height=200)
                submit_reporte = st.form_submit_button("Guardar Reporte")

            if submit_reporte:
                guardar_datos_paciente(paciente[1], paciente[2], paciente[3], paciente[4], paciente[5], paciente[6], paciente[7], paciente[8], paciente[9], reporte, id_paciente=paciente[0])
                st.success("Reporte guardado correctamente.")
                st.experimental_set_query_params(refresh=True)

            # Botón para generar el PDF del reporte
            if st.button("Generar PDF"):
                imagen_derecha = convertir_a_imagen(paciente[8])
                imagen_izquierda = convertir_a_imagen(paciente[9])
                pdf_file = generar_pdf(paciente[1], paciente[2], paciente[3], paciente[4], paciente[5], paciente[6], paciente[7], reporte, imagen_derecha, imagen_izquierda)
                with open(pdf_file, "rb") as pdf:
                    st.download_button("Descargar PDF", pdf, file_name=f"Reporte_{paciente[1]}.pdf")

    # Botón para cerrar sesión
    if st.button("Cerrar sesión", key="cerrar_sesion"):
        st.session_state.acceso_concedido = False
        st.session_state.tipo_usuario = None
        st.session_state.paciente_seleccionado = None
        st.experimental_set_query_params(refresh=True)
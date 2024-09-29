import streamlit as st
import re
import sqlite3

# Datos de acceso predeterminados para personal médico y especialista
USUARIOS_VALIDOS = {
    "personal1": "personalcontra",
    "especialista1": "especialistacontra"
}

# Verificar el acceso basado en usuario y contraseña
def verificar_acceso(usuario, contraseña):
    if usuario in USUARIOS_VALIDOS and USUARIOS_VALIDOS[usuario] == contraseña:
        return True
    else:
        return False

# Inicializar los estados necesarios para cada paciente
def inicializar_estado():
    if "pacientes" not in st.session_state:
        st.session_state.pacientes = {
            "Paciente 1": {"historial": {}, "reporte": {}, "revisado": False},
            "Paciente 2": {"historial": {}, "reporte": {}, "revisado": False},
            "Paciente 3": {"historial": {}, "reporte": {}, "revisado": False},
            "Paciente 4": {"historial": {}, "reporte": {}, "revisado": False},
            "Paciente 5": {"historial": {}, "reporte": {}, "revisado": False},
            "Paciente 6": {"historial": {}, "reporte": {}, "revisado": False},
        }

# Llamamos a la función para inicializar los estados
inicializar_estado()

# Estado de la sesión para saber si el usuario está logueado y su tipo
if "acceso_concedido" not in st.session_state:
    st.session_state.acceso_concedido = False
    st.session_state.tipo_usuario = None
    st.session_state.paciente_seleccionado = None

# Si el usuario aún no está autenticado, mostrar el formulario de inicio de sesión
if not st.session_state.acceso_concedido:
    # Formulario de inicio de sesión
    with st.form("form_login"):
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")

        # Botón de enviar
        submit_login = st.form_submit_button("Ingresar")

    # Verificar si el usuario y la contraseña son correctos
    if submit_login:
        if verificar_acceso(usuario, contraseña):
            st.success("Acceso concedido.")
            st.session_state.acceso_concedido = True
            st.session_state.tipo_usuario = usuario  # Guardamos el tipo de usuario
            # Redirigimos simulando un refresco de página
            st.experimental_set_query_params(refresh=True)
        else:
            st.error("Usuario o contraseña incorrectos.")
else:
    # Página de selección de pacientes
    st.title("Historial Médico")
    st.header(f"Bienvenido {st.session_state.tipo_usuario}")

    # Mostrar cada paciente como un botón
    for paciente, datos in st.session_state.pacientes.items():
        cols = st.columns([4, 1])  # Dividimos en dos columnas: botón de paciente y checkbox de "Ya revisado"
        with cols[0]:
            if st.button(paciente):
                st.session_state.paciente_seleccionado = paciente
                # Redirigimos simulando un refresco de página
                st.experimental_set_query_params(refresh=True)

        with cols[1]:
            st.session_state.pacientes[paciente]["revisado"] = st.checkbox("Ya revisado", value=datos["revisado"], key=f"revisado_{paciente}")

    # Si un paciente es seleccionado, mostrar las opciones de Historial Médico o Reporte
    if st.session_state.paciente_seleccionado:
        paciente = st.session_state.paciente_seleccionado
        st.subheader(f"{paciente}")
        seleccion = st.radio("Selecciona una opción", ("Historial Médico", "Reporte"))

        if seleccion == "Historial Médico":
            # Formulario de historial médico específico para cada paciente
            with st.form("form_historial"):
                nombre = st.text_input("Nombre y Apellidos", key=f"nombre_{paciente}", value=st.session_state.pacientes[paciente]["historial"].get("nombre", ""))
                edad = st.text_input("Edad", key=f"edad_{paciente}", value=st.session_state.pacientes[paciente]["historial"].get("edad", ""))
                sexo = st.text_input("Sexo", key=f"sexo_{paciente}", value=st.session_state.pacientes[paciente]["historial"].get("sexo", ""))
                sintomas_previos = st.text_area("Síntomas previos", key=f"sintomas_{paciente}", value=st.session_state.pacientes[paciente]["historial"].get("sintomas_previos", ""))

                # Campos para adjuntar fotos de los ojos
                foto_ojo_derecho = st.file_uploader("Foto ojo derecho", type=["png", "jpg", "jpeg"], key=f"foto_derecho_{paciente}")
                foto_ojo_izquierdo = st.file_uploader("Foto ojo izquierdo", type=["png", "jpg", "jpeg"], key=f"foto_izquierdo_{paciente}")

                submit_historial = st.form_submit_button("Guardar Historial")

            # Verificar si los campos obligatorios están completos y guardarlos en el estado
            if submit_historial:
                if not nombre or not edad or not sexo:
                    st.error("Nombre, Edad y Sexo son obligatorios.")
                else:
                    st.session_state.pacientes[paciente]["historial"] = {
                        "nombre": nombre,
                        "edad": edad,
                        "sexo": sexo,
                        "sintomas_previos": sintomas_previos,
                        "foto_ojo_derecho": foto_ojo_derecho,
                        "foto_ojo_izquierdo": foto_ojo_izquierdo
                    }
                    st.success("Historial médico guardado correctamente.")

        elif seleccion == "Reporte":
            # Formulario de reporte específico para cada paciente
            with st.form("form_reporte"):
                reporte_ojo_derecho = st.text_area("Añadir texto correspondiente al ojo derecho", key=f"reporte_derecho_{paciente}", value=st.session_state.pacientes[paciente]["reporte"].get("ojo_derecho", ""))
                reporte_ojo_izquierdo = st.text_area("Añadir texto correspondiente al ojo izquierdo", key=f"reporte_izquierdo_{paciente}", value=st.session_state.pacientes[paciente]["reporte"].get("ojo_izquierdo", ""))
                reporte_general = st.text_area("Reporte general", key=f"reporte_general_{paciente}", value=st.session_state.pacientes[paciente]["reporte"].get("general", ""))

                submit_reporte = st.form_submit_button("Guardar Reporte")

            if submit_reporte:
                st.session_state.pacientes[paciente]["reporte"] = {
                    "ojo_derecho": reporte_ojo_derecho,
                    "ojo_izquierdo": reporte_ojo_izquierdo,
                    "general": reporte_general
                }
                st.success("Reporte guardado correctamente.")

    # Botón para cerrar sesión
    if st.button("Cerrar sesión"):
        st.session_state.acceso_concedido = False
        st.session_state.tipo_usuario = None
        st.session_state.paciente_seleccionado = None
        # Redirigimos simulando un refresco de página
        st.experimental_set_query_params(refresh=True)
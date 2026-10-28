"""Recomendador de películas con Streamlit, comentado en español.
Ejecutar: python -m streamlit run app.py
Coloca base_conocimiento.json junto a este archivo o súbelo desde la interfaz.
"""
import json
from pathlib import Path
import streamlit as st


def validar_base(base):
    """Comprueba los datos antes de utilizarlos en la interfaz y las reglas."""
    if not isinstance(base, dict):
        raise ValueError("La base debe ser un objeto JSON.")
    for campo in ("categorias", "atributos", "exclusiones"):
        if not isinstance(base.get(campo), dict):
            raise ValueError(f"{campo} debe ser un objeto JSON.")
    for campo in ("categorias", "atributos"):
        if not base[campo] or not all(isinstance(v, str) and v.strip() for v in base[campo].values()):
            raise ValueError(f"{campo} debe contener nombres o preguntas de texto.")
    for campo in ("reglas", "peliculas"):
        if not isinstance(base.get(campo), list):
            raise ValueError(f"{campo} debe ser una lista.")
    for regla in base["reglas"]:
        if not isinstance(regla, dict) or regla.get("categoria") not in base["categorias"]:
            raise ValueError("Una regla contiene una categoría desconocida.")
        for operador in ("todos", "alguno", "ninguno"):
            nombres = regla.get(operador)
            if not isinstance(nombres, list) or any(not isinstance(n, str) or n not in base["atributos"] for n in nombres):
                raise ValueError(f"Lista de atributos inválida: {operador}.")
    for nombre, categoria in base["exclusiones"].items():
        if nombre not in base["atributos"] or not isinstance(categoria, str) or categoria not in base["categorias"]:
            raise ValueError("Una exclusión contiene un atributo o categoría desconocido.")
    for pelicula in base["peliculas"]:
        if not isinstance(pelicula, dict):
            raise ValueError("Cada película debe ser un objeto JSON.")
        for campo in ("titulo", "anio", "sinopsis"):
            if campo not in pelicula or not isinstance(pelicula[campo], (str, int)):
                raise ValueError(f"Una película tiene un campo inválido: {campo}.")
        categorias = pelicula.get("categorias")
        if not isinstance(categorias, list) or not categorias or any(not isinstance(c, str) or c not in base["categorias"] for c in categorias):
            raise ValueError("Una película contiene categorías inválidas.")
    return base


def evaluar_regla(regla, atributos):
    """Evalúa AND(todos) AND OR(alguno) AND NOT OR(ninguno).

    Una lista vacía no agrega restricciones.
    Los valores de atributos son las respuestas booleanas del usuario.
    """
    return (
        # AND: todos los atributos de esta lista deben ser verdaderos.
        # all sobre una lista vacía devuelve True.
        all(atributos[nombre] for nombre in regla["todos"])
        # OR: al menos uno debe ser verdadero; si no hay elementos, se acepta.
        and (not regla["alguno"] or any(
            atributos[nombre] for nombre in regla["alguno"]
        ))
        # NOT OR: ninguno de estos atributos debe ser verdadero.
        and not any(atributos[nombre] for nombre in regla["ninguno"])
    )


def ecuacion(regla):
    """Convierte una regla en texto para mostrar su expresión lógica."""
    # Copia los atributos obligatorios sin modificar la lista original.
    partes = list(regla["todos"])
    if regla["alguno"]:
        partes.append("(" + " OR ".join(regla["alguno"]) + ")")
    if regla["ninguno"]:
        partes.append("NOT (" + " OR ".join(regla["ninguno"]) + ")")
    # Una regla sin condiciones se representa con TRUE.
    # La categoría a la derecha de => es la conclusión de la regla.
    return (" AND ".join(partes) or "TRUE") + " => " + regla["categoria"]


def recomendar(base, atributos):
    """Selecciona películas según las reglas satisfechas y las exclusiones."""
    # Conserva únicamente las reglas que cumplen las respuestas del usuario.
    reglas = [r for r in base["reglas"] if evaluar_regla(r, atributos)]
    # Un conjunto reúne las categorías inferidas sin repetirlas.
    categorias = {r["categoria"] for r in reglas}
    resultados = []
    for pelicula in base["peliculas"]:
        # Obtiene las categorías compartidas entre las reglas y la película.
        coincidencias = categorias.intersection(pelicula["categorias"])
        # NOT se aplica también al catálogo: una película con varios géneros
        # se excluye si contiene cualquiera de las categorías rechazadas.
        # exclusiones relaciona el nombre de un atributo con una categoría.
        excluida = any(
            atributos[nombre] and categoria in pelicula["categorias"]
            for nombre, categoria in base["exclusiones"].items()
        )
        if coincidencias and not excluida:
            # Guarda la película junto con las categorías que la justifican.
            resultados.append((pelicula, coincidencias))
    # Ordena por mayor número de coincidencias y, en caso de empate, por título.
    resultados.sort(key=lambda item: (-len(item[1]), item[0]["titulo"]))
    return reglas, resultados


def mostrar_pelicula(pelicula, base, coincidencias=None):
    """Muestra los datos de una película y, si corresponde, su justificación."""
    st.subheader(f"{pelicula['titulo']} ({pelicula['anio']})")
    st.caption("Categorías: " + ", ".join(base["categorias"][c] for c in pelicula["categorias"]))
    st.write(pelicula["sinopsis"])
    if coincidencias:
        st.write("Motivo: coincide con " + ", ".join(base["categorias"][c] for c in sorted(coincidencias)) + ".")
    st.divider()


def main():
    # Streamlit vuelve a ejecutar el programa al interactuar con sus controles.
    st.set_page_config(page_title="Recomendador de películas", page_icon="🎬")
    st.title("🎬 Recomendador de películas")
    # El archivo subido tiene prioridad sobre el JSON de la carpeta.
    archivo = st.sidebar.file_uploader("Cargar base de conocimiento", type=["json"])
    try:
        if archivo is not None:
            base = validar_base(json.loads(archivo.getvalue().decode("utf-8-sig")))
        else:
            ruta = Path(__file__).with_name("base_conocimiento.json")
            if not ruta.exists():
                st.info("Sube tu archivo base_conocimiento.json en la barra lateral o colócalo en la misma carpeta que app.py.")
                st.stop()
            base = validar_base(json.loads(ruta.read_text(encoding="utf-8-sig")))
    except (OSError, ValueError, KeyError, TypeError) as error:
        st.error(f"No se pudo cargar la base de conocimiento: {error}")
        st.stop()

    st.header(str(base.get("plataforma", "Catálogo de películas")))
    st.caption(str(base.get("nota_catalogo", "")))
    opcion = st.sidebar.radio("Menú", ["Recomendar películas", "Consultar por categoría", "Ver reglas"])

    if opcion == "Recomendar películas":
        st.subheader("Responde según lo que quieres ver hoy")
        # El formulario reúne todas las respuestas y las envía al pulsar el botón.
        with st.form("preferencias"):
            atributos = {}
            for nombre, pregunta in base["atributos"].items():
                respuesta = st.radio(pregunta, ["Sí", "No"], index=None, key="atributo_" + nombre, horizontal=True)
                atributos[nombre] = None if respuesta is None else respuesta == "Sí"
            enviado = st.form_submit_button("Recomendar películas")
        if enviado:
            if any(valor is None for valor in atributos.values()):
                st.warning("Responde todas las preguntas antes de continuar.")
            else:
                reglas, resultados = recomendar(base, atributos)
                with st.expander("Reglas satisfechas"):
                    for regla in reglas:
                        st.code(ecuacion(regla), language="text")
                    if not reglas:
                        st.info("Ninguna. Puedes explorar el catálogo por categoría.")
                if not resultados:
                    st.info("No hay películas que cumplan estas preferencias y exclusiones.")
                else:
                    st.success(f"Películas recomendadas: {len(resultados)}")
                    for pelicula, coincidencias in resultados:
                        mostrar_pelicula(pelicula, base, coincidencias)

    elif opcion == "Consultar por categoría":
        categoria = st.selectbox("Elige una categoría", list(base["categorias"]), format_func=lambda c: base["categorias"][c])
        peliculas = [p for p in base["peliculas"] if categoria in p["categorias"]]
        st.caption(f"Películas encontradas: {len(peliculas)}")
        for pelicula in peliculas:
            mostrar_pelicula(pelicula, base)
    else:
        st.write("AND = y; OR = o; NOT = no; => = implica.")
        for nombre, pregunta in base["atributos"].items():
            st.write(f"{nombre}: {pregunta}")
        for regla in base["reglas"]:
            st.code(ecuacion(regla), language="text")
        st.info("Las exclusiones también se aplican a películas de varios géneros.")


if __name__ == "__main__":
    main()

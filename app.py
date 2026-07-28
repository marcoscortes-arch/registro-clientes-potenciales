import streamlit as st
import pandas as pd
import urllib.parse

# Configuración de la página
st.set_page_config(
    page_title="W.G.H. Car Shop - Buscador de Accesorios", 
    layout="wide", 
    page_icon="🚗"
)

# Estilo personalizado para el logo W.G.H.
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 1rem;
    }
    .wgh-header {
        font-family: 'Arial Black', Gadget, sans-serif;
        color: #e62117; /* Rojo WGH */
        font-size: 36px;
        text-align: center;
        margin-bottom: 0px;
    }
    .wgh-sub {
        font-family: Arial, Helvetica, sans-serif;
        color: #333;
        font-size: 18px;
        text-align: center;
        margin-top: -10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="wgh-header">W.G.H. Car Shop</div>', unsafe_allow_html=True)
st.markdown('<div class="wgh-sub">Buscador Rápido de Mascarillas y Accesorios</div>', unsafe_allow_html=True)

# 1. Enlace a tu Google Sheet (Publicado como CSV)
SHEET_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSDj39gzuKoA_6SgtWcVs5It-0WSzxGwb5it-9Ja012Al9pw3jpP6Ioxf8VrL66MQ/pub?output=csv"

@st.cache_data(ttl=300)  # Se actualiza automáticamente cada 5 minutos
def cargar_inventario():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = df.columns.str.strip()  # Limpia espacios extra en los nombres de columnas
        
        if "Año Inicial" in df.columns:
            df["Año Inicial"] = pd.to_numeric(df["Año Inicial"], errors='coerce').fillna(1900).astype(int)
        if "Año Final" in df.columns:
            df["Año Final"] = pd.to_numeric(df["Año Final"], errors='coerce').fillna(2100).astype(int)
        
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos de Google Sheets. Verifica el enlace CSV o las nuevas columnas. Error: {e}")
        return pd.DataFrame()

df = cargar_inventario()

# Pestañas principales
tab_campana, tab_inventario = st.tabs(["⚡ Modo Campaña Rápida (4 Campañas)", "🔍 Buscador de Inventario General"])

# ---------------------------------------------------------
# PESTAÑA 1: MODO CAMPAÑA RÁPIDA (TU FLUJO PRINCIPAL DE VENTAS)
# ---------------------------------------------------------
with tab_campana:
    st.markdown("### ⚡ Generador Instantáneo para Campañas")
    
    col_c1, col_c2 = st.columns([1, 1])
    
    with col_c1:
        campana_sel = st.selectbox(
            "1. Selecciona la Campaña:",
            [
                "Mascarilla D-Max (Todos los años)",
                "Mascarillas Ford (Varios modelos)",
                "Protectores de Puerta (Multimarca)",
                "Otras Mascarillas / Accesorios"
            ]
        )
        
        if "D-Max" in campana_sel:
            opciones_sub = ["D-Max 2014 - 2018", "D-Max 2019 - 2021", "D-Max 2022 - 2024", "D-Max Luv / Clásica"]
            precio_def = 175.0
        elif "Ford" in campana_sel:
            opciones_sub = ["Ford Ranger 2013 - 2016", "Ford Ranger 2017 - 2021", "Ford Ranger 2022+", "Ford F-150 / Raptor"]
            precio_def = 185.0
        elif "Protectores" in campana_sel:
            opciones_sub = ["Toyota Hilux", "Chevrolet D-Max", "Ford Ranger", "Nissan Frontier / NP300", "Great Wall Poer / Wingle"]
            precio_def = 120.0
        else:
            opciones_sub = ["Universal / Adaptable", "Modelo Específico"]
            precio_def = 150.0

        sub_sel = st.selectbox("2. Selecciona Modelo / Año / Versión:", opciones_sub)
        
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            precio_prod = st.number_input("Precio Oferta ($):", value=precio_def, step=5.0)
        with col_p2:
            costo_envio = st.number_input("Costo de Envío ($):", value=10.0, step=1.0)
            
        ciudad_cli = st.text_input("Ciudad del Cliente (Opcional):", placeholder="Ej. Cuenca, Quito, Guayaquil")
        incluir_saludo = st.checkbox("Incluir saludo ('Buenos días')", value=True)

    with col_c2:
        st.markdown("### 📲 Mensaje Formateado Listo")
        
        saludo_txt = "Buenos días" if incluir_saludo else ""
        ciudad_txt = f" para **{ciudad_cli.strip().title()}**" if ciudad_cli.strip() else ""
        
        msg_campana = f"{saludo_txt}\n\nEn oferta **${precio_prod:.2f}** más **${costo_envio:.2f}** de envío{ciudad_txt}."
        msg_campana += f"\n¿UD nos paga al recibir su pedido por Servientrega?"

        st.code(msg_campana, language="markdown")
        
        text_encoded = urllib.parse.quote(msg_campana.replace("**", "*"))
        link_wa_campana = f"https://api.whatsapp.com/send?text={text_encoded}"
        
        st.markdown(f"""
        <a href="{link_wa_campana}" target="_blank" style="text-decoration: none;">
            <button style="
                background-color: #25D366;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                width: 100%;
                cursor: pointer;
            ">
                📲 Enviar Texto por WhatsApp
            </button>
        </a>
        """, unsafe_allow_html=True)
        st.caption("💡 Tip: Copia el texto arriba con 1 clic o presiona el botón para abrir WhatsApp.")

# ---------------------------------------------------------
# PESTAÑA 2: BUSCADOR GENERAL DE INVENTARIO (TU CÓDIGO ORIGINAL)
# ---------------------------------------------------------
with tab_inventario:
    if not df.empty:
        st.markdown("### 🔍 Búsqueda Directa")
        busqueda_directa = st.text_input("Busca por SKU, nombre de mascarilla o palabra clave:", "")

        if busqueda_directa.strip():
            mask = df.astype(str).apply(lambda row: row.str.contains(busqueda_directa, case=False, na=False)).any(axis=1)
            df_filtrado = df[mask]
        else:
            st.markdown("### 🚘 Filtrar por Vehículo")
            col1, col2, col3 = st.columns(3)

            with col1:
                marcas = sorted([m for m in df["Marca"].dropna().unique() if str(m).strip()]) if "Marca" in df.columns else []
                marca_sel = st.selectbox("1. Marca", ["Todas"] + marcas)

            df_f1 = df if marca_sel == "Todas" or "Marca" not in df.columns else df[df["Marca"] == marca_sel]

            with col2:
                modelos = sorted([m for m in df_f1["Modelo"].dropna().unique() if str(m).strip()]) if "Modelo" in df_f1.columns else []
                modelo_sel = st.selectbox("2. Modelo", ["Todos"] + modelos)

            df_f2 = df_f1 if modelo_sel == "Todos" or "Modelo" not in df_f1.columns else df_f1[df_f1["Modelo"] == modelo_sel]

            with col3:
                anio_sel = st.number_input("3. Año del Vehículo", min_value=1980, max_value=2030, value=2016)

            if "Año Inicial" in df_f2.columns and "Año Final" in df_f2.columns:
                df_filtrado = df_f2[
                    (df_f2["Año Inicial"] <= anio_sel) & 
                    (df_f2["Año Final"] >= anio_sel)
                ]
            else:
                df_filtrado = df_f2

        st.divider()
        st.subheader(f"📦 Mascarillas Encontradas ({len(df_filtrado)})")

        if df_filtrado.empty:
            st.info("No se encontraron mascarillas compatibles con los criterios seleccionados.")
        else:
            for _, row in df_filtrado.iterrows():
                with st.container():
                    producto_nombre = row.get("Producto / Descripción", row.get("Producto", "Mascarilla"))
                    anio_in = row.get('Año Inicial', '')
                    anio_fin = row.get('Año Final', '')
                    st.markdown(f"#### {producto_nombre} ({anio_in}-{anio_fin})")

                    col_img1, col_img2, col_img3 = st.columns(3)
                    
                    with col_img1:
                        url_img1 = str(row.get("URL Imagen 1 (Principal)", "")).strip()
                        if url_img1 and url_img1.startswith("http"):
                            st.image(url_img1, caption="Principal", use_container_width=True)
                        else:
                            st.caption("📷 Sin Imagen 1")

                    with col_img2:
                        url_img2 = str(row.get("URL Imagen 2 (Exhibición)", "")).strip()
                        if url_img2 and url_img2.startswith("http"):
                            st.image(url_img2, caption="Exhibición", use_container_width=True)
                        else:
                            st.caption("📷 Sin Imagen 2")

                    with col_img3:
                        url_img3 = str(row.get("URL Imagen 3 (Instalada)", "")).strip()
                        if url_img3 and url_img3.startswith("http"):
                            st.image(url_img3, caption="Instalada", use_container_width=True)
                        else:
                            st.caption("📷 Sin Imagen 3")

                    col_info_detalles, col_action_wa = st.columns([3, 1])

                    with col_info_detalles:
                        st.write(f"🚗 **Compatibilidad:** {row.get('Marca', '')} {row.get('Modelo', '')}")
                        st.write(f"🏷️ **SKU:** {row.get('SKU / Código', 'N/A')} | 💵 **Precio:** ${row.get('Precio ($)', row.get('Precio', '0.00'))}")
                        if pd.notna(row.get("Ubicación Almacén")):
                            st.caption(f"📍 Ubicación: {row['Ubicación Almacén']}")

                    with col_action_wa:
                        texto_msj = (
                            f"¡Hola! 👋 Le comparto las imágenes de la *{producto_nombre}* para tu {row.get('Marca', '')} {row.get('Modelo', '')} que me consulto:\n\n"
                            f"💰 *Precio:* ${row.get('Precio ($)', row.get('Precio', '0.00'))}\n"
                            f"🔢 *Código/SKU:* {row.get('SKU / Código', 'N/A')}\n\n"
                            f"Aquí puedes ver cómo es y cómo queda:\n"
                        )
                        
                        if url_img1 and url_img1.startswith("http"):
                            texto_msj += f"1️⃣ *Producto:* {url_img1}\n"
                        if url_img2 and url_img2.startswith("http"):
                            texto_msj += f"2️⃣ *Exhibición:* {url_img2}\n"
                        if url_img3 and url_img3.startswith("http"):
                            texto_msj += f"3️⃣ *Instalada:* {url_img3}\n"
                        
                        texto_msj += "\n¿Te gustaría coordinar el envío o la instalación? Quedo atento. 🚗💨"

                        texto_encoded = urllib.parse.quote(texto_msj)
                        link_wa = f"https://api.whatsapp.com/send?text={texto_encoded}"

                        st.markdown(f"""
                        <a href="{link_wa}" target="_blank" style="text-decoration: none;">
                            <button style="
                                background-color: #e62117;
                                color: white;
                                border: none;
                                padding: 12px 24px;
                                border-radius: 8px;
                                font-size: 16px;
                                font-weight: bold;
                                width: 100%;
                                cursor: pointer;
                            ">
                                📲 Enviar 3 Fotos por WhatsApp
                            </button>
                        </a>
                        """, unsafe_allow_html=True)
                    
                    st.divider()

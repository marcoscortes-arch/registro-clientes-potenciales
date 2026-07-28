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
        
        # Asegurar tipos de datos numéricos para filtrado por año
        df["Año Inicial"] = pd.to_numeric(df["Año Inicial"], errors='coerce').fillna(1900).astype(int)
        df["Año Final"] = pd.to_numeric(df["Año Final"], errors='coerce').fillna(2100).astype(int)
        
        return df
    except Exception as e:
        st.error(f"Error al conectar con la base de datos de Google Sheets. Verifica el enlace CSV o las nuevas columnas. Error: {e}")
        return pd.DataFrame()

df = cargar_inventario()

if not df.empty:
    # 2. Buscador Directo por Palabra Clave
    st.markdown("### 🔍 Búsqueda Directa")
    busqueda_directa = st.text_input("Busca por SKU, nombre de mascarilla o palabra clave:", "")

    if busqueda_directa.strip():
        # Filtra si la palabra aparece en cualquier columna
        mask = df.astype(str).apply(lambda row: row.str.contains(busqueda_directa, case=False, na=False)).any(axis=1)
        df_filtrado = df[mask]
    else:
        # 3. Filtros en Cascada por Vehículo
        st.markdown("### 🚘 Filtrar por Vehículo")
        col1, col2, col3 = st.columns(3)

        with col1:
            marcas = sorted([m for m in df["Marca"].dropna().unique() if str(m).strip()])
            marca_sel = st.selectbox("1. Marca", ["Todas"] + marcas)

        df_f1 = df if marca_sel == "Todas" else df[df["Marca"] == marca_sel]

        with col2:
            modelos = sorted([m for m in df_f1["Modelo"].dropna().unique() if str(m).strip()])
            modelo_sel = st.selectbox("2. Modelo", ["Todos"] + modelos)

        df_f2 = df_f1 if modelo_sel == "Todos" else df_f1[df_f1["Modelo"] == modelo_sel]

        with col3:
            anio_sel = st.number_input("3. Año del Vehículo", min_value=1980, max_value=2030, value=2016)

        # Filtrar si el año seleccionado está dentro del rango
        df_filtrado = df_f2[
            (df_f2["Año Inicial"] <= anio_sel) & 
            (df_f2["Año Final"] >= anio_sel)
        ]

    # 4. Despliegue de Resultados
    st.divider()
    st.subheader(f"📦 Mascarillas Encontradas ({len(df_filtrado)})")

    if df_filtrado.empty:
        st.info("No se encontraron mascarillas compatibles con los criterios seleccionados.")
    else:
        for _, row in df_filtrado.iterrows():
            with st.container():
                producto_nombre = row.get("Producto / Descripción", row.get("Producto", "Mascarilla D-Max"))
                st.markdown(f"#### {producto_nombre} ({row['Año Inicial']}-{row['Año Final']})")

                # Fila para las 3 imágenes
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

                # Fila inferior para información y botón
                col_info_detalles, col_action_wa = st.columns([3, 1])

                with col_info_detalles:
                    st.write(f"🚗 **Compatibilidad:** {row['Marca']} {row['Modelo']}")
                    st.write(f"🏷️ **SKU:** {row.get('SKU / Código', 'N/A')} | 💵 **Precio:** ${row.get('Precio ($)', row.get('Precio', '0.00'))}")
                    if pd.notna(row.get("Ubicación Almacén")):
                        st.caption(f"📍 Ubicación: {row['Ubicación Almacén']}")

                with col_action_wa:
                    texto_msj = (
                        f"¡Hola! 👋 Te comparto las imágenes de la *{producto_nombre}* para tu {row['Marca']} {row['Modelo']} que me consultaste:\n\n"
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

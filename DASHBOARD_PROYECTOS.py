import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob
import plotly.express as px
import plotly.graph_objects as go

# ==========================================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================================

st.set_page_config(
    page_title="Proyectos DI",
    page_icon="📊",
    layout="wide"
)
# ==========================================================
# AJUSTE DEL ESPACIO SUPERIOR
# ==========================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 1rem;
        }
    </style>
    """,
    unsafe_allow_html=True
)


# ==========================================================
# ENCABEZADO
# ==========================================================

st.title("Inventario de Proyectos · Digital Innovation")


# ==========================================================
# EXCEL
# ==========================================================

df = pd.read_excel("BITACORA.xlsx")

# ==========================================================
# FILTROS
# ==========================================================

# ----------------------------------------------------------
# FUNCIÓN PARA LIMPIAR FILTROS
# ----------------------------------------------------------

def limpiar_filtros():
    st.session_state["filtro_año"] = "Todos"
    st.session_state["filtro_empresa"] = "Todas"
    st.session_state["filtro_solucion"] = "Todas"
    st.session_state["filtro_tipo"] = "Todos"
    st.session_state["filtro_responsable"] = "Todos"


# ----------------------------------------------------------
# TÍTULO DE FILTROS + BOTÓN LIMPIAR
# ----------------------------------------------------------

titulo_filtros, boton_limpiar = st.columns([6, 1])

with titulo_filtros:
    st.markdown(
        "<h3 style='margin-bottom:10px;'>Filtros</h3>",
        unsafe_allow_html=True
    )

with boton_limpiar:
    st.button(
        "↻ Limpiar",
        on_click=limpiar_filtros,
        use_container_width=True
    )


# ----------------------------------------------------------
# COLUMNAS DE FILTROS
# ----------------------------------------------------------

f1, f2, f3, f4, f5 = st.columns(5)



# ----------------------------------------------------------
# AÑO
# ----------------------------------------------------------

with f1:

    años = sorted(
        df["AÑO"]
        .dropna()
        .unique()
    )

    año_seleccionado = st.selectbox(
        "Año",
        options=["Todos"] + list(años),
        key="filtro_año"
    )


# ----------------------------------------------------------
# EMPRESA
# ----------------------------------------------------------

with f2:

    empresas = sorted(
        df["EMPRESA"]
        .dropna()
        .astype(str)
        .unique()
    )

    empresa_seleccionada = st.selectbox(
        "Empresa",
        options=["Todas"] + empresas,
        key="filtro_empresa"
    )


# ----------------------------------------------------------
# SOLUCIÓN
# ----------------------------------------------------------

with f3:

    soluciones = sorted(
        df["SOLUCION"]
        .dropna()
        .astype(str)
        .unique()
    )

    solucion_seleccionada = st.selectbox(
        "Solución",
        options=["Todas"] + soluciones,
        key="filtro_solucion"
    )


# ----------------------------------------------------------
# TIPO
# ----------------------------------------------------------

with f4:

    tipos = sorted(
        df["TIPO"]
        .dropna()
        .astype(str)
        .unique()
    )

    tipo_seleccionado = st.selectbox(
        "Tipo",
        options=["Todos"] + tipos,
        key="filtro_tipo"
    )


# ----------------------------------------------------------
# RESPONSABLE TIC
# ----------------------------------------------------------

with f5:

    responsables = sorted(
        df["RESPONSABLE - TIC"]
        .dropna()
        .astype(str)
        .unique()
    )

    responsable_seleccionado = st.selectbox(
        "Responsable TIC",
        options=["Todos"] + responsables,
        key="filtro_responsable"
    )


# ==========================================================
# APLICAR FILTROS
# ==========================================================

df_filtrado = df.copy()

if año_seleccionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["AÑO"] == año_seleccionado
    ]

if empresa_seleccionada != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["EMPRESA"].astype(str) == empresa_seleccionada
    ]

if solucion_seleccionada != "Todas":
    df_filtrado = df_filtrado[
        df_filtrado["SOLUCION"].astype(str) == solucion_seleccionada
    ]

if tipo_seleccionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["TIPO"].astype(str) == tipo_seleccionado
    ]

if responsable_seleccionado != "Todos":
    df_filtrado = df_filtrado[
        df_filtrado["RESPONSABLE - TIC"].astype(str) == responsable_seleccionado
    ]


df = df_filtrado


# ==========================================================
# CONTADOR
# ==========================================================

st.markdown(
    f"""
    <div style="
        color:#666666;
        font-size:16px;
        margin-top:8px;
        margin-bottom:18px;
    ">
        Mostrando <b>{len(df_filtrado)}</b> de <b>{len(df)}</b> proyectos
    </div>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# ESTILO DE INDICADORES
# ==========================================================

st.html("""
<style>

.metric-container {
    display: flex;
    gap: 20px;
    width: 100%;
    margin-bottom: 25px;
}

.metric-card {
    flex: 1;
    background: white;
    border: 1px solid #E0E0E0;
    border-radius: 18px;
    padding: 24px 28px;
    min-height: 150px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
}

.metric-title {
    font-size: 18px;
    color: #555555;
    margin-bottom: 10px;
}

.metric-value {
    font-size: 42px;
    font-weight: 600;
    color: #111111;
    line-height: 1.1;
}

.metric-subtitle {
    font-size: 16px;
    color: #666666;
    margin-top: 10px;
}

</style>
""")


# ==========================================================
# CÁLCULO DE INDICADORES
# ==========================================================

# 1. TOTAL DE PROYECTOS
total_proyectos = len(df)


# 2. CUMPLIMIENTO DOCUMENTAL PROMEDIO

cumplimiento = pd.to_numeric(
    df["CUMPLIMIENTO%"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace(",", ".", regex=False),
    errors="coerce"
)

cumplimiento_porcentaje = cumplimiento * 100

cumplimiento_promedio = cumplimiento_porcentaje.mean()


# 3. DOCUMENTACIÓN COMPLETA
# Proyectos con 100% de cumplimiento

proyectos_completos = (
    cumplimiento >= 1
).sum()

porcentaje_completos = (
    proyectos_completos / total_proyectos * 100
    if total_proyectos > 0
    else 0
)


# 4. DURACIÓN PROMEDIO
# Solo considera valores numéricos

duracion = pd.to_numeric(
    df["DURACION (MES)"],
    errors="coerce"
)

duracion_promedio = duracion.mean()


# ==========================================================
# MOSTRAR LOS 4 INDICADORES
# ==========================================================

st.html(f"""
<div class="metric-container">

    <!-- INDICADOR 1 -->
    <div class="metric-card">
        <div class="metric-title">
            Proyectos
        </div>

        <div class="metric-value">
            {total_proyectos}
        </div>

        <div class="metric-subtitle">
            en la selección actual
        </div>
    </div>


    <!-- INDICADOR 2 -->
    <div class="metric-card">
        <div class="metric-title">
            Cumplimiento documental
        </div>

        <div class="metric-value">
            {cumplimiento_promedio:.0f}%
        </div>

        <div class="metric-subtitle">
            proyectos con documentos obligatorios
        </div>
    </div>


    <!-- INDICADOR 3 -->
    <div class="metric-card">
        <div class="metric-title">
            Documentación completa
        </div>

        <div class="metric-value">
            {proyectos_completos}
        </div>

        <div class="metric-subtitle">
            {porcentaje_completos:.0f}% del total
        </div>
    </div>


    <!-- INDICADOR 4 -->
    <div class="metric-card">
        <div class="metric-title">
            Duración promedio
        </div>

        <div class="metric-value">
            {duracion_promedio:.1f}
        </div>

        <div class="metric-subtitle">
            meses por proyecto
        </div>
    </div>

</div>
""")



# ==========================================================
# DOCUMENTOS A EVALUAR
# ==========================================================

documentos = [
    "1. BUSINESS CASE",
    "2. PLAN DE TRABAJO",
    "3. KICKOFF",
    "4. INFORME DE CIERRE",
    "5. ACTA DE CIERRE",
    "6. MANUAL TECNICO"
]

# ==========================================================
# CALCULAR % DE CUMPLIMIENTO
# ==========================================================

def calcular_cumplimiento(row):

    completados = 0

    for documento in documentos:

        valor = str(row[documento]).strip().upper()

        if valor in ["SI", "SÍ"]:
            completados += 1

    # Siempre sobre 6 documentos
    return (completados / 6) * 100


df["CUMPLIMIENTO"] = df.apply(
    calcular_cumplimiento,
    axis=1
)


# ==========================================================
# GRÁFICAS RESUMEN
# ==========================================================

col_grafico1, separador, col_grafico2 = st.columns([1, 0.1, 1])

# ==========================================================
# GRÁFICA 1: PROYECTOS POR ESTADO
# ==========================================================

with col_grafico1:

    st.subheader("Proyectos por estado")
    st.caption("Distribución del estado actual")

    # Contar proyectos por estado
    estados = df["ESTADO"].value_counts()

    # Colores según estado
    colores_estado = {
        "CERRADO": "#141B18",
        "EN CURSO": "#67C941",
        "PLANIFICADO": "#11AAA8",
        "IDENTIFICADO": "#E5A12A",
        "POSTERGADO": "#8A55D7",
        "ANULADO": "#E60012",
        "PARALIZADO": "#E60012",
        "SIN ESTADO": "#777777"
    }

    colores = [
        colores_estado.get(estado, "#777777")
        for estado in estados.index
    ]

    # Crear gráfico
    fig1, ax1 = plt.subplots(figsize=(7, 5))

    ax1.pie(
        estados.values,
        colors=colores,
        startangle=90,
        wedgeprops=dict(width=0.35, edgecolor="white")
    )

    ax1.set_aspect("equal")

    # Leyenda con cantidad y porcentaje
    total = estados.sum()

    etiquetas = []

    for estado, cantidad in estados.items():

        porcentaje = cantidad / total * 100

        etiquetas.append(
            f"{estado}     {cantidad} ({porcentaje:.0f}%)"
        )

    ax1.legend(
        etiquetas,
        loc="center left",
        bbox_to_anchor=(1.0, 0.5),
        frameon=False,
        fontsize=10
    )

    plt.tight_layout()

    st.pyplot(fig1, use_container_width=True)

    plt.close(fig1)

# ==========================================================
# SEPARADOR
# ==========================================================

with separador:

    st.markdown(
        """
        <div style="
            border-left: 1px solid #DDDDDD;
            height: 500px;
            margin: auto;
        "></div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# GRÁFICA 2: CUMPLIMIENTO POR DOCUMENTO
# ==========================================================

with col_grafico2:

    st.markdown(
        "<h3 style='margin-bottom:0;'>Cumplimiento por documento</h3>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='color:#777; margin-top:4px;'>"
        "% de proyectos que cuentan con cada entregable"
        "</p>",
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # ORDEN DE LA DOCUMENTACIÓN
    # ------------------------------------------------------

    orden_documentos = [
        "Business Case",
        "Plan de Trabajo",
        "Kickoff",
        "Informe de Cierre",
        "Acta de Cierre",
        "Manual Técnico"
    ]

    # ------------------------------------------------------
    # CALCULAR DATOS
    # ------------------------------------------------------

    datos_cumplimiento = []

    for documento in documentos:

        valores = (
            df[documento]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        si = valores.isin(["SI", "SÍ"]).sum()
        no = (valores == "NO").sum()
        na = len(valores) - si - no

        porcentaje = (si / len(valores)) * 100

        nombre_documento = (
            documento
            .replace("1. ", "")
            .replace("2. ", "")
            .replace("3. ", "")
            .replace("4. ", "")
            .replace("5. ", "")
            .replace("6. ", "")
        )

        datos_cumplimiento.append({
            "DOCUMENTO": nombre_documento,
            "PORCENTAJE": porcentaje,
            "SI": si,
            "NO": no,
            "NA": na
        })

    cumplimiento_documentos = pd.DataFrame(
        datos_cumplimiento
    )

    # ------------------------------------------------------
    # GRÁFICA
    # ------------------------------------------------------

    fig_documentos = go.Figure()

    # ------------------------------------------------------
    # BARRA DE FONDO = 100%
    # ------------------------------------------------------

    fig_documentos.add_trace(
        go.Bar(
            y=cumplimiento_documentos["DOCUMENTO"],
            x=[100] * len(cumplimiento_documentos),
            orientation="h",
            marker_color="#EDEDED",
            hoverinfo="skip",
            showlegend=False
        )
    )

    # ------------------------------------------------------
    # BARRA DE CUMPLIMIENTO
    # ------------------------------------------------------

    fig_documentos.add_trace(
        go.Bar(
            y=cumplimiento_documentos["DOCUMENTO"],
            x=cumplimiento_documentos["PORCENTAJE"],
            orientation="h",
            marker_color="#E90012",

            text=cumplimiento_documentos["PORCENTAJE"],
            texttemplate="%{text:.0f}%",
            textposition="outside",

            customdata=cumplimiento_documentos[
                ["SI", "NO", "NA"]
            ].values,

            hovertemplate=(
                "<b>%{y}</b><br>"
                "<b>%{x:.0f}% cumplimiento</b><br>"
                "Sí: %{customdata[0]} · "
                "No: %{customdata[1]} · "
                "N/A: %{customdata[2]}"
                "<extra></extra>"
            ),

            showlegend=False
        )
    )

    # ------------------------------------------------------
    # CONFIGURACIÓN
    # ------------------------------------------------------

    fig_documentos.update_layout(

    barmode="overlay",

    height=350,

    margin=dict(
        l=10,
        r=60,
        t=10,
        b=10
    ),

    xaxis=dict(
        range=[0, 110],
        showgrid=False,
        visible=False
    ),

    yaxis=dict(
        showgrid=False,
        title=None,

        # ORDEN DE LAS BARRAS
        categoryorder="array",
        categoryarray=[
            "Business Case",
           "Plan de Trabajo",
           "Kickoff",
           "Informe de Cierre",
           "Acta de Cierre",
           "Manual Técnico"
        ],
        autorange="reversed"
    ),

    showlegend=False
   )

    st.plotly_chart(
        fig_documentos,
        width="stretch",
        config={"displayModeBar": False}
    )


st.divider()

# ==========================================================
# GRÁFICAS 3 Y 4
# PROYECTOS POR RESPONSABLE TIC Y POR EMPRESA
# ==========================================================

col_grafico3, separador, col_grafico4 = st.columns([1, 0.1, 1])

# ==========================================================
# GRÁFICA 3: PROYECTOS POR RESPONSABLE TIC
# ==========================================================

with col_grafico3:

    st.markdown(
        "<h3 style='margin-bottom:0;'>Proyectos por responsable</h3>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='color:#777; margin-top:4px;'>"
        "Proyectos por responsable TIC, por solución"
        "</p>",
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # CONFIGURACIÓN DE SOLUCIONES
    # ------------------------------------------------------

    soluciones = [
        "AUTOMATIZACION",
        "DIGITALIZACION",
        "NORMATIVA",
        "IA"
    ]

    colores_solucion = {
        "AUTOMATIZACION": "#4569C8",
        "DIGITALIZACION": "#10A9A6",
        "NORMATIVA": "#FF3333",
        "IA": "#FF9999"
    }

    # ------------------------------------------------------
    # LIMPIAR DATOS
    # ------------------------------------------------------

    datos = df[
        ["RESPONSABLE - TIC", "SOLUCION"]
    ].copy()

    datos = datos.dropna(
        subset=["RESPONSABLE - TIC"]
    )

    datos["RESPONSABLE - TIC"] = (
        datos["RESPONSABLE - TIC"]
        .astype(str)
        .str.strip()
    )

    datos["SOLUCION"] = (
        datos["SOLUCION"]
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # ------------------------------------------------------
    # TABLA DE CANTIDADES
    # ------------------------------------------------------

    tabla_soluciones = (
        datos
        .groupby(
            ["RESPONSABLE - TIC", "SOLUCION"]
        )
        .size()
        .unstack(fill_value=0)
    )

    # Asegurar que existan las 4 soluciones
    for solucion in soluciones:
        if solucion not in tabla_soluciones.columns:
            tabla_soluciones[solucion] = 0

    tabla_soluciones = tabla_soluciones[
        soluciones
    ]

    # ------------------------------------------------------
    # ORDENAR RESPONSABLES POR TOTAL
    # ------------------------------------------------------

    tabla_soluciones["TOTAL"] = (
        tabla_soluciones.sum(axis=1)
    )

    tabla_soluciones = (
        tabla_soluciones
        .sort_values(
            "TOTAL",
            ascending=False
        )
    )

    responsables = tabla_soluciones.index.tolist()

    # ------------------------------------------------------
    # GRÁFICA
    # ------------------------------------------------------

    fig_responsable = go.Figure()

    # ------------------------------------------------------
    # BARRAS APILADAS
    # ------------------------------------------------------

    for solucion in soluciones:

        valores = tabla_soluciones[
            solucion
        ].values

        # --------------------------------------------------
        # INFORMACIÓN COMPLETA DEL TOOLTIP
        # --------------------------------------------------

        customdata = []

        for responsable in responsables:

            auto = tabla_soluciones.loc[
                responsable, "AUTOMATIZACION"
            ]

            digi = tabla_soluciones.loc[
                responsable, "DIGITALIZACION"
            ]

            norma = tabla_soluciones.loc[
                responsable, "NORMATIVA"
            ]

            ia = tabla_soluciones.loc[
                responsable, "IA"
            ]

            customdata.append([
                auto,
                digi,
                norma,
                ia
            ])

        # --------------------------------------------------
        # BARRA
        # --------------------------------------------------

        fig_responsable.add_trace(
            go.Bar(
                x=responsables,
                y=valores,

                name=solucion,

                marker_color=colores_solucion[
                    solucion
                ],

                # IMPORTANTE:
                # No mostrar números dentro
                text=None,

                customdata=customdata,

                hovertemplate=(
                    "<b>%{x}</b><br><br>"

                    "<span style='color:#4569C8'>"
                    "■</span> "
                    "AUTOMATIZACION: "
                    "<b>%{customdata[0]}</b><br>"

                    "<span style='color:#10A9A6'>"
                    "■</span> "
                    "DIGITALIZACION: "
                    "<b>%{customdata[1]}</b><br>"

                    "<span style='color:#FF3333'>"
                    "■</span> "
                    "NORMATIVA: "
                    "<b>%{customdata[2]}</b><br>"

                    "<span style='color:#FF9999'>"
                    "■</span> "
                    "IA: "
                    "<b>%{customdata[3]}</b>"

                    "<extra></extra>"
                )
            )
        )

    # ------------------------------------------------------
    # TOTALES ENCIMA DE LAS BARRAS
    # ------------------------------------------------------

    fig_responsable.add_trace(
        go.Scatter(
            x=responsables,

            y=tabla_soluciones[
                "TOTAL"
            ].values,

            mode="text",

            text=tabla_soluciones[
                "TOTAL"
            ].values,

            textposition="top center",

            textfont=dict(
                size=14
            ),

            hoverinfo="skip",

            showlegend=False
        )
    )

    # ------------------------------------------------------
    # CONFIGURACIÓN
    # ------------------------------------------------------

    fig_responsable.update_layout(

        barmode="stack",

        height=400,

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=80
        ),

        xaxis=dict(
            showgrid=False,
            title=None,
            tickangle=-15
        ),

        yaxis=dict(
            showgrid=False,
            title=None
        ),

        legend=dict(
            title="Solución:",
            orientation="h",
            yanchor="top",
            y=-0.20,
            xanchor="left",
            x=0
        ),

        hoverlabel=dict(
            bgcolor="white",
            font_size=13,
            font_color="#555",
            bordercolor="#D9D9D9"
        )
    )

    # ------------------------------------------------------
    # MOSTRAR GRÁFICA
    # ------------------------------------------------------

    st.plotly_chart(
        fig_responsable,
        width="stretch",
        config={
            "displayModeBar": False
        }
    )

# ==========================================================
# SEPARADOR
# ==========================================================

with separador:

    st.markdown(
        """
        <div style="
            border-left: 1px solid #DDDDDD;
            height: 500px;
            margin: auto;
        "></div>
        """,
        unsafe_allow_html=True
    )


# ==========================================================
# GRÁFICA 4: PROYECTOS POR EMPRESA
# ==========================================================

with col_grafico4:

    st.markdown(
        "<h3 style='margin-bottom:0;'>Proyectos por empresa</h3>",
        unsafe_allow_html=True
    )

    st.markdown(
        "<p style='color:#777; margin-top:4px;'>"
        "Proyectos por empresa, por tipo"
        "</p>",
        unsafe_allow_html=True
    )

    # ------------------------------------------------------
    # DATOS
    # ------------------------------------------------------

    datos_empresa = (
        df.groupby(
            ["EMPRESA", "TIPO"]
        )
        .size()
        .reset_index(name="CANTIDAD")
    )

    # Eliminar empresas vacías
    datos_empresa = datos_empresa[
        datos_empresa["EMPRESA"].notna()
        & (datos_empresa["EMPRESA"].astype(str).str.strip() != "")
    ]

    # ------------------------------------------------------
    # TIPOS Y COLORES
    # ------------------------------------------------------

    tipos = [
        "DATA ANALYTICS",
        "MEJORA",
        "PILOTO",
        "PROYECTO",
        "REQUERIMIENTO"
    ]

    colores_tipo = {
        "DATA ANALYTICS": "#4569C8",
        "MEJORA": "#10A9A6",
        "PILOTO": "#E9A32A",
        "PROYECTO": "#8753D1",
        "REQUERIMIENTO": "#EA5360"
    }

    # ------------------------------------------------------
    # TABLA PIVOT
    # ------------------------------------------------------

    pivot_empresa = (
        datos_empresa
        .pivot_table(
            index="EMPRESA",
            columns="TIPO",
            values="CANTIDAD",
            aggfunc="sum",
            fill_value=0
        )
    )

    # Asegurar que existan las 5 categorías
    for tipo in tipos:
        if tipo not in pivot_empresa.columns:
            pivot_empresa[tipo] = 0

    pivot_empresa = pivot_empresa[tipos]

    # ------------------------------------------------------
    # TOTAL POR EMPRESA
    # ------------------------------------------------------

    pivot_empresa["TOTAL"] = pivot_empresa.sum(axis=1)

    # Ordenar de mayor a menor
    pivot_empresa = pivot_empresa.sort_values(
        "TOTAL",
        ascending=False
    )

    empresas = pivot_empresa.index.tolist()

    # ------------------------------------------------------
    # GRÁFICA
    # ------------------------------------------------------

    fig_empresa = go.Figure()

    for tipo in tipos:

        # Datos del tipo actual
        valores = pivot_empresa[tipo].values

        # --------------------------------------------------
        # CUSTOMDATA
        # Información completa de la empresa
        # --------------------------------------------------

        customdata = []

        for empresa in empresas:

            customdata.append([
                pivot_empresa.loc[empresa, "DATA ANALYTICS"],
                pivot_empresa.loc[empresa, "MEJORA"],
                pivot_empresa.loc[empresa, "PILOTO"],
                pivot_empresa.loc[empresa, "PROYECTO"],
                pivot_empresa.loc[empresa, "REQUERIMIENTO"]
            ])

        # --------------------------------------------------
        # TRACE
        # --------------------------------------------------

        fig_empresa.add_trace(
            go.Bar(
                x=empresas,
                y=valores,
                name=tipo,

                marker_color=colores_tipo[tipo],

                # NO mostrar números dentro
                text=None,

                customdata=customdata,

                hovertemplate=(
                    "<b>%{x}</b><br><br>"

                    "<span style='color:#4569C8'>■</span> "
                    "DATA ANALYTICS: %{customdata[0]}<br>"

                    "<span style='color:#10A9A6'>■</span> "
                    "MEJORA: %{customdata[1]}<br>"

                    "<span style='color:#E9A32A'>■</span> "
                    "PILOTO: %{customdata[2]}<br>"

                    "<span style='color:#8753D1'>■</span> "
                    "PROYECTO: %{customdata[3]}<br>"

                    "<span style='color:#EA5360'>■</span> "
                    "REQUERIMIENTO: %{customdata[4]}"

                    "<extra></extra>"
                )
            )
        )

    # ------------------------------------------------------
    # TOTALES ENCIMA DE LAS BARRAS
    # ------------------------------------------------------

    fig_empresa.add_trace(
        go.Scatter(
            x=empresas,
            y=pivot_empresa["TOTAL"].values,

            mode="text",

            text=pivot_empresa["TOTAL"].values,

            textposition="top center",

            textfont=dict(
                size=14
            ),

            hoverinfo="skip",

            showlegend=False
        )
    )

    # ------------------------------------------------------
    # CONFIGURACIÓN
    # ------------------------------------------------------

    fig_empresa.update_layout(

        barmode="stack",

        height=400,

        margin=dict(
            l=10,
            r=10,
            t=10,
            b=70
        ),

        xaxis=dict(
            showgrid=False,
            title=None,
            tickangle=-15
        ),

        yaxis=dict(
            showgrid=False,
            title=None
        ),

        legend=dict(
            title="Tipo:",
            orientation="h",
            yanchor="top",
            y=-0.20,
            xanchor="left",
            x=0
        ),

        hoverlabel=dict(
            bgcolor="white",
            font_size=14
        )
    )

    st.plotly_chart(
        fig_empresa,
        width="stretch",
        config={"displayModeBar": False}
    )

st.divider()

# ==========================================================
# TABLA DE PROYECTOS
# ==========================================================

# ==========================================================
# CONVERTIR SI / NO EN ✓ / ✕
# ==========================================================

def icono_documento(valor):

    valor = str(valor).strip().upper()

    if valor in ["SI", "SÍ"]:
        return "✅"

    elif valor == "NO":
        return "❌"

    else:
        return "-"


# Aplicar iconos directamente al DataFrame
for documento in documentos:

    df[documento] = df[documento].apply(
        icono_documento
    )

# ==========================================================
# FORMATO DEL ESTADO
# ==========================================================

def mostrar_estado(estado):

    estado = str(estado).strip().upper()

    if estado == "IMPLEMENTADO":
        return "IMPLEMENTADO"

    elif estado == "EN CURSO":
        return "EN CURSO"

    elif estado == "ANULADO":
        return "ANULADO"

    elif estado == "PARALIZADO":
        return "PARALIZADO"

    elif estado == "IDENTIFICADO":
        return "IDENTIFICADO"

    else:
        return estado


def colorear_estado(valor):

    if valor == "CERRADO":
        return "color: #222222; font-weight: bold;"

    elif valor == "EN CURSO":
        return "color: #008000; font-weight: bold;"

    elif valor in ["ANULADO", "PARALIZADO", "POSTERGADO"]:
        return "color: #FF0000; font-weight: bold;"

    elif valor == ["IDENTIFICADO","PLANIFICADO"]:
        return "color: #BFBF00; font-weight: bold;"

    return "font-weight: bold;"



# ==========================================================
# CREAR UNA SOLA TABLA
# ==========================================================

tabla = df[
    [
        "CODIGO",
        "PROYECTO",
        "EMPRESA",
        "TIPO",
        "SOLUCION",
        "ESTADO",
        "RESPONSABLE - TIC",

        "1. BUSINESS CASE",
        "2. PLAN DE TRABAJO",
        "3. KICKOFF",
        "4. INFORME DE CIERRE",
        "5. ACTA DE CIERRE",
        "6. MANUAL TECNICO",

        "CUMPLIMIENTO%"
    ]
].copy()

# ==========================================================
# CONVERTIR CUMPLIMIENTO% A PORCENTAJE PARA LA BARRA
# ==========================================================

tabla["CUMPLIMIENTO%"] = pd.to_numeric(
    tabla["CUMPLIMIENTO%"],
    errors="coerce"
).fillna(0) * 100

# ==========================================================
# RENOMBRAR COLUMNAS
# ==========================================================

tabla.columns = [
    "Código",
    "Proyecto",
    "Empresa",
    "Tipo",
    "Plataforma",
    "Estado",
    "Responsable TIC",

    "Business Case",
    "Plan de Trabajo",
    "Kickoff",
    "Informe de Cierre",
    "Acta de Cierre",
    "Manual Técnico",

    "Cumplimiento"
]

# ==========================================================
# BUSCADOR
# ==========================================================
busqueda = st.text_input(
    "🔍 Buscar proyecto",
    placeholder="Buscar por código o proyecto..."
)

if busqueda:
    tabla = tabla[
        tabla["Código"].astype(str).str.contains(busqueda, case=False, na=False) |
        tabla["Proyecto"].astype(str).str.contains(busqueda, case=False, na=False)
    ]


# ==========================================================
# MOSTRAR TABLA
# ==========================================================
tabla_estilizada = tabla.style.map(
    colorear_estado,
    subset=["Estado"]
)

st.dataframe(
    tabla_estilizada,
    column_config={

        # ------------------------------------------
        # INFORMACIÓN DEL PROYECTO
        # ------------------------------------------

        "Código": st.column_config.TextColumn(
            "Código"
        ),

        "Proyecto": st.column_config.TextColumn(
            "Proyecto",
            width="large"
        ),

        "Empresa": st.column_config.TextColumn(
            "Empresa"
        ),

        "Tipo": st.column_config.TextColumn(
            "Tipo"
        ),

        "Plataforma": st.column_config.TextColumn(
            "Plataforma"
        ),

        "Estado": st.column_config.TextColumn(
            "Estado"
        ),

        "Responsable TIC": st.column_config.TextColumn(
            "Responsable TIC"
        ),

        # ------------------------------------------
        # DOCUMENTACIÓN
        # ------------------------------------------

        "Business Case": st.column_config.TextColumn(
            "Business Case"
        ),

        "Plan de Trabajo": st.column_config.TextColumn(
            "Plan de Trabajo"
        ),

        "Kickoff": st.column_config.TextColumn(
            "Kickoff"
        ),

        "Informe de Cierre": st.column_config.TextColumn(
            "Informe de Cierre"
        ),

        "Acta de Cierre": st.column_config.TextColumn(
            "Acta de Cierre"
        ),

        "Manual Técnico": st.column_config.TextColumn(
            "Manual Técnico"
        ),

        # ------------------------------------------
        # CUMPLIMIENTO
        # ------------------------------------------

        "Cumplimiento": st.column_config.ProgressColumn(
            "Cumplimiento",
            help="Porcentaje de documentos completados",
            min_value=0,
            max_value=100,
            format="%.0f%%",
            color = "auto"
        )
    },

    use_container_width=True,
    hide_index=True,
    height=700
)
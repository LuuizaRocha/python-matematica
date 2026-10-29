import streamlit as st
import pandas as pd
import plotly.express as px
import os

# Configuração da página --------------

st.set_page_config(
    page_title="Dashboard Indicador - Afazeres Domésticos",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"

)

# Caminhos --------------

caminho_afazeres_padrao = r"H:\PythonEMatematica\Tabela.xls"

# Carregar Funções --------------

@st.cache_data
def carregar_e_limpar_afazeres(caminho_ou_arquivo):
    if isinstance(caminho_ou_arquivo, str):
        if caminho_ou_arquivo.lower().endswith(".csv"):
            bruto = pd.read_csv(caminho_ou_arquivo, header=None)
        else:
            bruto = pd.read_excel(caminho_ou_arquivo, engine="xlrd", header=None)
    else:
        nome = caminho_ou_arquivo.name.lower()
        if nome.endswith(".csv"):
            bruto = pd.read_csv(caminho_ou_arquivo, header=None)
        elif nome.endswith(".xls"):
            bruto = pd.read_excel(caminho_ou_arquivo, engine="xlrd", header=None)
        else:
            bruto = pd.read_excel(caminho_ou_arquivo, header=None)

    df = bruto.iloc[8:41].copy()

    df.columns = [
        "uf_regiao",
        "total",
        "total_branca",
        "total_preta_parda",
        "homem_branca",
        "homem_preta_parda",
        "mulher_branca",
        "mulher_preta_parda",
    ]
    df = df.reset_index(drop=True)

    for col in df.columns[1:]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["homens_media"] = ((df["homem_branca"] + df["homem_preta_parda"]) / 2).round(2)
    df["mulheres_media"] = ((df["mulher_branca"] + df["mulher_preta_parda"]) / 2).round(2)
    df["diferenca_genero"] = (df["mulheres_media"] - df["homens_media"]).round(2)

    return df


@st.cache_data
def carregar_e_limpar_formacao(caminho_ou_arquivo):
    if isinstance(caminho_ou_arquivo, str):
        if caminho_ou_arquivo.lower().endswith(".csv"):
            bruto = pd.read_csv(caminho_ou_arquivo, header=None)
        else:
            bruto = pd.read_excel(caminho_ou_arquivo, header=None)
    else:
        nome = caminho_ou_arquivo.name.lower()
        if nome.endswith(".csv"):
            bruto = pd.read_csv(caminho_ou_arquivo, header=None)
        else:
            bruto = pd.read_excel(caminho_ou_arquivo, header=None)

    f_bruto = bruto.iloc[3:36].copy()

    f_total = f_bruto.iloc[:, 0:4].copy()
    f_total.columns = ["uf_regiao", "total", "homens", "mulheres"]

    f_stem = f_bruto.iloc[:, [0, 4, 5, 6]].copy()
    f_stem.columns = ["uf_regiao", "total", "homens", "mulheres"]

    f_saude = f_bruto.iloc[:, [0, 7, 8, 9]].copy()
    f_saude.columns = ["uf_regiao", "total", "homens", "mulheres"]

    for sub_df in [f_total, f_stem, f_saude]:
        for col in ["total", "homens", "mulheres"]:
            sub_df[col] = pd.to_numeric(sub_df[col], errors="coerce")
        sub_df["pct_mulheres"] = ((sub_df["mulheres"] / sub_df["total"]) * 100).round(2)

    df_consolidado = pd.DataFrame({
        "uf_regiao": f_total["uf_regiao"].values,
        "total_graduados": f_total["total"].values,
        "mulheres_total": f_total["mulheres"].values,
        "pct_mulheres_total": f_total["pct_mulheres"].values,
        "stem_total": f_stem["total"].values,
        "pct_mulheres_stem": f_stem["pct_mulheres"].values,
        "saude_total": f_saude["total"].values,
        "pct_mulheres_saude": f_saude["pct_mulheres"].values,
    })

    return df_consolidado


# Barra Lateral --------------

st.sidebar.title("📌 Menu & Filtros")

st.sidebar.subheader("📂 Arquivos de Entrada")

file_afazeres = st.sidebar.file_uploader("Upload Tabela 1.1:", type=["xls", "xlsx", "csv"])

df_afazeres = None

try:
    if file_afazeres is not None:
        df_afazeres = carregar_e_limpar_afazeres(file_afazeres)
    elif os.path.exists(caminho_afazeres_padrao):
        df_afazeres = carregar_e_limpar_afazeres(caminho_afazeres_padrao)
except Exception as e:
    st.sidebar.error(f"Erro ao carregar Tabela 1.1.1: {e}")


# Variáveis Globais --------------

br_afazeres = df_afazeres[df_afazeres["uf_regiao"] == "Brasil"]

media_br = br_afazeres["total"].values[0] if not br_afazeres.empty else 0
homem_br = br_afazeres["homens_media"].values[0] if not br_afazeres.empty else 0
mulher_br = br_afazeres["mulheres_media"].values[0] if not br_afazeres.empty else 0

# Navegação

st.sidebar.markdown("---")
pagina = st.sidebar.radio(
    "Selecione a Visualização:",
    ["🏠 Visão Geral", "📊 Afazeres Domésticos", "📰 Notícias"]
)

REGIOES = ["Brasil", "Norte", "Nordeste", "Sudeste", "Sul", "Centro-Oeste"]

st.sidebar.markdown("---")
tipo_visao = st.sidebar.radio("Filtrar recorte:", ["Apenas Estados (27 UFs)", "Apenas Regiões e Brasil"])

if tipo_visao == "Apenas Estados (27 UFs)":
    df_af_fil = df_afazeres[~df_afazeres["uf_regiao"].isin(REGIOES)].copy()
else:
    df_af_fil = df_afazeres[df_afazeres["uf_regiao"].isin(REGIOES)].copy()
locais_disp = df_af_fil["uf_regiao"].tolist()
locais_sel = st.sidebar.multiselect("Filtrar UFs / Regiões:", locais_disp, default=locais_disp)

if locais_sel:
    df_af_fil = df_af_fil[df_af_fil["uf_regiao"].isin(locais_sel)]

# Página 1 --------------

if pagina == "🏠 Visão Geral":
    st.title("📊 Painel de Análise Social de Afazeres Domésticos - Gênero e Raça")
    st.markdown("Dados lidos do diretório especificado e tratados via **Pandas**.")

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Média Horas Casa (Brasil)", f"{media_br:.1f} h/sem")
    col2.metric("Média Homens", f"{homem_br:.1f} h/sem")
    col3.metric("Média Mulheres", f"{mulher_br:.1f} h/sem", delta=f"+{mulher_br - homem_br:.1f} h")

    st.markdown("---")
    st.subheader("📋 Visualização das Tabelas Tratadas (Pandas)")
    tab1 = st.tabs(["Tabela 1.1(Afazeres Domésticos)"])
    st.dataframe(df_af_fil, use_container_width=True) 

# Afazeres --------------

elif pagina == "📊 Afazeres Domésticos":
    st.title("🧹 Dedicação a Cuidados de Pessoas e Afazeres Domésticos")

    st.subheader("1. Horas Dedicadas por Localidade vs. Média Brasil")
    fig_tot = px.bar(
        df_af_fil.sort_values("total", ascending=True),
        x="total",
        y="uf_regiao",
        orientation="h",
        color="total",
        labels={"total": "Horas / Semana", "uf_regiao": "Localidade"},
        text_auto=".1f",
        color_continuous_scale="Blues"
    )
    if not br_afazeres.empty:
        fig_tot.add_vline(x=media_br, line_dash="dash", line_color="red", annotation_text=f"Média Brasil ({media_br:.1f}h)")
    st.plotly_chart(fig_tot, use_container_width=True)

    st.subheader("2. Comparativo Homens vs. Mulheres")
    df_melt_gen = df_af_fil.melt(
        id_vars=["uf_regiao"],
        value_vars=["homens_media", "mulheres_media"],
        var_name="Gênero",
        value_name="Horas"
    )
    df_melt_gen["Gênero"] = df_melt_gen["Gênero"].map({"homens_media": "Homens", "mulheres_media": "Mulheres"})

    fig_gen = px.bar(
        df_melt_gen,
        x="uf_regiao",
        y="Horas",
        color="Gênero",
        barmode="group",
        labels={"Horas": "Horas / Semana", "uf_regiao": "Localidade"},
        color_discrete_map={"Homens": "#2b5c8f", "Mulheres": "#d95f02"}
    )
    st.plotly_chart(fig_gen, use_container_width=True)

    st.subheader("3. Cruzamento por Sexo e Cor/Raça (Boxplot)")
    df_melt_raca = df_af_fil.melt(
        id_vars=["uf_regiao"],
        value_vars=["homem_branca", "homem_preta_parda", "mulher_branca", "mulher_preta_parda"],
        var_name="Grupo",
        value_name="Horas"
    )
    mapa_raca = {
        "homem_branca": "Homem Branco",
        "homem_preta_parda": "Homem Preto/Pardo",
        "mulher_branca": "Mulher Branca",
        "mulher_preta_parda": "Mulher Preta/Parda"
    }
    df_melt_raca["Grupo"] = df_melt_raca["Grupo"].map(mapa_raca)

    fig_box = px.box(
        df_melt_raca,
        x="Grupo",
        y="Horas",
        color="Grupo",
        points="all",
        title="Distribuição das Horas entre as Localidades Selecionadas"
    )
    st.plotly_chart(fig_box, use_container_width=True)

# Notícias

col1, col2 = st.columns(2)
if pagina == "📰 Notícias":
    with col1:
            st.title("A Carga Mental Feminina")
            st.subheader("Por que as mulheres estão exaustas?")

            st.text("Fazer a lista de compras do mercado, marcar a consulta das crianças – e muitas vezes do marido –, comparecer à reunião na escola, colocar as roupas para lavar, limpar a casa, organizar as contas, cozinhar, trabalhar fora… A lista de cuidados e afazeres é extensa. Poderíamos dizer que esse é um estresse que atinge toda pessoa adulta, mas na verdade, a sobrecarga é quase sempre feminina.  Segundo informações do Instituto Brasileiro de Geografia e Estatística (IBGE), em 2022, as mulheres gastaram 9,6 horas por semana a mais do que os homens com afazeres domésticos ou cuidados com pessoas. São 21,3 horas por semana no caso delas, e somente 11,7 no caso deles. O levantamento revelou ainda que, enquanto 91% das mulheres realizaram alguma atividade relacionada a afazeres domésticos, essa proporção foi de 79% entre os homens. A taxa de realização de afazeres domésticos é maior entre as mulheres negras (92,7%).  Para iniciar essa conversa, primeiro precisamos entender o que é carga mental. “A carga mental vem do conceito da psicologia mesmo. Quando o indivíduo libera uma energia mental para desenvolver algum tipo de trabalho, o tamanho dessa energia liberada – que são os pensamentos, resoluções, planejamento para se fazer o trabalho, preocupação com o trabalho a ser feito –, isso tudo é transformado numa carga”, explica Cíntia Aleixo, psicóloga especializada em saúde mental feminina.")
            st.markdown(''':blue-background[https://drauziovarella.uol.com.br/mulher/carga-mental-feminina-por-que-as-mulheres-estao-exaustas/]''')
            st.image("economia.jpg")

    
    with col2:   
        st.image("sobrecarga.webp")

        st.title("Economia do Cuidado")
        st.subheader("Como podemos visibilizar o trabalho invisível das mulheres na economia do cuidado?")

        st.text("A economia é um conjunto de regras invisíveis que organiza a forma como vivemos. No atual cenário, de pandemia, serviços essenciais de cuidado se tornaram visíveis aos olhos de muitas pessoas. Estamos todos, neste momento, precisando nos dedicar a cuidar da saúde coletiva para salvar milhares de vidas. O trabalho de cuidado envolve muitas horas e tempo dedicado ao cuidado com a casa e com pessoas: dar banho e fazer comida, faxinar a casa, comprar os alimentos que serão consumidos, cuidar das roupas (lavar, estender e guardar), prevenir doenças com boa alimentação e higiene em casa e remediar quando alguém fica ou está doente, fazer café da manhã, almoço, lanches e jantar para os filhos, educar e segue por horas a fio. A economia do cuidado é essencial para a humanidade. Todos nós precisamos de cuidados para existir. E, se hoje você é uma pessoa adulta, é porque alguém já desempenhou horas de trabalho de cuidado com alimentação, vacina, remédios, limpeza e higiene, educação, entre diversas outras funções por horas. E a sociedade, os empregadores que contratam pessoas (veja que óbvio), a gestão pública, as universidades, todas as demais esferas se aproveitam desse trabalho que é gratuito ou mal-remunerado (quando terceirizado).")
        st.markdown(''':blue-background[https://lab.thinkolga.com/economia-do-cuidado/]''')

 
        

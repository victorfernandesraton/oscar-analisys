import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import streamlit as st

st.title("O preço do oscar", anchor="h1")

st.write("""
Um estudo sobre as relações custo x prêmio do oscar nos últimos 40 anos.
Este estudo tem como objetivo uma análise sobre os custos corrigidos 
""")

st.title("Custo por categoria", anchor="h2")
st.write("""
    Análise de evolução de custo por categoria ao longo dos anos

    Os valores financeiros absolutos dos custos são extraidos do OMDB, onde é aplicado uma correção em cima do custo com a inflação atual (supostamente)

    Nesta metodologia eu excluo dos dados aqueles que não consegui obter a informação de custo
""")


nominated_enrriched_df = pd.read_csv("oscar_winners_enriched.csv", sep=";")
categories_df = nominated_enrriched_df["Category"].drop_duplicates()
nominated_enrriched_df = nominated_enrriched_df.rename(columns={"#": "Edition"})

category = st.selectbox(label="Categoria", options=categories_df)

if category in ["Best Foreign Language Film", "Best International Feature Film"]:
    category = ["Best Foreign Language Film", "Best International Feature Film"]
else:
    category = [category]


fig = plt.figure(figsize=(10, 8))


category_str = ", ".join(map(lambda x: f"'{x}'", category))
movie_df = nominated_enrriched_df.query(
    f"Category in [{category_str}] and Cost > 0 and Winner == True"
)
plt.title(f"Evolução do custos dos fimes  vencedores ma(s) categoria(s) {category_str}")
sns.set_theme(style="ticks")
sns.scatterplot(data=movie_df, x="Release", y="Cost")
sns.regplot(
    data=movie_df,
    x="Release",
    y="Cost",
    scatter_kws={"s": 100},
    line_kws={"color": "red"},
)


st.pyplot(fig)

st.markdown("""
**Metodologia:** Os dados de custo foram obtidos do OMDB e corrigidos pela inflação. Filmes sem informação de custo foram excluídos da análise.
""")

movie_df = movie_df.sort_values("Cost", ascending=False)
st.write("Filmes ganhadores")
st.dataframe(movie_df[["Edition", "Movie", "Cost", "Release"]])

movie_whitout_cost_df = nominated_enrriched_df.query(
    f"Category in [{category_str}] and Cost.isnull() and Winner == True"
)

st.write("Filmes sem informação de custo")
st.dataframe(movie_whitout_cost_df[["Edition", "Movie", "Cost", "Release"]])

st.markdown("---")

years = nominated_enrriched_df["Release"].drop_duplicates()

st.title("Relação de prêmios x indicações")

st.write("""
 O objetivo é tentar entender qual a proporção de prêmios ganhos por indicação com base no ano do filme, bem como estabeler um 
 "score" de quantos prêmios ganhou sob indicações de todos os tempos
""")

year = st.selectbox(
    label="Ano", options=map(lambda x: x + 1, years.sort_values(ascending=False))
)

movie_winner_indication_df = nominated_enrriched_df.query(f"Release == {year - 1}")

movie_wins_nominations = (
    movie_winner_indication_df.groupby(["Movie"])["Winner"]
    .agg(["sum", "size"])
    .reset_index()
)
movie_wins_nominations.columns = ["Movie", "Wins", "Nominations"]

criteria = st.selectbox("Critério de ordenação", ["Wins", "Nominations"])

top_5_nominated = movie_wins_nominations.nlargest(5, criteria)
top_5_nominated_melted = pd.melt(
    top_5_nominated,
    id_vars=["Movie"],
    value_vars=["Wins", "Nominations"],
    var_name="Award",
    value_name="Count",
)

fig, ax = plt.subplots(figsize=(10, 6))
sns.barplot(x="Movie", y="Count", hue="Award", data=top_5_nominated_melted, ax=ax)
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)

st.markdown("""
**Metodologia:** O score é calculado como a razão entre o número de prêmios ganhos e o número de indicações.
""")

st.write("Tabela de dados")

movie_wins_nominations["Score"] = (
    movie_wins_nominations["Wins"] / movie_wins_nominations["Nominations"]
).map("{:.2f}".format)

st.dataframe(movie_wins_nominations)

st.title("Relação Custo x Score x Indicações")

movie_wins_nominations = pd.merge(
    movie_wins_nominations,
    nominated_enrriched_df[["Movie", "Cost"]],
    on="Movie",
    how="left",
)

movie_wins_nominations["Score"] = (
    movie_wins_nominations["Wins"] / movie_wins_nominations["Nominations"]
)

fig, ax = plt.subplots(figsize=(10, 6))
sns.scatterplot(
    data=movie_wins_nominations,
    x="Cost",
    y="Score",
    size="Nominations",
    sizes=(20, 500),
    ax=ax,
)
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)

st.markdown("---")

st.title("Distribuição do Score")

fig, ax = plt.subplots(figsize=(10, 6))
sns.histplot(movie_wins_nominations["Score"], kde=True, ax=ax)
st.pyplot(fig)

st.markdown("---")

st.title("Regressão Linear do Score x Custo")

fig, ax = plt.subplots(figsize=(10, 6))
sns.regplot(x="Cost", y="Score", data=movie_wins_nominations, ax=ax)
plt.xticks(rotation=45, ha="right")
st.pyplot(fig)

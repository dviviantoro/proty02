import plotly.express as px

df = px.data.gapminder().query("continent=='Oceania'")
print(df)
fig = px.line(df, x="year", y="lifeExp", color='country')
fig.show()
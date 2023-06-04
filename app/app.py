import streamlit as st
import pandas as pd
import altair as alt


st.title('Gapminder')
st.write("Unlocking Lifetimes: Visualizing Progress in Longevity and Poverty Eradication")


@st.cache_resource
def load_and_preprocess_data():
    gdp = pd.read_csv('/app/files/gdp_pcap.csv')
    lex = pd.read_csv('/app/files/lex.csv')
    pop = pd.read_csv('/app/files/pop.csv')

    lex_filled = pd.concat([lex.iloc[:1], lex.iloc[1:].fillna(method='ffill')])
    pop_filled = pd.concat([pop.iloc[:1], pop.iloc[1:].fillna(method='ffill')])

    pop_tidy = pd.melt(pop_filled, id_vars='country', var_name='year', value_name='population')
    lex_tidy = pd.melt(lex_filled, id_vars='country', var_name='year', value_name='life_expectancy')
    gdp_tidy = pd.melt(gdp, id_vars='country', var_name='year', value_name='gdp')

    df_merged = pop_tidy.merge(lex_tidy, on=['country', 'year']).merge(gdp_tidy, on=['country', 'year'])
    df_merged['year'] = pd.to_numeric(df_merged['year'])
    return df_merged

# Load and preprocess the data
df = load_and_preprocess_data()

# Create a bubble chart using Altair
selection = alt.selection_single(
    fields=['year'], 
    init={'year': 2007}, 
    bind=alt.binding_range(min=1952, max=2007, step=5)
)

color = alt.condition(selection,
                      alt.Color('continent:N', legend=None),
                      alt.value('lightgray'))

base = alt.Chart(df).mark_circle().encode(
    x=alt.X('gdp:Q', scale=alt.Scale(type='log')),
    y=alt.Y('life_expectancy:Q'),
    size=alt.Size('population:Q'),
    color=color,
    tooltip=['country:N', 'continent:N', 'gdp:Q', 'life_expectancy:Q', 'population:Q']
).add_selection(
    selection
)

legend = alt.Chart(df).mark_point().encode(
    y=alt.Y('continent:N', axis=alt.Axis(orient='right')),
    color=color
)

chart = alt.hconcat(base, legend)

# Display the chart using Streamlit
st.altair_chart(chart)
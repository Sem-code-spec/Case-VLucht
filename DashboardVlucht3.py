import streamlit as st
import pandas as pd
import numpy as np
import seaborn as sns
import datetime
import os
import requests
import plotly.express as px
import plotly.graph_objects as go
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

#Data frame Vliegmaatschappij
df_vlieg_maatschappij = pd.read_csv('samengevoegde_luchtvaartmaatschappijen.csv')

#Data frame Vlucht
df_vlucht = pd.read_csv('airports-extended-clean (1).csv', delimiter=';')

#Data frame Schema
df_schema = pd.read_csv('schedule_airport.csv')


#Voeg een nieuwe kolom toe met alleen de letters uit de "FLT"-kolom
df_schema['Airline_code'] = df_schema['FLT'].str.extract('([A-Za-z]+)')
df_schema.groupby('Airline_code')
df_arilines = df_schema['Airline_code']


# Code voor de maanden/seizoenen
df_schema['STD'] = pd.to_datetime(df_schema['STD'], dayfirst=True)

def get_season(date):
    month = date.month
    if month in [12, 1, 2]:
        return 'Winter'
    elif month in [3, 4, 5]:
        return 'Lente'
    elif month in [6, 7, 8]:
        return 'Zomer'
    elif month in [9, 10, 11]:
        return 'Herfst'

df_schema['Season'] = df_schema['STD'].apply(get_season)

df_season_group = df_schema.groupby('Season').size()  # Example: count occurrences per season




# Zet de kolom 'STD' om naar datetime-indeling
df_schema['STD'] = pd.to_datetime(df_schema['STD'], dayfirst=True)

# Definieer een functie om de weeknummers op te halen
def get_week(date):
    # Haal de week uit de datum
    week_nummer = date.isocalendar().week
    return f"Week {week_nummer}"

# Pas de functie toe op de kolom 'STD' en maak een nieuwe kolom 'Week'
df_schema['Week'] = df_schema['STD'].apply(get_week)



# Zet de kolom 'STD' om naar datetime-indeling
df_schema['STD'] = pd.to_datetime(df_schema['STD'], dayfirst=True)

# Definieer een functie om de weeknummers en het jaar op te halen
def get_year_week(date):
    # Haal de week en het jaar uit de datum
    year = date.year
    week_nummer = date.isocalendar().week
    return f"{year}-Week {week_nummer}"

# Pas de functie toe op de kolom 'STD' en maak een nieuwe kolom 'Jaar_Week'
df_schema['Jaar_Week'] = df_schema['STD'].apply(get_year_week)

# Voeg ook een kolom toe voor het jaar
df_schema['Jaar'] = df_schema['STD'].dt.year



df_schema['STD'] = pd.to_datetime(df_schema['STD'], dayfirst=True)

def get_month(date):
    month = date.month
    if month == 1:
        return 'januari'
    elif month == 2:
        return 'februari'
    elif month == 3:
        return 'maart'
    elif month == 4:
        return 'april'
    elif month == 5:
        return 'mei'
    elif month == 6:
        return 'juni'
    elif month == 7:
        return 'juli'
    elif month == 8:
        return 'augustus'
    elif month == 9:
        return 'september'
    elif month == 10:
        return 'oktober'
    elif month == 11:
        return 'november'
    elif month == 12:
        return 'december'

# Pas de functie toe op de kolom 'STD' en maak een nieuwe kolom 'Maand'
df_schema['Maand'] = df_schema['STD'].apply(get_month)


df_schema['STA_STD_ltc'] = pd.to_datetime(df_schema['STA_STD_ltc'])
df_schema['ATA_ATD_ltc'] = pd.to_datetime(df_schema['ATA_ATD_ltc'])
df_schema['diff'] = df_schema['ATA_ATD_ltc'] - df_schema['STA_STD_ltc']
df_schema['diff_minutes'] = df_schema['diff'].dt.total_seconds() / 60
df_avg = df_schema.groupby('ACT')['diff_minutes'].mean().reset_index()

# Voeg een kolom toe om vertraagde vluchten aan te geven (meer dan 15 minuten te vroeg of meer dan 30 minuten te laat)
df_schema['Delayed'] = df_schema['diff_minutes'].apply(lambda x: 1 if x < -15 or x > 30 else 0)

# Voeg een kolom toe voor het uur van de dag
# Dit wordt gebruikt om de invloed van het tijdstip van de dag op de vertraging te analyseren
df_schema['Hour'] = df_schema['STA_STD_ltc'].dt.hour

#Pagina setup met Streamlit
st.set_page_config(page_title="Vluchtvertragingen Dashboard", layout="wide") # Full-screen breedte
st.title("Vluchtvertragingen Dashboard ")


# Sidebar navigatie voor meerdere pagina's
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Vluchten Analyse", "Vertraging Voorspelling", "Wereld Kaart"])

with tab1:
    st.header("Overzicht en Informatie")
    st.write("""
    Dit dashboard biedt een uitgebreid overzicht van vluchtvertragingen, gate en baan analyses, en voorspellingen voor vertragingen.
    Gebruik de navigatie in de zijbalk om door de verschillende analyses te bladeren:
    
    - **Vluchten Analyse**: Bekijk trends in het aantal vluchten per maand in de jaren 2019 en 2020.
    - **Vertraging Voorspelling**: Analyseer vertragingen op start- en landingsbanen en maak voorspellingen voor vertragingen.
    - **Kaartweergave**
             
    Met behulp van deze analyses kunt u inzicht krijgen in de oorzaken van vertragingen en betere vluchten uitzoeken in de toekomst.
    """)
    st.image("https://images.unsplash.com/photo-1466691623998-d607fab1ca29", caption="Vliegtuigen", use_column_width=True)

with tab2:
    st.header("Grafieken over verschillende invloeden op vertraging")

    #Vliegtuig types tegen over Gemiddelde verschil (min)
    fig = px.bar(df_avg, x='ACT', y='diff_minutes', labels={'diff_minutes': 'Gemiddeld verschil (min)', 'ACT': 'Vliegtuig types'},width=1100,
        height=500, color_discrete_sequence=['blue'])
    fig.update_layout(xaxis_tickangle=-45, title_text= 'Vertraging bij Vliegtuig types', title_x=0.5)
    st.plotly_chart(fig)

    #Seizoenen tegen over Gemiddelde verschil (min)
    df_avg2 = df_schema.groupby('Season')['diff_minutes'].mean().reset_index()
    fig = px.bar(df_avg2, x='Season', y='diff_minutes', labels={'diff_minutes': 'Gemiddeld verschil (min)', 'Season': 'Seizoenen'},width=1100, color_discrete_sequence=['blue'])
    fig.update_layout(title_text='Vertraging per Seizoen', title_x=0.5)
    st.plotly_chart(fig)

    #Land van Afkomst tegen over Gemiddeld verschil (min)
    df_avg3 = df_schema.groupby('Org/Des')['diff_minutes'].mean().reset_index()
    fig = px.bar(df_avg3, x='Org/Des', y='diff_minutes', labels={'diff_minutes': 'Gemiddeld verschil (min)', 'Org/Des': 'Land van afkomst'},width=1100, color_discrete_sequence=['blue'])
    fig.update_layout(title_text='Vertraging per land van Afkomst', title_x=0.5)
    st.plotly_chart(fig)


    #Luchtvaartmaatschappij tegen over Aantal vluchten/Gemiddeld verschil (min)

    #Samen voegen van df_schema en df_vlieg_maatschappij
    merged_df= pd.merge(df_schema, df_vlieg_maatschappij, left_on='Airline_code', right_on='Code', how='inner')

    # Groep de data en bereken het gemiddelde
    df_avg5 = merged_df.groupby('Luchtvaartmaatschappij')['diff_minutes'].mean().reset_index()
    # Groep de data en tel het aantal vluchten
    df_count = merged_df.groupby('Luchtvaartmaatschappij')['Luchtvaartmaatschappij'].count().reset_index(name='flight_count')

    # Voeg beide DataFrames samen op basis van luchtvaartmaatschappij
    df_combined = df_avg5.merge(df_count, on='Luchtvaartmaatschappij')

    # Groep de data en bereken het gemiddelde
    df_avg6 = merged_df.groupby('Luchtvaartmaatschappij')['diff_minutes'].mean().reset_index()
    # Groep de data en tel het aantal vluchten
    df_count = merged_df.groupby('Luchtvaartmaatschappij')['Luchtvaartmaatschappij'].count().reset_index(name='flight_count')

    # Voeg beide DataFrames samen op basis van luchtvaartmaatschappij
    df_combined = df_avg6.merge(df_count, on='Luchtvaartmaatschappij')

    # Groep de data en bereken het gemiddelde
    df_avg7 = merged_df.groupby('Luchtvaartmaatschappij')['diff_minutes'].mean().reset_index()
    # Groep de data en tel het aantal vluchten
    df_count = merged_df.groupby('Luchtvaartmaatschappij')['Luchtvaartmaatschappij'].count().reset_index(name='flight_count')

    # Voeg beide DataFrames samen op basis van luchtvaartmaatschappij
    df_combined = df_avg7.merge(df_count, on='Luchtvaartmaatschappij')

    # Groepeer op Jaar en Week om het gemiddelde te berekenen
    df_avg12 = merged_df.groupby(['Jaar', 'Week'])['diff_minutes'].mean().reset_index()

    # Sorteer op 'Jaar' en 'Week' voor correcte volgorde
    df_avg12 = df_avg12.sort_values(by=['Jaar', 'Week'])

    

    # Maak de bar chart aan
    fig = px.bar(
        df_combined,
        x='Luchtvaartmaatschappij',
        y='diff_minutes',  # Dit is de standaard y-waarde
        labels={
            'diff_minutes': 'Gemiddelde verschil (minuten)',
            'Luchtvaartmaatschappij': 'Luchtvaartmaatschappij'
        },
        color_discrete_sequence=['blue'],
        width=1500,  # Verhoog de breedte van de figuur
        height=1500  # Vergroot de hoogte van de figuur om meer ruimte te creëren
    )

    # Update de layout om de x-as titel toe te voegen
    fig.update_layout(
        title={
            'text': "Gemiddelde vertraging per luchtvaartmaatschappij",
            'y': 1,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        xaxis_title='',  # Voeg hier de x-as titel toe
        yaxis_title='Gemiddelde verschil (minuten)',  # Voeg hier de y-as titel toe
    )

    fig.add_annotation(
        text='Luchtvaartmaatschappij',            # Tekst van de tweede titel
        xref='paper', yref='paper',     # Referentie naar de grafiek (paper betekent dat het in de grafiek zelf zit)
        x=0.5, y=-0.4,                   # Plaatsing van de titel (x=0.5 plaatst het in het midden, y=1.1 plaatst het net boven de grafiek)
        showarrow=False,                # Geen pijlen bij de annotatie
        font=dict(size=16, color='black'))


    # Draai de x-as labels voor betere leesbaarheid
    fig.update_layout(
        xaxis_tickangle=-45,
        xaxis_title_standoff=1000,  # Verlaag de afstand tussen de x-as titel en de as
        margin=dict(t=10),
    )

    # Voeg een dropdown menu toe voor het wijzigen van statistieken en luchtvaartmaatschappijen
    fig.update_layout(
        updatemenus=[
            {
                'buttons': [
                    {
                        'label': 'Gemiddelde verschil (minuten)',
                        'method': 'update',
                        'args': [{'y': [df_combined['diff_minutes']]}, {'title': 'Gemiddelde verschil (minuten)'}]
                    },
                    {
                        'label': 'Aantal vluchten',
                        'method': 'update',
                        'args': [{'y': [df_combined['flight_count']]}, {'title': 'Aantal vluchten per luchtvaartmaatschappij'}]
                    }
                ],
                'direction': 'down',
                'showactive': True,
                'x': 0.67,  # Positioneer de dropdown
                'xanchor': 'left',
                'y': 1.15,  # Positioneer de dropdown
                'yanchor': 'top'
            },
            {
                'buttons': [
                    {
                        'label': 'Alle luchtvaartmaatschappijen',
                        'method': 'update',
                        'args': [
                            {'x': [df_combined['Luchtvaartmaatschappij']], 'y': [df_combined['diff_minutes']], 'visible': True},
                            {'title': 'Alle luchtvaartmaatschappijen'}
                        ]
                    }
                ] + [
                    {
                        'label': luchtvaartmaatschappij,
                        'method': 'update',
                        'args': [
                            {'x': [df_combined['Luchtvaartmaatschappij'][df_combined['Luchtvaartmaatschappij'] == luchtvaartmaatschappij]],
                            'y': [df_combined['diff_minutes'][df_combined['Luchtvaartmaatschappij'] == luchtvaartmaatschappij]],
                            'visible': True},  # Zorg dat deze luchtvaartmaatschappij zichtbaar is
                            {'title': f'Data voor {luchtvaartmaatschappij}'}
                        ]
                    } for luchtvaartmaatschappij in df_combined['Luchtvaartmaatschappij']
                ],
                'direction': 'down',
                'showactive': True,
                'x': 0.85,  # Positioneer de dropdown
                'xanchor': 'left',
                'y': 1.15,  # Positioneer de dropdown
                'yanchor': 'top'
            },
        ]
    )

    # Toon de figuur
    st.plotly_chart(fig)






with tab3:
    st.header("Vertraging Voorspelling")


    # Zorg ervoor dat 'Jaar' en 'Week' numeriek zijn, als ze dat nog niet zijn
    merged_df['Jaar'] = pd.to_numeric(merged_df['Jaar'], errors='coerce')

    # Als 'Week' geen strings zijn, zet deze om naar strings en gebruik .str.extract()
    if merged_df['Week'].dtype != 'object':
        merged_df['Week'] = merged_df['Week'].astype(str)

    # Extraheer alleen de numerieke waarden uit de Week-kolom
    merged_df['Week'] = pd.to_numeric(merged_df['Week'].str.extract(r'(\d+)')[0], errors='coerce')

    # Groepeer op Jaar en Week om het gemiddelde te berekenen
    df_avg12 = merged_df.groupby(['Jaar', 'Week'])['diff_minutes'].mean().reset_index()
    df_avg12 = df_avg12.sort_values(by=['Jaar', 'Week'])

    # Gemiddelde verschil per dag (STD)
    df_avg10 = merged_df.groupby('STD')['diff_minutes'].mean().reset_index()

    # Eerste plot: Gemiddelde verschil per dag (STD)
    fig1 = px.line(df_avg10, x='STD', y='diff_minutes', 
                labels={'diff_minutes': 'Gemiddelde verschil (minuten)', 'STD': 'Datum'},
                color_discrete_sequence=['blue'])

    # Tweede plot: Gemiddelde verschil per week (Jaar en Week)
    fig2 = px.line(df_avg12, x='Week', y='diff_minutes', 
                color='Jaar',
                labels={'diff_minutes': 'Gemiddelde verschil (minuten)', 'Week': 'Weken'},
                color_discrete_sequence=['blue', 'orange'])

    # Voeg een nieuwe figuur toe
    fig = go.Figure()

    # Voeg data van de eerste figuur (per dag) toe
    for trace in fig1.data:
        fig.add_trace(trace)

    # Voeg data van de tweede figuur (per week) toe
    for trace in fig2.data:
        fig.add_trace(trace)

    # Begin met alleen de eerste grafiek (daggegevens) zichtbaar
    visibility_per_dag = [True] * len(fig1.data) + [False] * len(fig2.data)
    visibility_per_week = [False] * len(fig1.data) + [True] * len(fig2.data)

    # Voeg dropdown-menu toe om te wisselen tussen beide grafieken
    fig.update_layout(
        updatemenus=[
            {
                'buttons': [
                    {
                        'label': 'Per Dag',
                        'method': 'update',
                        'args': [
                            {'visible': visibility_per_dag},  # Toon alleen de eerste grafiek
                            {'title': 'Gemiddelde verschil per Dag', 
                            'xaxis': {'title': 'Datum'}, 
                            'yaxis': {'title': 'Gemiddelde verschil (minuten)'}}
                        ]
                    },
                    {
                        'label': 'Per Week',
                        'method': 'update',
                        'args': [
                            {'visible': visibility_per_week},  # Toon alleen de tweede grafiek
                            {'title': 'Gemiddelde verschil per Week', 
                            'xaxis': {'title': 'Weken'}, 
                            'yaxis': {'title': 'Gemiddelde verschil (minuten)'}}
                        ]
                    }
                ],
                'direction': 'down',
                'showactive': True
            }
        ],
        title="Gemiddelde verschil per Dag",  # Zorg ervoor dat de titel van grafiek 1 wordt weergegeven bij start
        xaxis_title="Datum",  # X-as titel van de eerste grafiek
        yaxis_title="Gemiddelde verschil (minuten)"  # Y-as titel van de eerste grafiek
    )

    # Maak grafiek 1 standaard zichtbaar
    for trace in fig.data:
        trace.visible = False  # Verberg alle tracés

    for i in range(len(fig1.data)):  # Maak tracés van de eerste figuur zichtbaar
        fig.data[i].visible = True

    # Toon de plot
    st.plotly_chart(fig)



    # Groepeer op de STD-datum om het aantal vluchten per datum te tellen
    df_vluchten = df_schema.groupby('STD').size().reset_index(name='Aantal_Vluchten')

    # Zorg ervoor dat de kolommen 'Jaar' en 'Week' bestaan in merged_df voordat je ze omzet
    if 'Jaar' in merged_df.columns and 'Week' in merged_df.columns:
        # Converteer 'Jaar' naar numeriek
        merged_df['Jaar'] = pd.to_numeric(merged_df['Jaar'], errors='coerce')

        # Controleer de type van de 'Week' kolom en zet deze om naar string als dat nodig is
        if merged_df['Week'].dtype != 'object':
            merged_df['Week'] = merged_df['Week'].astype(str)

        # Extract het weeknummer en converteer naar numeriek
        merged_df['Week'] = pd.to_numeric(merged_df['Week'].str.extract(r'(\d+)')[0], errors='coerce')

        # Controleer op NaN-waarden en verwijder ze indien nodig
        merged_df = merged_df.dropna(subset=['Jaar', 'Week'])

        # Groepeer op Jaar en Week om het aantal vluchten te tellen
        df_avg13 = merged_df.groupby(['Jaar', 'Week']).size().reset_index(name='Aantal_Vluchten')

        # Sorteer op 'Jaar' en 'Week' voor correcte volgorde
        df_avg13 = df_avg13.sort_values(by=['Jaar', 'Week'])

        # Maak de lijnplot voor het aantal vluchten per week
        fig_week = px.line(df_avg13, x='Week', y='Aantal_Vluchten', 
                       color='Jaar',  # Voeg het jaar toe als kleur voor onderscheid
                       labels={'Aantal_Vluchten': 'Aantal Vluchten', 'Week': 'Weken'},
                       color_discrete_sequence=['blue', 'orange'])

    # Maak de lijnplot voor het aantal vluchten per datum
    fig_date = px.line(df_vluchten, x='STD', y='Aantal_Vluchten', 
                    labels={'Aantal_Vluchten': 'Aantal vluchten', 'STD': 'Datum'}, 
                    color_discrete_sequence=['blue'])

    # Voeg een nieuwe figuur toe
    fig = go.Figure()

    # Voeg data van de eerste figuur (per week) toe
    for trace in fig_week.data:
        fig.add_trace(trace)

    # Voeg data van de tweede figuur (per datum) toe
    for trace in fig_date.data:
        fig.add_trace(trace)

    # Begin met alleen de eerste grafiek (weken) zichtbaar
    visibility_per_week = [True] * len(fig_week.data) + [False] * len(fig_date.data)
    visibility_per_date = [False] * len(fig_week.data) + [True] * len(fig_date.data)

    # Voeg dropdown-menu toe om te wisselen tussen beide grafieken
    fig.update_layout(
        updatemenus=[
            {
                'buttons': [
                    {
                        'label': 'Per Week',
                        'method': 'update',
                        'args': [
                            {'visible': visibility_per_week},  # Toon alleen de eerste grafiek
                            {'title': 'Aantal Vluchten per Week', 
                            'xaxis': {'title': 'Weken'}, 
                            'yaxis': {'title': 'Aantal Vluchten'}}
                        ]
                    },
                    {
                        'label': 'Per Datum',
                        'method': 'update',
                        'args': [
                            {'visible': visibility_per_date},  # Toon alleen de tweede grafiek
                            {'title': 'Aantal Vluchten per Datum', 
                            'xaxis': {'title': 'Datum'}, 
                            'yaxis': {'title': 'Aantal Vluchten'}}
                        ]
                    }
                ],
                'direction': 'down',
                'showactive': True
            }
        ],
        title="Aantal Vluchten per Week",  # Zorg ervoor dat de titel van grafiek 1 wordt weergegeven bij start
        xaxis_title="Weken",  # X-as titel van de eerste grafiek
        yaxis_title="Aantal Vluchten"  # Y-as titel van de eerste grafiek
    )

    # Maak grafiek 1 standaard zichtbaar
    for trace in fig.data:
        trace.visible = False  # Verberg alle tracés

    for i in range(len(fig_week.data)):  # Maak tracés van de eerste figuur zichtbaar
        fig.data[i].visible = True

    # Toon de plot
    st.plotly_chart(fig)






    # Berekening voor het maken van hoeveel % kans op vertraging
    if not df_schema.empty:
        # Vertraging Voorspelling
        bestemming = st.selectbox("Selecteer Bestemming", df_schema['Org/Des'].unique())
        maand = st.selectbox("Selecteer Maand", list(datetime.date(1900, i, 1).strftime('%B') for i in range(1, 13)))
        maand_nummer = list(datetime.date(1900, i, 1).strftime('%B') for i in range(1, 13)).index(maand) + 1
        bestemming_data = df_schema[(df_schema['Org/Des'] == bestemming) & (df_schema['STD'].dt.month == maand_nummer)]

        if 'Delayed' in bestemming_data.columns and not bestemming_data.empty:
            vertraagde_vluchten_count = bestemming_data['Delayed'].sum()
            totaal_vluchten = bestemming_data.shape[0]
            vertraging_kans = (vertraagde_vluchten_count / totaal_vluchten) * 100 if totaal_vluchten > 0 else 0
            if vertraging_kans > 40:
                st.markdown(f"<p style='color: red;'>De kans op vertraging voor vluchten naar {bestemming} in de maand {maand} is {vertraging_kans:.2f}%.</p>", unsafe_allow_html=True)
            else:
                st.markdown(f"<p style='color: green;'>De kans op vertraging voor vluchten naar {bestemming} in de maand {maand} is {vertraging_kans:.2f}%.</p>", unsafe_allow_html=True)
        else:
            st.write("Geen data beschikbaar voor de geselecteerde combinatie van bestemming en maand, of de kolom 'Delayed' ontbreekt in de dataset.")

        # Vertraging per Tijdstip van de Dag
        st.header("Vertraging per Tijdstip van de Dag")
        vertraging_per_uur = df_schema.groupby('Hour')['diff_minutes'].mean().reset_index()
        fig = px.line(vertraging_per_uur, x='Hour', y='diff_minutes', labels={'Hour': 'Uur van de dag', 'diff_minutes': 'Gemiddelde vertraging (minuten)'}, width=1100, color_discrete_sequence=['blue'])
        fig.update_layout(xaxis=dict(dtick=1))
        st.plotly_chart(fig)

        # Analyseer landings- en startbanen
        if 'RWY' in df_schema.columns:
            st.header("Analyse van Vertragingen per Landings-/Startbaan")
            vertraagde_vluchten = df_schema[df_schema['Delayed'] == 1]  # Filter alleen vertraagde vluchten
            if not vertraagde_vluchten.empty:
                baan_vertragingen = vertraagde_vluchten.groupby('RWY')['diff_minutes'].mean().sort_values(ascending=False)
                plt.figure(figsize=(10, 6))
                sns.barplot(x=baan_vertragingen.index, y=baan_vertragingen.values, palette='Blues_d')
                plt.xlabel('Landings-/Startbaan')
                plt.ylabel('Gemiddelde Vertraging (minuten)')
                plt.title('Gemiddelde Vertraging per Landings-/Startbaan (alleen vertraagde vluchten)')
                plt.grid(axis='y', linestyle='--', alpha=0.7)
                st.pyplot(plt)
            else:
                st.write("Geen vertraagde vluchten gevonden om te analyseren.")
        else:
            st.write("Kolom 'RWY' ontbreekt in de dataset.")


with tab4:
    st.header("Wereld Kaart")
    @st.cache_data()
    def csv(csv):
        df = pd.read_csv(csv, index_col=0)
        df['uur'] = df['afstand'] / 900000
        df['minuut'] = (df['afstand'] % 900000) / 15000
        df['seconde'] = (df['afstand'] % 900000 % 15000) / 250
        return df

    airports_fil = csv('airport_fil.csv')
    @st.cache_data()
    def make_map(df):
        m = folium.Map(location=(30, 10), zoom_start=2.2, tiles="cartodb positron")
        for _, row in df.iterrows():
            folium.Marker(
                location=[row[6], row[7]],
                popup=f'Gemiddelde vliegtijd is \n {int(row["uur"])}:{int(row["minuut"])}:{int(row["seconde"])}',
                tooltip=f'<b>{row[1]}</b>'
            ).add_to(m)
        return m
    
    # Folium kaart in de Streamlit app
    st_data = st_folium(make_map(airports_fil), width='100%', height=600)



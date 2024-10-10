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



#Pagina setup met Streamlit
st.set_page_config(page_title="Flight Delay's Dashboard", layout="wide") # Full-screen breedte
st.title("Flight Delay's Dashboard")

# Define a function to display a blue title
def blue_title(text):
    st.markdown(f"<h1 style='color: blue;'>{text}</h1>", unsafe_allow_html=True)


# Sidebar navigatie voor meerdere pagina's
tab1, tab2, tab3, tab4 = st.tabs(["Home", "Pagin 1", "Pagina 2", "Pagina 3"])

with tab1:
    blue_title("Home Page")
    st.write("Op dit dashboard wordt er gekenen naar wat er invloed heeft op de vertraging van vliegtuigen")

with tab2:
    blue_title("Pagina 1")
    st.header("Grafieken over verschillende invloeden op vertraging")

    #Vliegtuig types tegen over Gemiddelde verschil (min)
    fig = px.bar(df_avg, x='ACT', y='diff_minutes', labels={'diff_minutes': 'Gemiddeld verschil (min)', 'ACT': 'Vliegtuig types'},width=1100,
        height=500, color_discrete_sequence=['blue'])
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig)

    #Seizoenen tegen over Gemiddelde verschil (min)
    df_avg2 = df_schema.groupby('Season')['diff_minutes'].mean().reset_index()
    fig = px.bar(df_avg2, x='Season', y='diff_minutes', labels={'diff_minutes': 'Gemiddeld verschil (min)', 'Season': 'Seizoenen'},width=1100, color_discrete_sequence=['blue'])
    st.plotly_chart(fig)

    #Land van Afkomst tegen over Gemiddeld verschil (min)
    df_avg3 = df_schema.groupby('Org/Des')['diff_minutes'].mean().reset_index()
    fig = px.bar(df_avg3, x='Org/Des', y='diff_minutes', labels={'diff_minutes': 'Gemiddeld verschil (min)', 'Org/Des': 'Land van afkomst'},width=1100, color_discrete_sequence=['blue'])
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


    # Figuur van Datum tegenover Gemiddeld verschil (min)
    df_avg10 = merged_df.groupby('STD')['diff_minutes'].mean().reset_index()
    fig = px.line(df_avg10, x='STD', y='diff_minutes', labels={'diff_minutes': 'Gemiddelde verschil (min)', 'STD': 'Datum'},width=1100, color_discrete_sequence=['blue'])
    st.plotly_chart(fig)


    #Figuur van Weken tegenover gemiddeld verschil (min)

    # Zorg ervoor dat 'Jaar' en 'Week' numeriek zijn, als ze dat nog niet zijn
    merged_df['Jaar'] = pd.to_numeric(merged_df['Jaar'], errors='coerce')
    merged_df['Week'] = pd.to_numeric(merged_df['Week'].str.extract(r'(\d+)')[0], errors='coerce')

    # Groepeer op Jaar en Week om het gemiddelde te berekenen
    df_avg12 = merged_df.groupby(['Jaar', 'Week'])['diff_minutes'].mean().reset_index()

    # Sorteer op 'Jaar' en 'Week' voor correcte volgorde
    df_avg12 = df_avg12.sort_values(by=['Jaar', 'Week'])

    # Maak de lijnplot met Jaar en Week
    fig = px.line(df_avg12, x='Week', y='diff_minutes', 
                color='Jaar',  # Voeg het jaar toe als kleur voor onderscheid
                labels={'diff_minutes': 'Gemiddelde verschil (minuten)', 'Week': 'Weken'},
                width=1100, color_discrete_sequence=['blue', 'orange'])

    # Laat de plot zien
    st.plotly_chart(fig)

    

    #Figuur van weken tegenover Aantal Vluchten

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

        # Maak de lijnplot met Jaar en Week
        fig = px.line(df_avg13, x='Week', y='Aantal_Vluchten', 
                    color='Jaar',  # Voeg het jaar toe als kleur voor onderscheid
                    labels={'Aantal_Vluchten': 'Aantal Vluchten', 'Week': 'Weken'},
                    width=1100, color_discrete_sequence=['blue', 'orange'])

        # Laat de plot zien
        st.plotly_chart(fig)
    else:
        print("De kolommen 'Jaar' en/of 'Week' zijn niet gevonden in merged_df.")



    # Figuur Datum tegenover Aantal vluchten

    # Definieer de maanden in de juiste volgorde
    maanden = [
        'januari', 'februari', 'maart', 'april', 'mei', 'juni', 
        'juli', 'augustus', 'september', 'oktober', 'november', 'december'
    ]

    # Zet de 'Maand' kolom om naar een categorische datatype met de juiste volgorde
    df_schema['STD'] = pd.Categorical(df_schema['STD'])

    # Bereken het aantal vluchten per maand
    df_vluchten = df_schema.groupby('STD').size().reset_index(name='Aantal_Vluchten')

    # Maak de lijnplot
    fig = px.line(df_vluchten, x='STD', y='Aantal_Vluchten', 
                labels={'Aantal_Vluchten': 'Aantal vluchten', 'STD': 'Datum'}, 
                width=1100, color_discrete_sequence=['blue'])

    st.plotly_chart(fig)

with tab3:
    blue_title("Pagina 2")

with tab4:
    @st.cache_data()
    def csv(csv):
        df = pd.read_csv(csv, index_col=0)
        df['uur'] = df['afstand']/900000
        df['minuut'] = df['afstand']%900000/15000
        df['seconde'] = df['afstand']%900000%15000/250
        return df
    airports_fil = csv('airport_fil.csv')
    
    @st.cache_data()
    def make_map(df):
        m = folium.Map(location=(30, 10), zoom_start=2.2, tiles="cartodb positron")
        for row in df.iterrows():
            folium.Marker(location = [row[1][6],row[1][7]],
                                popup = f'gem vliegtijd \n {int(row[1][-3])}:{int(row[1][-2])}:{int(row[1][-2])}' ,
                                tooltip='<b>'+f'{row[1][1]}' +'<b>',
                                ).add_to(m)
        return m
    st_data = st_folium(make_map(airports_fil))



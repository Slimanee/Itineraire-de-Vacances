'''
configuration environnement virtuel pour le projet ->  venv, dans la console : python -m venv .venv
Dans Vscode, Command Palette (CTRL+SHIFT+P) and selecting > Python: Select Interpreter -> selectionner l'environnement venv
'''


# import librairies
from datetime import datetime
print("Début import librairies à {date}".format(date=datetime.today()))
import requests
import json
import os
import pandas as pd
# librairie à priori nécessaire pour se connecter à postgres
import psycopg2
from sqlalchemy import create_engine
#import seaborn as sns
print("Fin import librairies à {date} \n".format(date=datetime.today()))


def chargement_fichier_datatourisme():
    '''
    Chargement du fichier sur https://diffuseur.datatourisme.fr/ pour le stocker en local dans le 
    repertoire data.
    
    On teste avant de charger si on ne l'a pas déjà chargé pour la date du jour
    
    Les fichiers sont enregistrés dans le répertoire 'data' du répertoire de travail 
    au format datatourism_YYYYMMDD.json

    '''
    # définition du webservice pour récupérer le fichier datatourisme
    key = '380d2fe9-2c9c-4190-a79e-8301b37d03fb'
    #url = 'https://diffuseur.datatourisme.fr/webservice/bfadcf44012b7156ca3e297b468c4f75/' + key
    url = 'https://api.github.com'


    # test existence répertoire de recupération des données, s'il n'existe pas > creation du répertoire
    if os.path.isdir(path) == False:
        print ("Creation du chemin '{path}' non existant".format(path=path))
        os.mkdir(path)
    else:
        print("Chemin {path} OK".format(path=path))

    # test existence fichier déja téléchargé aujourd'hui dans le chemin
    if os.path.isfile(nom_fichier) == True:
        print("Fichier {nom_fichier} déjà telechargé aujourd'hui".format(nom_fichier=nom_fichier))
    else:
        print("Début telechargement fichier à" , datetime.today())
        # TODO regarder le site https://www.nylas.com/blog/use-python-requests-module-rest-apis/#:~:text=The%20GET%20method%20is%20used,function%20to%20do%20exactly%20this.&text=The%20response%20object%20contains%20all,headers%20and%20the%20data%20payload.
        # pour voir l'exemple avec try catch
        fichier_datatourism = requests.get(url)
        print("Fin téléchargement fichier à" , datetime.today())

        print("Début ecriture du fichier {nom_fichier} à {date}".format(nom_fichier=nom_fichier, date=datetime.today()))
        with open(nom_fichier, 'w') as file:
            json.dump(fichier_datatourism.json(), file)
        print("Fin ecriture du fichier {nom_fichier} à {date} \n".format(nom_fichier=nom_fichier, date=datetime.today()))


def traitement_fichier_datatourism():
    # lecture fichier pour traitement
    print("Début lecture fichier {nom_fichier} à {date}".format(nom_fichier=nom_fichier, date=datetime.today()))
    with open(nom_fichier, 'r') as file:
        data = json.load(file)
    print("Fin lecture fichier {nom_fichier} à {date} \n".format(nom_fichier=nom_fichier, date=datetime.today()))    


    df = pd.json_normalize(data['@graph'])
    columns = {
        'dc:identifier': 'id',
        '@id': 'url',
        '@type': 'type',
        'rdfs:label.@value': 'nom',
        'rdfs:comment.@value': 'commentaire',
        'hasContact.schema:email': 'contact_email',
        'hasContact.schema:telephone': 'contact_telephone',
        'hasContact.foaf:homepage': 'contact_homepage',
        'isLocatedAt.schema:address.schema:streetAddress': 'adresse',
        'isLocatedAt.schema:address.schema:addressLocality': 'ville',
        'isLocatedAt.schema:address.schema:postalCode': 'code_postal',
        'isLocatedAt.schema:geo.schema:latitude.@value': 'latitude',
        'isLocatedAt.schema:geo.schema:longitude.@value': 'longitude',
        'isLocatedAt.schema:geo.latlon.@value': 'latlon',
        'isLocatedAt.schema:geo.schema:elevation.@value': 'altitude',
        'isLocatedAt.schema:openingHoursSpecification.schema:validFrom.@value': 'ouvert_date_de',
        'isLocatedAt.schema:openingHoursSpecification.schema:validThrough.@value': 'ouvert_date_a',
        'isLocatedAt.schema:openingHoursSpecification.schema:opens.@value': 'ouvert_heure_de',
        'isLocatedAt.schema:openingHoursSpecification.schema:closes.@value': 'ouvert_heure_a',
        'isLocatedAt.schema:openingHoursSpecification.additionalInformation.@value': 'horaire',
        'schema:offers.schema:priceSpecification.schema:minPrice': 'prix_min',
        'schema:offers.schema:priceSpecification.schema:maxPrice': 'prix_max',
        'schema:offers.schema:priceSpecification.schema:priceCurrency': 'currency',
        'schema:offers.schema:priceSpecification.appliesOnPeriod.startDate.@value': 'prix_de',
        'schema:offers.schema:priceSpecification.appliesOnPeriod.endDate.@value': 'prix_a',
    }
    df = df[columns.keys()]  # Keep only useful columns
    df = df.rename(columns=columns)
    df = df.dropna(subset=['id', 'nom', 'longitude', 'latitude', 'latlon'])  # Suppress row without mandatory data
    df = df.set_index('id', verify_integrity=True)  # Ensure column id contains only unique values
    df.insert(len(df.columns), 'updated_at', pd.Timestamp.utcnow())  # Add datetime column to know when data were refreshed

    # Filter/cleanup useful types
    #df['type'] = df['type'].apply(lambda x: list({i.replace('schema:', '') for i in x} - {'urn:resource', 'olo:OrderedList', 'PlaceOfInterest', 'PointOfInterest'}))
    df_types = df.explode(column='type')[['type', 'updated_at']]  # Create type dataframe for types mapping
    df_types.index.names = ['poi_id']  # Change id to poi_id in type dataframe
    df = df.drop(columns=['type'])  # Remove type column from poi dataframe

    # Extract price min/max info from list/dictionary if exists
    df['prix_min'] = df['prix_min'].apply(lambda x: [e['@value'] for e in x] if isinstance(x, list) else x)
    df['prix_max'] = df['prix_max'].apply(lambda x: [e['@value'] for e in x] if isinstance(x, list) else x)

    df = df.applymap(lambda x: ', '.join(x) if isinstance(x, list) else x)  # Transform lists into comma-separated strings

    return df, df_types

# Visualisation rapide de notre dataframe POI. Le noir correspond au données remplies, le beige représente les NaN.
# Les principales informations des POI nécessaires au projet sont présentes : "nom", "longitude", "latitude", "latlon".
#sns.heatmap(df.isnull(), cbar=False)


def chargement_data_postgres(df, df_types):
    user = 'postgres'
    password = 'password'
    host = '127.0.0.1'
    port = '5432'
    database = 'postgres'
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{database}')
    
    with engine.begin() as connection:
        print("Début chargement postgres à {date}".format(date=datetime.today()))
        df.to_sql('itineraire_poi', connection, if_exists='replace')
        df_types.to_sql('itineraire_types', connection, if_exists='replace')
        print("Fin chargement postgres à {date} \n".format(date=datetime.today()))
        #results = connection.execute("SELECT * FROM TEST;")
        #print(results.fetchall())



# définition des variables communes
# définition chemin et nom fichier du jour à telecharger
date_jour = datetime.today().strftime('%Y%m%d')
path="data"
fichier="datatourism_{date_jour}.json".format(date_jour=date_jour)
nom_fichier = path + "\\" + fichier

#chargement_fichier_datatourisme()

df, df_types = traitement_fichier_datatourism()

print(df_types.head())
pd.set_option('display.max_columns', 30)
print(df.head())

chargement_data_postgres(df, df_types)



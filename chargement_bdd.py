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
import re
import connexion_bdd
# librairie à priori nécessaire pour se connecter à postgres

#import seaborn as sns
print("Fin import librairies à {date} \n".format(date=datetime.today()))


#------------------------------------------------
# définition des variables communes
# définition chemin et nom fichier du jour à telecharger
date_jour = datetime.today().strftime('%Y%m%d')
path="data"
fichier="datatourism_{date_jour}.json".format(date_jour=date_jour)
nom_fichier = path + "\\" + fichier

categories = {
    'WalkingTour': 'Itinéraire pédestre',
    'CyclingTour': 'Itinéraire cyclable',
    'HorseTour': 'Itinéraire équestre',
    'RoadTour': 'Itinéraire routier',
    'FluvialTour': 'Itinéraire fluvial ou maritime',
    'UnderwaterRoute': 'Itinéraire sous-marin',
    'Accommodation': 'Hébergement',
    'FoodEstablishment': 'Restauration',
    'CulturalSite': 'Site culturel',
    'NaturalHeritage': 'Site naturel',
    'SportsAndLeisurePlace': 'Site sportif, récréatif et de loisirs',
}


#------------------------------------------------
def recup_fichier_datatourisme():
    '''
    Chargement du fichier sur https://diffuseur.datatourisme.fr/ pour le stocker en local dans le 
    repertoire data.
    
    On teste avant de charger si on ne l'a pas déjà chargé pour la date du jour
    
    Les fichiers sont enregistrés dans le répertoire 'data' du répertoire de travail 
    au format datatourism_YYYYMMDD.json

    '''
    # définition du webservice pour récupérer le fichier datatourisme
    key = '380d2fe9-2c9c-4190-a79e-8301b37d03fb'
    url = 'https://diffuseur.datatourisme.fr/webservice/bfadcf44012b7156ca3e297b468c4f75/' + key
    #url = 'https://api.github.com'


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


#------------------------------------------------
def traitement_fichier_datatourism():
    '''
    lecture du fichier 
    constitution dataframe df : POI et caracteritiques avec les champs principaux du fichier json
    constitution dataframe df_type : types / POI

    '''
    # lecture fichier pour traitement
    print("Début lecture fichier {nom_fichier} à {date}".format(nom_fichier=nom_fichier, date=datetime.today()))
    with open(nom_fichier, 'r') as file:
        data = json.load(file)
    print("Fin lecture fichier {nom_fichier} à {date} \n".format(nom_fichier=nom_fichier, date=datetime.today()))    


    print("Début traitement données à {date}".format(date=datetime.today()))
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

    # Conversion columns
    convert_dict = {'latitude': float,
                    'longitude': float
                    }
    df = df.astype(convert_dict)

    df = df.set_index('id', verify_integrity=True)  # Ensure column id contains only unique values
    df.insert(len(df.columns), 'updated_at', pd.Timestamp.utcnow())  # Add datetime column to know when data were refreshed

    #df['type'] = df['type'].apply(lambda x: [t for t in x if not t.startswith("schema:") and t not in ['urn:resource', 'olo:OrderedList', 'PointOfInterest']])

    # -- partie constitution dataframe des poi / type 
    # Filter/cleanup useful types
    #df['type'] = df['type'].apply(lambda x: list({i.replace('schema:', '') for i in x} - {'urn:resource', 'olo:OrderedList', 'PlaceOfInterest', 'PointOfInterest'}))
    df_types = df.explode(column='type')[['type', 'updated_at']]  # Create type dataframe for types mapping
    df_types.index.names = ['poi_id']  # Change id to poi_id in type dataframe


    # Extract price min/max info from list/dictionary if exists
    df['prix_min'] = df['prix_min'].apply(lambda x: [e['@value'] for e in x] if isinstance(x, list) else x)
    df['prix_max'] = df['prix_max'].apply(lambda x: [e['@value'] for e in x] if isinstance(x, list) else x)
    df = df.applymap(lambda x: ', '.join(x) if isinstance(x, list) else x)  # Transform lists into comma-separated strings
 

    # --partie constitution dataframe simplifié
    print("Nom des colonnes : \n" , df.columns)
    #	id, url, type, nom, commentaire, contact_email, contact_telephone, contact_homepage, adresse, ville, code_postal, latitude, longitude
    df_poi = df[["url", "type", "nom", "commentaire", "contact_email", "contact_telephone", 
             "contact_homepage", "adresse", "ville", "code_postal", "latitude", "longitude", "updated_at" ]]
    # df_poi = df_poi.dropna(subset=['id', 'nom', 'longitude', 'latitude', 'type'])  # Suppress row with null mandatory data
    df_poi['type'] = df_poi['type'].apply(categorie)  # keep only one high-level categorie
    df_poi = df_poi.dropna(subset=['type'])
    #df_poi = df_poi.set_index('id', verify_integrity=True)  # Ensure column id contains only unique values
    #print(df_poi.head())
    #--
   

    #df = df.set_index('id', verify_integrity=True)  # Ensure column id contains only unique values

    # -- partie constitution dataframe des poi / type 
    # Filter/cleanup useful types
    #df['type'] = df['type'].apply(lambda x: list({i.replace('schema:', '') for i in x} - {'urn:resource', 'olo:OrderedList', 'PlaceOfInterest', 'PointOfInterest'}))
    #df_types = df.explode(column='type')[['type', 'updated_at']]  # Create type dataframe for types mapping
    #df_types.index.names = ['poi_id']  # Change id to poi_id in type dataframe
    df = df.drop(columns=['type'])  # Remove type column from poi dataframe

    print("Fin traitement données à {date}".format(date=datetime.today()))

    return df, df_types , df_poi

#------------------------------------------------
def traitement_classes_type():
    '''
    lecture du fichier du fichier classe_fr.csv 
    constitution dataframe 
    rajout du niveau hierarchique

    '''
    # 2nde méthode traitement des classements des types
    urlclasses = "https://gitlab.adullact.net/adntourisme/datatourisme/ontology/-/raw/master/Documentation/classes_fr.csv"
    df_classes = pd.read_csv(urlclasses)  # index, URI\tLabel, ParentURI, LabelURI
    #df_classes = df_classes.reset_index()
    #df_classes = df_classes.applymap(lambda x: removeprefix(removesuffix(x, '>'), '<https://www.datatourisme.fr/ontology/core#')) 

    df_classes = df_classes.applymap(keep_type())

    get_parent(df_classes, "PointOfInterest")
    df_classes.rename(columns={"URI": "type", "Label": "label_type", "ParentURI":"parent_type", "ParentLabel":"label_parent_type" }, inplace=True)

    #print("Nom des colonnes" , df_classes.columns)

    return df_classes

#------------------------------------------------
# petite fonction de manipulations des données
def categorie(type):
    for c in categories.keys():
        if c in type.split(', '):
            return c
    return None

def keep_type(text):
    match = re.search('<https://www.datatourisme.fr/ontology/core#(.+?)>', text)
    if match:
        return match.group(1)
    return text

def get_parent(df_classes, label, level=0):
    level += 1
    df_classes.loc[df_classes['ParentURI'] == label, 'level'] = level
    for child_label in df_classes.loc[df_classes['ParentURI'] == label, 'URI']:
        get_parent(df_classes, child_label, level)


'''
-------------------------------------------------------------------
Partie principale : partie recupération / traitement /  chargement bdd du fichier Datatourism - point d'interet
-------------------------------------------------------------------
'''
#definition de la connexion postgres
engine = connexion_bdd.connect_postgres()

# recupération du fichier datatourism et stockage en local
#recup_fichier_datatourisme()

# lecture du fichier en local, traitement données du fichier et constitution des dataframes
df, df_types, df_poi = traitement_fichier_datatourism()
# pd.set_option('display.max_columns', 30)
print("dataframe poi complet :\n" , df.head())
print("dataframe des types / poi : \n" , df_types.head())
print("dataframe poi simplifié : \n" , df_poi.head())

# chargement données datatourims dans postgres
with engine.begin() as connection:
    print("Début chargement postgres à {date}".format(date=datetime.today()))
    df.to_sql('itineraire_poi', connection, if_exists='replace')
    df_types.to_sql('itineraire_types', connection, if_exists='replace')
    df_poi.to_sql('poi', connection, if_exists='replace') 
    print("Fin chargement postgres à {date} \n".format(date=datetime.today()))


# récupération du fichier classes_fr, traitement pour intégrer le niveau
# df_classes = traitement_classes_type()
# print("df_classe :\n " , df_classes.head())
# with engine.begin() as connection:
#     df_classes.to_sql('classes_types', connection, if_exists='replace')
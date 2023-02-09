import pandas as pd
import requests
from sqlalchemy import create_engine


KEY = '380d2fe9-2c9c-4190-a79e-8301b37d03fb'
URL = 'https://diffuseur.datatourisme.fr/webservice/bfadcf44012b7156ca3e297b468c4f75/' + KEY
DATABASE_URL = 'postgresql://postgres:password@localhost:5432/postgres'

data = requests.get(URL).json()
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
}

df = df[columns.keys()]  # Keep only useful columns
df = df.rename(columns=columns)
df = df.applymap(lambda x: ', '.join(x) if isinstance(x, list) else x)  # Transform lists into strings

print(df.head())

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

def categorie(type):
    for c in categories.keys():
        if c in type.split(', '):
            return c
    return None

df['type'] = df['type'].apply(categorie)  # keep only one high-level categorie
df = df.dropna(subset=['id', 'nom', 'longitude', 'latitude', 'type'])  # Suppress row with null mandatory data
# Conversion columns
convert_dict = {'latitude': float,
                    'longitude': float
                    }
df = df.astype(convert_dict)

df = df.set_index('id', verify_integrity=True)  # Ensure column id contains unique values


with create_engine(DATABASE_URL).begin() as connection:
    df.to_sql('poi', connection, if_exists='replace')  # Load dataframe in postgresql
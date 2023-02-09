/* 4 types de POI : 
Product : un objet touristique qui peut se consommer (ex: une chambre d'hôtel, une pratique d'activité, une visite guidée, ...)
Tour :  un itinéraire touristique est un POI qui propose un itinéraire composé d’étapes formant un parcours. 
EntertainmentAndEvent : manifestations, festivals, exposition, ou tout autre évènement ayant un début et une fin
PlaceOfInterest : un lieu ayant un intérêt touristique (ex: un site naturel, un site culturel, un village, un restaurant, ...)
*/
select t.*, p.* from itineraire_poi p
join itineraire_types t on t.poi_id = p.id 
join (select distinct poi_id from itineraire_types 
	where type like '%PlaceOfInterest%' 
	order by poi_id) liste
	on liste.poi_id = p.id
order by p.id, t.type
limit 50


select t.*, c.*, p.* from itineraire_poi p
join itineraire_types t on t.poi_id = p.id 
join (select distinct poi_id from itineraire_types 
	where type like '%PlaceOfInterest%' 
	order by poi_id) liste
	on liste.poi_id = p.id
left join classes_type c on t.type = c.type
order by p.id, t.type
limit 50

select * from itineraire_poi
where upper(nom) like '%GALOC%'
limit 10;

select type, count(*) from itineraire_types 
where type in ('Product','Tour','EntertainmentAndEvent','PlaceOfInterest')
group by type;

select distinct type from itineraire_types
order by type;

select * from itineraire_poi 
where id = '268543' limit 10; 

select * from itineraire_types
where poi_id = '268543' ;

select count(distinct id) from itineraire_poi;
-- 41099 POI

select count(distinct poi_id) from itineraire_types
where type = 'PointOfInterest' ;
-- 41099 POI >> ils sont tous PointOfInterest

select count(distinct poi_id) from itineraire_types
where type = 'urn:resource' ;
-- 41099 POI >> ils sont tous urn:resource

-- il faut enlever tous les types 'schema:%xxx', 'PointOfInterest', 'urn:resource'

select * from classes_types
order by level desc;

-- liste des sous types de PlaceOfInterest
select distinct type, label_type from classes_types c2
where c2.level = 2 and c2.parent_type='PlaceOfInterest'
order by  2;

/*
"Store"	"Commerce de détail"
"TastingProvider"	"Fournisseur de dégustation"
"Accommodation"	"Hébergement"
"MedicalPlace"	"Lieu de santé"
"ActivityProvider"	"Prestataire d'activité"
"ServiceProvider"	"Prestataire de service"
"FoodEstablishment"	"Restauration"
"TouristInformationCenter"	"Service d'information touristique"
"ConvenientService"	"Service pratique"
"CulturalSite"	"Site culturel"
"BusinessPlace"	"Site d'affaires"
"NaturalHeritage"	"Site naturel"
"SportsAndLeisurePlace"	"Site sportif, récréatif et de loisirs"
"Transport"	"Transport"
*/

-- liste des sous sous types
select c3.*, c2.* from classes_types c2
join classes_types c3 on c3.parent_type = c2.type and c2.level = 2
where c2.parent_type='PlaceOfInterest' 
and c2.type in ('CulturalSite', 'NaturalHeritage', 'FoodEstablishment')
order by c2.label_type, c3.label_type;

---------------------------------
-- selection d'un premier extrait de points d'interet pour neo4j
---------------------------------
-- recherche de type à prendre en compte
select c3.*, c2.* from classes_types c2
join classes_types c3 on c3.parent_type = c2.type and c2.level = 2
where c2.parent_type='PlaceOfInterest' 
and c2.type in ('CulturalSite', 'NaturalHeritage', 'FoodEstablishment')
and c3.label_type in ('Restaurant','Musée','Site religieux','Cascade','Point de vue')
order by c2.label_type, c3.label_type;


select t.*, p.* from itineraire_poi p
join itineraire_types t on t.poi_id = p.id 
where t.type in ('Restaurant','Museum','ReligiousSite','Waterfall','PointOfView')
order by p.id, t.type
limit 50

-- verif nombre de points
select count(*) from itineraire_poi p
join itineraire_types t on t.poi_id = p.id 
where t.type in ('Restaurant','Museum','ReligiousSite','Waterfall','PointOfView');

-- verif unicité
select p.id ,count(*) from itineraire_poi p
join itineraire_types t on t.poi_id = p.id 
where t.type in ('Restaurant','Museum','ReligiousSite','Waterfall','PointOfView')
group by p.id order by 2 desc;

-- requete d'extraction pour les noeuds
select p.id, p.latitude, p.longitude, t.type 
-- , p.url, p.contact_homepage
from itineraire_poi p
join itineraire_types t on t.poi_id = p.id 
where t.type in ('Restaurant','Museum','ReligiousSite','Waterfall','PointOfView')
and p.id not in ('202098', '202099')
order by p.id, t.type
limit 50

-- pour les liens 
-- extraction des types >> similarité de type pour les recherches de parcours
-- autre  liens ? categorie de prix, temps de visite, popularité, 
-- Proximité geographique utiliser les clusters ?



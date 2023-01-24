/* 4 types de POI : 
Product : un objet touristique qui peut se consommer (ex: une chambre d'hôtel, une pratique d'activité, une visite guidée, ...)
Tour :  un itinéraire touristique est un POI qui propose un itinéraire composé d’étapes formant un parcours. 
EntertainmentAndEvent : manifestations, festivals, exposition, ou tout autre évènement ayant un début et une fin
PlaceOfInterest : un lieu ayant un intérêt touristique (ex: un site naturel, un site culturel, un village, un restaurant, ...)
*/
select t.*, p.* from itineraire_poi p
join itineraire_types t on t.poi_id = p.id 
join (select distinct poi_id from itineraire_types 
	where type like '%EntertainmentAndEvent%' 
	order by poi_id) liste
	on liste.poi_id = p.id
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

-- on enleve tous les types 'schema:%', 'PointOfInterest', 'urn:resource'




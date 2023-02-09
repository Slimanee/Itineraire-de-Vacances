-- Table: public.itineraire_poi

-- DROP TABLE IF EXISTS public.itineraire_poi;

CREATE TABLE IF NOT EXISTS public.itineraire_poi_2
(
    id text COLLATE pg_catalog."default",
    url text COLLATE pg_catalog."default",
    nom text COLLATE pg_catalog."default",
    commentaire text COLLATE pg_catalog."default",
    contact_email text COLLATE pg_catalog."default",
    contact_telephone text COLLATE pg_catalog."default",
    contact_homepage text COLLATE pg_catalog."default",
    adresse text COLLATE pg_catalog."default",
    ville text COLLATE pg_catalog."default",
    code_postal text COLLATE pg_catalog."default",
    latitude text COLLATE pg_catalog."default",
    longitude text COLLATE pg_catalog."default",
    latlon text COLLATE pg_catalog."default",
    altitude text COLLATE pg_catalog."default",
    ouvert_date_de text COLLATE pg_catalog."default",
    ouvert_date_a text COLLATE pg_catalog."default",
    ouvert_heure_de text COLLATE pg_catalog."default",
    ouvert_heure_a text COLLATE pg_catalog."default",
    horaire text COLLATE pg_catalog."default",
    prix_min text COLLATE pg_catalog."default",
    prix_max text COLLATE pg_catalog."default",
    currency text COLLATE pg_catalog."default",
    prix_de text COLLATE pg_catalog."default",
    prix_a text COLLATE pg_catalog."default",
    updated_at timestamp with time zone
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.itineraire_poi
    OWNER to postgres;
-- Index: ix_itineraire_poi_id

-- DROP INDEX IF EXISTS public.ix_itineraire_poi_id;

CREATE INDEX IF NOT EXISTS ix_itineraire_poi_id
    ON public.itineraire_poi USING btree
    (id COLLATE pg_catalog."default" ASC NULLS LAST)
    TABLESPACE pg_default;
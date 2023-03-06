import folium
import pandas as pd
import route
import streamlit as st


def type_to_icon(s):
    if "Hébergement" in s:
        return "icons/lodging.png"
    if "Restauration" in s:
        return "icons/restaurant.png"
    if "Site culturel" in s:
        return "icons/museum.png"
    if "Site naturel" in s:
        return "icons/park.png"
    if "Site sportif et de loisirs" in s:
        return "icons/golf.png"
    return "icons/business.png"


def array_to_string(s):
    return ", ".join([x.strip('"') for x in s.strip("{}").split(",")]) if s else ""


def float_to_5dstring(s):
    return "" if pd.isnull(s) else f"{int(s):05d}"


@st.cache_resource
def get_map(df_communes, df, df_hotel_restaurant, mode):
    m = folium.Map(control_scale=True)

    folium.Marker(
        location=[df_communes.iloc[0].latitude, df_communes.iloc[0].longitude],
        tooltip=f"Point de départ: {df_communes.iloc[0].commune} ({df_communes.iloc[0].departement})",
        icon=folium.features.CustomIcon(
            icon_image=type_to_icon("Depart"), icon_size=(50, 50)
        ),
    ).add_to(m)

    for row in pd.concat([df, df_hotel_restaurant]).itertuples():
        html = (
            f"<b>{row.nom}</b><br>"
            f"{row.description}<br>"
            f"#️⃣ {array_to_string(row.type)}<br>"
            f"☎️ {array_to_string(row.telephone)}<br>"
            f"✉️ {array_to_string(row.email)}<br>"
            f"@ {array_to_string(row.site_internet)}<br>"
            f"🏠 {array_to_string(row.adresse)} {float_to_5dstring(row.code_postal)} {array_to_string(row.ville)}"
        )
        folium.Marker(
            location=[row.latitude, row.longitude],
            popup=folium.Popup(html, min_width=400, max_width=400),
            tooltip=row.nom,
            icon=folium.features.CustomIcon(
                icon_image=type_to_icon(row.type), icon_size=(50, 50)
            ),
        ).add_to(m)

    locations = route.get_route(df[["latitude", "longitude"]].values.tolist() + [[df_communes.iloc[0].latitude, df_communes.iloc[0].longitude]], mode)
    folium.PolyLine(locations, weight=5).add_to(m)

    df_loc = pd.DataFrame(locations + df_hotel_restaurant[["latitude", "longitude"]].values.tolist())
    sw = df_loc.min().values.tolist()
    ne = df_loc.max().values.tolist()
    m.fit_bounds([sw, ne])

    return m

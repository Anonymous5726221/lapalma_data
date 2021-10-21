import zipfile
from datetime import datetime as dt

from pykml.factory import KML_ElementMaker as KML
import lxml.etree as ET


def df_to_kml(df):
    styles = {
        "mag0": {
            "name": "mag_0_2.png",
            "scale": 0.4375
        },
        "mag1": {
            "name": "mag_2_3.png",
            "scale": 0.4375
        },
        "mag2": {
            "name": "mag_3_4.png",
            "scale": 0.4375
        },
        "mag3": {
            "name": "mag_4_9.png",
            "scale": 0.4375
        },
    }

    doc = KML.kml(
        KML.Document(
            KML.Name(f"Last {len(df)} eq in La Palma"),
            KML.Folder(
                KML.name(f"Last {len(df)} eq in La Palma"),
            )
        )
    )


    for ix, r in df.iterrows():

        if r.mag <= 2:
            style = styles.get("mag0")
        elif 2 < r.mag <= 3:
            style = styles.get("mag1")
        elif 3 < r.mag <= 4:
            style = styles.get("mag2")
        else:
            style = styles.get("mag3")

        pm = KML.Placemark(
            KML.description(f"{r.magtype} {r.mag} @ {r.depth}. ({r.time})\nhttps://www.emsc.eu/Earthquake/earthquake.php?id={r.source_id}"),
            KML.Point(
                KML.coordinates(f"{r.lon},{r.lat}")
            ),
            KML.LookAt(
                KML.longitude(r.lon),
                KML.latitude(r.lat),
                KML.altitude(r.depth)
            ),
            KML.TimeStamp(
                KML.when((r.time).strftime('%Y-%m-%dT%H:%MZ')),
            ),
            KML.Style(
                KML.IconStyle(
                    KML.scale(style.get("scale")),
                    KML.Icon(
                        KML.href(style.get("name"))
                    ),
                ),
            )
        )

        doc.Document.Folder.append(
            pm
        )

    return ET.tostring(doc, pretty_print=True)


def kml_to_zip(df):
    data = df_to_kml(df)

    tmp_zip = f"/tmp/{int(dt.utcnow().timestamp() * 1000000)}_canary_eq.zip"

    zf = zipfile.ZipFile(
        tmp_zip,
        mode='w',
        compression=zipfile.ZIP_DEFLATED,
    )
    try:
        zf.write('assets/mag_0_2.png', "mag_0_2.png")
        zf.write('assets/mag_2_3.png', "mag_2_3.png")
        zf.write('assets/mag_3_4.png', "mag_3_4.png")
        zf.write('assets/mag_4_9.png', "mag_4_9.png")
        zf.writestr("canary_eq.kml", data=data)
    finally:
        zf.close()

    return tmp_zip


def df_to_csv(df):
    tmp_csv = f"/tmp/{int(dt.utcnow().timestamp() * 1000000)}_canary_eq.csv"

    df.to_csv(tmp_csv)

    return tmp_csv

import logging
from zipfile import ZipFile
from urllib.parse import urlparse
import os
import json

import requests
from georss_generic_client import GenericFeed
import lxml.etree as ET

from ..server import cache


logger = logging.getLogger(__name__)

COPERNICUS_JSON = os.path.join(os.path.abspath(os.sep), "tmp", "copernicus_data.json")
COPERNICUS_FEED_URL = "https://emergency.copernicus.eu/mapping/list-of-components/EMSR546/aemfeed"


def copernicus_entries():
    logger.info("Fetching Copernicus publication")

    feed = GenericFeed(
        (28.668274, -17.854698),
        filter_categories=["Product: Production finished", "Product: Quality approved"],
        url=COPERNICUS_FEED_URL
    )
    status, entries = feed.update()

    if status != "OK":
        raise Exception(f"Failed to get entries from Copernicus: {status}")

    return entries


def entry_data_url(entry):
    logger.info("Retrieving data url from copernicus publication")

    parser = ET.HTMLParser()
    html_tree = ET.fromstring(entry.description, parser)

    page_link = html_tree.xpath("./body/div/div/a")[0].attrib.get("href")

    r = requests.get(page_link)
    html_tree = ET.fromstring(r.content, parser)

    path = html_tree.xpath("//div[contains(@class, 'field-content')]/a")[0].attrib.get("href")

    url = "https://emergency.copernicus.eu" + path

    return url


def download_copernicus_zip(url):
    logger.info("Downloading archive from Copernicus website")

    filename = str(urlparse(url).path.split("/")[-1])
    filepath = os.path.join(os.path.abspath(os.sep), "tmp", filename)

    # Check if today data was downloaded already
    if os.path.exists(filepath):
        logger.info("Data previously downloaded, using cache.")
        return filepath

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:93.0) Gecko/20100101 Firefox/93.0"
    }

    forms_data_clicked = {
        "confirmation": "1",
        "op": "+Download+file+",
        "form_id": "emsmapping_disclaimer_download_form"
    }

    r = requests.post(url, headers=headers, data=forms_data_clicked)

    if r.status_code != 200:
        raise ConnectionError(r.status_code, r.reason)

    with open(filepath, "wb") as outf:
        outf.write(r.content)

    return filepath


def extract_copernicus_layers(filepath):

    layers = {}
    with ZipFile(filepath) as zp:
        for f in zp.namelist():
            if f.endswith(".json"):
                with zp.open(f) as zf:
                    layers[layer_name(f)] = json.load(zf)

    with open(COPERNICUS_JSON, "w") as outf:
        json.dump(layers, outf, indent=2)

    return list(layers.keys())


def layer_options(layers):
    layers_matcher = {
        "areaOfInterest_Area": "Area of interest (Copernicus observed area)",
        "builtUp_Point": "Built up (Building destroyed or damaged. WIP)",
        "facilities_Area": "Facilities Area (Not too sure)",
        "hydrography_Line": "Hydrography (Water lines? WIP)",
        "imageFootprint_Area": "Image Footprint",
        "naturalLandUse_Area": "Natural Land Use (Different type of lands (Forestry, agriculture, ... WIP)",
        "observedEvent_Area": "Lava Flow (Lava flow area)",
        "observedEvent_Point": "Current Vents (Current vents location. WIP)",
        "physiography_Line": "Physiography (Relief lines)",
        "transportation_Line": "Transportation (Damaged transportation infrastructure. WIP)",
    }

    return {k: v for k, v in layers_matcher.items() if k in layers}


def layer_name(filename):

    sel = filename.split("_")[4]
    name = sel[0:-1]
    geometry = sel[-1]

    GEOMETRY = {
        "A": "Area",
        "P": "Point",
        "L": "Line"
    }

    return "_".join([name, GEOMETRY.get(geometry, "Unknown")])


def overlay(name):

    with open(COPERNICUS_JSON) as inf:
        overlays = json.load(inf)
        return overlays.get(name)


@cache.memoize(timeout=3600*24)
def get_copernicus_data():

    entries = copernicus_entries()
    data_url = entry_data_url(entries[-1])
    data_filepath = download_copernicus_zip(data_url)

    layers = extract_copernicus_layers(data_filepath)

    return layers


if __name__ == '__main__':
    layers = get_copernicus_data()

    with open("copernicus_data.json", "w") as outf:
        json.dump(layers, outf, indent=2)

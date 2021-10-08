from datetime import datetime as dt
from datetime import timedelta
from datetime import timezone
from urllib.parse import urlencode

import requests


CANARY_BOX = {
    "min_lattitude": 27,
    "max_lattitude": 30.4,
    "min_logitude": -19.20,
    "max_longitude": -13.20,
}


class SeismicPortal(object):

    def __init__(self):
        self.url = "https://www.seismicportal.eu"
        pass

    def _paginate(self, url, q):

        s = requests.Session()

        # r = requests.get(url, params={k: v for k, v in q.items() if v})
        qry = urlencode({k: v for k, v in q.items() if v}).replace('%3A', ':')

        req = requests.Request(method='GET', url=url)
        prep = req.prepare()
        prep.url = "?".join([url, qry])
        r = s.send(prep)

        if r.status_code != 200:
            raise ConnectionError(r.status_code, r.reason)

        data = r.json().get("features")

        if len(data) == q.get("limit"):
            q["offset"] += q["limit"]

            data.extend(self._paginate(url, q))

        return data

    def download_earthquakes(
            self,
            start_time=dt.now() - timedelta(days=7),
            end_time=dt.now(),
            min_lattitude=0.0,
            max_lattitude=0.0,
            min_logitude=0.0,
            max_longitude=0.0,
            circle_lattitude=0.0,
            circle_longitude=0.0,
            min_radius=0.0,
            max_radius=0.0,
            min_depth=0.0,
            max_depth=0.0,
            min_magnitude=0.0,
            max_magnitude=0.0,
            magnitude_type="",
            include_all_origins=False,
            include_arrivals=False,
            event_id="",
            limit=1000,
            offset=1,
            order_by="",
            contibutor="",
            catalog="",
            update_after="",
            format="json",
            results=0
    ):
        dt.now().astimezone()
        url = "".join([self.url, "/fdsnws/event/1/query"])

        start_time = start_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
        end_time = end_time.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")

        q = {
            "start": start_time,
            "end": end_time,
            "minlat": min_lattitude,
            "maxlat": max_lattitude,
            "minlon": min_logitude,
            "maxlon": max_longitude,
            "lat": circle_lattitude,
            "lon": circle_longitude,
            "minradius": min_radius,
            "maxradius": max_radius,
            "mindepth": min_depth,
            "maxdepth": max_depth,
            "minmag": min_magnitude,
            "maxmag": max_magnitude,
            "magtype": magnitude_type,
            "includeallorigins": include_all_origins,
            "includearrivals": include_arrivals,
            "eventid": event_id,
            "limit": limit,
            "offset": offset,
            "orderby": order_by,
            "contibutor": contibutor,
            "catalog": catalog,
            "updateafter": update_after,
            "format": "json"
        }

        data = self._paginate(url, q)

        print(f"{len(data)} earthquakes downloaded.")
        
        return data

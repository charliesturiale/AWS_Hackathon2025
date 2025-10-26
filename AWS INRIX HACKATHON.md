**API ENDPOINT TOKEN: Mxc2vd1fRYxkD4S4Y22GO3dGJ**

---

**311 Reports API Endpoint:**  
[https://data.sfgov.org/resource/vw6y-z8j6.json?$query=SELECT%0A%20%20%60requested\_datetime%60%2C%0A%20%20%60status\_description%60%2C%0A%20%20%60service\_name%60%2C%0A%20%20%60service\_subtype%60%2C%0A%20%20%60point\_geom%60%0AWHERE%0A%20%20caseless\_one\_of(%0A%20%20%20%20%60service\_name%60%2C%0A%20%20%20%20%22Aggressive%2FThreatening%22%2C%0A%20%20%20%20%22Encampment%22%2C%0A%20%20%20%20%22Encampments%22%0A%20%20)%0A%20%20AND%20(%60requested\_datetime%60%0A%20%20%20%20%20%20%20%20%20%3E%20%222025-10-19T01%3A26%3A14%22%20%3A%3A%20floating\_timestamp)%0AORDER%20BY%20%60requested\_datetime%60%20DESC%20NULL%20LAST](https://data.sfgov.org/resource/vw6y-z8j6.json?$query=SELECT%0A%20%20%60requested_datetime%60%2C%0A%20%20%60status_description%60%2C%0A%20%20%60service_name%60%2C%0A%20%20%60service_subtype%60%2C%0A%20%20%60point_geom%60%0AWHERE%0A%20%20caseless_one_of\(%0A%20%20%20%20%60service_name%60%2C%0A%20%20%20%20%22Aggressive%2FThreatening%22%2C%0A%20%20%20%20%22Encampment%22%2C%0A%20%20%20%20%22Encampments%22%0A%20%20\)%0A%20%20AND%20\(%60requested_datetime%60%0A%20%20%20%20%20%20%20%20%20%3E%20%222025-10-19T01%3A26%3A14%22%20%3A%3A%20floating_timestamp\)%0AORDER%20BY%20%60requested_datetime%60%20DESC%20NULL%20LAST)

{  
    "requested\_datetime": "2025-10-24T22:49:55.000",  
    "status\_description": "Open",  
    "service\_name": "Encampment",  
    "service\_subtype": "encampment",  
    "point\_geom": {  
      "type": "Point",  
      "coordinates": \[-122.42352075, 37.78433716\]  
    }  
  },

311 Cases API Documentation: [https://dev.socrata.com/foundry/data.sfgov.org/vw6y-z8j6](https://dev.socrata.com/foundry/data.sfgov.org/vw6y-z8j6)

---

**Real-Time PD Dispatch Reports API Endpoint:**  
[https://data.sfgov.org/resource/gnap-fj3t.json?$query=SELECT%0A%20%20%60entry\_datetime%60%20AS%20%60entry\_datetime%60%2C%0A%20%20%60call\_type\_original\_desc%60%20AS%20%60call\_type\_original\_desc%60%2C%0A%20%20%60call\_type\_final\_desc%60%20AS%20%60call\_type\_final\_desc%60%2C%0A%20%20%60intersection\_name%60%20AS%20%60intersection\_name%60%2C%0A%20%20%60intersection\_point%60%20AS%20%60intersection\_point%60%0AWHERE%0A%20%20caseless\_one\_of(%0A%20%20%20%20%60call\_type\_original\_desc%60%2C%0A%20%20%20%20%22EXPLOSIVE%20FOUND%22%2C%0A%20%20%20%20%22SUSPICIOUS%20PERSON%22%2C%0A%20%20%20%20%22FIGHT%20W%2FWEAPONS%22%2C%0A%20%20%20%20%22FIGHT%20NO%20WEAPON%22%2C%0A%20%20%20%20%22ASSAULT%20%2F%20BATTERY%20DV%22%2C%0A%20%20%20%20%22PURSE%20SNATCH%22%2C%0A%20%20%20%20%22EXPLOSION%22%2C%0A%20%20%20%20%22ROBBERY%22%2C%0A%20%20%20%20%22THREATS%20%2F%20HARASSMENT%22%2C%0A%20%20%20%20%22STRONGARM%20ROBBERY%22%2C%0A%20%20%20%20%22INDECENT%20EXPOSURE%22%2C%0A%20%20%20%20%22PERSON%20BREAKING%20IN%22%2C%0A%20%20%20%20%22BURGLARY%22%0A%20%20)%0AORDER%20BY%20%60entry\_datetime%60%20DESC%20NULL%20LAST](https://data.sfgov.org/resource/gnap-fj3t.json?$query=SELECT%0A%20%20%60entry_datetime%60%20AS%20%60entry_datetime%60%2C%0A%20%20%60call_type_original_desc%60%20AS%20%60call_type_original_desc%60%2C%0A%20%20%60call_type_final_desc%60%20AS%20%60call_type_final_desc%60%2C%0A%20%20%60intersection_name%60%20AS%20%60intersection_name%60%2C%0A%20%20%60intersection_point%60%20AS%20%60intersection_point%60%0AWHERE%0A%20%20caseless_one_of\(%0A%20%20%20%20%60call_type_original_desc%60%2C%0A%20%20%20%20%22EXPLOSIVE%20FOUND%22%2C%0A%20%20%20%20%22SUSPICIOUS%20PERSON%22%2C%0A%20%20%20%20%22FIGHT%20W%2FWEAPONS%22%2C%0A%20%20%20%20%22FIGHT%20NO%20WEAPON%22%2C%0A%20%20%20%20%22ASSAULT%20%2F%20BATTERY%20DV%22%2C%0A%20%20%20%20%22PURSE%20SNATCH%22%2C%0A%20%20%20%20%22EXPLOSION%22%2C%0A%20%20%20%20%22ROBBERY%22%2C%0A%20%20%20%20%22THREATS%20%2F%20HARASSMENT%22%2C%0A%20%20%20%20%22STRONGARM%20ROBBERY%22%2C%0A%20%20%20%20%22INDECENT%20EXPOSURE%22%2C%0A%20%20%20%20%22PERSON%20BREAKING%20IN%22%2C%0A%20%20%20%20%22BURGLARY%22%0A%20%20\)%0AORDER%20BY%20%60entry_datetime%60%20DESC%20NULL%20LAST)

{  
    "entry\_datetime": "2025-10-26T02:11:01.000",  
    "call\_type\_original\_desc": "FIGHT NO WEAPON",  
    "call\_type\_final\_desc": "FIGHT NO WEAPON",  
    "intersection\_name": "01ST ST \\\\ HOWARD ST",  
    "intersection\_point": {  
      "type": "Point",  
      "coordinates": \[-122.396034766, 37.788535931\]  
    }  
  },

Real-Time PD Dispatch Reports API Documentation: [https://dev.socrata.com/foundry/data.sfgov.org/gnap-fj3t](https://dev.socrata.com/foundry/data.sfgov.org/gnap-fj3t)
# Nearby agrovets (fake DB – editable)
AGROVETS = [
    {"name": "Kenya Agrovet Center", "lat": -1.286389, "lon": 36.817223},
    {"name": "GreenLife Agrovet", "lat": -1.2921, "lon": 36.8219},
    {"name": "AgriFarm Supplies", "lat": -1.2801, "lon": 36.8155},
]

import math

def distance(lat1, lon1, lat2, lon2):
    R = 6371
    d = math.radians(lat2-lat1)
    dl = math.radians(lon2-lon1)
    a = (math.sin(d/2)**2 +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) *
         math.sin(dl/2)**2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))


def find_nearby_agrovet(lat, lon):
    if not lat or not lon:
        return None

    lat = float(lat)
    lon = float(lon)

    closest = None
    min_dist = 999999

    for a in AGROVETS:
        dist = distance(lat, lon, a["lat"], a["lon"])
        if dist < min_dist:
            min_dist = dist
            closest = a

    closest["distance"] = round(min_dist, 1)
    return closest



# Treatment guide
def treatment_guide(label):
    treatments = {
        "Maize - Leaf Blight": "Apply Mancozeb or Copper fungicide.",
        "Maize - Rust": "Use Tilt (Propiconazole) or Mancozeb.",
        "Maize - Corn Smut": "Remove infected cobs + crop rotation.",
        "Tomato - Early Blight": "Apply Ridomil Gold or Mancozeb.",
        "Tomato - Late Blight": "Use Metalaxyl + Chlorothalonil.",
        "Tomato - Mosaic Virus": "Remove infected plant + insect control.",
        "Beans - Rust": "Spray Copper Oxychloride.",
        "Beans - Angular Leaf Spot": "Use Mancozeb weekly.",
        "Kales - Black Rot": "Apply Copper-based fungicides.",
        "Kales - Downy Mildew": "Use Ridomil or Copper sprays.",
        "Cabbage - Black Rot": "Destroy infected plants + rotate crops.",
        "Cabbage - Clubroot": "Apply lime to soil; improve drainage.",
        "Healthy": "Your crop appears healthy!"
    }

    return treatments.get(label, "No treatment found.")




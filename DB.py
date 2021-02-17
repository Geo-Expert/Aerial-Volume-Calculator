import numpy as np
import pandas
import shapely.wkt
import pyproj
from shapely.ops import transform
from datetime import datetime


def recent_date(array):
    dates = []
    for date in array[:, 1]:
        dates.append(datetime.strptime(date, "%d/%m/%Y").date())
    indices = array[:, 0] - 1
    sorted_indices = indices[np.argsort(dates)]
    return sorted_indices[-1]


def poly_within_poly(poly1, poly2):
    return poly1.within(poly2)


def project_poly(poly, target_epsg):
    source_epsg = 4326
    transformation = pyproj.Transformer.from_crs(source_epsg, target_epsg, always_xy=True)
    projected_poly = transform(transformation.transform, poly)
    return projected_poly


def read_db(db_path):
    db = pandas.read_csv(db_path)
    return db.values


def find_terrain(db_path, aoi):
    indices = []
    db = read_db(db_path)

    for i in range(db.shape[0]):
        terrain_epsg = db[i, 4]
        terrain_poly = db[i, 6]
        terrain_poly = shapely.wkt.loads(terrain_poly)
        projected_aoi = project_poly(aoi, terrain_epsg)

        if poly_within_poly(projected_aoi, terrain_poly):
            indices.append(i)

    if len(indices) == 1:
        index = indices[0]

    elif len(indices) > 1:
        match_db = db[indices]
        index = recent_date(match_db[:, (0, 5)])

    else:
        return None, None, None, None, None, 401

    terrain_poly = db[index, 6]
    terrain_poly = shapely.wkt.loads(terrain_poly)
    terrain_path = db[index, 2]
    terrain_date = db[index, 5]
    terrain_sample_size = db[index, 3]
    terrain_epsg = db[index, 4]
    projected_aoi = project_poly(aoi, terrain_epsg)

    return terrain_poly, terrain_path, terrain_date, terrain_sample_size, projected_aoi, 200



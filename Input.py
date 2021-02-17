import json
import shapely.wkt


def check_geometry(poly):
    return poly.is_valid


def read_json(path):
    with open(path) as f:
        data = json.load(f)
        return data


def validate_input(aoi, sample_size, units):

    if sample_size <= 0:
        return 402

    if units != 'cubic_meters' and units != 'cubic_foot':
        return 403

    geometry = check_geometry(aoi)
    if not geometry:
        return 404

    return 200

# def output(volume, date):
#
#     json_output = {'volume': volume, 'date': terrain_date}


def input(path):

    data = read_json(path)
    aoi = data['area']
    aoi = shapely.wkt.loads(aoi)
    sample_size = data['sampling_distance']
    units = data['volume_units']
    status_code = validate_input(aoi, sample_size, units)
    return status_code, aoi, sample_size, units
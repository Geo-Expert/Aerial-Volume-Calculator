import os
import Input
import DB
import Volume


def main(json_path):
    folder_path = os.path.dirname(str(json_path))[2:]
    db_path = 'db.csv'
    status_code, aoi, req_sample_size, units = Input.input(json_path)
    if status_code != 200:
        print('status: ', status_code)
        return None, status_code

    terrain_poly, terrain_path, terrain_date, orig_sample_size, projected_aoi, status_code = DB.find_terrain(os.path.join(folder_path, db_path), aoi)
    if status_code != 200:
        print('status: ', status_code)
        return None, status_code

    volume = Volume.calc_volume(os.path.join(folder_path, terrain_path), projected_aoi, req_sample_size, orig_sample_size, units, terrain_poly)

    json_output = {'volume': volume, 'date': terrain_date}

    return json_output, status_code
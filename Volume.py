from PIL import Image
import numpy as np
from pykrige.ok import OrdinaryKriging
from shapely import geometry
import scipy.ndimage.interpolation as interp


def translate_aoi(aoi, sample_size):
    xy_aoi = np.asarray(list(zip(*aoi.exterior.coords.xy)))
    x_aoi, y_aoi = xy_aoi[:, 0], xy_aoi[:, 1]
    x_min_aoi, y_max_aoi = aoi.bounds[0], aoi.bounds[3]
    x = ((x_aoi - x_min_aoi) / sample_size).astype(int)
    y = ((y_max_aoi - y_aoi) / sample_size).astype(int)
    new_aoi = geometry.Polygon(np.vstack((x, y)).T)
    return new_aoi


def poly_mask(grid, poly):
    masked_grid = np.copy(grid)
    for i in range(masked_grid.shape[0]):
        for j in range(masked_grid.shape[1]):
            point = geometry.Point(j, i)
            if point.within(poly) is False:
                masked_grid[i, j] = 0
    return masked_grid


def resample_grid(grid, orig_sample_size, req_sample_size):
    factor = orig_sample_size / req_sample_size
    new_grid = interp.zoom(grid, factor, output=float, order = 3, mode='constant')
    return new_grid


def kriging(x, y, z, shape):
    gridx = np.arange(0.0, shape[1], 1)
    gridy = np.arange(0.0, shape[0], 1)
    kriging = OrdinaryKriging(x, y, z, variogram_model="linear", verbose=False, enable_plotting=False)
    ground_grid, ss = kriging.execute("grid", gridx, gridy)
    return ground_grid


def ground_surface(terrain, sample_size, aoi):
    xy_aoi = np.asarray(list(zip(*aoi.exterior.coords.xy)))
    x_aoi, y_aoi = xy_aoi[:, 0], xy_aoi[:, 1]
    x_min_aoi, y_max_aoi = aoi.bounds[0], aoi.bounds[3]
    x = ((x_aoi - x_min_aoi)/sample_size).astype(int)
    y = ((y_max_aoi - y_aoi)/sample_size).astype(int)
    z = terrain[y, x]
    ground_grid = kriging(x, y, z, terrain.shape)
    return np.asarray(ground_grid)


def clip_raster_to_aoi(raster, raster_bbox, sample_size, aoi_bbox):
    min_x_aoi, min_y_aoi, max_x_aoi, max_y_aoi = aoi_bbox[0], aoi_bbox[1], aoi_bbox[2], aoi_bbox[3]
    min_x_raster, max_y_raster = raster_bbox[0], raster_bbox[3]
    min_x = int((min_x_aoi - min_x_raster) / sample_size) - 1
    min_y = int((max_y_raster - max_y_aoi) / sample_size) - 1
    max_x = int((max_x_aoi - min_x_raster) / sample_size) + 1
    max_y = int((max_y_raster - min_y_aoi) / sample_size) + 1
    cliped_raster = raster[min_y:max_y, min_x:max_x]
    return cliped_raster


def read_tiff(path):
    im = Image.open(path)
    return np.array(im)


def calc_volume(terrain_path, aoi, req_sample_size, orig_sample_size, units, terrain_poly):
    terrain = read_tiff(terrain_path)
    terrain = clip_raster_to_aoi(terrain, terrain_poly.bounds, orig_sample_size, aoi.bounds)
    ground = ground_surface(terrain, orig_sample_size, aoi)
   
    terrain = resample_grid(terrain, orig_sample_size, req_sample_size)
    ground = resample_grid(ground, orig_sample_size, req_sample_size)
    delta = terrain - ground
    
    aoi = translate_aoi(aoi, req_sample_size)
    delta = poly_mask(delta, aoi)
    delta[delta < 0] = 0
    
    sum_heights = np.sum(delta)
    volume = req_sample_size * req_sample_size * sum_heights
    if units == 'cubic_foot':
        volume = volume * 35.3146667
    return round(volume,5)
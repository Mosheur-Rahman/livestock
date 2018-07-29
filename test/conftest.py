__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# -------------------------------------------------------------------------------------------------------------------- #
# Imports

# Module imports
import pytest
import os

# Livestock imports
from livestock import geometry

# -------------------------------------------------------------------------------------------------------------------- #
# CMF Functions and Classes


@pytest.fixture()
def data_folder():
    parent = os.path.dirname(__file__)
    return os.path.join(parent, 'test_data')


@pytest.fixture(params=[0, 1])
def obj_file_paths(data_folder, request):
    obj_folder = os.path.join(data_folder, 'obj_to_shp')
    return os.path.join(obj_folder, f'mesh_{request.param}.obj')


@pytest.fixture()
def shapely_polygons(obj_file_paths):
    return geometry.obj_to_polygons(obj_file_paths)

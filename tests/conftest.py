__author__ = "Christian Kongsgaard"
__license__ = "MIT"

# ---------------------------------------------------------------------------- #
# Imports

# Module imports
import pytest
import os
import shutil
import cmf

# Livestock imports
from livestock import geometry
from livestock import hydrology


# ---------------------------------------------------------------------------- #
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


@pytest.fixture(params=['run_off'])
def input_files(tmpdir, data_folder, request):
    test_folder = tmpdir.mkdir('test')
    data_path = os.path.join(data_folder, request.param)
    files = os.listdir(data_path)

    for file in files:
        shutil.copyfile(os.path.join(data_path, file),
                        os.path.join(test_folder, file))

    return test_folder


@pytest.fixture()
def cmf_data(input_files):
    return hydrology.load_cmf_files(input_files)


@pytest.fixture()
def project_with_cells(cmf_data):
    (ground_list, mesh_path, weather_dict, trees_dict, outputs,
     solver_settings, boundary_dict) = cmf_data

    project = cmf.project()

    return hydrology.mesh_to_cells(project, mesh_path, False)


@pytest.fixture()
def retention_curve(cmf_data):
    (ground_list, mesh_path, weather_dict, trees_dict, outputs,
     solver_settings, boundary_dict) = cmf_data

    curve_dict = ground_list[0]['ground_type']['retention_curve']
    return hydrology.create_retention_curve(curve_dict)


@pytest.fixture()
def solve_ready_project(cmf_data):
    (ground_list, mesh_path, weather_dict, trees_dict, outputs,
     solver_settings, boundary_dict) = cmf_data

    project = cmf.project()
    hydrology.mesh_to_cells(project, mesh_path, False)

    for ground in ground_list:
        hydrology.configure_cells(project, ground)

    if trees_dict:
        for key in trees_dict.keys():
            hydrology.add_tree_to_project(project,
                                          trees_dict[key]['face_index'],
                                          trees_dict[key]['property'])

    # Create the weather
    if weather_dict:
        hydrology.create_weather(project)

    # Create boundary conditions
    if boundary_dict:
        hydrology.create_boundary_conditions(project)

    return project, solver_settings, outputs


@pytest.fixture()
def drain_mesh(data_folder):

    yield os.path.join(data_folder, 'drainage_flow')

    os.remove(os.path.join(data_folder, 'results.json'))


@pytest.fixture()
def mock_solver(monkeypatch):

    class MockClass():
        def __init__(self, project, tolerance):
            self.project = project
            self.tol = tolerance
            self.t = None

        def run(self, start_time, end_time, time_step):
            current_time = start_time
            while current_time < end_time:
                yield current_time
                current_time += time_step

    monkeypatch.setattr(cmf, 'CVodeIntegrator', MockClass)


@pytest.fixture()
def mock_gather_results(monkeypatch):

    def mock_return(cmf_project, results, time):
        pass

    monkeypatch.setattr(hydrology, 'gather_results', mock_return)
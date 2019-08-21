import os
import sys
from traceback import format_exc

from farmware_tools import device
from water_dose import WaterDose
from point_sort import PointSort
from input_store import InputStore
from plants import Plants
from control import Control

# import static logger and create shortcut function
from logger import Logger
log = Logger.log

device.log("WE ARE HERE", "success")

if __name__ == "__main__":
    # get farmware name from path
    FARMWARE_NAME = "smart-water-doser-dev"
    try:
        FARMWARE_NAME = ((__file__.split(os.sep))[len(__file__.split(os.sep)) - 3]).replace('-master', '')
    except:
        pass

    Logger.FARMWARE_NAME = FARMWARE_NAME

    # First try block logs under "init" for debugging reasons
    try:
        # create new instance of the InputStore. this will load the user input or defaults
        input_store = InputStore(FARMWARE_NAME)
        # set logger level
        Logger.set_level(input_store.input['debug'])

        log('Started with python version {}'.format(sys.version_info), message_type='info', title="init")

        currpos = {'x': 680, 'y': 380} if device.get_current_position() is None \
            else device.get_current_position()

        # init instances
        water_dose = WaterDose(FARMWARE_NAME, input_store.input)
        control = Control(FARMWARE_NAME)

        # load the plants
        plant_search_radius = input_store.input['plant_search_radius']
        plants = Plants(FARMWARE_NAME,
                        config={
                            'filter_plant_stage': ['planted', 'sprouted'],
                            'filter_min_x': currpos['x'] - plant_search_radius,
                            'filter_max_x': currpos['x'] + plant_search_radius,
                            'filter_min_y': currpos['y'] - plant_search_radius,
                            'filter_max_y': currpos['y'] + plant_search_radius,
                        })
        points_plants = plants.load_points_with_filters()

        # get closest plant to currpos
        points_sorted = PointSort.sort_points_by_dist(points_plants, currpos)
        if len(points_sorted) > 0:
            plant_closest = points_sorted[0]
            log("closest_point is {}".format(plant_closest), title="main")

        # use spread and age from MLH to decide Xms to water.
        dose_ms = water_dose.calc_watering_params(plant_closest)
        control.execute_watering(dose_ms)

    except Exception as e:
        log("Exception thrown: {}, traceback: {}".format(e, format_exc()), message_type='error', title="main")
        raise Exception(e)

    log('End', message_type='success', title=FARMWARE_NAME)
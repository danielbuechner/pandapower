# -*- coding: utf-8 -*-

# Copyright (c) 2016-2020 by University of Kassel and Fraunhofer Institute for Energy Economics
# and Energy System Technology (IEE), Kassel. All rights reserved.


from pandapower import pp_dir
import pandapower as pp
import numpy as np
import os
import pytest

folder = os.path.join(pp_dir, "test", "test_files", "old_versions")
found_versions = [file.split("_")[1].split(".json")[0] for _, _, files
                  in os.walk(folder) for file in files]


@pytest.mark.slow
@pytest.mark.parametrize("found_version", found_versions)
def test_convert_format(found_version):
    filename = os.path.join(folder, "example_%s.json" % found_version)
    if not os.path.isfile(filename):
        raise ValueError("File for version %s does not exist" % found_version)
    try:
        net = pp.from_json(filename, convert=False)
    except:
        raise UserWarning("Can not load network saved in pandapower version %s" % found_version)
    vm_pu_old = net.res_bus.vm_pu.copy()
    pp.convert_format(net)
    try:
        pp.runpp(net, run_control="controller" in net and len(net.controller) > 0)
    except:
        raise UserWarning("Can not run power flow in network "
                          "saved with pandapower version %s" % found_version)
    if not np.allclose(vm_pu_old.values, net.res_bus.vm_pu.values):
        raise UserWarning("Power flow results mismatch "
                          "with pandapower version %s" % found_version)


def test_convert_format_pq_bus_meas():
    try:
        net = pp.from_json(os.path.join(folder, "example_2.3.1.json"), convert=False)
    except:
        raise UserWarning("Can not load network for pq bus meas test")
    net = pp.convert_format(net)
    pp.runpp(net)

    bus_p_meas = net.measurement.query("element_type=='bus' and measurement_type=='p'").set_index("element", drop=True)
    assert np.allclose(net.res_bus.p_mw, bus_p_meas["value"])


if __name__ == '__main__':
    pytest.main([__file__])

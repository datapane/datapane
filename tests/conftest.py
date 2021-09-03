from datapane.common import DPMode, _setup_dp_logging, set_dp_mode

# run this at global level as want debug logging for all tests
set_dp_mode(DPMode.APP)
_setup_dp_logging(verbosity=2)


# @pytest.fixture(scope="session")
# def dp_init():
#     from datapane.common import DPMode, _setup_dp_logging, set_dp_mode
#     # init API with full debug logging
#     set_dp_mode(DPMode.APP)
#     _setup_dp_logging(verbosity=2)
#     yield
#     print("closing dp_init")

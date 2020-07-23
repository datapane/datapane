from datapane.common import DPMode, set_dp_mode, setup_local_logging

# run this at global level as want debug logging for all tests
set_dp_mode(DPMode.APP)
setup_local_logging(verbosity=2)


# @pytest.fixture(scope="session")
# def dp_init():
#     from datapane.common.utils import setup_local_logging
#     # init API with full debug logging
#     print("dp_init")
#     setup_local_logging(verbosity=2)
#     yield
#     print("closing dp_init")

import os
from pathlib import Path
from unittest import mock


@mock.patch("click.get_app_dir", autospec=True)
def test_new_config(gad, tmp_path: Path, monkeypatch):
    # TODO - is there a way to run this within the normal test framework, i.e. perhaps unloading/reloading datapane module so we can
    #  setup our mocks/patches first?

    # patch the config file path and no_analytics
    gad.return_value = str(tmp_path)
    monkeypatch.chdir(tmp_path)

    with mock.patch("datapane.client.analytics.posthog", autospec=True) as posthog, mock.patch(
        "datapane.client.analytics._NO_ANALYTICS", False
    ), mock.patch("datapane.client.api.user.ping", autospect=True) as ping:

        ping.return_value = "joebloggs@datapane.com"

        from datapane.client import config as c

        # check pre-invariants
        assert c.config.version == 4
        assert c.config.email == ""
        assert not c.config.completed_action
        assert posthog.identify.call_count == 0
        assert posthog.capture.call_count == 0

        # run login event
        import datapane as dp
        from datapane.client import config as c

        email = dp.login(token="TOKEN")
        assert email == "joebloggs@datapane.com"

        # check config file
        assert c.config.version == 4
        assert c.config.email == "joebloggs@datapane.com"
        assert c.config.completed_action

        # check analytics
        assert posthog.identify.call_count == 1
        assert posthog.capture.call_count == 2

        # load and check config file
        _config = c.Config.load()
        assert c.config.version == 4
        assert _config.email == "joebloggs@datapane.com"
        assert _config.completed_action

        # run additional event
        # depends on fe-components - only run locally
        if "CI" not in os.environ:
            from tests.client.local.api.test_reports import gen_report_simple

            report = gen_report_simple()
            report.save(path="test_out.html", name="My Wicked Report", author="Datapane Team")
            assert posthog.identify.call_count == 1
            assert posthog.capture.call_count == 3

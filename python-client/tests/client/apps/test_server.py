"""
Testing
-------

Due to their interactive nature, automated tests for datapane/app/server.py
are hard to write. Instead, below are some manual test cases that should be
done when making significant changes to server.py

* Clear out `/tmp/dp-*` (temporary directories created for serving apps)

* Create an example app in `simple.py`

    import datapane as dp
    dp.serve(dp.View(dp.Text("Some text")))

* run directly: python simple.py

  - It should print:

      ...
      App running on http://127.0.0.1:8080/
      Hit Ctrl-C to quit.

  - Visiting the URL should display the app with "Some text"
  - You should have a `/tmp/dp-*' folder
  - Hitting Ctrl-C should cleanly quit with no message printed
  - /tmp/dp-* folder should be gone

* run `python simple.py` in two terminals:

  - the second instance should open on port 8081

* run `PORT=8082 python simple.py` in a terminal:

  - It should print:

    ...
    App running on http://0.0.0.0:8082/
    ...

* copy the simple.py script into a Jupyter notebook cell and press Ctrl-Enter

  - It should show a button "Stop app server"
  - It should print the following on a normal background below the button:

      Bottle v0.13-dev server starting up (using CherootServer)...
      App running on http://127.0.0.1:8080/

  - The next cell should be active and responsive (testing that server is
    running in a background thread)

  - Visiting the URL should display the app with "Some text"

  - Pressing the stop button should print:

      Stopping server...stopped.
      Re-run cell to run server again.

    and the button should appear disabled and have the caption "Stopped"

  - /tmp/dp-* folder should be gone

  - Re-visiting the URL in a browser should immediately return an error like:

       can’t establish a connection to the server at 127.0.0.1:8080

  - Re-running the cell should run the server again, on the same port.

  - Re-starting the kernel and running all cells without first stopping the app server
    should run the app again on the same port. (testing automatic shutdown)

  - Run the app, then stop the Jupyter notebook kernel without first stopping the app server

    - /tmp/dp-*/ should be gone.

      FIXME this currently fails, despite use of `atexit`


* copy the following script into errors.py:

    import datapane as dp

    dp.serve(
        dp.View(
            dp.Interactive(
                lambda params: 1 / 0, target="target", controls=dp.Controls(dp.TextBox("input", "Input", default="X"))
            ),
            dp.Empty(name="target"),
        )
    )

  - Test in terminal:
    - python errors.py
    - Open app, press 'Go'
    - ZeroDivisionError should appear in terminal with stack trace


  - Test in Jupyter as above. ZeroDivisionError should appear in notebook window in colored background


* Fallback UI:

  * Prepare a venv that has Jupyter Lab installed but not ipywidgets
  * Prepare another venv that has datapane and ipywidgets, and install it as an IPython kernel:

      ipython kernel install --name "my-venv" --user

  * Open Jupyter Lab in the first venv, and run the `simple.py` app using the my-venv kernel
  * Expected output:

      - Your app is running on: http://127.0.0.1:8080
      - You're seeing this message because 'Jupyer Widgets' is not installed in your Jupyter notebook/lab environment.
         so the UI for controlling the app server is not visible. See Jupyter Widgets Installation instructions
      - Use dp.serve(ui="console") to use the console UI instead.

"""

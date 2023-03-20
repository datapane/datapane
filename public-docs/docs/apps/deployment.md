You can host a Datapane app from inside your current Python environment, whether that's your local machine, or a hosted notebook like Colab or Databricks.

## Local App Serving

To host your app, run `dp.serve_app`.

!!! note
    A port will be chosen automatically, but you can manually specify `port` and `host`.

```python
import datapane as dp

view = dp.View(...)

dp.serve_app(view)
```

### Creating a public URL

Datapane has built-in support for ngrok, which allows you to create a public, shareable URL for your data app. Simply add `public=True` to your serve command. This will prompt you to enter your ngrok token, and will return a URL which you can share.

```python
dp.serve_app(app, public=True)
```

### Embed mode

If you are embedding your app in a third-party product, you will need to pass `embed_mode=True` to `dp.serve`. This disables specific security policies which will not work within an `iframe`.

## Datapane Cloud

Datapane Cloud will shortly provide App hosting specific and optimized to the needs of App running and hosting, including access-controls, security and authentication features that organizations require.

At the same time, you can easily host your app via any web server hosting service (especially those that work with Python  / WSGI-based apps), including the services listed here.

## Fly.io

[Fly.io](https://fly.io) provides a simple way to build and deploy your app. Fly has a generous free tier where you can host your data app on the web. Note that the free tier is limited to 256mb of RAM, so if you are doing any data processing, you may want to upgrade.

### Getting started

You will need:

- [A Fly account](https://fly.io/app/sign-up)
- [`flyctl` installed](https://fly.io/docs/hands-on/install-flyctl/)

One of either:

- A `requirements.txt` for pip dependencies
- A Dockerfile

Datapane CLI provides a helper for generating a Dockerfile:

```bash
$ datapane app generate dockerfile
```

### Deploying your app

Once done, you can deploy your app with the following commands:

1. Create and configure a new app from source code or a Docker image.
```bash
$ flyctl launch --remote-only --build-only
```
1. Deploy your app
```bash
$ flyctl deploy --remote-only -e 'PORT=8080'
```
1. Save your config file for future deploys
```bash
$ flyctl config save
```

This will:

- Generate a fly.toml file
- Push and build your app on their servers
- Provide you with a URL to access your App

---

## Render.com

[Render](https://render.com/) provides a simple way to build and deploy your projects from a git repository.

To get started, you'll need:

- [A Render account](https://render.com/)
- Your source code in a git repository
- A `requirements.txt` for `pip` dependencies
- A `Dockerfile`. You can generate this with `datapane app generate dockerfile`

Once done, you can setup a deployment from the [dashboard](https://dashboard.render.com/select-repo?type=web):

- Create a new Web Service
- Select your repository
- Name your service
- click `Create` (at the end of the page)

This will start building your App, then deploying it. Once complete, you'll be able to find the URL in the Dashboard.

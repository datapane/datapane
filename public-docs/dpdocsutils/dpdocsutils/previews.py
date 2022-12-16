from IPython.display import IFrame


def embed_local_app(app_path, width, height):
    return IFrame(app_path, width=width, height=height, extras=['loading="lazy"'])

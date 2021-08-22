import os
import http
import click
import folium
import tempfile
import atexit
import itertools
from http.server import HTTPServer
from multiprocessing import Pool
from PIL import Image, ImageColor
import parser

ZOOM_LEVEL = 4


def serve_http(port, folder):
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=folder, **kwargs)
    http_server = HTTPServer(("", port), Handler)
    print("http://127.0.0.1:{}/index.html".format(port))
    http_server.serve_forever()


def generate_image(tile, tmp_folder):
    print("generating image for tile: {}".format(tile.id))
    size = parser.TILE_WIDTH*parser.BITMAP_WIDTH // ZOOM_LEVEL
    im = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    for block in tile.blocks.values():
        for i in range(parser.BITMAP_WIDTH):
            for j in range(parser.BITMAP_WIDTH):
                x = block.x * parser.BITMAP_WIDTH + i
                y = block.y * parser.BITMAP_WIDTH + j
                x //= ZOOM_LEVEL
                y //= ZOOM_LEVEL
                if block.is_visited(i, j):
                    im.putpixel((x, y), ImageColor.getcolor('black', 'RGB'))
    im.save(os.path.join(tmp_folder.name, "{}.png".format(tile.id)))


@click.command()
@click.option('--port', default=8080, help='http port for the web ui')
@click.argument('DIR')
def main(port, dir):
    """Load [Fog of World] data from DIR.

    DIR is the path to the [Fog of World] folder, the given folder should contain a subfolder [Sync].
    """
    fog_map = parser.FogMap(dir)

    tmp_folder = tempfile.TemporaryDirectory()

    def exit_handler():
        tmp_folder.cleanup()
    atexit.register(exit_handler)

    m = folium.Map()
    with Pool(4) as pool:
        pool.starmap(generate_image, zip(fog_map.tile_map.values(), itertools.repeat(tmp_folder)))

    for tile in fog_map.tile_map.values():
        folium.raster_layers.ImageOverlay(
            "http://127.0.0.1:{}/{}.png".format(port, tile.id), tile.bounds(), opacity=1).add_to(m)
        print(tile.bounds())

    m.save(os.path.join(tmp_folder.name, "index.html"))
    serve_http(port, tmp_folder.name)


if __name__ == "__main__":
    main()

# The parser here is not designed to be a well-coded library with
# good performance, it is more like a demo for showing the data
# structure.
import os
import zlib
import struct


FILENAME_ENCODING = {k: v for v, k in enumerate("olhwjsktri")}
MAP_WIDTH  = 512
TILE_WIDTH = 128
TILE_HEADER_LEN = TILE_WIDTH**2
TILE_HEADER_SIZE = TILE_HEADER_LEN*2

class Tile():

    def __init__(self, sync_folder, filename):
        file = os.path.join(sync_folder, filename)
        # parse filename
        # TODO: figure out what the rest part of the filename is
        self.id = 0
        for v in [FILENAME_ENCODING[c] for c in filename[4:10]]:
            self.id = self.id * 10 + v
        self.x = self.id % MAP_WIDTH
        self.y = self.id // MAP_WIDTH
        print("Loading tile. id: {}, x: {}, y: {}".format(self.id, self.x, self.y))
        with open(file, "rb") as f:
            data = f.read()
            data = zlib.decompress(data)
        # header is a 2d array of shorts, it contains the maping of blocks
        header = struct.unpack(str(TILE_HEADER_LEN) +
                               "H", data[:TILE_HEADER_SIZE])


class FogMap():
    # The toplevel class that represent the whole data.
    # The whole map is divided into 512*512 tiles. Each tile
    # is a file and it includes 128*128 blocks. Each block is
    # a 64*64 bitmap.
    def __init__(self, path):
        self.path = os.path.join(path, '')
        sync_folder = os.path.join(self.path, 'Sync')
        assert os.path.isdir(sync_folder)
        for filename in os.listdir(sync_folder):
            if len(filename) == 12:
                tile = Tile(sync_folder, filename)

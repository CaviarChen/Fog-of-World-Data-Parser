# The parser here is not designed to be a well-coded library with
# good performance, it is more like a demo for showing the data
# structure.
import os
import math
import zlib
import struct
import hashlib


FILENAME_ENCODING = {k: v for v, k in enumerate("olhwjsktri")}
MAP_WIDTH = 512
TILE_WIDTH = 128
TILE_HEADER_LEN = TILE_WIDTH**2
TILE_HEADER_SIZE = TILE_HEADER_LEN*2
BLOCK_BITMAP_SIZE = 512
BLOCK_EXTRA_DATA = 3
BLOCK_SIZE = BLOCK_BITMAP_SIZE + BLOCK_EXTRA_DATA
BITMAP_WIDTH = 64


class Block():

    def __init__(self, x, y, data):
        self.x = x
        self.y = y
        self.bitmap = data[:BLOCK_BITMAP_SIZE]
        # TODO: not sure what this is. checksum?
        self.extra_data = data[BLOCK_BITMAP_SIZE:BLOCK_SIZE]

    def is_visited(self, x, y):
        bit_offset = 7 - x % 8
        i = x // 8
        j = y
        return self.bitmap[i+j*8] & (1 << bit_offset)


def _tile_x_y_to_lng_lat(x: int, y: int):
    lng = x/512*360-180
    lat = math.atan(math.sinh(math.pi-2*math.pi*y/512))*180/math.pi
    return (lng, lat)


class Tile():

    def __init__(self, sync_folder, filename):
        file = os.path.join(sync_folder, filename)
        # parse filename
        self.id = 0
        for v in [FILENAME_ENCODING[c] for c in filename[4:10]]:
            self.id = self.id * 10 + v
        self.x = self.id % MAP_WIDTH
        self.y = self.id // MAP_WIDTH
        print("Loading tile. id: {}, x: {}, y: {}".format(self.id, self.x, self.y))

        # filename should start with md5(tileId)
        if (hashlib.md5(str(self.id).encode()).hexdigest()[0:4] != filename[0:4]):
            print("WARNING: the filename {} is not valid.".format(filename))

        with open(file, "rb") as f:
            data = f.read()
            data = zlib.decompress(data)
        # header is a 2d array of shorts, it contains the maping of blocks
        header = struct.unpack(str(TILE_HEADER_LEN) +
                               "H", data[:TILE_HEADER_SIZE])
        self.blocks = {}
        for i, block_idx in enumerate(header):
            if block_idx > 0:
                block_x = i % TILE_WIDTH
                block_y = i // TILE_WIDTH
                start_offset = TILE_HEADER_SIZE + (block_idx-1) * BLOCK_SIZE
                end_offset = start_offset + BLOCK_SIZE
                block_data = data[start_offset:end_offset]
                self.blocks[(block_x, block_y)] = Block(
                    block_x, block_y, block_data)

    def bounds(self):
        (lng1, lat1) = _tile_x_y_to_lng_lat(self.x, self.y)
        (lng2, lat2) = _tile_x_y_to_lng_lat(self.x+1, self.y+1)
        return ((min(lat1, lat2), min(lng1, lng2)), (max(lat1, lat2), max(lng1, lng2)))



class FogMap():
    # The toplevel class that represent the whole data.
    # The whole map is divided into 512*512 tiles. Each tile
    # is a file and it includes 128*128 blocks. Each block is
    # a 64*64 bitmap.
    def __init__(self, path):
        self.path = os.path.join(path, '')
        sync_folder = os.path.join(self.path, 'Sync')
        assert os.path.isdir(sync_folder)
        self.tile_map = {}
        for filename in os.listdir(sync_folder):
            if len(filename) == 12:
                tile = Tile(sync_folder, filename)
                self.tile_map[(tile.x, tile.y)] = tile

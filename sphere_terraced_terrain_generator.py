import array
import math
import random
from functools import reduce

import numpy as np
from panda3d.core import Vec3, Point3, Vec2

from shapes import Cubesphere
from noise import SimplexNoise, PerlinNoise, CellularNoise
from noise import Fractal2D, Fractal3D
from themes import themes, Island

from terraced_terrain import SphericalTerracedTerrainMixin


class TerracedTerrainGenerator(SphericalTerracedTerrainMixin, Cubesphere):
    """A class to generate a terraced terrain.
        Args:
            noise (func): Function that generates noise.
            scale (float): The smaller this value is, the more sparse the noise becomes.
            segs_s (int): The number of vertices in the polygon that forms the ground; minimum is 3.
            radius (float): Length from the center of the polygon forming the ground to each vertex.
            max_depth (int): The number of times that triangles, formed by the center point and each
                             vertex of the polygon that forms the ground, are further divided into triangles.
            octaves (int): The number of loops to calculate the height of the vertex coordinates.
            theme (str): one of "mountain", "snowmountain" and "desert".
    """

    def __init__(self, noise, scale=10, segs_c=5, radius=4,
                 max_depth=6, octaves=6, theme='mountain'):
    # def __init__(self, noise, scale=2,
    #              max_depth=4, octaves=6, theme='mountain'):
        terrain_scale = 1
        super().__init__(max_depth, terrain_scale)
        # self.center = Point3(0, 0, 0)
        self.noise = noise
        self.noise_scale = scale
        self.segs_c = segs_c
        self.radius = radius
        self.max_depth = max_depth
        self.octaves = octaves
        self.theme = themes.get(theme.lower())


    @classmethod
    def from_simplex(cls, scale=15, segs_c=5, radius=3,
                     max_depth=5, octaves=3, theme='mountain'):
        noise = SimplexNoise()
        # noise = Fractal3D(noise.snoise3)
        return cls(noise.snoise3, scale, segs_c, radius, max_depth, octaves, theme)
        # return cls(noise.fractal, scale, segs_c, radius, max_depth, octaves, theme)

        # noise = PerlinNoise()
        # return cls(noise.pnoise3, scale, segs_c, radius, max_depth, octaves, theme)

    @classmethod
    def from_perlin(cls, scale=15, segs_c=5, radius=3,
                    max_depth=5, octaves=6, theme='mountain'):
        noise = PerlinNoise()
        return cls(noise.pnoise3, scale, segs_c, radius, max_depth, octaves, theme)

    @classmethod
    def from_cellular(cls, scale=10, segs_c=5, radius=3,
                      max_depth=6, octaves=3, theme='mountain'):
        noise = CellularNoise()
        return cls(noise.fdist3, scale, segs_c, radius, max_depth, octaves, theme)

    @classmethod
    def from_fractal(cls, scale=10, segs_c=5, radius=3,
                     max_depth=6, octaves=3, theme='island'):
        simplex = SimplexNoise()
        noise = Fractal2D(simplex.snoise2)
        return cls(noise.fractal, scale, segs_c, radius, max_depth, octaves, theme)

    def create_terraced_terrain(self, vertex_cnt, vdata_values, prim_indices):
        t = random.uniform(0, 1000)
        offsets = [Vec3(random.randint(-1000, 1000),
                        random.randint(-1000, 1000),
                        random.randint(-1000, 1000)) for _ in range(self.octaves)]

        for subdiv_face in self.generate_triangles():
            vertices = []
            for vertex in subdiv_face:
                if (h := self.noise_octaves(t, offsets, *vertex)) < self.theme.LAYER_01.threshold:
                    h = self.theme.LAYER_01.threshold

                normalized_vert = vertex.normalized()
                vert = normalized_vert * (1 + h)
                vertices.append(vert)

            vertex_cnt += self.meandering_triangles(vertices, vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt

    def get_geom_node(self):
        vdata_values = array.array('f', [])
        prim_indices = array.array('I', [])
        vertex_cnt = 0

        vertex_cnt += self.create_terraced_terrain(vertex_cnt, vdata_values, prim_indices)
        # create a geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'spherical_terraced_terrain')

        return geom_node
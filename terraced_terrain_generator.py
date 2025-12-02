import array
import math
import random
import copy

import numpy as np
from panda3d.core import Vec3, Point3, Vec2

# from shapes.create_geometry import ProceduralGeometry
from noise import SimplexNoise, PerlinNoise, CellularNoise
from noise import Fractal2D
from themes import themes, Island

from mask.radial_gradient_generator import RadialGradientMask
from shapes.spherical_polyhedron import TriangleGenerator
from terraced_terrain import FlatTerracedTerrainMixin


class TerracedTerrainGenerator(FlatTerracedTerrainMixin, TriangleGenerator):
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
        super().__init__(max_depth=6)
        self.center = Point3(0, 0, 0)
        self.noise = noise
        self.noise_scale = scale
        self.scale = scale
        self.segs_c = segs_c
        self.radius = radius
        self.max_depth = max_depth
        self.octaves = octaves
        self.theme = themes.get(theme.lower())

    @classmethod
    def from_simplex(cls, scale=8, segs_c=5, radius=3,
                     max_depth=6, octaves=3, theme='mountain'):
        noise = SimplexNoise()
        return cls(noise.snoise2, scale, segs_c, radius, max_depth, octaves, theme)

    @classmethod
    def from_perlin(cls, scale=15, segs_c=5, radius=3,
                    max_depth=6, octaves=3, theme='mountain'):
        noise = PerlinNoise()
        return cls(noise.pnoise2, scale, segs_c, radius, max_depth, octaves, theme)

    @classmethod
    def from_cellular(cls, scale=10, segs_c=5, radius=3,
                      max_depth=6, octaves=3, theme='mountain'):
        noise = CellularNoise()
        return cls(noise.fdist2, scale, segs_c, radius, max_depth, octaves, theme)

    @classmethod
    def from_fractal(cls, scale=10, segs_c=5, radius=3,
                     max_depth=6, octaves=3, theme='island'):
        simplex = SimplexNoise()
        noise = Fractal2D(simplex.snoise2)
        return cls(noise.fractal, scale, segs_c, radius, max_depth, octaves, theme)

    def get_polygon_vertices(self, theta):
        rad = math.radians(theta)
        x = self.radius * math.cos(rad) + self.center.x
        y = self.radius * math.sin(rad) + self.center.y

        return Point3(x, y, 0)

    def generate_base_polygon(self):
        """Generate vertices for the polygon that will form the ground.
        """
        deg = 360 / self.segs_c

        for i in range(self.segs_c):
            current_i = i + 1

            if (next_i := current_i + 1) > self.segs_c:
                next_i = 1
            pt1 = self.get_polygon_vertices(deg * current_i)
            pt2 = self.get_polygon_vertices(deg * next_i)

            yield (pt1, pt2)

    def create_terraced_terrain(self, vertex_cnt, vdata_values, prim_indices):
        t = random.uniform(0, 1000)
        offsets = [Vec2(random.randint(-1000, 1000),
                        random.randint(-1000, 1000)) for _ in range(self.octaves)]

        for p1, p2 in self.generate_base_polygon():
            for subdiv_face in self.subdivide([p1, p2, self.center]):
                vertices = []
                # subdiv_face = copy.deepcopy(tmp)
                for vertex in subdiv_face:
                    h = self.noise_octaves(t, offsets, vertex.x, vertex.y)

                    if self.theme == Island:
                        r, _, _ = self.mask.get_gradient(vertex.x, vertex.y)
                        h = 0.02 if r >= h else h - r
                    else:
                        if h <= self.theme.LAYER_01.threshold:
                            h = self.theme.LAYER_01.threshold

                    vert = Vec3(vertex)
                    vert.z = h
                    vertices.append(vert)

                vertex_cnt += self.meandering_triangles(vertices, vertex_cnt, vdata_values, prim_indices)

        return vertex_cnt

    def get_geom_node(self):
        vdata_values = array.array('f', [])
        prim_indices = array.array('I', [])
        vertex_cnt = 0

        if self.theme == Island:
            self.mask = RadialGradientMask(
                height=self.radius, width=self.radius, center_h=0, center_w=0)

        # vertex_cnt += self.generate_terraced_terrain(vertex_cnt, vdata_values, prim_indices)
        vertex_cnt += self.create_terraced_terrain(vertex_cnt, vdata_values, prim_indices)

        # create a geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'terraced_terrain')

        return geom_node
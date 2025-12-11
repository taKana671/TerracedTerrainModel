import array
import math
import random

from panda3d.core import Vec3, Point3

from .terraced_terrain import FlatTerracedTerrainMixin
from .themes import themes, Island
from mask.radial_gradient_generator import RadialGradientMask
from noise import SimplexNoise, PerlinNoise, CellularNoise
from noise import Fractal2D
from shapes.spherical_polyhedron import TriangleGenerator


class FlatTerracedTerrain(FlatTerracedTerrainMixin, TriangleGenerator):
    """A class to generate a terraced terrain.
        Args:
            noise (func): Function that generates noise.
            noise_scale (float): The smaller this value is, the more sparse the noise becomes.
            segs_c (int): The number of vertices in the polygon that forms the ground; minimum is 3.
            radius (float): Length from the center of the polygon that forms the ground to each vertex.
            max_depth (int): The number of times that triangles, formed by the center point and each
                             vertex of the polygon that forms the ground, are further divided into triangles.
            octaves (int): The number of times to apply the noise algorithm. Each iteration represent an octave.
            amplitude  (float): Noise strength.
            frequency (float): Basic frequency of terrain.
            persistence (float): At the end of each iteration, the amplitude is decreased by multiplying itself by persistence, less than 1.
            lacunarity (float): At the end of each iteration, the frequency is increased by multiplying itself by lacunarity, greater than 1.
            theme (str): one of "mountain", "snowmountain", "desert" and "island".
    """

    def __init__(self,
                 noise_gen,
                 noise_scale=10,
                 segs_c=5,
                 radius=4,
                 max_depth=5,
                 octaves=3,
                 persistence=0.375,
                 lacunarity=2.52,
                 amplitude=1.0,
                 frequency=0.055,
                 theme='mountain'
                 ):
        super().__init__(max_depth)
        self.center = Point3(0, 0, 0)
        self.noise_scale = noise_scale
        self.segs_c = segs_c
        self.radius = radius
        self.theme = themes.get(theme.lower())

        self.noise = Fractal2D(
            noise_gen=noise_gen,
            gain=persistence,
            lacunarity=lacunarity,
            octaves=octaves,
            amplitude=amplitude,
            frequency=frequency
        )

    @classmethod
    def from_simplex(cls, noise_scale=8, segs_c=5, radius=3,
                     max_depth=6, octaves=3, **kwargs):
        simplex = SimplexNoise()

        return cls(
            simplex.snoise2,
            noise_scale=noise_scale,
            segs_c=segs_c,
            radius=radius,
            max_depth=max_depth,
            octaves=octaves,
            **kwargs)

    @classmethod
    def from_perlin(cls, noise_scale=15, segs_c=5, radius=3,
                    max_depth=6, octaves=3, **kwargs):
        perlin = PerlinNoise()

        return cls(
            perlin.pnoise2,
            noise_scale=noise_scale,
            segs_c=segs_c,
            radius=radius,
            max_depth=max_depth,
            octaves=octaves,
            **kwargs)

    @classmethod
    def from_cellular(cls, noise_scale=10, segs_c=5, radius=3,
                      max_depth=6, octaves=3, **kwargs):
        cellular = CellularNoise()

        return cls(
            cellular.fdist2,
            noise_scale=noise_scale,
            segs_c=segs_c,
            radius=radius,
            max_depth=max_depth,
            octaves=octaves,
            **kwargs)

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
        offset_x = random.uniform(-1000, 1000)
        offset_y = random.uniform(-1000, 1000)

        for p1, p2 in self.generate_base_polygon():
            for subdiv_face in self.subdivide([p1, p2, self.center]):
                vertices = []

                for vertex in subdiv_face:
                    x = (vertex.x + offset_x) * self.noise_scale
                    y = (vertex.y + offset_y) * self.noise_scale
                    h = self.noise.noise_octaves(x, y)

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
        if self.theme == Island:
            self.mask = RadialGradientMask(
                height=self.radius, width=self.radius, center_h=0, center_w=0)

        vdata_values = array.array('f', [])
        prim_indices = array.array('I', [])
        vertex_cnt = 0

        vertex_cnt += self.create_terraced_terrain(vertex_cnt, vdata_values, prim_indices)

        # create a geom node.
        geom_node = self.create_geom_node(
            vertex_cnt, vdata_values, prim_indices, 'flat_terraced_terrain')

        return geom_node
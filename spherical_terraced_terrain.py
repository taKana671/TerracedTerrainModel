import array
import random

from panda3d.core import Vec3

from shapes import Cubesphere
from noise import SimplexNoise, PerlinNoise, CellularNoise, Fractal3D
from themes import themes
from terraced_terrain import SphericalTerracedTerrainMixin


class SphericalTerracedTerrain(SphericalTerracedTerrainMixin, Cubesphere):
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

    def __init__(self,
                 noise_gen,
                 terrain_scale=1,
                 noise_scale=10,
                 max_depth=5,
                 octaves=3,
                 persistence=0.375,
                 lacunarity=2.52,
                 amplitude=1.0,
                 frequency=0.055,
                 theme='mountain'
                 ):
        super().__init__(max_depth, terrain_scale)
        self.noise_scale = noise_scale
        self.theme = themes.get(theme.lower())

        self.noise = Fractal3D(
            noise_gen=noise_gen,
            gain=persistence,
            lacunarity=lacunarity,
            octaves=octaves,
            amplitude=amplitude,
            frequency=frequency
        )

    @classmethod
    def from_simplex(cls, terrain_scale=1, noise_scale=15,
                     max_depth=5, octaves=3, theme='mountain'):
        simplex = SimplexNoise()
        return cls(simplex.snoise3, terrain_scale, noise_scale, max_depth, octaves, theme=theme)

    @classmethod
    def from_perlin(cls, terrain_scale=1, noise_scale=18,
                    max_depth=5, octaves=4, theme='mountain'):
        perlin = PerlinNoise()
        return cls(perlin.pnoise3, terrain_scale, noise_scale, max_depth, octaves, theme=theme)

    @classmethod
    def from_cellular(cls, terrain_scale=1, noise_scale=15,
                      max_depth=5, octaves=3, theme='mountain'):
        cellular = CellularNoise()
        return cls(cellular.fdist3, terrain_scale, noise_scale, max_depth, octaves, theme=theme)

    def create_terraced_terrain(self, vertex_cnt, vdata_values, prim_indices):
        offset = Vec3(*[random.uniform(-1000, 1000) for _ in range(3)])

        for subdiv_face in self.generate_triangles():
            vertices = []
            for vertex in subdiv_face:
                scaled_verts = (vertex + offset) * self.noise_scale

                if (h := self.noise.noise_octaves(*scaled_verts)) < self.theme.LAYER_01.threshold:
                    h = self.theme.LAYER_01.threshold

                normalized_vert = vertex.normalized()
                vert = normalized_vert * (1 + h)
                vertices.append(vert)

            vertex_cnt += self.meandering_triangles(
                vertices, vertex_cnt, vdata_values, prim_indices)

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
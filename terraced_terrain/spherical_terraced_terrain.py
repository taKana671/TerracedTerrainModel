import array
import random

from panda3d.core import Vec3

from .terraced_terrain import SphericalTerracedTerrainMixin
from .themes import themes
from noise import SimplexNoise, PerlinNoise, CellularNoise, Fractal3D
from shapes import Cubesphere


class SphericalTerracedTerrain(SphericalTerracedTerrainMixin, Cubesphere):
    """A class to generate a terraced terrain.
        Args:
            noise_gen (func): Function that generates noise.
            terrain_scale (float): Scale of sphere.
            noise_scale (float): The smaller this value is, the more sparse the noise becomes.
            max_depth (int): The number of times that triangles, formed by the center point and each
                             vertex of the polygon that forms the ground, are further divided into triangles.
            octaves (int): The number of times to apply the noise algorithm. Each iteration represent an octave.
            amplitude  (float): Noise strength.
            frequency (float): Basic frequency of terrain.
            persistence (float): At the end of each iteration, the amplitude is decreased by multiplying itself by persistence, less than 1.
            lacunarity (float): At the end of each iteration, the frequency is increased by multiplying itself by lacunarity, greater than 1.
            theme (str): one of "mountain", "snow" and "desert".
    """

    def __init__(self,
                 noise_gen,
                 terrain_scale=1,
                 noise_scale=10,
                 max_depth=5,
                 octaves=3,
                 amplitude=1.0,
                 frequency=0.055,
                 persistence=0.375,
                 lacunarity=2.52,
                 theme='mountain'
                 ):
        super().__init__(max_depth, terrain_scale)
        self.noise_scale = noise_scale

        if (theme_name := theme.lower()) == 'island':
            raise ValueError("Island is only for flat terraced terrain at this time.")
        self.theme = themes.get(theme_name)

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
                     max_depth=5, octaves=3, **kwargs):
        simplex = SimplexNoise()

        return cls(
            simplex.snoise3,
            terrain_scale=terrain_scale,
            noise_scale=noise_scale,
            max_depth=max_depth,
            octaves=octaves,
            **kwargs)

    @classmethod
    def from_perlin(cls, terrain_scale=1, noise_scale=18,
                    max_depth=5, octaves=4, **kwargs):
        perlin = PerlinNoise()

        return cls(
            perlin.pnoise3,
            terrain_scale=terrain_scale,
            noise_scale=noise_scale,
            max_depth=max_depth,
            octaves=octaves,
            **kwargs)

    @classmethod
    def from_cellular(cls, terrain_scale=1, noise_scale=15,
                      max_depth=5, octaves=3, **kwargs):
        cellular = CellularNoise()
        return cls(
            cellular.fdist3,
            terrain_scale=terrain_scale,
            noise_scale=noise_scale,
            max_depth=max_depth,
            octaves=octaves,
            **kwargs)

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
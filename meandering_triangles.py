import numpy as np
import array
import math
import random
import copy

import numpy as np
from panda3d.core import Vec3, Point3, Vec2


class TerracedTerrainMixin:

    def meandering_triangles(self, vertices, vertex_cnt, vdata_values, prim_indices):
        # Each point's heights above "sea level".
        v1, v2, v3 = vertices
        h1, h2, h3 = self.get_height(v1, v2, v3)

        li = [int(h_ * 10) for h_ in (h1, h2, h3)]
        h_min = np.floor(min(li))
        h_max = np.floor(max(li))

        for h in np.arange(h_min, h_max + 1, 0.5):
            h *= 0.1
            points_above = 0

            # indicate triangles above the plane.
            match [val for val in [h1, h2, h3] if val > h]:

                case [x]:
                    # One vector is above. If v1 or v2, swap vertices.
                    points_above = 1
                    if x == h1:
                        v1, v2, v3 = v2, v3, v1
                    elif x == h2:
                        v1, v2, v3 = v3, v1, v2

                case [x, y]:
                    # Two are above. If v2 and v3, or v1 and v3, swap vertices.
                    points_above = 2
                    if x == h2 and y == h3:
                        v1, v2, v3 = v2, v3, v1
                    elif x == h1 and y == h3:
                        v1, v2, v3 = v3, v1, v2

                case [_, _, _]:
                    # All are above.
                    points_above = 3

            h1, h2, h3 = self.get_height(v1, v2, v3)
            # for each point of the triangle, we also need its projections
            # to the current plane and the plane below. Just set its vertical component to the plane's height.

            # current plane
            v1_c, v2_c, v3_c = self.get_current_plane((v1, v2, v3), (h1, h2, h3), h)

            # generate mesh polygons for each of the three cases.
            if points_above == 3:
                # add one triangle.
                color = self.theme.color(v1_c.z)
                self.create_triangle_vertices([v1_c, v2_c, v3_c], color, vdata_values)
                prim_indices.extend([vertex_cnt, vertex_cnt + 1, vertex_cnt + 2])
                vertex_cnt += 3
                continue

            # the plane below; used to make vertical walls between planes.
            v1_b, v2_b, v3_b = self.get_plane_below((v1, v2, v3), (h1, h2, h3), h)

            # find locations of new points that are located on the sides of the triangle's projections,
            # by interpolating between vectors based on their heights.

            # interpolation value for v1 and v3
            # h is np.float64. if h1 - h3 == 0, t1 becomes -inf.
            t1 = 0 if (denom := h1 - h3) == 0 else (h1 - h) / denom
            # t1 = (h1 - h) / (h1 - h3)
            v1_c_n = self.lerp(v1_c, v3_c, t1)
            v1_b_n = self.lerp(v1_b, v3_b, t1)

            # interpolation value for v2 and v3
            # h is np.float64. if h2 - h3 == 0, t2 becomes -inf.
            t2 = 0 if (denom := h2 - h3) == 0 else (h2 - h) / denom
            # t2 = (h2 - h) / (h2 - h3)
            v2_c_n = self.lerp(v2_c, v3_c, t2)
            v2_b_n = self.lerp(v2_b, v3_b, t2)

            if points_above == 2:
                color = self.theme.color(v1_c.z)
                # add roof part of the step
                quad = [v1_c, v2_c, v2_c_n, v1_c_n]
                self.create_quad_vertices(quad, color, vdata_values, wall=False)

                prim_indices.extend([
                    *(vertex_cnt, vertex_cnt + 1, vertex_cnt + 2),
                    *(vertex_cnt + 2, vertex_cnt + 3, vertex_cnt)
                ])
                vertex_cnt += 4

                # add wall part of the step
                quad = [v1_c_n, v2_c_n, v2_b_n, v1_b_n]
                self.create_quad_vertices(quad, color, vdata_values, wall=True)

                prim_indices.extend([
                    *(vertex_cnt, vertex_cnt + 1, vertex_cnt + 2),
                    *(vertex_cnt, vertex_cnt + 2, vertex_cnt + 3)
                ])
                vertex_cnt += 4

            elif points_above == 1:
                color = self.theme.color(v3_c.z)
                # add roof part of the step
                self.create_triangle_vertices([v3_c, v1_c_n, v2_c_n], color, vdata_values)
                prim_indices.extend([vertex_cnt, vertex_cnt + 1, vertex_cnt + 2])
                vertex_cnt += 3

                # add wall part of the step
                quad = [v2_c_n, v1_c_n, v1_b_n, v2_b_n]
                self.create_quad_vertices(quad, color, vdata_values, wall=True)
                prim_indices.extend([
                    *(vertex_cnt, vertex_cnt + 1, vertex_cnt + 3),
                    *(vertex_cnt + 1, vertex_cnt + 2, vertex_cnt + 3)
                ])
                vertex_cnt += 4

        return vertex_cnt

    def create_triangle_vertices(self, tri, color, vdata_values):
        normal = Vec3(0, 0, 1)

        for vert in tri:
            # norm = vert.normalized() * 2
            # vert = norm * (1 + vert.z)    
            # vdata_values.extend(vert)

            vdata_values.extend(vert)
            vdata_values.extend(color)
            vdata_values.extend(normal)
            u, v = self.calc_uv(vert.x, vert.y)
            vdata_values.extend((u, v))

    def create_quad_vertices(self, quad, color, vdata_values, wall=False):
        normal = Vec3(0, 0, 1)

        for vert in quad:
            if wall:
                normal = Vec3(vert.x, vert.y, 0).normalized()

            # norm = vert.normalized() * 2
            # vert = norm * (1 + vert.z)    
            # vdata_values.extend(vert)

            vdata_values.extend(vert)
            vdata_values.extend(color)
            vdata_values.extend(normal)
            u, v = self.calc_uv(vert.x, vert.y)
            vdata_values.extend((u, v))

    def calc_uv(self, x, y):
        u = 0.5 + x / self.radius * 0.5
        v = 0.5 + y / self.radius * 0.5
        return u, v

    def lerp(self, start, end, t):
        """Args
            start: start_point
            end: end point
            t: Interpolation rate; between 0.0 and 1.0
        """
        return start + (end - start) * t

    def noise_octaves(self, t, offsets, *components):
        """Use noise octaves to calculate the height of a vertex
           based on its coordinates and the number of octaves to be applied.
            Args:
                t (float): Elapsed time
                offsets (Vec3): Offset vertices' position by a random value.
                components (tuple): vertex components; for a plane, x and y; for a sphere, x, y, and z.
        """
        height = 0
        amplitude = 1.0
        frequency = 0.055
        persistence = 0.375  # 0.5
        lacunarity = 2.52    # 2.5

        for i in range(self.octaves):
            offset = offsets[i]
            vert = [comp * frequency + o for comp, o in zip(components, offset)]
            noise = self.noise(*[(v + t) * self.scale for v in vert])
            # fx = x * frequency + offset.x
            # fy = y * frequency + offset.y
            # noise = self.noise((fx + t) * self.scale, (fy + t) * self.scale)

            height += amplitude * noise
            frequency *= lacunarity
            amplitude *= persistence

        return height


class FlatTerracedTerrainMixin(TerracedTerrainMixin):
    """A mixin class for flat terraced terrain.
    """

    def get_height(self, v1, v2, v3):
        return v1.z, v2.z, v3.z

    def get_current_plane(self, vertices, _, h):
        return [Point3(v.x, v.y, h) for v in vertices]

    def get_plane_below(self, vertices, _, h):
        return [Point3(v.x, v.y, h - 0.05) for v in vertices]

    def get_color(self, thresh):
        return self.theme.color(thresh)


class SphericalTerracedTerrainMixin(TerracedTerrainMixin):
    """A mixin class for spherical terraced terrain.
    """

    def get_height(self, v1, v2, v3):
        return v1.length(), v2.length(), v3.length()

    def get_current_plane(self, vertices, vector_lengths, h):
        return [(v / l) * h for v, l in zip(vertices, vector_lengths)]

    def get_plane_below(self, vertices, vector_lengths, h):
        return [(v / l) * (h - 0.05) for v, l in zip(vertices, vector_lengths)]

    def get_color(self, thresh):
        return self.theme.color(thresh - 1)
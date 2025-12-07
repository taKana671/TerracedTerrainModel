import numpy as np

from panda3d.core import Vec3, Point3


class TerracedTerrainMixin:

    def meandering_triangles(self, vertices, index_offset, vdata_values, prim_indices):
        vertex_cnt = 0

        # Each point's heights above "sea level".
        v1, v2, v3 = vertices
        h1, h2, h3 = self.get_height(v1, v2, v3)

        li = [int(h_ * 10) for h_ in (h1, h2, h3)]
        h_min = np.floor(min(li))
        h_max = np.floor(max(li))

        for h in np.arange(h_min, h_max + 1, 0.5):
            h *= 0.1
            points_above = 0

            # Indicate triangles above the plane.
            match [val for val in [h1, h2, h3] if val > h]:

                case [x]:
                    points_above = 1
                    if x == h1:
                        v1, v2, v3 = v2, v3, v1
                    elif x == h2:
                        v1, v2, v3 = v3, v1, v2

                case [x, y]:
                    points_above = 2
                    if x == h2 and y == h3:
                        v1, v2, v3 = v2, v3, v1
                    elif x == h1 and y == h3:
                        v1, v2, v3 = v3, v1, v2

                case [_, _, _]:
                    points_above = 3

            # For each point of the triangle, need its projections to the current plane and the plane below.
            # Just set its vertical component to the plane's height.

            # Since swapped values of the points, let's find their heights again
            h1, h2, h3 = self.get_height(v1, v2, v3)
            # current plane
            v1_c, v2_c, v3_c = self.get_current_plane((v1, v2, v3), (h1, h2, h3), h)

            # Generate mesh polygons for each of the three cases.
            if points_above == 3:
                # add one triangle.
                tri = [v1_c, v2_c, v3_c]
                self.add_triangle(tri, h, index_offset, vdata_values, prim_indices)
                index_offset += 3
                vertex_cnt += 3
                continue

            # The plane below; used to make vertical walls between planes.
            v1_b, v2_b, v3_b = self.get_plane_below((v1, v2, v3), (h1, h2, h3), h)

            # Find locations of new points that are located on the sides of the triangle's projections,
            # by interpolating between vectors based on their heights.

            # Interpolation value for v1 and v3
            t1 = 0 if (denom := h1 - h3) == 0 else (h1 - h) / denom
            v1_c_n = self.lerp(v1_c, v3_c, t1)
            v1_b_n = self.lerp(v1_b, v3_b, t1)

            # Interpolation value for v2 and v3
            t2 = 0 if (denom := h2 - h3) == 0 else (h2 - h) / denom
            v2_c_n = self.lerp(v2_c, v3_c, t2)
            v2_b_n = self.lerp(v2_b, v3_b, t2)

            if points_above == 2:
                # Add roof part of the step
                quad = [v1_c, v2_c, v2_c_n, v1_c_n]
                self.add_step_roof(quad, h, index_offset, vdata_values, prim_indices)
                index_offset += 4

                # Add wall part of the step.
                quad = [v1_c_n, v2_c_n, v2_b_n, v1_b_n]
                self.add_step_wall(quad, h, index_offset, vdata_values, prim_indices)
                index_offset += 4

                vertex_cnt += 8

            elif points_above == 1:
                # Add roof part of the step.
                tri = [v3_c, v1_c_n, v2_c_n]
                self.add_triangle(tri, h, index_offset, vdata_values, prim_indices)
                index_offset += 3

                # Add wall part of the step.
                quad = [v2_c_n, v1_c_n, v1_b_n, v2_b_n]
                self.add_step_wall(quad, h, index_offset, vdata_values, prim_indices)
                index_offset += 4

                vertex_cnt += 7

        return vertex_cnt

    def add_triangle(self, tri_vertices, color_thresh, index_offset, vdata_values, prim_indices):
        self.create_triangle_vertices(tri_vertices, color_thresh, vdata_values)

        prim_indices.extend([index_offset, index_offset + 1, index_offset + 2])

    def add_step_roof(self, quad_vertices, color_thresh, index_offset, vdata_values, prim_indices):
        self.create_quad_vertices(quad_vertices, color_thresh, vdata_values, wall=False)

        prim_indices.extend([
            *(index_offset, index_offset + 1, index_offset + 2),
            *(index_offset + 2, index_offset + 3, index_offset)
        ])

    def add_step_wall(self, quad_vertices, color_thresh, index_offset, vdata_values, prim_indices):
        self.create_quad_vertices(quad_vertices, color_thresh, vdata_values, wall=True)

        prim_indices.extend([
            *(index_offset, index_offset + 1, index_offset + 3),
            *(index_offset + 1, index_offset + 2, index_offset + 3)
        ])

    def lerp(self, start, end, t):
        """Args
            start: start_point
            end: end point
            t: Interpolation rate; between 0.0 and 1.0
        """
        return start + (end - start) * t

    def calculate_quad_normal(self, vertices):
        """The four vertices of the quadrilateral lie on a single plane.
           However, since the normal at each vertex differed,
           the quadrilateral was divided into two triangles, and the normal
           for each triangle were calculated and averaged.
        """
        v1_0 = vertices[1] - vertices[0]
        v2_0 = vertices[3] - vertices[0]

        v1_2 = vertices[3] - vertices[2]
        v2_2 = vertices[1] - vertices[2]

        total = v2_0.cross(v1_0) + v2_2.cross(v1_2)
        normal = (total / 2).normalized()
        return normal


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

    def calc_uv(self, x, y):
        u = 0.5 + x / self.radius * 0.5
        v = 0.5 + y / self.radius * 0.5
        return u, v

    def create_triangle_vertices(self, vertices, color_thresh, vdata_values):
        color = self.get_color(color_thresh)
        normal = Vec3(0, 0, 1)

        for vertex in vertices:
            uv = self.calc_uv(vertex.x, vertex.y)
            vdata_values.extend([*vertex, *color, *normal, *uv])

    def create_quad_vertices(self, vertices, color_thresh, vdata_values, wall=False):
        color = self.get_color(color_thresh)
        normal = self.calculate_quad_normal(vertices) if wall else Vec3(0, 0, 1)

        for vertex in vertices:
            uv = self.calc_uv(vertex.x, vertex.y)
            vdata_values.extend([*vertex, *color, *normal, *uv])


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

    def create_triangle_vertices(self, vertices, color_thresh, vdata_values):
        color = self.get_color(color_thresh)

        for vert in vertices:
            vertex = vert * self.scale
            normal = vert.normalized()
            uv = self.calc_uv(normal)

            vdata_values.extend([*vertex, *color, *normal, *uv])

    def create_quad_vertices(self, vertices, color_thresh, vdata_values, wall=False):
        color = self.get_color(color_thresh)
        normal = self.calculate_quad_normal(vertices) if wall else None

        for vert in vertices:
            if not wall:
                normal = vert.normalized()

            vertex = vert * self.scale
            uv = self.calc_uv(vertex.normalized())

            vdata_values.extend([*vertex, *color, *normal, *uv])

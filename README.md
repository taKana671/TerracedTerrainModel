# TerracedTerrainModel

This repository uses the meandering triangles algorithm to create a 3D model of spherical or flat terraced terrain. 
For spherical terrain, a base sphere is created by repeatedly subdividing each face of the cube into triangles and normalizing the distance from the center to each vertex. For flat terrain, a ground is created by repeatedly dividing a polygon into triangles.
And noise such as simplex and cellular is used to calculate the height of each vertex. 
Then, the meandering triangles algorithm is used to form a staircase-like terrain.
The terrain is colored by setting color information directly to the vertices.
In addition, by running `terraced_terrain_editor.py`, you can create a 3D model while checking how the terrain changes depending on the parameters.
<br/><br/>

<img width="985" height="678" alt="Image" src="https://github.com/user-attachments/assets/f9554fae-68ef-46ca-b633-55b7da3addb7" />
<img width="990" height="688" alt="Image" src="https://github.com/user-attachments/assets/6ebe960b-382e-4df1-aee9-a740138969dc" />

# References

The meandering triangles algorithm is based on below:
* https://icospheric.com/blog/2016/07/17/making-terraced-terrain/
* https://blog.lslabs.dev/posts/ttg
  
# Requirements

* Panda3D 1.10.15
* numpy 2.2.4
* Cython 3.0.12
* opencv-contrib-python 4.11.0.88
* opencv-python 4.11.0.88
  
# Environment

* Python 3.13
* Windows11

# Usage

### Clone this repository with submodule.
```
git clone --recursive https://github.com/taKana671/TerracedTerrainModel.git
```

### Build cython code.

If cytnon code is not built, noise is calculated using python code.
```
cd TerracedTerrainModel
python setup.py build_ext --inplace
```

If the error like "ModuleNotFoundError: No module named ‘distutils’" occurs, install the setuptools.
```
pip install setuptools
```

### Code sample

Create an instance of SphericalTerracedTerrain or FlatTerracedTerrain and call the create method to return the panda3D's NodePath of the terrain's 3D model. 

```
from terraced_terrain.spherical_terraced_terrain import SphericalTerracedTerrain

generator = SphericalTerracedTerrain.from_simplex()     # SimplexNoise is specified.
# generator = SphericalTerracedTerrain.from_cellular()  # CellularNoise is specified.
# generator = SphericalTerracedTerrain.from_perlin()    # PerlinNoise is specified.

model = generator.create()
```

### Usage of terraced_terrain_editor.py

Run terraced_terrain_editor.py and select the terrain type(Flat or Sphere), noise and theme. 
If you want to change the parameters, edit the values in the entry boxes and click the [Reflet Changes] button.

```
python terraced_terrain_editor.py
```

<img width="1195" height="623" alt="Image" src="https://github.com/user-attachments/assets/d312c6db-cb1a-4d30-94d5-4a5a7c98e437" />


### Parameters

* _noise: func_
  * Function that generates noise.

* _noise_scale: float_
  * The smaller this value is, the more sparse the noise becomes.
    
* _segs_s: int_
  * Only for flat terraced terrain.
  * The number of vertices in the polygon that forms the ground; minimum is 3; defalut is 5.

* _radius: float_
  * Only for flat terraced terrain.
  * Length from the center of the polygon forming the ground to each vertex; default is 3.

* _terrace_scale: float_
  * Only for spherical terraced terrain.
  * Scale of sphere.

* _max_depth: int_
  * The number of times that triangles are further divided into triangles.

* _octaves: int_
  * The number of times to apply the noise algorithm. Each iteration represent an octave.

* _amplitude: float_
  * Noise strength.

* _frequency: float_
  * Basic frequency of terrain.

* _persistence: float_
  * At the end of each iteration, the amplitude is decreased by multiplying itself by persistence, less than 1.

* _lacunarity: float_
  * At the end of each iteration, the frequency is increased by multiplying itself by lacunarity, greater than 1.

* _theme: str_
  * one of "mountain", "snow" and "desert".

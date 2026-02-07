# Strawberry Renderer
  strawberry-renderer is a software renderer written in python with pygame. Currently in progress.


### What it can do:
  - It can render medium, small sized obj files 
  - Flat shading for directional or point lights.
  - Back face culling
  - Clipping per polygon basis

### What it can't do (for now):
  - Fragment Shading
  - Texturing
  - Scenes
  - Shadow mapping
  - Depth Buffering

### How can you use it

You can render your custom meshes using the `Mesh` and `Renderer` classes.
You can create light sources using the `Light` class.

You can render obj files with: 

```
python3 -m renderer path_to_obj
```
That is it for now.

### Screenshots:
#### Michelangelos low polygon david:
![david](https://raw.githubusercontent.com/unhappygirl/strawberry-renderer/refs/heads/main/screenshots/ss1.png)

#### Utah Teapot
![teapot](https://raw.githubusercontent.com/unhappygirl/strawberry-renderer/refs/heads/main/screenshots/teapot.png)

#### A trumpet
![trumpet](https://raw.githubusercontent.com/unhappygirl/strawberry-renderer/refs/heads/main/screenshots/trumpet.png)

#### Wireframe cow
![cow](https://raw.githubusercontent.com/unhappygirl/strawberry-renderer/refs/heads/main/screenshots/cow.png)

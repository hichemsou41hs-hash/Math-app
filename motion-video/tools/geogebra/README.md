# GeoGebra (headless)
Render a GeoGebra scene to PNG with the pre-installed Playwright:
  NODE_PATH=$(npm root -g) node render.js /abs/path/scene.html out.png
The scene page loads https://www.geogebra.org/apps/deployggb.js and runs GeoGebra commands in appletOnLoad, then sets window.done=true.
See example_cube.html (3D cube + inscribed sphere).

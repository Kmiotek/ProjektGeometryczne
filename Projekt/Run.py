import Fortune
from Visualization import Plot

Voronoi = Fortune.Voronoi([(4, 1), (0, 9), (1, 5), (7, 10), (-3, 11), (8, 4), (6, 13), (3, 1)])
Voronoi.calculate_voronoi_diagram()
plot = Plot(Voronoi.scenes)
plot.draw()

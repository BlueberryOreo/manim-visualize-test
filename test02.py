from manimlib import *
import numpy as np
from functools import partial

def sin_wave(x, amplitude=1, frequency=1, phase=0):
    return amplitude * np.sin(frequency * x + phase)


class Signal(Scene):
    colors = [RED, ORANGE, YELLOW, GREEN, BLUE, PURPLE]

    def construct(self):
        axes = Axes((-2 * PI, 5 * PI, PI / 2), (-5, 5))
        # x_values = np.arange(-2 * PI, 5 * PI, PI / 2)
        # axes.add_coordinate_labels(x_values=x_values)

        self.play(Write(axes, lag_ratio=0.01, run_time=1))

        sin_funcs = [partial(sin_wave, amplitude=0.5, frequency=PI / i, phase=i / 2) for i in range(1, 10)]

        combined_sin_func = lambda x: 0
        combined_sin_graph = axes.get_graph(
            combined_sin_func,
            color=LIGHT_BROWN,
        )
        self.play(ShowCreation(combined_sin_graph))
        
        for idx, func in enumerate(sin_funcs):
            sin_graph = axes.get_graph(
                func,
                color=self.colors[idx % len(self.colors)],
                stroke_opacity=0.3,
            )
            self.play(ShowCreation(sin_graph))
            new_combined_sin_func = lambda x, f1=combined_sin_func, f2=func: f1(x) + f2(x)
            new_combined_sin_graph = axes.get_graph(
                new_combined_sin_func,
                color=LIGHT_BROWN,
            )
            self.play(ReplacementTransform(combined_sin_graph, new_combined_sin_graph))
            combined_sin_func = new_combined_sin_func
            combined_sin_graph = new_combined_sin_graph
            self.wait(0.5)

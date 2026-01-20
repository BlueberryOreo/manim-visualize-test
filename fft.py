import torch
import torch.fft as fft
from manimlib import *
from functools import partial
from copy import deepcopy

def sin_func(x, amplitude=1, frequency=1):
    if not isinstance(x, torch.Tensor):
        x = torch.tensor(x)
    return amplitude * torch.sin(frequency * x)

def sample_signal(func, num_samples=16, n_pi=2):
    x = torch.linspace(0, n_pi * torch.pi, num_samples)
    y = func(x)
    return x, y # (num_samples,)

def sin_str(amplitude, frequency):
    return f"{amplitude}\\sin({frequency}x)"

class FFTVisualization(Scene):
    sample_range: list = list(range(2, 33))
    function_text: TexText
    fft_desc_text: TexText
    dft_formula: TexText
    colors = [RED, ORANGE, GREEN, BLUE, PURPLE]

    def setup(self):
        self.camera.init_frame(frame_shape=(20, 10), center_point=ORIGIN)
        self.dft_formula = TexText(r"""
                                   $$
                                      F(k) = \sum_{n=0}^{N-1} f(n) \cdot e^{-2\pi j k n / N}
                                   $$
                                   """)

    def construct(self):
        axes = Axes((-1 * PI, 5 * PI, PI / 2), (-2, 2))
        axes2 = Axes((-1, 1), (0, 1), width=6, height=3)
        # axes.shift(UP * 1)
        axes2.shift(DOWN * 2.5 + RIGHT * 0.5)
        # axes.add_coordinate_labels(font_size=8)
        axes2.add_coordinate_labels(font_size=24)

        self.add(axes)
        # self.add(axes2)
        amplitude = 1.0
        frequency = 1.0

        sin_func1 = partial(sin_func, amplitude=amplitude, frequency=frequency)
        sin_func2 = partial(sin_func, amplitude=amplitude, frequency=frequency * 3)
        sin_funcs = [sin_func1, sin_func2]
        ssin_func = lambda x: sin_func1(x) + 0.5 * sin_func2(x)
        # ssin_func = lambda x: sin_func1(x)

        ssin_str = sin_str(amplitude, frequency) + " + " + sin_str(0.5, frequency * 3)
        self.function_text = TexText("\\text{Signal }: $f(x)= " + ssin_str + "$").to_edge(UP)
        self.fft_desc_text = TexText("\\text{FFT Computation for }$f(x)= " + ssin_str + "$").to_edge(UP)

        signals = []
        fft_results = []
        fft_graphs = []
        n_pi = 4
        # Prepare signals with different sample sizes
        for n in self.sample_range:
            x, y = sample_signal(ssin_func, num_samples=n, n_pi=n_pi)

            signal_points = [axes.c2p(xi.item(), yi.item()) for xi, yi in zip(x, y)]
            signal = VGroup(*[Dot(point, fill_color=BLUE, radius=0.04) for point in signal_points])
            f_always(signal.move_to, lambda: axes.c2p(n_pi * PI / 2, 0) - signal.get_center())
            signals.append(signal)

            fft_results.append(fft.fft(y)) # (num_samples,)
            # Prepare FFT graph
            fft_magnitudes = torch.abs(fft_results[-1])
            freq_x = torch.fft.fftfreq(n, d=(n_pi * torch.pi) / n)
            fft_points = [axes2.c2p(freq_x[i].item(), fft_magnitudes[i].item() / n) for i in range(n)]
            fft_graph = VGroup(*[Dot(point, fill_color=RED, radius=0.04) for point in fft_points])
            fft_graphs.append(fft_graph)
        
        signals2 = deepcopy(signals)
        sample_text = [
            Text(f"Sample {n}").to_edge(DR) for n in self.sample_range
        ]
        sample_text2 = deepcopy(sample_text)

        # self.embed()

        # **************************************
        # Animation
        # ===============================
        # Show original signal
        self.play(FadeIn(self.function_text, run_time=2))
        graphs = []
        if len(sin_funcs) > 1:
            for i, func in enumerate(sin_funcs):
                graph = axes.get_graph(
                    func,
                    color=self.colors[i % len(self.colors)],
                    stroke_opacity=0.4,
                )
                self.play(ShowCreation(graph, run_time=0.5))
                graphs.append(graph)
        graph = axes.get_graph(
            ssin_func,
            color=YELLOW,
        )
        graphs.append(graph)
        self.play(ShowCreation(graph, run_time=2))
        self.wait(1)
        self.play(FadeOut(VGroup(*graphs), run_time=1))
        self.remove(*graphs)

        # ===============================
        # Display signals with decreasing time intervals
        self.play(Write(signals[0], lag_ratio=0.01, run_time=2), FadeIn(sample_text[0], run_time=2))
        run_time = 2
        wait_time = 0.5
        for i in range(1, len(signals)):
            self.play(
                ReplacementTransform(signals[i-1], signals[i]),
                ReplacementTransform(sample_text[i-1], sample_text[i]),
                run_time=run_time,
            )
            self.wait(wait_time)
            run_time /= 1.5
            wait_time /= 1.5
        
        self.wait(2)
        self.play(FadeOut(signals[-1]), FadeOut(self.function_text), FadeOut(sample_text[-1]))
        self.remove(signals[-1], self.function_text, sample_text[-1])

        # ===============================
        # Show FFT computation with different sample sizes
        self.play(axes.animate.shift(UP * 1), FadeIn(axes2))
        self.dft_formula.to_edge(DL).shift(LEFT * 2)
        self.play(Write(self.fft_desc_text, run_time=2), Write(self.dft_formula, run_time=2))
        self.play(Write(signals2[0], lag_ratio=0.01, run_time=2), Write(fft_graphs[0], lag_ratio=0.01, run_time=2), FadeIn(sample_text2[0], run_time=2))
        # self.embed()
        
        for i in range(1, len(signals)):
            self.play(
                ReplacementTransform(signals2[i-1], signals2[i]),
                ReplacementTransform(fft_graphs[i-1], fft_graphs[i]),
                ReplacementTransform(sample_text2[i-1], sample_text2[i]),
                run_time=1
            )
            self.wait(0.2)
        
from manim.animation.fading import FadeIn, FadeInFrom
from manim.utils.rate_functions import linear
from animation import SquareDanceAnimator
from generation import AztecGenerator

class VideoAnimation(SquareDanceAnimator):

    def construct(self):
        self.renderer.camera.background_color = self.background_color
        self.renderer.camera.init_background()

        self.slow()
        self.fast()
        self.super_fast()

    def slow(self):
        a = AztecGenerator()
        a.generate(n=10)
        self.from_obj(a.obj)
        self.wait(1)
        self.reset()

    def fast(self):
        ITERATIONS = 30

        self.ANIMATION_STEPS = [["RESIZE", "EXPAND", "REMOVE", "MOVE", "CREATE"]]
        self.ARROW_CREATE_ANIM = FadeIn
        self.ARROW_OVERLAY_COLOUR = None
        self.DESTRUCTION_OVERLAY_STARTING_ALPHA = 0.3
        self.ARROW_CREATE_ANIM = FadeInFrom
        self.MOVEMENT_RATE_FUNC = linear
        self.SQUARE_CREATE_RATE_FUNC = linear
        self.ITERATION_WAIT = 0
        self.SPEED = lambda i: 2 / pow((ITERATIONS - i) * 0.8 / ITERATIONS, 2)

        a = AztecGenerator()
        a.generate(n=ITERATIONS)
        self.from_obj(a.obj)
        self.wait(1)
        self.reset()

    def super_fast(self):
        ITERATIONS = 60

        self.ANIMATION_STEPS = [["RESIZE", "EXPAND", "REMOVE", "MOVE", "CREATE"]]
        self.SQUARE_CREATE_ANIM = None
        self.ARROW_BG_KWARGS = self.ARROW_FINAL_BG_KWARGS
        self.ARROW_DIR_COLOR = self.ARROW_FINAL_DIR_COLOR
        self.TRANSFORM_FINAL = False    
        self.ARROW_LAG_RATIO = 0
        self.ARROW_CREATE_RUNTIME = 0
        self.ARROW_OVERLAY_COLOUR = None
        self.MOVEMENT_RUNTIME = 0
        self.DESTRUCTION_OVERLAY_COLOUR = None
        self.DESTRUCTION_ARROW_ANIM = None
        self.ITERATION_WAIT = 0
        self.SPEED = lambda i: 4 / pow((ITERATIONS - i) * 0.9 / ITERATIONS, 3)

        a = AztecGenerator()
        a.generate(n=ITERATIONS)
        self.from_obj(a.obj)
        self.wait(1)
        self.reset()

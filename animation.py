import math
from manim import Scene, Tex
from manim.animation.composition import AnimationGroup, LaggedStart
from manim.animation.fading import FadeIn, FadeOut
from manim.animation.transform import ApplyMethod, Transform
from manim.constants import PI, RIGHT, UP
from manim.mobject.geometry import Arrow, Rectangle, Square
from manim.utils.color import BLACK, BLUE, GREEN, RED, WHITE, YELLOW
from manim.utils.rate_functions import smooth

class SquareDanceAnimator(Scene):

    CONFIG = {
        "background_color": "#feeafa",
    }

    scale = 0.5

    # SEED
    TEXT_COLOR = BLACK

    # SQUARES
    OPEN_SQUARE_KWARGS = {
        "color": BLACK
    }
    SQUARE_CREATE_ANIM = FadeIn
    SQUARE_CREATE_RATE_FUNC = lambda self, t: smooth(t)
    SQUARE_LAG_RATIO = 0.1
    SQUARE_CREATE_RUNTIME = 0.5

    # ARROW CREATION
    ARROW_BG_KWARGS = (lambda self, dx, dy: {
        "color": BLACK,
        "fill_color": WHITE,
        "fill_opacity": 1,
    })
    ARROW_DIR_COLOR = BLUE

    TRANSFORM_FINAL = True
    ARROW_FINAL_BG_KWARGS = (lambda self, dx, dy: {
        "color": BLACK,
        "fill_color": (
            RED if dx > 0 else (
                YELLOW if dx < 0 else (
                    BLUE if dy > 0 else (
                        GREEN
                    )
                )
            )
        ),
        "fill_opacity": 1,
    })
    ARROW_FINAL_DIR_COLOR = None

    ARROW_CREATE_ANIM = None
    ARROW_LAG_RATIO = 0.1
    ARROW_CREATE_RUNTIME = 1
    ARROW_OVERLAY_COLOUR = GREEN
    ARROW_OVERLAY_STARTING_ALPHA = 0.5

    # MOVEMENT
    MOVEMENT_LAG_RATIO = 0
    MOVEMENT_RUNTIME = 1
    MOVEMENT_RATE_FUNC = lambda self, t: smooth(t)

    # DESTRUCTION
    DESTRUCTION_OVERLAY_COLOUR = RED
    DESTRUCTION_OVERLAY_STARTING_ALPHA = 0.7
    DESTRUCTION_ARROW_ANIM = FadeOut
    DESTRUCTION_LAG_RATIO = 0.1
    DESTRUCTION_RUNTIME = 1

    # GENERAL
    ITERATION_WAIT = 0.2

    def from_obj(self, obj):
        self.seed_text = self.create_seed_obj(obj)
        self.add(self.seed_text)
        self.arrow_blocks = {}
        for iteration_obj in obj["generation_data"]:
            self.increment_animate(iteration_obj)
            if self.ITERATION_WAIT > 0:
                self.wait(self.ITERATION_WAIT)
        if self.TRANSFORM_FINAL:
            self.transform_arrows()

    def create_seed_obj(self, obj):
        seed = obj["general_info"]["seed"]
        seed_text = Tex(seed, color=self.TEXT_COLOR)
        seed_text.to_corner(UP + RIGHT)
        return seed_text

    def increment_animate(self, iteration_obj):
        # Generate the open squares.
        iteration = iteration_obj["iteration"]
        self.generate_squares(iteration)
        destroyed = iteration_obj["destroyed_blocks"]
        self.destroy_existing(destroyed)
        moved = iteration_obj["moved_blocks"]
        self.move_existing(moved)
        created = iteration_obj["created_blocks"]
        self.create_arrows(created)

    def generate_squares(self, iteration):
        squares = []
        for a in range(-iteration-1, iteration+1):
            b1 = iteration - math.floor(abs(a + 0.5))
            b2 = -iteration + math.floor(abs(a + 0.5)) - 1
            squares.append(self._generate_open_square([(a+0.5) * self.scale, (b1+0.5) * self.scale, 0]))
            squares.append(self._generate_open_square([(a+0.5) * self.scale, (b2+0.5) * self.scale, 0]))
        if self.SQUARE_CREATE_ANIM is not None and self.SQUARE_CREATE_RUNTIME > 0:
            self.play(LaggedStart(*(self.SQUARE_CREATE_ANIM(v, rate_func=self.SQUARE_CREATE_RATE_FUNC) for v in squares), lag_ratio=self.SQUARE_LAG_RATIO), run_time=self.SQUARE_CREATE_RUNTIME)
        else:
            self.add(*squares)

    def _generate_open_square(self, position):
        sq = Square(side_length=self.scale, **self.OPEN_SQUARE_KWARGS)
        sq.move_to(position)
        return sq

    def destroy_existing(self, destroyed_blocks):
        all_anims = []
        for id1, id2 in destroyed_blocks:
            # Generate a square containing both arrow blocks, and fade colour.
            if self.DESTRUCTION_RUNTIME > 0:
                anims = []
                if self.DESTRUCTION_ARROW_ANIM is not None:
                    anims.append(self.DESTRUCTION_ARROW_ANIM(self.arrow_blocks[id1]))
                    anims.append(self.DESTRUCTION_ARROW_ANIM(self.arrow_blocks[id2]))
                if self.DESTRUCTION_OVERLAY_COLOUR is not None:
                    top = max(self.arrow_blocks[id1].get_top()[1], self.arrow_blocks[id2].get_top()[1])
                    right = max(self.arrow_blocks[id1].get_right()[0], self.arrow_blocks[id2].get_right()[0])
                    fade_square = Square(side_length=self.scale * 2, color=self.DESTRUCTION_OVERLAY_COLOUR)
                    fade_square.set_opacity(self.DESTRUCTION_OVERLAY_STARTING_ALPHA)
                    fade_square.move_to([right - self.scale, top - self.scale, 0])
                    self.add(fade_square)
                    anims.append(FadeOut(fade_square))
                all_anims.append(AnimationGroup(*anims))
            else:
                self.remove(self.arrow_blocks[id1], self.arrow_blocks[id2])
            del self.arrow_blocks[id1]
            del self.arrow_blocks[id2]
        if self.DESTRUCTION_RUNTIME > 0 and len(all_anims) > 0:
            self.play(LaggedStart(*all_anims, lag_ratio=self.DESTRUCTION_LAG_RATIO), run_time=self.DESTRUCTION_RUNTIME)

    def move_existing(self, moved_blocks):
        anims = []
        for id, (dx, dy) in moved_blocks:
            new_pos = self.arrow_blocks[id].get_center()
            new_pos[0] = new_pos[0] + dx * self.scale
            new_pos[1] = new_pos[1] + dy * self.scale
            if self.MOVEMENT_RUNTIME > 0:
                anims.append(ApplyMethod(self.arrow_blocks[id].move_to, new_pos, rate_func=self.MOVEMENT_RATE_FUNC))
            else:
                self.arrow_blocks[id].move_to(new_pos)
        if self.MOVEMENT_RUNTIME > 0 and len(anims) > 0:
            self.play(LaggedStart(*anims, lag_ratio=self.MOVEMENT_LAG_RATIO), run_time=self.MOVEMENT_RUNTIME)

    def create_arrows(self, created):
        all_anims = []
        for (id1, (p11, p12), (d1x, d1y)), (id2, (p21, p22), (d2x, d2y)) in created:
            self.arrow_blocks[id1] = self._create_arrow(
                [((p11[0] + p12[0])/2 + 0.5) * self.scale, ((p11[1] + p12[1])/2 + 0.5) * self.scale, 0],
                [d1x, d1y],
            )
            self.arrow_blocks[id2] = self._create_arrow(
                [((p21[0] + p22[0])/2 + 0.5) * self.scale, ((p21[1] + p22[1])/2 + 0.5) * self.scale, 0],
                [d2x, d2y],
            )
            self.add(self.arrow_blocks[id1], self.arrow_blocks[id2])
            if self.ARROW_CREATE_RUNTIME > 0:
                anims = []
                if self.ARROW_OVERLAY_COLOUR is not None:
                    top = max(self.arrow_blocks[id1].get_top()[1], self.arrow_blocks[id2].get_top()[1])
                    right = max(self.arrow_blocks[id1].get_right()[0], self.arrow_blocks[id2].get_right()[0])
                    fade_square = Square(side_length=self.scale * 2, color=self.ARROW_OVERLAY_COLOUR)
                    fade_square.set_opacity(self.ARROW_OVERLAY_STARTING_ALPHA)
                    fade_square.move_to([right - self.scale, top - self.scale, 0])
                    self.add(fade_square)
                    anims.append(FadeOut(fade_square))
                if self.ARROW_CREATE_ANIM is not None:
                    anims.append(self.ARROW_CREATE_ANIM(self.arrow_blocks[id1]))
                    anims.append(self.ARROW_CREATE_ANIM(self.arrow_blocks[id2]))
                all_anims.append(AnimationGroup(*anims))
        if self.ARROW_CREATE_RUNTIME > 0 and len(all_anims) > 0:
            self.play(LaggedStart(*all_anims, lag_ratio=self.ARROW_LAG_RATIO), run_time=self.ARROW_CREATE_RUNTIME)

    def _create_arrow(self, pos, direction, final=False):
        # First the bg rect.
        if direction[0] == 0:
            width, height = 2, 1
        else:
            width, height = 1, 2
        rect = Rectangle(
            width=width*self.scale, 
            height=height*self.scale, 
            **(
                self.ARROW_FINAL_BG_KWARGS(*direction)
                if final else
                self.ARROW_BG_KWARGS(*direction)
            )
        )
        rect.move_to(pos)
        rect.direction = direction
        col = self.ARROW_FINAL_DIR_COLOR if final else self.ARROW_DIR_COLOR
        if col is not None:
            arrow = Arrow(color=col)
            arrow.scale(self.scale * 0.5)
            if direction[0] == 1 and direction[1] == 0:
                pass
            elif direction[0] == 0 and direction[1] == 1:
                arrow.rotate(PI/2)
            elif direction[0] == -1 and direction[1] == 0:
                arrow.rotate(PI)
            elif direction[0] == 0 and direction[1] == -1:
                arrow.rotate(3*PI/2)
            else:
                raise ValueError(f"Unknown direction {direction}")
            arrow.move_to(pos)
            rect.add(arrow)
        return rect

    def transform_arrows(self):
        anims = []
        for id in self.arrow_blocks:
            new_arrow = self._create_arrow(self.arrow_blocks[id].get_center(), self.arrow_blocks[id].direction, final=True)
            anims.append(Transform(self.arrow_blocks[id], new_arrow))
        self.play(LaggedStart(*anims))

    def construct(self):
        self.renderer.camera.background_color = self.background_color
        self.renderer.camera.init_background()

        from generation import AztecGenerator
        a = AztecGenerator()
        a.generate(n=5, seed="HD7XEC")
        self.from_obj(a.obj)
        self.wait(1)

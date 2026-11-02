
from ui.components.animation_engine import AnimationEngine


class StyleRankAnimator:

    def __init__(self, parent):

        self.engine = AnimationEngine(parent)

    # =====================================================
    # RANK UP
    # =====================================================

    def mostrar_rank_up(self, rank, points):

        self.engine.play(
            animation_type="rank_up",
            data={
                "rank": rank["name"],
                "title": rank["title"],
                "color": rank["color"],
                "message": f"+{points} STYLE POINTS"
            },
            fullscreen=False,
            duration=2.8
        )

    # =====================================================
    # RANK DOWN
    # =====================================================

    def mostrar_rank_down(
        self,
        previous_rank,
        current_rank,
        lost_points
    ):

        self.engine.play(
            animation_type="rank_down",
            data={
                "previous": previous_rank["name"],
                "rank": current_rank["name"],
                "message": f"-{lost_points} STYLE POINTS"
            },
            fullscreen=False,
            duration=2.4
        )

    # =====================================================
    # SSS
    # =====================================================

    def mostrar_sss(self, rank):

        self.engine.play(
            animation_type="sss",
            data={
                "rank": rank["name"],
                "title": rank["title"],
                "color": rank["color"]
            },
            fullscreen=True,
            duration=5.0
        )

    # =====================================================
    # CERRAR
    # =====================================================

    def cerrar(self):
        self.engine.close()

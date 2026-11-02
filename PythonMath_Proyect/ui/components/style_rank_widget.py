
import customtkinter as ctk

from mathematics.exercises.style_system import StyleSystem
from ui.components.style_animations import StyleRankAnimator


class StyleRankWidget(ctk.CTkFrame):

    def __init__(self, parent, **kwargs):

        super().__init__(
            parent,
            fg_color="#111827",
            corner_radius=12,
            border_width=1,
            border_color="#334155",
            **kwargs
        )

        self.style_system = StyleSystem()
        self.animator = StyleRankAnimator(self)

        self.crear_interfaz()
        self.actualizar_interfaz()

    # =====================================================
    # INTERFAZ COMPACTA
    # =====================================================

    def crear_interfaz(self):

        # ENCABEZADO
        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(
            fill="x",
            padx=15,
            pady=(12, 5)
        )

        self.rank_label = ctk.CTkLabel(
            header,
            text="D",
            font=("Arial", 30, "bold"),
            text_color="#A1A1AA"
        )
        self.rank_label.pack(side="left")

        self.rank_title = ctk.CTkLabel(
            header,
            text="DISMAL",
            font=("Poppins", 13, "bold"),
            text_color="#A1A1AA"
        )
        self.rank_title.pack(
            side="left",
            padx=10
        )

        self.points_label = ctk.CTkLabel(
            header,
            text="0 PTS",
            font=("Poppins", 12, "bold"),
            text_color="#F1F5F9"
        )
        self.points_label.pack(side="right")

        # BARRA DE PROGRESO
        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=9,
            corner_radius=10,
            progress_color="#A1A1AA",
            fg_color="#374151"
        )
        self.progress_bar.pack(
            fill="x",
            padx=15,
            pady=(5, 3)
        )

        self.progress_bar.set(0)

        self.next_rank_label = ctk.CTkLabel(
            self,
            text="NEXT RANK: CRAZY",
            font=("Poppins", 10),
            text_color="#94A3B8"
        )
        self.next_rank_label.pack(
            anchor="w",
            padx=15,
            pady=(0, 8)
        )

        # ESTADÍSTICAS
        stats = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        stats.pack(
            fill="x",
            padx=15,
            pady=(0, 12)
        )

        self.correct_label = ctk.CTkLabel(
            stats,
            text="CORRECT: 0",
            font=("Poppins", 10),
            text_color="#22C55E"
        )
        self.correct_label.pack(side="left")

        self.streak_label = ctk.CTkLabel(
            stats,
            text="STREAK: 0",
            font=("Poppins", 10),
            text_color="#F97316"
        )
        self.streak_label.pack(side="right")

    # =====================================================
    # ACTUALIZACIÓN VISUAL
    # =====================================================

    def actualizar_interfaz(self):

        stats = self.style_system.get_statistics()

        rank = stats["rank"]
        next_rank = self.style_system.get_next_rank()

        self.rank_label.configure(
            text=rank["name"],
            text_color=rank["color"]
        )

        self.rank_title.configure(
            text=rank["title"],
            text_color=rank["color"]
        )

        self.points_label.configure(
            text=f'{stats["points"]} PTS'
        )

        self.progress_bar.configure(
            progress_color=rank["color"]
        )

        self.progress_bar.set(
            self.style_system.get_progress()
        )

        if next_rank:

            faltantes = (
                next_rank["points"] - stats["points"]
            )

            self.next_rank_label.configure(
                text=(
                    f'NEXT RANK: {next_rank["title"]} '
                    f'({faltantes} PTS)'
                )
            )

        else:

            self.next_rank_label.configure(
                text="MAXIMUM STYLE RANK REACHED!"
            )

        self.correct_label.configure(
            text=f'CORRECT: {stats["correct"]}'
        )

        self.streak_label.configure(
            text=f'STREAK: {stats["streak"]}'
        )

    # =====================================================
    # REGISTRAR EJERCICIO
    # =====================================================

    def registrar_ejercicio(
        self,
        correct,
        difficulty="facil",
        used_hint=False,
        elapsed_seconds=None
    ):

        resultado = self.style_system.register_result(
            correct=correct,
            difficulty=difficulty,
            used_hint=used_hint,
            elapsed_seconds=elapsed_seconds
        )

        self.actualizar_interfaz()

        # RANK UP
        if resultado["rank_up"]:

            if resultado["current_rank"]["name"] == "SSS":

                self.animator.mostrar_sss(
                    resultado["current_rank"]
                )

            else:

                self.animator.mostrar_rank_up(
                    resultado["current_rank"],
                    resultado["earned_points"]
                )

        # RANK DOWN
        elif resultado["rank_down"]:

            self.animator.mostrar_rank_down(
                resultado["previous_rank"],
                resultado["current_rank"],
                resultado["lost_points"]
            )

        return resultado


    # =====================================================
    # REINICIAR SESIÓN
    # =====================================================

    def reiniciar_sesion(self):

        self.style_system.reset_session()
        self.actualizar_interfaz()

    # =====================================================
    # ESTADÍSTICAS COMPLETAS
    # =====================================================

    def obtener_estadisticas(self):

        return self.style_system.get_statistics()

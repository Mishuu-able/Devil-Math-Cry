
import tkinter as tk
import math
import random
import time


class AnimationEngine:

    def __init__(self, parent):
        self.parent = parent
        self.window = None
        self.canvas = None
        self.after_id = None

        self.running = False
        self.start_time = 0
        self.duration = 0

        self.width = 0
        self.height = 0

        self.animation_type = None
        self.data = {}
        self.particles = []

    # =====================================================
    # INICIAR ANIMACIÓN
    # =====================================================

    def play(
        self,
        animation_type,
        data,
        fullscreen=False,
        duration=3.0
    ):

        self.close()

        self.animation_type = animation_type
        self.data = data
        self.duration = duration

        self.window = tk.Toplevel(self.parent)
        self.window.overrideredirect(True)
        self.window.attributes("-topmost", True)

        self.window.configure(bg="#080A12")

        if fullscreen:
            self.width = self.window.winfo_screenwidth()
            self.height = self.window.winfo_screenheight()

            self.window.geometry(
                f"{self.width}x{self.height}+0+0"
            )

        else:
            root = self.parent.winfo_toplevel()

            root.update_idletasks()

            root_x = root.winfo_rootx()
            root_y = root.winfo_rooty()

            root_width = root.winfo_width()
            root_height = root.winfo_height()

            self.width = min(650, root_width - 40)
            self.height = 300

            x = root_x + (root_width - self.width) // 2
            y = root_y + (root_height - self.height) // 2

            self.window.geometry(
                f"{self.width}x{self.height}+{x}+{y}"
            )

        self.canvas = tk.Canvas(
            self.window,
            width=self.width,
            height=self.height,
            bg="#080A12",
            highlightthickness=0
        )

        self.canvas.pack(fill="both", expand=True)

        self.window.bind("<Escape>", lambda event: self.close())
        self.window.protocol(
            "WM_DELETE_WINDOW",
            self.close
        )

        self._crear_particulas()

        self.start_time = time.perf_counter()
        self.running = True

        self._animate()

    # =====================================================
    # PARTÍCULAS
    # =====================================================

    def _crear_particulas(self):

        self.particles = []

        total = 100 if self.animation_type == "sss" else 35

        for _ in range(total):

            self.particles.append({
                "x": random.uniform(0, self.width),
                "y": random.uniform(0, self.height),
                "speed": random.uniform(0.5, 2.5),
                "size": random.randint(1, 4),
                "phase": random.uniform(0, math.pi * 2)
            })

    # =====================================================
    # BUCLE DE ANIMACIÓN
    # =====================================================

    def _animate(self):

        if not self.running or self.canvas is None:
            return

        elapsed = time.perf_counter() - self.start_time
        progress = min(elapsed / self.duration, 1.0)

        self.canvas.delete("all")

        if self.animation_type == "rank_up":
            self._draw_rank_up(progress)

        elif self.animation_type == "rank_down":
            self._draw_rank_down(progress)

        elif self.animation_type == "sss":
            self._draw_sss(progress)

        if progress >= 1.0:
            self.close()
            return

        self.after_id = self.window.after(
            16,
            self._animate
        )

    # =====================================================
    # PARTÍCULAS EN CANVAS
    # =====================================================

    def _draw_particles(self, color, progress):

        for particle in self.particles:

            x = particle["x"]
            y = particle["y"]

            y -= particle["speed"] * 2

            particle["y"] = y

            if y < 0:
                particle["y"] = self.height

            pulse = (
                math.sin(
                    progress * 15 + particle["phase"]
                ) + 1
            ) / 2

            size = particle["size"] * (0.5 + pulse)

            self.canvas.create_oval(
                x - size,
                y - size,
                x + size,
                y + size,
                fill=color,
                outline=""
            )

    # =====================================================
    # RANK UP
    # =====================================================

    def _draw_rank_up(self, progress):

        color = self.data["color"]

        w = self.width
        h = self.height

        self.canvas.create_rectangle(
            0, 0, w, h,
            fill="#080A12",
            outline=""
        )

        self._draw_particles(color, progress)

        # Entrada lateral
        entrance = min(progress * 4, 1)
        eased = 1 - (1 - entrance) ** 3

        center_x = w / 2
        center_y = h / 2

        offset = (1 - eased) * -w

        # Diagonal
        self.canvas.create_polygon(
            offset,
            0,
            offset + 100,
            0,
            offset + 300,
            h,
            offset + 200,
            h,
            fill=color,
            outline=""
        )

        # Línea de energía
        line_x = -100 + (w + 200) * min(progress * 2, 1)

        self.canvas.create_line(
            line_x,
            0,
            line_x - 150,
            h,
            fill=color,
            width=3
        )

        # Título
        self.canvas.create_text(
            center_x,
            48,
            text="STYLE RANK UP",
            font=("Arial", 16, "bold"),
            fill="#FFFFFF"
        )

        # Rango
        rank_x = center_x + offset

        self.canvas.create_text(
            rank_x,
            center_y - 12,
            text=self.data["rank"],
            font=("Arial", 100, "bold"),
            fill=color
        )

        # Nombre
        self.canvas.create_text(
            center_x,
            center_y + 78,
            text=self.data["title"],
            font=("Arial", 20, "bold"),
            fill=color
        )

        # Puntos
        self.canvas.create_text(
            center_x,
            h - 35,
            text=self.data["message"],
            font=("Arial", 14, "bold"),
            fill="#FFFFFF"
        )

    # =====================================================
    # RANK DOWN
    # =====================================================

    def _draw_rank_down(self, progress):

        w = self.width
        h = self.height

        color = "#EF4444"

        # Flash de impacto
        flash = max(0, 1 - progress * 8)

        background = "#30070D" if flash > 0.3 else "#080A12"

        self.canvas.create_rectangle(
            0, 0, w, h,
            fill=background,
            outline=""
        )

        self._draw_particles(color, progress)

        center_x = w / 2
        center_y = h / 2

        # Interferencia horizontal
        random.seed(int(progress * 100))

        for _ in range(9):

            y = random.randint(0, h)
            offset = random.randint(-15, 15)

            self.canvas.create_line(
                0,
                y,
                w,
                y + offset,
                fill=color,
                width=random.randint(1, 3)
            )

        random.seed()

        self.canvas.create_text(
            center_x,
            48,
            text="STYLE RANK DOWN",
            font=("Arial", 17, "bold"),
            fill=color
        )

        # Transición entre rangos
        previous = self.data["previous"]
        current = self.data["rank"]

        self.canvas.create_text(
            center_x - 100,
            center_y,
            text=previous,
            font=("Arial", 65, "bold"),
            fill="#64748B"
        )

        self.canvas.create_text(
            center_x,
            center_y,
            text="→",
            font=("Arial", 35, "bold"),
            fill="#FFFFFF"
        )

        self.canvas.create_text(
            center_x + 100,
            center_y,
            text=current,
            font=("Arial", 65, "bold"),
            fill=color
        )

        self.canvas.create_text(
            center_x,
            h - 45,
            text=self.data["message"],
            font=("Arial", 14, "bold"),
            fill="#FFFFFF"
        )

    # =====================================================
    # SSS FULLSCREEN
    # =====================================================

    def _draw_sss(self, progress):

        w = self.width
        h = self.height

        color = "#E879F9"

        self.canvas.create_rectangle(
            0, 0, w, h,
            fill="#08020D",
            outline=""
        )

        self._draw_particles(color, progress)

        center_x = w / 2
        center_y = h / 2

        # Diagonales
        for i in range(7):

            offset = (i - 3) * 120

            self.canvas.create_line(
                center_x + offset - progress * 200,
                0,
                center_x + offset + progress * 200,
                h,
                fill="#45134F",
                width=2
            )

        # Flash inicial
        flash = max(0, 1 - progress * 5)

        if flash > 0:
            self.canvas.create_rectangle(
                0, 0, w, h,
                fill="#FFFFFF",
                outline=""
            )

        # Rango gigante
        scale = min(1, progress * 4)

        font_size = int(
            180 + 100 * scale
        )

        self.canvas.create_text(
            center_x,
            center_y - 50,
            text="SSS",
            font=("Arial", font_size, "bold"),
            fill=color
        )

        self.canvas.create_text(
            center_x,
            center_y + 105,
            text="SMOKIN' SEXY STYLE",
            font=("Arial", 28, "bold"),
            fill="#FFFFFF"
        )

        self.canvas.create_line(
            center_x - 350,
            center_y + 145,
            center_x + 350,
            center_y + 145,
            fill=color,
            width=4
        )

        self.canvas.create_text(
            center_x,
            center_y + 190,
            text="YOU ARE UNSTOPPABLE",
            font=("Arial", 17, "bold"),
            fill=color
        )

    # =====================================================
    # CERRAR
    # =====================================================

    def close(self):

        self.running = False

        window = self.window

        self.window = None
        self.canvas = None
        self.after_id = None

        if window is None:
            return

        try:
            if window.winfo_exists():
                window.destroy()
        except Exception:
            pass

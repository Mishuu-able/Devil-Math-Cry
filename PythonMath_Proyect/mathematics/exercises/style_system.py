
class StyleSystem:

    RANKS = [
        {"name": "D", "title": "DISMAL", "points": 0, "color": "#A1A1AA"},
        {"name": "C", "title": "CRAZY", "points": 200, "color": "#60A5FA"},
        {"name": "B", "title": "BLAST", "points": 450, "color": "#22C55E"},
        {"name": "A", "title": "AWESOME", "points": 750, "color": "#EAB308"},
        {"name": "S", "title": "STYLISH", "points": 1100, "color": "#F97316"},
        {"name": "SS", "title": "SMOKIN'", "points": 1600, "color": "#EF4444"},
        {"name": "SSS", "title": "SMOKIN' SEXY STYLE", "points": 2200, "color": "#E879F9"}
    ]

    # Penalizaciones base según dificultad
    PENALTIES = {
        "facil": 50,
        "intermedio": 100,
        "dificil": 175
    }

    # Multiplicadores según rango actual
    RANK_MULTIPLIERS = {
        "D": 1.0,
        "C": 1.0,
        "B": 1.1,
        "A": 1.2,
        "S": 1.35,
        "SS": 1.5,
        "SSS": 1.75
    }

    def __init__(self):
        self.reset_session()

    def reset_session(self):
        """Reinicia todas las estadísticas de la sesión."""

        self.points = 0
        self.correct_answers = 0
        self.incorrect_answers = 0
        self.current_streak = 0
        self.best_streak = 0
        self.total_exercises = 0

    def get_rank(self):
        """Obtiene el rango correspondiente a los puntos actuales."""

        current_rank = self.RANKS[0]

        for rank in self.RANKS:
            if self.points >= rank["points"]:
                current_rank = rank
            else:
                break

        return current_rank

    def get_next_rank(self):
        """Obtiene el siguiente rango, si existe."""

        current_rank = self.get_rank()
        index = self.RANKS.index(current_rank)

        if index + 1 >= len(self.RANKS):
            return None

        return self.RANKS[index + 1]

    def get_progress(self):
        """Calcula el progreso hacia el siguiente rango."""

        current_rank = self.get_rank()
        next_rank = self.get_next_rank()

        if next_rank is None:
            return 1.0

        rango_actual = current_rank["points"]
        rango_siguiente = next_rank["points"]

        progreso = (
            (self.points - rango_actual)
            / (rango_siguiente - rango_actual)
        )

        return max(0.0, min(progreso, 1.0))

    def calculate_penalty(self, difficulty, rank):
        """Calcula la penalización según dificultad y rango."""

        difficulty = difficulty.lower()

        base_penalty = self.PENALTIES.get(
            difficulty,
            self.PENALTIES["facil"]
        )

        multiplier = self.RANK_MULTIPLIERS.get(
            rank["name"],
            1.0
        )

        return round(base_penalty * multiplier), base_penalty, multiplier

    def register_result(
        self,
        correct,
        difficulty="facil",
        used_hint=False,
        elapsed_seconds=None
    ):
        """
        Registra el resultado de un ejercicio.

        Calcula recompensas, penalizaciones y cambios de rango.
        """

        previous_points = self.points
        previous_rank = self.get_rank()

        penalty_points = 0
        penalty_base = 0
        penalty_multiplier = 1.0

        self.total_exercises += 1

        earned_points = 0

        if correct:

            self.correct_answers += 1
            self.current_streak += 1

            self.best_streak = max(
                self.best_streak,
                self.current_streak
            )

            # Recompensa por respuesta correcta
            earned_points += 100

            # Recompensa por no utilizar pistas
            if not used_hint:
                earned_points += 50

            # Recompensa por velocidad
            if (
                elapsed_seconds is not None
                and 0 <= elapsed_seconds < 30
            ):
                earned_points += 25

            # Recompensa por dificultad
            if difficulty.lower() == "dificil":
                earned_points += 100

            elif difficulty.lower() == "intermedio":
                earned_points += 50

            # Bonus por racha
            if self.current_streak % 3 == 0:
                earned_points += 75

        else:

            self.incorrect_answers += 1
            self.current_streak = 0

            # PENALIZACIÓN PROGRESIVA
            penalty_points, penalty_base, penalty_multiplier = (
                self.calculate_penalty(
                    difficulty,
                    previous_rank
                )
            )

            # Nunca permitir puntuación negativa
            penalty_points = min(
                penalty_points,
                self.points
            )

            self.points -= penalty_points

        # Aplicar recompensas
        self.points += earned_points

        new_rank = self.get_rank()

        rank_up = (
            new_rank["name"] != previous_rank["name"]
            and self.points > previous_points
        )

        rank_down = (
            new_rank["name"] != previous_rank["name"]
            and self.points < previous_points
        )

        return {
            "earned_points": earned_points,
            "total_points": self.points,

            "correct": self.correct_answers,
            "incorrect": self.incorrect_answers,

            "streak": self.current_streak,
            "best_streak": self.best_streak,

            "previous_rank": previous_rank,
            "current_rank": new_rank,

            "rank_up": rank_up,
            "rank_down": rank_down,

            "progress": self.get_progress(),
            "next_rank": self.get_next_rank(),

            "lost_points": penalty_points,
            "penalty_base": penalty_base,
            "penalty_multiplier": penalty_multiplier
        }

    def get_accuracy(self):
        """Calcula el porcentaje de respuestas correctas."""

        if self.total_exercises == 0:
            return 0

        return round(
            (self.correct_answers / self.total_exercises) * 100,
            1
        )

    def get_statistics(self):

        return {
            "points": self.points,
            "rank": self.get_rank(),
            "correct": self.correct_answers,
            "incorrect": self.incorrect_answers,
            "total": self.total_exercises,
            "streak": self.current_streak,
            "best_streak": self.best_streak,
            "accuracy": self.get_accuracy()
        }

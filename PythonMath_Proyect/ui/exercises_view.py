
import customtkinter as ctk
import threading
import time

from mathematics.ai.ai_service import AIService
from mathematics.exercises.linear_generator import LinearExerciseGenerator
from ui.components.style_rank_widget import StyleRankWidget
from ui.theme import (
    EXERCISES_BG as FONDO,
    EXERCISES_CARD as TARJETA,
    EXERCISES_CARD_SECONDARY as TARJETA_SECUNDARIA,

    EXERCISES_PRIMARY as ROJO,
    EXERCISES_PRIMARY_HOVER as ROJO_HOVER,
    EXERCISES_PRIMARY_DARK as ROJO_OSCURO,

    EXERCISES_TAB_BG as TAB_BG,
    EXERCISES_TAB_HOVER as TAB_HOVER,

    EXERCISES_TEXT as TEXTO,
    EXERCISES_TEXT_SECONDARY as TEXTO_SECUNDARIO,
    EXERCISES_TEXT_LIGHT as TEXTO_CLARO,
    EXERCISES_TEXT_MUTED as TEXTO_SUAVE,
    EXERCISES_WHITE as BLANCO,

    SUCCESS_COLOR,
    ERROR_COLOR,
    WARNING_COLOR,

    FONT_FAMILY as FUENTE
)


class ExercisesView(ctk.CTkFrame):

    def __init__(self, parent):
        super().__init__(
            parent,
            fg_color= FONDO,
            corner_radius=0
        )

        self.pack(fill="both", expand=True)

        # CHATBOT
        self.ai_service = AIService()
        self.esperando_respuesta = False
        self.loading_message = None

        # EJERCICIOS PROCEDURALES
        self.exercise_generator = LinearExerciseGenerator()
        self.exercise_start_time = None
        self.exercise_respondido = False

        self.crear_interfaz()

    # ========================================================
    # INTERFAZ PRINCIPAL
    # ========================================================

    def crear_interfaz(self):

        header = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )
        header.pack(
            fill="x",
            padx=30,
            pady=(24, 15)
        )

        ctk.CTkLabel(
            header,
            text="Ejercicios",
            font=("Poppins", 27, "bold"),
            text_color= TEXTO
        ).pack(anchor="w")

        ctk.CTkLabel(
            header,
            text="Practica matemáticas y resuelve tus dudas.",
            font=("Poppins", 13),
            text_color= TEXTO_SECUNDARIO
        ).pack(anchor="w", pady=(5, 0))

        # PESTAÑAS
        self.tabs = ctk.CTkTabview(
            self,
            fg_color= TARJETA_SECUNDARIA,
            segmented_button_fg_color= TARJETA,
            segmented_button_selected_color= ROJO,
            segmented_button_selected_hover_color= ROJO_HOVER,
            segmented_button_unselected_color= TARJETA,
            segmented_button_unselected_hover_color= TAB_HOVER,
            text_color= BLANCO
        )

        self.tabs.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 25)
        )

        self.chat_tab = self.tabs.add("REBELLION")
        self.practice_tab = self.tabs.add("PRACTICE MODE")

        self.crear_chat()
        self.crear_practica()

    # ========================================================
    # PESTAÑA: CHATBOT YAMATO
    # ========================================================

    def crear_chat(self):

        content = self.chat_tab

        assistant_header = ctk.CTkFrame(
            content,
            fg_color= TARJETA,
            corner_radius=10
        )
        assistant_header.pack(
            fill="x",
            padx=15,
            pady=15
        )

        ctk.CTkLabel(
            assistant_header,
            text="🤖 REBELLION ASSISTANT",
            font=("Poppins", 17, "bold"),
            text_color= TEXTO
        ).pack(
            side="left",
            padx=15,
            pady=12
        )

        ctk.CTkLabel(
            assistant_header,
            text="● En línea",
            font=("Poppins", 11),
            text_color= SUCCESS_COLOR
        ).pack(
            side="right",
            padx=15
        )

        # CHAT
        self.chat_area = ctk.CTkScrollableFrame(
            content,
            fg_color= FONDO,
            corner_radius=10
        )
        self.chat_area.pack(
            fill="both",
            expand=True,
            padx=15,
            pady=(0, 15)
        )

        self.agregar_mensaje(
            "assistant",
            "¡Hola! Soy tu asistente matemático.\n\n"
            "Puedes enviarme ejercicios de álgebra, "
            "cálculo, límites, funciones y otras áreas "
            "de las matemáticas.\n\n"
            "Estoy aquí para ayudarte a comprender "
            "los procedimientos."
        )

        # CONFIGURACIÓN
        options = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        options.pack(
            fill="x",
            padx=15,
            pady=(0, 10)
        )

        self.nivel_selector = ctk.CTkOptionMenu(
            options,
            values=[
                "primaria",
                "secundaria",
                "universidad"
            ],
            width=150,
            height=35,
            fg_color=TARJETA,
            button_color=ROJO,
            button_hover_color=ROJO_HOVER,
            dropdown_fg_color=TARJETA,
            dropdown_hover_color=ROJO_HOVER,
            dropdown_text_color=TEXTO,
            text_color=BLANCO
        )
        self.nivel_selector.set("universidad")
        self.nivel_selector.pack(
            side="left",
            padx=(0, 10)
        )

        self.modo_selector = ctk.CTkOptionMenu(
            options,
            values=[
                "procedimiento",
                "respuesta"
            ],
            width=160,
            height=35,
            fg_color=TARJETA,
            button_color=ROJO,
            button_hover_color=ROJO_HOVER,
            dropdown_fg_color=TARJETA,
            dropdown_hover_color=ROJO_HOVER,
            dropdown_text_color=TEXTO,
            text_color=BLANCO
        )
        self.modo_selector.set("procedimiento")
        self.modo_selector.pack(side="left")

        # INPUT
        input_container = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )
        input_container.pack(
            fill="x",
            padx=15,
            pady=(0, 15)
        )

        self.message_input = ctk.CTkEntry(
            input_container,
            placeholder_text="Escribe tu pregunta matemática...",
            height=45,
            font=("Poppins", 13)
        )
        self.message_input.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 10)
        )

        self.message_input.bind(
            "<Return>",
            self.enviar_mensaje
        )

        self.send_button = ctk.CTkButton(
            input_container,
            text="Enviar",
            width=100,
            height=45,
            fg_color= ROJO,
            hover_color= ROJO_HOVER,
            command=self.enviar_mensaje
        )
        self.send_button.pack(side="right")

    # ========================================================
    # MENSAJES DEL CHAT
    # ========================================================

    def agregar_mensaje(self, role, message):

        es_usuario = role == "user"

        bubble = ctk.CTkFrame(
            self.chat_area,
            fg_color= ROJO_OSCURO if es_usuario else TARJETA,
            corner_radius=12
        )

        bubble.pack(
            anchor="e" if es_usuario else "w",
            padx=10,
            pady=7
        )

        ctk.CTkLabel(
            bubble,
            text=message,
            font=("Poppins", 12),
            text_color= BLANCO,
            wraplength=500,
            justify="left"
        ).pack(
            padx=15,
            pady=10
        )

        self.after(
            50,
            lambda: self.chat_area._parent_canvas.yview_moveto(1.0)
        )

    # ========================================================
    # ENVÍO DE MENSAJES A YAMATO
    # ========================================================

    def enviar_mensaje(self, event=None):

        if self.esperando_respuesta:
            return

        message = self.message_input.get().strip()

        if not message:
            return

        nivel = self.nivel_selector.get()
        modo = self.modo_selector.get()

        self.agregar_mensaje("user", message)
        self.message_input.delete(0, "end")

        self.esperando_respuesta = True

        self.send_button.configure(
            state="disabled",
            text="..."
        )

        self.loading_message = ctk.CTkFrame(
            self.chat_area,
            fg_color=TARJETA,
            corner_radius=12
        )

        self.loading_message.pack(
            anchor="w",
            padx=10,
            pady=7
        )

        ctk.CTkLabel(
            self.loading_message,
            text="Resolviendo ejercicio... 🧠",
            text_color= BLANCO,
            font=("Poppins", 12)
        ).pack(
            padx=15,
            pady=10
        )

        threading.Thread(
            target=self.consultar_ia,
            args=(message, nivel, modo),
            daemon=True
        ).start()

    # ========================================================
    # CONSULTA A LA IA
    # ========================================================

    def consultar_ia(self, message, nivel, modo):

        try:
            respuesta = self.ai_service.preguntar(
                mensaje=message,
                nivel=nivel,
                modo=modo
            )
            error = None

        except Exception as e:
            respuesta = None
            error = str(e)

        try:
            self.after(
                0,
                lambda: self.finalizar_consulta(
                    respuesta,
                    error
                )
            )
        except RuntimeError:
            pass

    # ========================================================
    # FINALIZAR CONSULTA
    # ========================================================

    def finalizar_consulta(self, respuesta, error):

        if self.loading_message is not None:
            self.loading_message.destroy()
            self.loading_message = None

        self.esperando_respuesta = False

        self.send_button.configure(
            state="normal",
            text="Enviar"
        )

        if error:
            self.agregar_mensaje(
                "assistant",
                f"No pude obtener una respuesta:\n\n{error}"
            )
        else:
            self.agregar_mensaje(
                "assistant",
                respuesta
            )

    # ========================================================
    # PESTAÑA: PRACTICE MODE
    # ========================================================

    def crear_practica(self):

         # STYLE RANK: SOLO VISIBLE EN TRAINING MODE
        self.style_widget = StyleRankWidget(self.practice_tab)

        self.style_widget.pack(
            fill="x",
            padx=10,
            pady=(5, 10)
        )

        # CONTENEDOR CON SCROLL
        content = ctk.CTkScrollableFrame(
            self.practice_tab,
            fg_color="transparent",
            scrollbar_button_color= ROJO_OSCURO,
            scrollbar_button_hover_color= ROJO
        )

        content.pack(
            fill="both",
            expand=True,
            padx=5,
            pady=5
        )

        # ENCABEZADO
        ctk.CTkLabel(
            content,
            text="⚔️ TRAINING ROOM",
            font=("Poppins", 21, "bold"),
            text_color= TEXTO
        ).pack(
            anchor="w",
            padx=25,
            pady=(20, 5)
        )

        ctk.CTkLabel(
            content,
            text="Resuelve ejercicios y demuestra tu habilidad matemática.",
            font=("Poppins", 12),
            text_color= TEXTO_SECUNDARIO
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 20)
        )

        # CONFIGURACIÓN DE DIFICULTAD
        difficulty_frame = ctk.CTkFrame(
            content,
            fg_color=TARJETA,
            corner_radius=10
        )
        difficulty_frame.pack(
            fill="x",
            padx=25,
            pady=(0, 20)
        )

        ctk.CTkLabel(
            difficulty_frame,
            text="Dificultad:",
            font=("Poppins", 12, "bold"),
            text_color= BLANCO
        ).pack(
            side="left",
            padx=15,
            pady=12
        )

        self.difficulty_selector = ctk.CTkOptionMenu(
            difficulty_frame,
            values=[
                "facil",
                "intermedio",
                "dificil"
            ],
            width=150,
            height=35,
            fg_color=TARJETA,
            button_color=ROJO,
            button_hover_color=ROJO_HOVER,
            dropdown_fg_color=TARJETA,
            dropdown_hover_color=ROJO_HOVER,
            dropdown_text_color=TEXTO,
            text_color=BLANCO
        )
        self.difficulty_selector.set("facil")
        self.difficulty_selector.pack(
            side="left",
            padx=10,
            pady=10
        )

        # TARJETA DEL EJERCICIO
        exercise_card = ctk.CTkFrame(
            content,
            fg_color=FONDO,
            corner_radius=15
        )
        exercise_card.pack(
            fill="x",
            padx=25,
            pady=(0, 15)
        )

        ctk.CTkLabel(
            exercise_card,
            text="RESUELVE LA SIGUIENTE ECUACIÓN",
            font=("Poppins", 12, "bold"),
            text_color= TEXTO_SECUNDARIO
        ).pack(
            pady=(20, 10)
        )

        self.exercise_label = ctk.CTkLabel(
            exercise_card,
            text="Presiona GENERAR para comenzar.",
            font=("Cambria Math", 27, "bold"),
            text_color= TEXTO
        )
        self.exercise_label.pack(
            padx=15,
            pady=(5, 25)
        )

        # GENERAR EJERCICIO
        self.generate_button = ctk.CTkButton(
            content,
            text="⚔️ GENERAR EJERCICIO",
            height=42,
            fg_color= ROJO_HOVER,
            hover_color= ROJO_OSCURO,
            font=("Poppins", 13, "bold"),
            command=self.generar_ejercicio
        )

        self.generate_button.pack(
            fill="x",
            padx=25,
            pady=(0, 15)
        )

        # RESPUESTA
        ctk.CTkLabel(
            content,
            text="Introduce el valor de x:",
            font=("Poppins", 12),
            text_color= TEXTO_CLARO
        ).pack(
            anchor="w",
            padx=25,
            pady=(0, 5)
        )

        self.answer_entry = ctk.CTkEntry(
            content,
            placeholder_text="Ejemplo: 5",
            height=42,
            font=("Poppins", 14)
        )
        self.answer_entry.pack(
            fill="x",
            padx=25,
            pady=(0, 12)
        )

        self.answer_entry.bind(
            "<Return>",
            lambda event: self.comprobar_respuesta()
        )

        self.check_button = ctk.CTkButton(
            content,
            text="COMPROBAR RESPUESTA",
            height=42,
            fg_color= ROJO,
            hover_color= ROJO_HOVER,
            command=self.comprobar_respuesta,
            state="disabled"
        )
        self.check_button.pack(
            fill="x",
            padx=25,
            pady=(0, 15)
        )

        # RESULTADO
        self.practice_status = ctk.CTkLabel(
            content,
            text="Esperando ejercicio...",
            font=("Poppins", 13, "bold"),
            text_color= TEXTO_SECUNDARIO,
            wraplength=600,
            justify="left"
        )
        self.practice_status.pack(
            anchor="w",
            padx=25,
            pady=(0, 10)
        )

        # PROCEDIMIENTO
        self.procedure_box = ctk.CTkTextbox(
            content,
            height=145,
            fg_color= TARJETA,
            text_color= TEXTO_SUAVE,
            font=("Poppins", 12),
            corner_radius=10,
            wrap="word"
        )
        self.procedure_box.pack(
            fill="both",
            expand=True,
            padx=25,
            pady=(0, 20)
        )

        self.procedure_box.insert(
            "1.0",
            "Aquí aparecerá el procedimiento cuando compruebes tu respuesta."
        )
        self.procedure_box.configure(state="disabled")

    # ========================================================
    # GENERAR EJERCICIO
    # ========================================================

    def generar_ejercicio(self):

        dificultad = self.difficulty_selector.get()

        ejercicio = self.exercise_generator.generar_ejercicio(
            dificultad
        )

        self.exercise_respondido = False
        self.exercise_start_time = time.time()

        self.exercise_label.configure(
            text=ejercicio["ecuacion"]
        )

        self.answer_entry.configure(state="normal")
        self.answer_entry.delete(0, "end")

        self.check_button.configure(state="normal")

        self.practice_status.configure(
            text="Resuelve la ecuación y comprueba tu respuesta.",
            text_color= TEXTO_SECUNDARIO
        )

        self.procedure_box.configure(state="normal")
        self.procedure_box.delete("1.0", "end")
        self.procedure_box.insert(
            "1.0",
            "Ejercicio generado.\n\n"
            "Despeja la variable x y escribe tu respuesta."
        )
        self.procedure_box.configure(state="disabled")

        self.answer_entry.focus()

    # ========================================================
    # COMPROBAR RESPUESTA
    # ========================================================

    def comprobar_respuesta(self):

        if self.exercise_respondido:
            return

        respuesta = self.answer_entry.get().strip()

        if not respuesta:
            self.practice_status.configure(
                text="Introduce una respuesta antes de continuar.",
                text_color= WARNING_COLOR
            )
            return

        resultado = self.exercise_generator.verificar_respuesta(
            respuesta
        )

        # Respuesta inválida: no consume el ejercicio ni da puntos.
        if not resultado["valida"]:
            self.practice_status.configure(
                text=resultado["mensaje"],
                text_color= WARNING_COLOR
            )
            return

        self.exercise_respondido = True

        elapsed = (
            time.time() - self.exercise_start_time
            if self.exercise_start_time is not None
            else None
        )

        dificultad = self.difficulty_selector.get()

        # REGISTRAR RESULTADO EN EL STYLE RANK
        ranking_result = self.style_widget.registrar_ejercicio(
            correct=resultado["correcta"],
            difficulty=dificultad,
            used_hint=False,
            elapsed_seconds=elapsed
        )

        self.answer_entry.configure(state="disabled")
        self.check_button.configure(state="disabled")

        if resultado["correcta"]:

            self.practice_status.configure(
                text=(
                    "¡RESPUESTA CORRECTA! +"
                    f"{ranking_result['earned_points']} STYLE POINTS"
                ),
                text_color= SUCCESS_COLOR
            )

        else:

            self.practice_status.configure(
                text=(
                    "RESPUESTA INCORRECTA. "
                    f"La solución era x = {resultado['respuesta_correcta']}.\n"
                    f"-{ranking_result['lost_points']} STYLE POINTS"
                ),
                text_color= ERROR_COLOR
            )

        # MOSTRAR PROCEDIMIENTO
        pasos = self.exercise_generator.obtener_procedimiento()

        procedimiento = "\n\n".join(
            f"• {paso}" for paso in pasos
        )

        self.procedure_box.configure(state="normal")
        self.procedure_box.delete("1.0", "end")
        self.procedure_box.insert(
            "1.0",
            procedimiento
        )
        self.procedure_box.configure(state="disabled")

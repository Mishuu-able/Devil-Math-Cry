import customtkinter as ctk
import threading

from mathematics.ai.ai_service import AIService


class MathChat(ctk.CTkFrame):

    # ==============================================
    # PALETA DE COLORES - DEVIL MATH CRY
    # ==============================================

    COLOR_FONDO = "#151314"
    COLOR_PANEL = "#1D1A1C"
    COLOR_BURBUJA_IA = "#282326"
    COLOR_BURBUJA_USUARIO = "#49252B"

    COLOR_ROJO = "#A8323D"
    COLOR_ROJO_HOVER = "#C0444E"

    COLOR_TEXTO = "#F2ECEC"
    COLOR_TEXTO_SUAVE = "#B8AAAD"

    COLOR_BORDE = "#392D30"

    # ==============================================
    # INICIALIZACIÓN
    # ==============================================

    def __init__(
        self,
        parent,
        contexto=None,
        titulo="Rebellion - Asistente matemático"
    ):

        super().__init__(
            parent,
            fg_color=self.COLOR_FONDO,
            corner_radius=14,
            border_width=1,
            border_color=self.COLOR_BORDE
        )

        self.parent = parent
        self.contexto = contexto or {}

        self.ai_service = AIService()

        self.historial = []
        self.procesando = False

        self.crear_interfaz()

    # ==============================================
    # INTERFAZ
    # ==============================================

    def crear_interfaz(self):

        # ------------------------------------------
        # ENCABEZADO
        # ------------------------------------------

        encabezado = ctk.CTkFrame(
            self,
            fg_color="transparent",
            corner_radius=0
        )

        encabezado.pack(
            fill="x",
            padx=18,
            pady=(15, 5)
        )

        identidad = ctk.CTkFrame(
            encabezado,
            fg_color="transparent"
        )

        identidad.pack(
            side="left",
            fill="x",
            expand=True
        )

        ctk.CTkLabel(
            identidad,
            text="REBELLION",
            font=("Poppins", 17, "bold"),
            text_color=self.COLOR_ROJO_HOVER
        ).pack(anchor="w")

        ctk.CTkLabel(
            identidad,
            text="Asistente matemático",
            font=("Poppins", 11),
            text_color=self.COLOR_TEXTO_SUAVE
        ).pack(
            anchor="w",
            pady=(0, 2)
        )

        ctk.CTkLabel(
            encabezado,
            text="● EN LÍNEA",
            font=("Poppins", 9, "bold"),
            text_color="#9C777D"
        ).pack(
            side="right",
            padx=(8, 2)
        )

        # Separador

        ctk.CTkFrame(
            self,
            height=1,
            fg_color=self.COLOR_BORDE,
            corner_radius=0
        ).pack(
            fill="x",
            padx=18,
            pady=(7, 8)
        )

        # ------------------------------------------
        # CONFIGURACIÓN
        # ------------------------------------------

        configuracion = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        configuracion.pack(
            fill="x",
            padx=18,
            pady=(3, 10)
        )

        configuracion.grid_columnconfigure(
            (0, 1),
            weight=1
        )

        ctk.CTkLabel(
            configuracion,
            text="NIVEL ACADÉMICO",
            font=("Poppins", 9, "bold"),
            text_color=self.COLOR_TEXTO_SUAVE
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=(0, 8),
            pady=(0, 5)
        )

        ctk.CTkLabel(
            configuracion,
            text="MODO DE RESPUESTA",
            font=("Poppins", 9, "bold"),
            text_color=self.COLOR_TEXTO_SUAVE
        ).grid(
            row=0,
            column=1,
            sticky="w",
            padx=(8, 0),
            pady=(0, 5)
        )

        # Estilo compatible con CTkOptionMenu

        estilo_opciones = {
            "height": 32,
            "corner_radius": 8,

            "fg_color": self.COLOR_PANEL,

            "button_color": "#633039",
            "button_hover_color": self.COLOR_ROJO,

            "dropdown_fg_color": self.COLOR_PANEL,
            "dropdown_hover_color": "#49252B",

            "text_color": self.COLOR_TEXTO,
            "dropdown_text_color": self.COLOR_TEXTO,

            "font": ("Poppins", 10),
            "dropdown_font": ("Poppins", 10)
        }

        # Selector de nivel

        self.selector_nivel = ctk.CTkOptionMenu(
            configuracion,
            values=[
                "Primaria",
                "Secundaria",
                "Universidad"
            ],
            **estilo_opciones
        )

        self.selector_nivel.set("Universidad")

        self.selector_nivel.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(0, 8)
        )

        # Selector de modo

        self.selector_modo = ctk.CTkOptionMenu(
            configuracion,
            values=[
                "Procedimiento paso a paso",
                "Respuesta directa"
            ],
            **estilo_opciones
        )

        self.selector_modo.set(
            "Procedimiento paso a paso"
        )

        self.selector_modo.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=(8, 0)
        )

        # ------------------------------------------
        # ÁREA DE CONVERSACIÓN
        # ------------------------------------------

        self.chat_frame = ctk.CTkScrollableFrame(
            self,
            fg_color=self.COLOR_PANEL,
            corner_radius=12,
            scrollbar_button_color="#604047",
            scrollbar_button_hover_color=self.COLOR_ROJO
        )

        self.chat_frame.pack(
            fill="both",
            expand=True,
            padx=18,
            pady=(2, 8)
        )

        # Mensaje inicial

        self.agregar_mensaje(
            "Rebellion",
            "¡Hola! Soy Rebellion. "
            "¿Qué te gustaría aprender o consultar?"
        )

        # ------------------------------------------
        # INDICADOR DE ESTADO
        # ------------------------------------------

        self.estado_label = ctk.CTkLabel(
            self,
            text="",
            font=("Poppins", 10),
            text_color=self.COLOR_TEXTO_SUAVE
        )

        self.estado_label.pack(
            pady=(0, 2)
        )

        # ------------------------------------------
        # ENTRADA DE MENSAJES
        # ------------------------------------------

        entrada_frame = ctk.CTkFrame(
            self,
            fg_color=self.COLOR_PANEL,
            corner_radius=12,
            border_width=1,
            border_color=self.COLOR_BORDE
        )

        entrada_frame.pack(
            fill="x",
            padx=18,
            pady=(3, 16)
        )

        self.entrada = ctk.CTkEntry(
            entrada_frame,
            height=42,
            placeholder_text="Escribe tu pregunta...",
            font=("Poppins", 11),
            fg_color="transparent",
            border_width=0,
            text_color=self.COLOR_TEXTO,
            placeholder_text_color="#8F8588"
        )

        self.entrada.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(12, 5),
            pady=5
        )

        self.entrada.bind(
            "<Return>",
            lambda evento: self.enviar_mensaje()
        )

        # Botón enviar

        self.boton_enviar = ctk.CTkButton(
            entrada_frame,
            text="➤",
            width=38,
            height=36,
            corner_radius=9,
            font=("Poppins", 15, "bold"),
            fg_color=self.COLOR_ROJO,
            hover_color=self.COLOR_ROJO_HOVER,
            text_color="#FFFFFF",
            command=self.enviar_mensaje
        )

        self.boton_enviar.pack(
            side="right",
            padx=(3, 6),
            pady=6
        )

    # ==============================================
    # AGREGAR MENSAJES AL CHAT
    # ==============================================

    def agregar_mensaje(self, emisor, mensaje):

        es_usuario = emisor == "Tú"

        color = (
            self.COLOR_BURBUJA_USUARIO
            if es_usuario
            else self.COLOR_BURBUJA_IA
        )

        alineacion = "e" if es_usuario else "w"

        tarjeta = ctk.CTkFrame(
            self.chat_frame,
            fg_color=color,
            corner_radius=12,
            border_width=1,
            border_color=(
                "#63343B"
                if es_usuario
                else "#383034"
            )
        )

        tarjeta.pack(
            anchor=alineacion,
            padx=7,
            pady=6
        )

        nombre = (
            "TÚ"
            if es_usuario
            else "REBELLION"
        )

        ctk.CTkLabel(
            tarjeta,
            text=nombre,
            font=("Poppins", 9, "bold"),
            text_color=(
                "#E47B83"
                if es_usuario
                else self.COLOR_ROJO_HOVER
            )
        ).pack(
            anchor="w",
            padx=12,
            pady=(8, 2)
        )

        ctk.CTkLabel(
            tarjeta,
            text=mensaje,
            font=("Poppins", 11),
            text_color=self.COLOR_TEXTO,
            justify="left",
            anchor="w",
            wraplength=520
        ).pack(
            anchor="w",
            padx=12,
            pady=(2, 10)
        )

        # Desplazar automáticamente al último mensaje

        self.chat_frame._parent_canvas.yview_moveto(1.0)

    # ==============================================
    # CONSTRUIR MENSAJE CON CONTEXTO
    # ==============================================

    # ==============================================
    # CONSTRUIR MENSAJE CON CONTEXTO
    # ==============================================

    def construir_mensaje(self, pregunta):

        LIMITE = 1000

        encabezado = (
            "Eres Rebellion, un asistente especializado "
            "en matemáticas.\n"
        )

        # ------------------------------------------
        # CONTEXTO MATEMÁTICO
        # ------------------------------------------

        contexto_texto = ""

        if self.contexto:

            contexto_texto = "CONTEXTO DEL EJERCICIO:\n"

            for clave, valor in self.contexto.items():

                contexto_texto += f"{clave}: {valor}\n"

        # ------------------------------------------
        # HISTORIAL RECIENTE
        # ------------------------------------------

        historial_texto = ""

        # Excluimos el último mensaje porque es
        # la pregunta actual.
        historial_reciente = self.historial[:-1][-2:]

        if historial_reciente:

            historial_texto = "\nHISTORIAL RECIENTE:\n"

            for emisor, mensaje in historial_reciente:

                historial_texto += (
                    f"{emisor}: {mensaje}\n"
                )

        # ------------------------------------------
        # PREGUNTA ACTUAL
        # ------------------------------------------

        pregunta_texto = (
            "\nPREGUNTA ACTUAL:\n"
            + pregunta
        )

        # ------------------------------------------
        # CONSTRUIR MENSAJE
        # ------------------------------------------

        mensaje = (
            encabezado
            + contexto_texto
            + historial_texto
            + pregunta_texto
        )

        # Reducir primero el historial si supera
        # el límite permitido.
        while len(mensaje) > LIMITE and historial_reciente:

            historial_reciente.pop(0)

            historial_texto = "\nHISTORIAL RECIENTE:\n"

            for emisor, texto in historial_reciente:

                historial_texto += f"{emisor}: {texto}\n"

            mensaje = (
                encabezado
                + contexto_texto
                + historial_texto
                + pregunta_texto
            )

        # Si todavía supera el límite, reducir
        # el contexto matemático.
        if len(mensaje) > LIMITE:

            espacio_contexto = (
                LIMITE
                - len(encabezado)
                - len(historial_texto)
                - len(pregunta_texto)
            )

            contexto_texto = contexto_texto[
                :max(0, espacio_contexto)
            ]

            mensaje = (
                encabezado
                + contexto_texto
                + historial_texto
                + pregunta_texto
            )

        # Última protección: conservar el inicio
        # de la pregunta si ella misma es demasiado larga.
        if len(mensaje) > LIMITE:

            espacio_pregunta = (
                LIMITE
                - len(encabezado)
                - len(contexto_texto)
                - len(historial_texto)
            )

            pregunta_texto = (
                "\nPREGUNTA ACTUAL:\n"
                + pregunta[:max(0, espacio_pregunta - 20)]
            )

            mensaje = (
                encabezado
                + contexto_texto
                + historial_texto
                + pregunta_texto
            )

        return mensaje[:LIMITE]

    # ==============================================
    # ENVIAR MENSAJE
    # ==============================================

    def enviar_mensaje(self):

        if self.procesando:
            return

        pregunta = self.entrada.get().strip()

        if not pregunta:
            return

        self.entrada.delete(0, "end")

        self.agregar_mensaje(
            "Tú",
            pregunta
        )

        self.historial.append(
            ("Usuario", pregunta)
        )

        mensaje = self.construir_mensaje(
            pregunta
        )

        nivel = self.selector_nivel.get().lower()

        modo = (
            "procedimiento"
            if self.selector_modo.get()
            == "Procedimiento paso a paso"
            else "directo"
        )

        self.procesando = True

        self.boton_enviar.configure(
            state="disabled",
            text="..."
        )

        self.estado_label.configure(
            text="Rebellion está pensando..."
        )

        hilo = threading.Thread(
            target=self.procesar_pregunta,
            args=(mensaje, nivel, modo),
            daemon=True
        )

        hilo.start()

    # ==============================================
    # PROCESAMIENTO EN SEGUNDO PLANO
    # ==============================================

    def procesar_pregunta(
        self,
        mensaje,
        nivel,
        modo
    ):

        try:

            respuesta = self.ai_service.preguntar(
                mensaje,
                nivel,
                modo
            )

            self.after(
                0,
                lambda respuesta=respuesta:
                self.mostrar_respuesta(respuesta)
            )

        except Exception as error:

            mensaje_error = str(error)

            self.after(
                0,
                lambda mensaje_error=mensaje_error:
                self.mostrar_error(mensaje_error)
            )

    # ==============================================
    # MOSTRAR RESPUESTA
    # ==============================================

    def mostrar_respuesta(self, respuesta):

        self.agregar_mensaje(
            "Rebellion",
            respuesta
        )

        self.historial.append(
            ("Rebellion", respuesta)
        )

        self.finalizar_envio()

    # ==============================================
    # MOSTRAR ERROR
    # ==============================================

    def mostrar_error(self, error):

        self.agregar_mensaje(
            "Rebellion",
            f"No pude procesar tu solicitud.\n\n{error}"
        )

        self.finalizar_envio()

    # ==============================================
    # FINALIZAR SOLICITUD
    # ==============================================

    def finalizar_envio(self):

        self.procesando = False

        self.boton_enviar.configure(
            state="normal",
            text="➤"
        )

        self.estado_label.configure(
            text=""
        )

        self.entrada.focus()

    # ==============================================
    # ACTUALIZAR CONTEXTO
    # ==============================================

    def actualizar_contexto(self, contexto):

        self.contexto = contexto or {}

    # ==============================================
    # OCULTAR CHAT
    # ==============================================

    def ocultar(self):

        self.pack_forget()
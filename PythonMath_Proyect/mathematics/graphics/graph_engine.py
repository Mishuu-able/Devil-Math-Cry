
import numpy as np
import sympy as sp

from sympy.core.relational import Relational


# ============================================================
# EVALUACIÓN SEGURA
# ============================================================

def _evaluar_seguro(funcion, *variables):
    resultado = np.asarray(
        funcion(*variables),
        dtype=np.complex128
    )

    resultado = np.real_if_close(resultado)

    if np.iscomplexobj(resultado):
        resultado = np.where(
            np.abs(np.imag(resultado)) < 1e-10,
            np.real(resultado),
            np.nan
        )

    return np.asarray(resultado, dtype=float)


# ============================================================
# DETECCIÓN DE PUNTOS SINGULARES
# ============================================================

def _obtener_puntos_singulares(
    expresion,
    variable,
    x_min,
    x_max
):
    """
    Busca puntos singulares reales dentro del intervalo.

    Se utiliza principalmente para localizar discontinuidades
    de funciones racionales y evitar que la gráfica conecte
    puntos a través de ellas.
    """

    puntos = []

    try:
        singularidades = sp.calculus.singularities(
            expresion,
            variable
        )

        if isinstance(singularidades, sp.FiniteSet):

            for punto in singularidades:

                if punto.is_real is not True:
                    continue

                try:
                    valor = float(sp.N(punto))

                    if x_min <= valor <= x_max:
                        puntos.append(valor)

                except (TypeError, ValueError, OverflowError):
                    continue

    except (NotImplementedError, ValueError, TypeError):
        pass

    # También buscamos ceros del denominador.
    # Esto ayuda con expresiones racionales.
    try:
        numerador, denominador = sp.fraction(
            sp.together(expresion)
        )

        if denominador != 1:

            raices = sp.solveset(
                denominador,
                variable,
                domain=sp.S.Reals
            )

            if isinstance(raices, sp.FiniteSet):

                for raiz in raices:

                    if raiz.is_real is not True:
                        continue

                    try:
                        valor = float(sp.N(raiz))

                        if x_min <= valor <= x_max:
                            puntos.append(valor)

                    except (TypeError, ValueError, OverflowError):
                        continue

    except (NotImplementedError, ValueError, TypeError):
        pass

    # Eliminar duplicados y ordenar
    return sorted(set(puntos))


def _obtener_extremos_dominio(expresion, variable, x_min, x_max):
    """
    Obtiene los extremos finitos del dominio real
    y determina desde qué lado existe la función.
    """

    extremos = []

    try:
        dominio = sp.calculus.util.continuous_domain(
            expresion,
            variable,
            sp.S.Reals
        )

        if isinstance(dominio, sp.Interval):
            intervalos = [dominio]

        elif isinstance(dominio, sp.Union):
            intervalos = [
                intervalo
                for intervalo in dominio.args
                if isinstance(intervalo, sp.Interval)
            ]

        else:
            return extremos

        for intervalo in intervalos:

            for punto, lado in (
                (intervalo.start, "derecho"),
                (intervalo.end, "izquierdo")
            ):

                if punto in (sp.S.NegativeInfinity, sp.S.Infinity):
                    continue

                try:
                    valor = float(sp.N(punto))
                except (TypeError, ValueError, OverflowError):
                    continue

                if not x_min <= valor <= x_max:
                    continue

                extremos.append({
                    "x": valor,
                    "lado": lado,
                    "incluido": intervalo.contains(punto) is sp.true
                })

    except (NotImplementedError, TypeError, ValueError):
        pass

    # Eliminar extremos duplicados.
    unicos = {}

    for extremo in extremos:
        clave = (extremo["x"], extremo["lado"])
        unicos[clave] = extremo

    return list(unicos.values())


def _clasificar_singularidades_racionales(
    expresion,
    variable,
    x_min,
    x_max
):
    """
    Clasifica los ceros del denominador como:

    - Huecos: límites laterales finitos e iguales.
    - Asíntotas verticales: al menos un límite lateral
      es infinito o no es finito.
    """

    huecos = []
    asintotas_verticales = []

    try:

        _, denominador = sp.fraction(
            sp.together(expresion)
        )

        if denominador == 1:
            return huecos, asintotas_verticales

        raices = sp.solveset(
            denominador,
            variable,
            domain=sp.S.Reals
        )

        if not isinstance(raices, sp.FiniteSet):
            return huecos, asintotas_verticales

        for raiz in raices:

            if raiz.is_real is not True:
                continue

            try:
                punto = float(sp.N(raiz))

                if not x_min <= punto <= x_max:
                    continue

                limite_izquierdo = sp.limit(
                    expresion,
                    variable,
                    raiz,
                    dir="-"
                )

                limite_derecho = sp.limit(
                    expresion,
                    variable,
                    raiz,
                    dir="+"
                )

                ambos_finitos = (
                    limite_izquierdo.is_finite is True
                    and limite_derecho.is_finite is True
                )

                limites_iguales = (
                    sp.simplify(
                        limite_izquierdo - limite_derecho
                    ) == 0
                )

                if ambos_finitos and limites_iguales:
                    huecos.append(punto)

                else:
                    asintotas_verticales.append(punto)

            except (
                TypeError,
                ValueError,
                NotImplementedError
            ):
                continue

    except (
        TypeError,
        ValueError,
        NotImplementedError
    ):
        pass

    return (
        sorted(set(huecos)),
        sorted(set(asintotas_verticales))
    )


def _obtener_asintotas_racionales(expresion, variable):
    """
    Calcula las asíntotas horizontales, oblicuas
    o polinómicas mediante división de polinomios.
    """

    resultado = {
        "horizontal": None,
        "oblicua": None,
        "polinomica": None
    }

    try:

        numerador, denominador = sp.fraction(
            sp.together(expresion)
        )

        P = sp.Poly(numerador, variable)
        Q = sp.Poly(denominador, variable)

        grado_p = P.degree()
        grado_q = Q.degree()

        cociente, _ = sp.div(P, Q)

        diferencia = grado_p - grado_q

        if diferencia < 0:

            resultado["horizontal"] = sp.Integer(0)

        elif diferencia == 0:

            resultado["horizontal"] = sp.simplify(
                cociente.as_expr()
            )

        elif diferencia == 1:

            resultado["oblicua"] = sp.simplify(
                cociente.as_expr()
            )

        else:

            resultado["polinomica"] = sp.simplify(
                cociente.as_expr()
            )

    except (sp.PolynomialError, TypeError, ValueError):
        pass

    return resultado


def _obtener_puntos_piecewise(expresion, variable, x_min, x_max):
    """
    Extrae los puntos donde cambian las condiciones
    de una función Piecewise.
    """

    if not isinstance(expresion, sp.Piecewise):
        return []

    puntos = set()

    for rama, condicion in expresion.args:

        relaciones = condicion.atoms(Relational)

        for relacion in relaciones:

            ecuacion = relacion.lhs - relacion.rhs

            try:
                raices = sp.solveset(
                    ecuacion,
                    variable,
                    domain=sp.S.Reals
                )

                if not isinstance(raices, sp.FiniteSet):
                    continue

                for raiz in raices:

                    if raiz.is_real is not True:
                        continue

                    valor = float(sp.N(raiz))

                    if x_min <= valor <= x_max:
                        puntos.add(valor)

            except (TypeError, ValueError, NotImplementedError):
                continue

    return sorted(puntos)


def _limite_rama_piecewise(expresion, variable, punto, direccion):
    """
    Identifica qué rama de Piecewise corresponde a cada lado
    del punto y calcula su límite.
    """

    epsilon = sp.Symbol(
        "_epsilon",
        positive=True
    )

    desplazamiento = (
        -epsilon if direccion == "-" else epsilon
    )

    for rama, condicion in expresion.args:

        if condicion == sp.true:
            return sp.limit(
                rama,
                variable,
                punto,
                dir=direccion
            )

        condicion_lateral = sp.simplify(
            condicion.subs(
                variable,
                punto + desplazamiento
            )
        )

        if condicion_lateral == sp.true:
            return sp.limit(
                rama,
                variable,
                punto,
                dir=direccion
            )

        if condicion_lateral == sp.false:
            continue

    return sp.limit(
        expresion,
        variable,
        punto,
        dir=direccion
    )


def _son_distintos(a, b):
    try:
        diferencia = sp.simplify(a - b)

        return (
            diferencia != 0
            and diferencia.is_zero is not True
        )

    except Exception:
        return True


def _obtener_discontinuidades_piecewise(
    expresion,
    variable,
    puntos
):
    """
    Comprueba si los puntos de cambio de rama producen
    una discontinuidad real.
    """

    discontinuidades = []

    for punto in puntos:

        izquierda = _limite_rama_piecewise(
            expresion,
            variable,
            punto,
            "-"
        )

        derecha = _limite_rama_piecewise(
            expresion,
            variable,
            punto,
            "+"
        )

        valor = sp.simplify(
            expresion.subs(variable, punto)
        )

        if (
            _son_distintos(izquierda, derecha)
            or _son_distintos(izquierda, valor)
            or _son_distintos(derecha, valor)
        ):
            discontinuidades.append(punto)

    return discontinuidades


def _obtener_singularidades_trigonometricas(
    expresion,
    variable,
    x_min,
    x_max
):
    puntos = set()

    funciones = {
        sp.tan: sp.cos,
        sp.sec: sp.cos,
        sp.cot: sp.sin,
        sp.csc: sp.sin
    }

    for funcion, denominador in funciones.items():

        for termino in expresion.atoms(funcion):

            argumento = termino.args[0]

            # Solo procesamos argumentos lineales: ax + b
            try:
                a = sp.diff(argumento, variable)
                b = sp.simplify(argumento - a * variable)

                if (
                    a.has(variable)
                    or b.has(variable)
                    or a.is_real is not True
                    or b.is_real is not True
                    or a.is_zero is True
                ):
                    continue

                a = float(a)
                b = float(b)

                if abs(a) < 1e-12:
                    continue

                # Resolver las posiciones de los polos.
                if denominador == sp.cos:
                    base = np.pi / 2
                else:
                    base = 0

                minimo = min(a * x_min + b, a * x_max + b)
                maximo = max(a * x_min + b, a * x_max + b)

                k_min = int(np.floor((minimo - base) / np.pi)) - 1
                k_max = int(np.ceil((maximo - base) / np.pi)) + 1

                for k in range(k_min, k_max + 1):

                    polo = (base + k * np.pi - b) / a

                    if x_min <= polo <= x_max:
                        puntos.add(polo)

            except (TypeError, ValueError, OverflowError):
                continue

    # ====================================================
    # POTENCIAS NEGATIVAS DE SENO Y COSENO
    # ====================================================

    for termino in expresion.atoms(sp.Pow):

        # Solo nos interesan potencias negativas.
        if termino.exp.is_negative is not True:
            continue

        base = termino.base

        # Detectar únicamente seno y coseno.
        if base.func not in (sp.sin, sp.cos):
            continue

        argumento = base.args[0]

        try:

            a = sp.diff(argumento, variable)
            b = sp.simplify(argumento - a * variable)

            if (
                a.has(variable)
                or b.has(variable)
                or a.is_real is not True
                or b.is_real is not True
                or a.is_zero is True
            ):
                continue

            a = float(a)
            b = float(b)

            if abs(a) < 1e-12:
                continue

            # Ceros del denominador:
            # cos(u) = 0 -> u = pi/2 + k*pi
            # sin(u) = 0 -> u = k*pi

            if base.func == sp.cos:
                base_polos = np.pi / 2
            else:
                base_polos = 0

            minimo = min(
                a * x_min + b,
                a * x_max + b
            )

            maximo = max(
                a * x_min + b,
                a * x_max + b
            )

            k_min = int(
                np.floor((minimo - base_polos) / np.pi)
            ) - 1

            k_max = int(
                np.ceil((maximo - base_polos) / np.pi)
            ) + 1

            for k in range(k_min, k_max + 1):

                polo = (
                    base_polos + k * np.pi - b
                ) / a

                if x_min <= polo <= x_max:
                    puntos.add(polo)

        except (TypeError, ValueError, OverflowError):
            continue


    return sorted(puntos)


# ============================================================
# GENERACIÓN DE DATOS 2D
# ============================================================

def generar_datos_2d(
    expresion,
    x_min=-10,
    x_max=10,
    puntos=500
):
    """
    Genera datos 2D y separa automáticamente las ramas
    de funciones con discontinuidades conocidas.
    """

    variable = next(
        (
            simbolo
            for simbolo in expresion.free_symbols
            if simbolo.name == "x"
        ),
        sp.Symbol("x")
    )

    # ====================================================
    # EXTREMOS DEL DOMINIO REAL
    # ====================================================

    extremos_dominio = _obtener_extremos_dominio(
        expresion,
        variable,
        x_min,
        x_max
    )

    funcion = sp.lambdify(
        variable,
        expresion,
        modules=["numpy"]
    )

    # Muestreo normal
    valores_x = np.linspace(
        x_min,
        x_max,
        puntos
    )

    # Singularidades de funciones racionales
    singularidades = _obtener_puntos_singulares(
        expresion,
        variable,
        x_min,
        x_max
    )
    
    # Singularidades de funciones trigonométricas
    singularidades_trigonometricas = (
        _obtener_singularidades_trigonometricas(
            expresion,
            variable,
            x_min,
            x_max
        )
    )

    # Unificar todas las singularidades
    singularidades = sorted(set(
        singularidades + singularidades_trigonometricas
    ))


    # Cambios de rama de Piecewise
    puntos_cambio = _obtener_puntos_piecewise(
        expresion,
        variable,
        x_min,
        x_max
    )

    # Detectar discontinuidades reales de Piecewise
    discontinuidades = []

    if isinstance(expresion, sp.Piecewise):

        discontinuidades = (
            _obtener_discontinuidades_piecewise(
                expresion,
                variable,
                puntos_cambio
            )
        )

    # Unir todos los puntos especiales
    puntos_especiales = sorted(
        set(singularidades + puntos_cambio)
    )

    if puntos_especiales:

        valores_x = np.unique(
            np.concatenate([
                valores_x,
                np.asarray(puntos_especiales)
            ])
        )

    # Evaluar función
    valores_y = _evaluar_seguro(
        funcion,
        valores_x
    )

    valores_y[~np.isfinite(valores_y)] = np.nan

    # Romper la curva en discontinuidades
    for punto in singularidades + discontinuidades:

        indice = np.where(
            np.isclose(
                valores_x,
                punto,
                atol=1e-10
            )
        )[0]

        if len(indice):
            valores_y[indice] = np.nan

    # Clasificar singularidades racionales
    huecos, asintotas_verticales = (
        _clasificar_singularidades_racionales(
            expresion,
            variable,
            x_min,
            x_max
        )
    )

    # ====================================================
    # ASÍNTOTAS DE FUNCIONES RACIONALES
    # ====================================================

    asintotas = _obtener_asintotas_racionales(
        expresion,
        variable
    )

    return {
        "type": "curve",
        "expression": str(expresion),

        "x": valores_x,
        "y": valores_y,

        "singularities": singularidades,
        "holes": huecos,
        "vertical_asymptotes": asintotas_verticales,

        "domain_extremes": extremos_dominio,

        "asymptotes": asintotas,

        "breakpoints": puntos_cambio,
        "discontinuities": discontinuidades,

        "metadata": {
            "x_label": "X",
            "y_label": "Y",
            "has_singularities": bool(singularidades),
            "has_discontinuities": bool(discontinuidades)
        }
    }



# ============================================================
# GENERACIÓN DE DATOS 3D
# ============================================================

def generar_datos_3d(
    expresion,
    x_min=-5,
    x_max=5,
    y_min=-5,
    y_max=5,
    puntos=100
):
    """
    Genera una superficie matemática 3D.

    Se conserva la estructura original para mantener
    la compatibilidad con Graph3D.
    """

    x, y = sp.symbols("x y")

    funcion = sp.lambdify(
        (x, y),
        expresion,
        modules=["numpy"]
    )

    valores_x = np.linspace(
        x_min,
        x_max,
        puntos
    )

    valores_y = np.linspace(
        y_min,
        y_max,
        puntos
    )

    X, Y = np.meshgrid(
        valores_x,
        valores_y
    )

    Z = _evaluar_seguro(
        funcion,
        X,
        Y
    )

    # Garantizar dimensiones compatibles
    Z = np.broadcast_to(
        Z,
        X.shape
    ).copy()

    Z[~np.isfinite(Z)] = np.nan

    return {
        "type": "surface",
        "expression": str(expresion),

        "x": valores_x,
        "y": valores_y,

        "X": X,
        "Y": Y,
        "Z": Z,

        "metadata": {
            "x_label": "X",
            "y_label": "Y",
            "z_label": "Z"
        }
    }

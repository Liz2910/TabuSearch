from typing import Callable, Any, Iterable, Tuple, Optional, Dict
import math
import random

class TabuSearchResult:
    def __init__(self, mejorSolucion, mejorCosto, iteraciones, historial):
        self.mejorSolucion = mejorSolucion
        self.mejorCosto = mejorCosto
        self.iteraciones = iteraciones
        self.historial = historial

def tabu_search(
    SolucionInicial: Any,
    Objetivo: Callable[[Any], float],
    Vecino: Callable[[Any], Iterable[Tuple[Any, Any]]],
    ternura: int = 7,
    max_iters: int = 100,
    aspiracion: Optional[Callable[[float, float], bool]] = None,
    Igualdad: Optional[Callable[[Any, Any], bool]] = None,
    rng: Optional[random.Random] = None,
    callback: Optional[Callable[[Dict[str, Any]], None]] = None,  
) -> TabuSearchResult:
    if rng is None:
        rng = random.Random()

    if Igualdad is None:
        Igualdad = lambda a, b: a == b

    
    listaTabu: Dict[Any, int] = {}

    solucionActual = SolucionInicial
    costoActual = Objetivo(solucionActual)
    mejorSolucion = solucionActual
    mejorCosto = costoActual
    historial = [(0, solucionActual, costoActual, mejorSolucion, mejorCosto)]

    def esTabu(movimiento: Any, iteracion: int) -> bool:
        return movimiento in listaTabu and listaTabu[movimiento] > iteracion

    def marcarTabu(movimiento: Any, iteracion: int, duracion: int):
        listaTabu[movimiento] = iteracion + duracion


    if aspiracion is None:
        aspiracion = lambda costoMejor, costoCandidato: costoCandidato < costoMejor

    for iteracion in range(1, max_iters + 1):
        candidatos = []
        for candidato, movimiento in Vecino(solucionActual):
            costo = Objetivo(candidato)
            candidatos.append((candidato, movimiento, costo))

        if not candidatos:
          
            break

       
        candidatosFactibles = []
        candidatosAspirantes = []
        for candidato, movimiento, costo in candidatos:
            if esTabu(movimiento, iteracion):
                if aspiracion(mejorCosto, costo):
                    candidatosAspirantes.append((candidato, movimiento, costo))
            else:
                candidatosFactibles.append((candidato, movimiento, costo))

        conjuntoCandidatos = candidatosAspirantes if candidatosAspirantes else candidatosFactibles
        if not conjuntoCandidatos:
            
            conjuntoCandidatos = candidatos

        costoMinimo = min(c for _, _, c in conjuntoCandidatos)
        mejoresCandidatos = [(c, m, co) for (c, m, co) in conjuntoCandidatos if math.isclose(co, costoMinimo) or co == costoMinimo]
        candidato, movimiento, costoCandidato = rng.choice(mejoresCandidatos)

        
        solucionActual = candidato
        costoActual = costoCandidato
        marcarTabu(movimiento, iteracion, ternura)

      
        if costoActual < mejorCosto and not Igualdad(solucionActual, mejorSolucion):
            mejorSolucion = solucionActual
            mejorCosto = costoActual

        historial.append((iteracion, solucionActual, costoActual, mejorSolucion, mejorCosto))

    
        datosCallback = {
            "iteracion": iteracion,
            "solucionActual": solucionActual,
            "costoActual": costoActual,
            "mejorSolucion": mejorSolucion,
            "mejorCosto": mejorCosto,
            "movimientoElegido": movimiento,
            "tamanoListaTabu": len(listaTabu),
            "candidatosEvaluados": len(candidatos),
        }
        try:
            if callable(callback):
                callback(datosCallback)
        except Exception as e:
           
            pass

    return TabuSearchResult(mejorSolucion, mejorCosto, len(historial) - 1, historial)

if __name__ == "__main__":
    import random
    import math

    # Prueba 1: f(x) = x^2
    def objetivo1(sol):
        x = sol[0]
        return x**2

    def vecinos1(sol):
        for dx in [-1, 1]:
            yield [sol[0] + dx], dx


    # Prueba 2: f(x) = x^2 + 10*sin(x)
    def objetivo2(sol):
        x = sol[0]
        return x**2 + 10 * math.sin(x)

    def vecinos2(sol):
        for dx in [-1, 1]:
            yield [sol[0] + dx], dx


    # Prueba 3: f(x, y) = x^2 + y^2 + 25*(sin(x) + cos(y))^2
    def objetivo3(sol):
        x, y = sol
        return x**2 + y**2 + 25 * (math.sin(x) + math.cos(y))**2

    def vecinos3(sol):
        for i in range(2):  # dos variables: x, y
            nueva = sol.copy()
            nueva[i] += random.choice([-1, 1])
            yield nueva, i

    def ejecutar_prueba(nombre, objetivo, vecinos, sol_inicial):
        print(f"\nEjecutando {nombre}")

        resultado = tabu_search(
            SolucionInicial=sol_inicial,
            Objetivo=objetivo,
            Vecino=vecinos,
            ternura=7,
            max_iters=50
        )

        print("Mejor solución encontrada: ", resultado.mejorSolucion)
        print("Costo: ", resultado.mejorCosto)
        print("Iteraciones: ", resultado.iteraciones)
        return resultado

    # Prueba 1: Parabólica simple
    sol_inicial_1 = [random.randint(-10, 10)]
    ejecutar_prueba("Prueba 1 - f(x) = x^2", objetivo1, vecinos1, sol_inicial_1)

    # Prueba 2: Función multimodal
    sol_inicial_2 = [random.randint(-10, 10)]
    ejecutar_prueba("Prueba 2 - f(x) = x^2 + 10*sin(x)", objetivo2, vecinos2, sol_inicial_2)

    # Prueba 3: Función bidimensional
    sol_inicial_3 = [random.randint(-5, 5), random.randint(-5, 5)]
    ejecutar_prueba("Prueba 3 - f(x, y) = x^2 + y^2 + 25*(sin(x) + cos(y))^2", objetivo3, vecinos3, sol_inicial_3)
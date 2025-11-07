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
    import matplotlib.pyplot as plt

    # Generar ciudades
    N_CIUDADES = 10
    ciudades = [(random.randint(0, 100), random.randint(0, 100)) for _ in range(N_CIUDADES)]

    # Función de distancia total
    def distancia_total(ruta):
        total = 0
        for i in range(len(ruta)):
            x1, y1 = ciudades[ruta[i]]
            x2, y2 = ciudades[ruta[(i + 1) % len(ruta)]]
            total += math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)
        return total

    # Función de vecinos (intercambio de dos ciudades)
    def vecinos_tsp(ruta):
        for i in range(len(ruta)):
            for j in range(i + 1, len(ruta)):
                nueva = ruta.copy()
                nueva[i], nueva[j] = nueva[j], nueva[i]
                yield nueva, (i, j)

    # Ejecutar Tabu Search
    ruta_inicial = list(range(N_CIUDADES))
    random.shuffle(ruta_inicial)

    print("\nPROBLEMA DEL VIAJERO (TSP)")
    print("\nRuta inicial:", ruta_inicial)
    print("Distancia inicial:", distancia_total(ruta_inicial))

    resultado = tabu_search(
        SolucionInicial=ruta_inicial,
        Objetivo=distancia_total,
        Vecino=vecinos_tsp,
        ternura=5,
        max_iters=100
    )

    print("\nMejor ruta encontrada:", resultado.mejorSolucion)
    print("Distancia total:", resultado.mejorCosto)
    print("Iteraciones:", resultado.iteraciones)

    # 5. Graficar la ruta final
    ruta_final = resultado.mejorSolucion
    x = [ciudades[i][0] for i in ruta_final + [ruta_final[0]]]
    y = [ciudades[i][1] for i in ruta_final + [ruta_final[0]]]

    plt.figure(figsize=(7, 6))
    plt.plot(x, y, marker='o')
    plt.title("Ruta óptima encontrada (Búsqueda Tabú)")
    for idx, (cx, cy) in enumerate(ciudades):
        plt.text(cx + 1, cy + 1, str(idx))
    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")
    plt.grid(True)
    plt.show()
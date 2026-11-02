from collections import deque
import time

# Cada estado como una tupla (misIzq, canIzq, boteIzq)
# 1 si el bote está a la izquierda y 0 si está a la derecha

Estado = tuple[int, int, int]
Accion = tuple[int, int]
Camino = list[tuple[Accion | None, Estado]]
ResultadoBusqueda = tuple[Camino, int] | None
# ResultadoBusqueda = (camino, nodosExpandidos) o None si no hay solución


estadoInicial: Estado = (3, 3, 1)
estadoMeta: Estado = (0, 0, 0)
accionesBase: tuple[Accion, ...] = (
    (1, 0),  # Un misionero
    (0, 1),  # Un caníbal
    (2, 0),  # Dos misioneros
    (0, 2),  # Dos caníbales
    (1, 1),  # Un misionero y un caníbal
)

def esEstadoValido(estado: Estado) -> bool:
    # Comprueba las restricciones de las orillas

    if len(estado) != 3 or any(type(valor) is not int for valor in estado):
        return False

    misIzq, canIzq, boteIzq = estado
    if not (0 <= misIzq <= 3 and 0 <= canIzq <= 3 and boteIzq in (0, 1)):
        return False

    misDer = 3 - misIzq
    canDer = 3 - canIzq
    segIzq = misIzq == 0 or misIzq >= canIzq
    segDer = misDer == 0 or misDer >= canDer
    return segIzq and segDer

def esMeta(estado: Estado) -> bool:
    # Indica si todos cruzaron a la derecha
    return estado == estadoMeta

def aplicarAccion(estado: Estado, accion: Accion) -> Estado:
    # Aplica una acción legal y devuelve el nuevo estado

    if not esEstadoValido(estado) or accion not in accionesBase:
        raise ValueError("Estado o combinación de pasajeros no válida.")

    misIzq, canIzq, boteIzq = estado
    numMis, numCan = accion

    if boteIzq == 1:
        if numMis > misIzq or numCan > canIzq:
            raise ValueError("No hay suficientes pasajeros en la izquierda.")
        estadoSig = (misIzq - numMis, canIzq - numCan, 0)
    else:
        if numMis > 3 - misIzq or numCan > 3 - canIzq:
            raise ValueError("No hay suficientes pasajeros en la derecha.")
        estadoSig = (misIzq + numMis, canIzq + numCan, 1)

    if not esEstadoValido(estadoSig):
        raise ValueError("La acción dejaría una orilla en estado inseguro.")
    return estadoSig

def generarSucesores(estado: Estado) -> list[tuple[Accion, Estado]]:
    # Devuelve todos los pares tipo (acción, estado siguiente) válidos desde el estado actual

    sucesores = []
    for accion in accionesBase:
        try:
            estadoSig = aplicarAccion(estado, accion)
        except ValueError:
            continue
        sucesores.append((accion, estadoSig))
    return sucesores

def bfs(inicio: Estado, meta: Estado) -> ResultadoBusqueda:
    # Cada elemento de la cola son los cruces hasta el estado actual,
    # representado como lista de pares (acción, estado)
    # Retorna (camino, nodosExpandidos) o None si no hay solución

    # Primer paso NONE porque es el estado inicial
    colaInicial: Camino = [(None, inicio)]
    cola: deque[Camino] = deque([colaInicial])
    visitados: set[Estado] = {inicio}
    # Evita los bucles por visitar el mismo estado dos veces
    nodosExpandidos: int = 0

    while cola:
        camino = cola.popleft()
        _, estadoActual = camino[-1]
        nodosExpandidos += 1
        # Se expande cada nodo extraído

        if esMeta(estadoActual):
            return camino, nodosExpandidos

        for accion, estadoSig in generarSucesores(estadoActual):
            if estadoSig not in visitados:
                visitados.add(estadoSig)
                cola.append(camino + [(accion, estadoSig)])

    return None

def dfs(inicio: Estado, meta: Estado) -> ResultadoBusqueda:
    # Cada elemento de la pila son los cruces hasta el estado actual,
    # representado como lista de pares (acción, estado)
    # Retorna (camino, nodosExpandidos) o None si no hay solución

    # Primer paso NONE porque es el estado inicial
    pilaInicial: Camino = [(None, inicio)]
    pila: list[Camino] = [pilaInicial]
    visitados: set[Estado] = {inicio}
    # Evita los bucles por visitar el mismo estado dos veces
    nodosExpandidos: int = 0

    while pila:
        camino = pila.pop()
        # Ultimo elemento para la profundidad
        _, estadoActual = camino[-1]
        nodosExpandidos += 1
        # Se expande cada nodo extraído

        if esMeta(estadoActual):
            return camino, nodosExpandidos

        for accion, estadoSig in generarSucesores(estadoActual):
            if estadoSig not in visitados:
                visitados.add(estadoSig)
                pila.append(camino + [(accion, estadoSig)])

    return None

def imprimirCamino(camino: Camino) -> None:
    # Muestra los cruces con el estado resultante en ambas orillas.
    ladoBote = {1: "Izquierda", 0: "Derecha"}
    print(f"{'Paso':<5} {'Acción':<28} {'MisIzq':>6} {'CanIzq':>6} {'Bote':>10} {'MisDer':>6} {'CanDer':>6}")

    for paso, (accion, estado) in enumerate(camino):
        misIzq, canIzq, boteIzq = estado
        misDer = 3 - misIzq
        canDer = 3 - canIzq

        if accion is None:
            descripcion = "Estado inicial"
        else:
            numMis, numCan = accion
            _, estadoAnterior = camino[paso - 1]
            direccion = "→ Der" if estadoAnterior[2] == 1 else "← Izq"
            partes = []
            if numMis:
                partes.append(f"{numMis} mis.")
            if numCan:
                partes.append(f"{numCan} can.")
            descripcion = f"{direccion}  ({', '.join(partes)})"

        print(f"{paso:<5} {descripcion:<28} {misIzq:>6} {canIzq:>6} {ladoBote[boteIzq]:>10} {misDer:>6} {canDer:>6}")

def benchmarkear(algoritmo, inicio: Estado, meta: Estado) -> tuple[ResultadoBusqueda, float]:
    # Ejecuta el algoritmo y mide su tiempo de ejecución en segundos
    # Retorna (resultado, tiempoSegundos)

    inicio_t = time.perf_counter()
    resultado = algoritmo(inicio, meta)
    fin_t = time.perf_counter()
    return resultado, fin_t - inicio_t

def imprimirBenchmark(metricas: list[tuple[str, int, float, int]]) -> None:
    # Imprime la tabla comparativa con las métricas de cada algoritmo
    # Cada fila de métricas es (nombre, nodosExpandidos, tiempoSegundos, longitudCamino)

    ancho = 62
    print("=" * ancho)
    print(f"{'TABLA COMPARATIVA DE ALGORITMOS':^{ancho}}")
    print("=" * ancho)
    print(f"{'Algoritmo':<12} {'Nodos expandidos':>18} {'Tiempo (s)':>14} {'Long. camino':>14}")
    print("-" * ancho)

    for nombre, nodos, tiempo, longitud in metricas:
        print(f"{nombre:<12} {nodos:>18} {tiempo:>14.6f} {longitud:>14}")

    print("=" * ancho)

def main() -> None:
    # Ejecuta BFS y DFS, imprime los caminos y la tabla comparativa del benchmarking

    metricas: list[tuple[str, int, float, int]] = []

    print("=== Misioneros y Caníbales — BFS ===\n")
    resultadoBFS, tiempoBFS = benchmarkear(bfs, estadoInicial, estadoMeta)

    if resultadoBFS is None:
        print("No se encontró solución.")
    else:
        caminoBFS, nodosBFS = resultadoBFS
        print(f"Solución encontrada en {len(caminoBFS) - 1} cruces:\n")
        imprimirCamino(caminoBFS)
        metricas.append(("BFS", nodosBFS, tiempoBFS, len(caminoBFS) - 1))

    print("\n=== Misioneros y Caníbales — DFS ===\n")
    resultadoDFS, tiempoDFS = benchmarkear(dfs, estadoInicial, estadoMeta)

    if resultadoDFS is None:
        print("No se encontró solución.")
    else:
        caminoDFS, nodosDFS = resultadoDFS
        print(f"Solución encontrada en {len(caminoDFS) - 1} cruces:\n")
        imprimirCamino(caminoDFS)
        metricas.append(("DFS", nodosDFS, tiempoDFS, len(caminoDFS) - 1))

    print()
    imprimirBenchmark(metricas)

if __name__ == "__main__":
    main()

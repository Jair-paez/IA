# Cada estado como una tupla (misIzq, canIzq, boteIzq)
# 1 si el bote está a la izquierda y 0 si está a la derecha 

Estado = tuple[int, int, int]
Accion = tuple[int, int]


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
    # Aplica una acción legal y devuelve el nuevo estado.

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



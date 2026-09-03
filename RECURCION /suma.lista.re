"""
Autor: Tu nombre
Fecha: 02/09/2026
Aplicación: Sumar los elementos de una lista con recursión
"""


def sumar_lista(lista):
    """
    Función para sumar los elementos de una lista mediante recursión.

    @param lista: Recibe una lista de números.
    @return: Devuelve la suma de todos los elementos.
    """

    # Caso base: si la lista está vacía, devuelve cero.
    if len(lista) == 0:
        return 0

    # Caso recursivo: suma el primer elemento con el resto.
    return lista[0] + sumar_lista(lista[1:])


numeros = [2, 4, 6, 8]

resultado = sumar_lista(numeros)

print("La suma de los elementos es:", resultado)

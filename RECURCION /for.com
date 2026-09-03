"""
Autor: Tu nombre
Fecha: 02/09/2026
Aplicación: Factorial utilizando for
"""


def factorial_for(n):
    """
    Función para calcular el factorial mediante un ciclo for.

    @param n: Recibe un número entero no negativo.
    @return: Devuelve el factorial de n.
             n! = n * (n-1) * (n-2) * ... * 1
    """

    factorial = 1

    for numero in range(1, n + 1):
        factorial = factorial * numero

    return factorial


print(factorial_for(3))

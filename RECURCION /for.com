def factorial(n):
    resultado = 1

    for numero in range(1, n + 1):
        resultado *= numero

    return resultado


print(factorial(3))

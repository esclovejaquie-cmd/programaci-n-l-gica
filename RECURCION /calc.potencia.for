
"""
Autor: Tu nombre
Fecha: 02/09/2026
Aplicación: Cálculo de una potencia utilizando for
"""


def calcular_potencia(base, exponente):
    """
    Función para calcular una potencia mediante un ciclo for.

    @param base: Número que se multiplicará por sí mismo.
    @param exponente: Cantidad de veces que se multiplica la base.
    @return: Resultado de elevar la base al exponente.
             potencia = base ** exponente
    """

    resultado = 1

    # Multiplica la base tantas veces como indique el exponente.
    for i in range(exponente):
        resultado = resultado * base

    return resultado


base = int(input("Escribe la base: "))
exponente = int(input("Escribe el exponente: "))

if exponente < 0:
    print("Este programa solamente acepta exponentes no negativos.")
else:
    potencia = calcular_potencia(base, exponente)
    print(base, "elevado a", exponente, "es:", potencia)

 #Escribe la base: 2,Escribe el exponente: 3,2 elevado a 3 es: 8

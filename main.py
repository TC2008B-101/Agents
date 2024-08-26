import random
import json

# Esto va a ser el json de entrada
clima = 0 # 0-3
mantenimiento = 0.4 # 0-1
minuto = 840 # 0-1439

# Duracion promedio compartida por socioformador
tramo1 = 120
tramo2 = 30
tramo3 = 95

tramos = [tramo1, tramo2, tramo3]
horaFinal = minuto
tiempoFinal = 0
Recorrido = []

for i in range(len(tramos)):
    eventos = []
    # Aplicando estado de clima
    if clima == 1:
        tramos[i] *= 1.05
    if clima == 2:
        tramos[i] *= 1.15
    if clima == 3:
        tramos[i] *= 1.2
    if clima == 4:
        tramos[i] *= 2
    
    # Aplicando estado de mantenimiento
    if mantenimiento >= 0.5:
        tramos[i] *= 1.05

        # Probabilidad de evento de ponchado
        probPonchado = mantenimiento - 0.3
        poncharGenerator = random.random()
        
        if probPonchado <= poncharGenerator:
            tiempoPonchado = 30
            tramos[i] += tiempoPonchado
            evento = ("Ponchadura", tiempoPonchado)
            eventos.append(evento)

    # Evento de paro de policia
    policiaGenerator = random.random()
    if policiaGenerator <= 0.10:
        tiempoPolicia = random.randint(5,70)
        tramos[i] += tiempoPolicia
        evento = ("Policia", tiempoPolicia)
        eventos.append(evento)

    # Evento de necesidades (baño, comer, dormir)
    necesidadesGenerator = random.random()
    if necesidadesGenerator <= 0.1:
        necesidad = random.randint(1,3)

        if necesidad == 1:
            tiempoBanio = 10
            tramos[i] += tiempoBanio
            eventos.append(("Baño", tiempoBanio))

        if necesidad == 2:
            tiempoComer = 20
            tramos[i] += tiempoComer
            eventos.append(("Comer", tiempoComer))

        if necesidad == 3:
            tiempoDormir = 30
            tramos[i] += tiempoDormir
            eventos.append(("Dormir", tiempoDormir))

    # En primer tramo evento de cargamento
    if i == 0:
        tiempoCargamento = 120
        tramos[i] += tiempoCargamento
        eventos.append(("Cargamento", tiempoCargamento))

    # En segundo tramo evento de moja pollos
    if i == 1 and (tiempoFinal <= 1320 or tiempoFinal >= 270):
        tiempoMojado = 5
        tramos[i] += tiempoMojado
        eventos.append(("Mojado pollos", tiempoMojado))

    # Añadir tiempo de tramo a tiempoFinal
    tiempoFinal += tramos[i] 
    horaFinal += tramos[i]

    # Calcular hora
    if horaFinal > 1439:
        horaFinal -= 1439
    
    Recorrido.append([tramos[i], eventos])

Recorrido.append(tiempoFinal)
Recorrido.append(horaFinal)

print(f"Tiempo final: {Recorrido[-2]} minutos")
print(f"Hora inicial: {minuto//60} horas {minuto%60} minutos")
print(f"Hora final: {Recorrido[-1]//60} horas {Recorrido[-1]%60} minutos") 
print(f"Tramo 1: {Recorrido[0]}")
print(f"Tramo 2: {Recorrido[1]}")
print(f"Tramo 3: {Recorrido[2]}")
import random
import statistics as st

# Esto va a ser el json de entrada
clima = 0 # 0-3
mantenimiento = 0.4 # 0-1
minuto = 840 # 0-1439

# Duracion calculada con distribución normal
tramo1 = int((st.NormalDist(120, 20).samples(1))[0])
tramo2 = int((st.NormalDist(30, 10).samples(1))[0])
tramo3 = int((st.NormalDist(95, 20).samples(1))[0])

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
            tiempoPonchado = int((st.NormalDist(30, 5).samples(1))[0])
            tramos[i] += tiempoPonchado
            horaFinal += tiempoPonchado
            evento = ("Ponchadura", tiempoPonchado)
            eventos.append(evento)

    # Evento de paro de policia
    policiaGenerator = random.random()
    if policiaGenerator <= 0.10:
        tiempoPolicia = int((st.NormalDist(15, 10).samples(1))[0])
        tramos[i] += tiempoPolicia
        horaFinal += tiempoPolicia
        evento = ("Policia", tiempoPolicia)
        eventos.append(evento)

    # Evento de necesidades (baño, comer, dormir)
    necesidadesGenerator = random.random()
    if necesidadesGenerator <= 0.1:
        necesidad = random.randint(1,3)

        if necesidad == 1:
            tiempoBanio = int((st.NormalDist(10, 2).samples(1))[0])
            tramos[i] += tiempoBanio
            horaFinal += tiempoBanio
            eventos.append(("Baño", tiempoBanio))

        if necesidad == 2:
            tiempoComer = int((st.NormalDist(20, 5).samples(1))[0])
            tramos[i] += tiempoComer
            horaFinal += tiempoComer
            eventos.append(("Comer", tiempoComer))

        if necesidad == 3:
            tiempoDormir = int((st.NormalDist(30, 10).samples(1))[0])
            tramos[i] += tiempoDormir
            horaFinal += tiempoDormir
            eventos.append(("Dormir", tiempoDormir))

    # En primer tramo evento de cargamento
    if i == 0:
        tiempoCargamento = int((st.NormalDist(120, 15).samples(1))[0])
        tramos[i] += tiempoCargamento
        horaFinal += tiempoCargamento
        eventos.append(("Cargamento", tiempoCargamento))

    # En segundo tramo evento de moja pollos
    if i == 1 and (tiempoFinal <= 1320 or tiempoFinal >= 270):
        tiempoMojado = int((st.NormalDist(5, 2).samples(1))[0])
        tramos[i] += tiempoMojado
        horaFinal += tiempoMojado
        eventos.append(("Mojado pollos", tiempoMojado))

    # Añadir tiempo de tramo a tiempoFinal
    tiempoFinal += tramos[i] 

    # Calcular hora
    if horaFinal > 1439:
        horaFinal -= 1439
    
    Recorrido.append([tramos[i], eventos])

Recorrido.append(tiempoFinal)
Recorrido.append(horaFinal)

print(f"Tiempo final: {Recorrido[-2]} minutos")
print(f"Hora final: {Recorrido[-1]//60} horas {Recorrido[-1]%60} minutos")
print(f"Tramo 1: {Recorrido[0]}")
print(f"Tramo 2: {Recorrido[1]}")
print(f"Tramo 3: {Recorrido[2]}")
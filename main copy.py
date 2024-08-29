import random
import json
import statistics as st
from datetime import datetime, timedelta

# Probabilidades de eventos
PROBABILIDAD_CLIMA = {0: 0.01, 1: 0.10, 2: 0.20, 3: 0.30}  # Aumenta con la gravedad del clima
PROBABILIDAD_MANTENIMIENTO = {0: 0.02, 0.1: 0.03, 0.2: 0.04, 0.3: 0.05, 0.4: 0.06, 0.5: 0.07, 0.6: 0.08, 0.7: 0.09, 0.8: 0.10, 0.9: 0.10, 1: 0.10}  # Probabilidad de ponchadura según el mantenimiento

# Función para manejar todos los eventos posibles
def evaluar_eventos(hora_actual, checkpoint, clima, mantenimiento, fatiga, checkpoint_para_baño):
    eventos = []
    tiempo_extra = timedelta()  # Tiempo adicional debido a eventos
    # Tiempo por defecto entre checkpoints
    tiempo_por_defecto = int((st.NormalDist(checkpoint["regular_duration"], checkpoint["regular_duration"]*0.2).samples(1))[0])
    tiempo_entre_checkpoints = timedelta(minutes=tiempo_por_defecto)

    # Evaluar ponchadura
    probabilidad_clima = PROBABILIDAD_CLIMA[clima] * 0.1  # El clima aporta un 10% a la probabilidad total
    probabilidad_mantenimiento = PROBABILIDAD_MANTENIMIENTO[mantenimiento] * 0.9  # El mantenimiento aporta un 90%
    probabilidad_total = probabilidad_clima + probabilidad_mantenimiento
    
    if random.random() < probabilidad_total:  # Si la probabilidad es suficiente, ocurre una ponchadura
        eventos.append({"event_name": "Ponchadura", "duration": int(st.NormalDist(30, 5).samples(1)[0])})
        tiempo_extra += timedelta(minutes=eventos[-1]["duration"])

    # Evaluar parada para el baño
    probabilidad_base_baño = 0.1 if 360 <= hora_actual.hour * 60 + hora_actual.minute <= 720 else 0.05
    if checkpoint["segment_id"] == checkpoint_para_baño or random.random() < probabilidad_base_baño:
        eventos.append({"event_name": "Parada para banio", "duration": int(st.NormalDist(15, 5).samples(1)[0])})
        tiempo_extra += timedelta(minutes=eventos[-1]["duration"])

    # Evaluar si se necesita dormir debido a la fatiga
    fatiga += tiempo_extra.total_seconds() / 3600  # Duración del tramo en horas
    fatiga += tiempo_entre_checkpoints.total_seconds() * 20 / 3600  # Aumenta la fatiga en 20% por cada hora
    if fatiga > 70:  # Si la fatiga supera el 70%, se necesita descansar
        eventos.append({"event_name": f"Fatiga (Nivel: {fatiga}%)", "duration": 60})
        tiempo_extra += timedelta(hours=1)
        fatiga = 0  # Resetea la fatiga después de dormir

    # Evaluar robo de cargamento entre la 1:00 AM y 4:00 AM
    hora_minima_robo = 1 * 60  # 1:00 AM en minutos
    hora_maxima_robo = 4 * 60  # 4:00 AM en minutos
    if hora_minima_robo <= hora_actual.hour * 60 + hora_actual.minute <= hora_maxima_robo:
        if int(st.NormalDist(7, 3).samples(1)[0]) < 5:
            eventos.append({"event_name": "Robo de cargamento", "duration": int(st.NormalDist(60, 10).samples(1)[0])})
            tiempo_extra += timedelta(minutes=eventos[-1]["duration"])

    # Evaluar baño de cargamento entre las 5:00 AM y 10:00 PM
    hora_minima_bano = 5 * 60  # 5:00 AM en minutos
    hora_maxima_bano = 22 * 60  # 10:00 PM en minutos
    if hora_minima_bano <= hora_actual.hour * 60 + hora_actual.minute <= hora_maxima_bano and checkpoint['segment_id'] == 2:
        eventos.append({"event_name": "Banio de cargamento", "duration": int(st.NormalDist(5, 2).samples(1)[0])})
        tiempo_extra += timedelta(minutes=eventos[-1]["duration"])

    return eventos, tiempo_extra, fatiga

# Simular el trayecto del tráiler
def simular_trayecto(data, hora_inicio):
    eventos_totales = []
    hora_actual = datetime.combine(datetime.today(), hora_inicio)
    duracion_total = timedelta()  # Inicializa la duración total en 0
    fatiga = 0  # Estado inicial de fatiga
    tiempos_checkpoint = {}  # Diccionario para guardar los tiempos de cada checkpoint

    checkpoint_para_baño = random.choice([checkpoint["segment_id"] for checkpoint in data["segment"]])

    for checkpoint in data["segment"]:
        clima = data["weather"]
        mantenimiento = data["maintenance"]
        tiempo_por_defecto = int((st.NormalDist(checkpoint["regular_duration"], checkpoint["regular_duration"] * 0.2).samples(1))[0])
        tiempo_entre_checkpoints = timedelta(minutes=tiempo_por_defecto)
        json_events = []

        print(f"\nCheckpoint {checkpoint['segment_id']} - Clima: {clima}, Mantenimiento: {mantenimiento}, Hora actual: {hora_actual.strftime('%H:%M')}")

        # Evaluar todos los eventos
        eventos, tiempo_extra, fatiga = evaluar_eventos(hora_actual, checkpoint, clima, mantenimiento, fatiga, checkpoint_para_baño)

        for evento in eventos:
            evento.update({"checkpoint": checkpoint['segment_id'], "time": hora_actual.strftime('%H:%M')})
            eventos_totales.append(evento)

        tiempo_entre_checkpoints += tiempo_extra

        # Manejar eventos preestablecidos
        for event in checkpoint["events"]:
            if not any(e['event_name'] == event["event_name"] and e["checkpoint"] == checkpoint['segment_id'] for e in eventos_totales):
                eventos_totales.append({"event_name": event["event_name"], "checkpoint": checkpoint['segment_id'], "time": hora_actual.strftime('%H:%M'), "duration": event["event_time"]})
                print(f"{event['event_name']} en el checkpoint {checkpoint['segment_id']} a las {hora_actual.strftime('%H:%M')}!")

                calculo_minutos = int((st.NormalDist(event["event_time"], event["event_time"] * 0.2).samples(1))[0])
                tiempo_entre_checkpoints += timedelta(minutes=calculo_minutos)

                json_events.append({"event_name": event["event_name"], "event_time": calculo_minutos})

        checkpoint["events"] = json_events
        duracion_total += tiempo_entre_checkpoints
        hora_actual += tiempo_entre_checkpoints
        tiempo_tardado = int(tiempo_entre_checkpoints.total_seconds() // 60)
        checkpoint["estimated_time"] = tiempo_tardado
        tiempos_checkpoint[f"Checkpoint {checkpoint['segment_id']}"] = tiempo_tardado
        print(f"Tiempo tardado en el checkpoint {checkpoint['segment_id']}: {tiempo_tardado} minutos")

    hora_llegada = (datetime.combine(datetime.today(), hora_inicio) + duracion_total).time()
    print(f"\nHora de inicio del tráiler: {hora_inicio.strftime('%H:%M')}")
    print(f"Hora de llegada calculada: {hora_llegada.strftime('%H:%M')}")

    data["total_time"] = duracion_total.days * 24 * 60 + duracion_total.seconds // 60
    data["end_time"] = data["start_time"] + data["total_time"]

    # Guardar los eventos en un archivo JSON
    with open('eventos.json', 'w') as eventos_file:
        json.dump(eventos_totales, eventos_file, indent=4)

    # Guardar el resultado en un archivo JSON
    output_data = {
        "hora_inicio": hora_inicio.strftime('%H:%M'),
        "tiempos_checkpoint": tiempos_checkpoint,
        "hora_llegada_calculada": hora_llegada.strftime('%H:%M')
    }

    with open('output.json', 'w') as output_file:
        json.dump(output_data, output_file, indent=4)

    with open('Agentes.json', 'w') as output_file:
        json.dump(data, output_file, indent=4)

    return eventos_totales, hora_llegada

# Ejecutar la simulación
if __name__ == "__main__":
    with open('Agentes.json', 'r') as file:
        data = json.load(file)
    
    hora_inicio = datetime.strptime(f"{data['start_time']//60}:{data['start_time']%60}", '%H:%M').time()

    print("Iniciando la simulacion del trayecto del trailer...\n")
    eventos, hora_llegada = simular_trayecto(data, hora_inicio)

    print("\nEventos ocurridos durante el trayecto:")
    if eventos:
        for evento in eventos:
            print(f"{evento['event_name']} en el checkpoint {evento['checkpoint']} a las {evento['time']} (Duración: {evento['duration']} minutos)")
    else:
        print("No hubo eventos durante el trayecto.")

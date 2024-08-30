import random
import json
import statistics as st
from datetime import datetime, timedelta

# Probabilidades de eventos
PROBABILIDAD_CLIMA = {0: 0.01, 1: 0.10, 2: 0.20, 3: 0.30}  # Aumenta con la gravedad del clima
PROBABILIDAD_MANTENIMIENTO = {0: 0.02, 0.1: 0.03, 0.2: 0.04, 0.3: 0.05, 0.4: 0.06, 0.5: 0.07, 0.6: 0.08, 0.7: 0.09, 0.8: 0.10, 0.9: 0.10, 1: 0.10}  # Probabilidad de ponchadura según el mantenimiento

# Función para manejar todos los eventos posibles
def evaluar_eventos(current_time, segment, clima, mantenimiento): 
    events = []
    extra_time = timedelta()  # Tiempo adicional debido a eventos
    # Tiempo por defecto entre checkpoints
    # default_time = (st.NormalDist(segment["regular_duration"][0], segment["regular_duration"][1]).samples(1))[0]
    # default_time = int((st.NormalDist(checkpoint["regular_duration"], checkpoint["regular_duration"]*0.2).samples(1))[0])
    # time_between_checkpoints = timedelta(minutes=default_time)

    with open('events.json', 'r') as file:
        eventsjson = json.load(file)

    for type_of_event in eventsjson:

        # MANDATORY (prestablecidos)
        if type_of_event == "mandatory_events":
            for event in eventsjson["mandatory_events"]:

                if event["segment"] == segment and (event["time_window"][0] <= current_time and event["time_window"][1] >= current_time):
                    t = st.NormalDist(event["duration"], event["deviation"]).samples(1)[0]
                    events.append({
                        "event_name": event["name"],
                        "event_time": t,
                        "time_of_event": 0
                    })
                    print(event)

                    extra_time += timedelta(minutes=t)    
            
        # TODO: evaluar el tiempo, similar a los regulares

        # RANDOM (regulares)
        if type_of_event == "random_events":
            for event in eventsjson["random_events"]:

                if event["probability"] >= random.random():
                    t = st.NormalDist(event["duration"], event["deviation"]).samples(1)[0]
                    events.append({
                        "event_name": event["name"],
                        "event_time": t,
                        "time_of_event": 0
                    })

                    extra_time += timedelta(minutes=t)

    # # Evaluar ponchadura
    # probabilidad_clima = PROBABILIDAD_CLIMA[clima] * 0.1  # El clima aporta un 10% a la probabilidad total
    # probabilidad_mantenimiento = PROBABILIDAD_MANTENIMIENTO[mantenimiento] * 0.9  # El mantenimiento aporta un 90%
    # probabilidad_total = probabilidad_clima + probabilidad_mantenimiento

    # if random.random() < probabilidad_total:  # Si la probabilidad es suficiente, ocurre una ponchadura
    #     eventos.append({"event_name": "Ponchadura", "duration": int(st.NormalDist(30, 5).samples(1)[0])})
    #     extra_time += timedelta(minutes=eventos[-1]["duration"])

    # # Evaluar parada para el baño
    # probabilidad_base_baño = 0.1 if 360 <= actual_hour.hour * 60 + actual_hour.minute <= 720 else 0.05
    # if checkpoint["segment_id"] == checkpoint_para_baño or random.random() < probabilidad_base_baño:
    #     eventos.append({"event_name": "Parada para banio", "duration": int(st.NormalDist(15, 5).samples(1)[0])})
    #     extra_time += timedelta(minutes=eventos[-1]["duration"])

    # # Evaluar si se necesita dormir debido a la fatiga
    # fatiga += extra_time.total_seconds() / 3600  # Duración del tramo en horas
    # fatiga += time_between_checkpoints.total_seconds() * 20 / 3600  # Aumenta la fatiga en 20% por cada hora
    # if fatiga > 70:  # Si la fatiga supera el 70%, se necesita descansar
    #     eventos.append({"event_name": f"Fatiga (Nivel: {fatiga}%)", "duration": 60})
    #     extra_time += timedelta(hours=1)
    #     fatiga = 0  # Resetea la fatiga después de dormir

    # # Evaluar robo de cargamento entre la 1:00 AM y 4:00 AM
    # hora_minima_robo = 1 * 60  # 1:00 AM en minutos
    # hora_maxima_robo = 4 * 60  # 4:00 AM en minutos
    # if hora_minima_robo <= actual_hour.hour * 60 + actual_hour.minute <= hora_maxima_robo:
    #     if int(st.NormalDist(7, 3).samples(1)[0]) < 5:
    #         eventos.append({"event_name": "Robo de cargamento", "duration": int(st.NormalDist(60, 10).samples(1)[0])})
    #         extra_time += timedelta(minutes=eventos[-1]["duration"])

    # # Evaluar baño de cargamento entre las 5:00 AM y 10:00 PM
    # hora_minima_bano = 5 * 60  # 5:00 AM en minutos
    # hora_maxima_bano = 22 * 60  # 10:00 PM en minutos
    # if hora_minima_bano <= actual_hour.hour * 60 + actual_hour.minute <= hora_maxima_bano and checkpoint['segment_id'] == 2:
    #     eventos.append({"event_name": "Bao de cargamento", "duration": int(st.NormalDist(5, 2).samples(1)[0])})
    #     extra_time += timedelta(minutes=eventos[-1]["duration"])

    return events, extra_time

# Simular el trayecto del tráiler
def simular_trayecto(data, start_time):
    current_time = datetime.combine(datetime.today(), start_time)
    total_time = timedelta()  # Inicializa la duración total en 0
    # tiempos_checkpoint = {}  # Diccionario para guardar los tiempos de cada checkpoint

    # checkpoint_para_baño = random.choice([checkpoint["segment_id"] for checkpoint in data["segment"]])

    for segment in data["segment"]:
        clima = data["weather"]
        mantenimiento = data["maintenance"]
        
        print(f"\nCheckpoint {segment['segment_id']} - Clima: {clima}, Mantenimiento: {mantenimiento}, Hora actual: {current_time.strftime('%H:%M')}")

        segment_duration = (st.NormalDist(segment["regular_duration"][0], segment["regular_duration"][0] * 0.2).samples(1))[0] # TODO: Cambiar desviacion estandar
        current_time += timedelta(minutes=segment_duration)
        
        # Evaluar todos los eventos
        events, extra_time = evaluar_eventos(current_time, segment, clima, mantenimiento)

        for event in events:
            # TODO: fix time
            t = random.randint(0, int(extra_time.days * 24 * 60 + extra_time.seconds // 60))
            time_of_event = current_time + timedelta(minutes=t)
            event.update({"time_of_event": time_of_event.strftime('%H:%M:%S')})
            print(event)

        current_time += extra_time

        

        # # Manejar eventos preestablecidos
        # for event in checkpoint["events"]:
        #     if not any(e['event_name'] == event["event_name"] and e["checkpoint"] == checkpoint['segment_id'] for e in total_events):
        #         total_events.append({"event_name": event["event_name"], "checkpoint": checkpoint['segment_id'], "time": actual_hour.strftime('%H:%M'), "duration": event["event_time"]})
        #         print(f"{event['event_name']} en el checkpoint {checkpoint['segment_id']} a las {actual_hour.strftime('%H:%M')}!")

        #         calculo_minutos = int((st.NormalDist(event["event_time"], event["event_time"] * 0.2).samples(1))[0])
        #         time_between_checkpoints += timedelta(minutes=calculo_minutos)

        #         json_events.append({"event_name": event["event_name"], "event_time": calculo_minutos})

        segment["events"] = events
        total_segment_time = segment_duration + (extra_time.days * 24 * 60 + extra_time.seconds // 60 + extra_time.seconds%60)
        total_time += timedelta(minutes=total_segment_time) 
        segment["estimated_time"] = total_segment_time
        print(f"Tiempo tardado en el checkpoint {segment['segment_id']}: {total_segment_time} minutos")

    print(data)

    end_time = (datetime.combine(datetime.today(), start_time) + total_time).time()
    print(f"\nHora de inicio del tráiler: {start_time.strftime('%H:%M')}")
    print(f"Hora de llegada calculada: {end_time.strftime('%H:%M')}")

    data["total_time"] = total_time.days * 24 * 60 + total_time.seconds // 60 + total_time.seconds%60
    data["end_time"] = data["start_time"] + data["total_time"]

    with open('Agentes.json', 'w') as output_file:
        json.dump(data, output_file, indent=4)

    return events, data

# Ejecutar la simulación
if __name__ == "__main__":
    with open('Agentes.json', 'r') as file:
        data = json.load(file)
    
    start_time = datetime.strptime(f"{data['start_time']//60}:{data['start_time']%60}", '%H:%M').time()

    print("Iniciando la simulacion del trayecto del trailer...\n")
    eventos, data = simular_trayecto(data, start_time)

    print("\nEventos ocurridos durante el trayecto:")
    if eventos:
        for evento in eventos:
            print(f"{evento['event_name']} a las {evento['time_of_event']} (Duración: {evento['event_time']} minutos)")
    else:
        print("No hubo eventos durante el trayecto.")

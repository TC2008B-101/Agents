import random
import json
import statistics as st
from datetime import datetime, timedelta

# Probabilidades de eventos
PROBABILIDAD_CLIMA = {0: 0.01, 1: 0.10, 2: 0.20, 3: 0.30}  # Aumenta con la gravedad del clima
PROBABILIDAD_MANTENIMIENTO = {0: 0.02, 0.1: 0.03, 0.2: 0.04, 0.3: 0.05, 0.4: 0.06, 0.5: 0.07, 0.6: 0.08, 0.7: 0.09, 0.8: 0.10, 0.9: 0.10, 1: 0.10}  # Probabilidad de ponchadura según el mantenimiento

# Function for managing all possible events
# TODO: MANEJAR IMPACTO DE CLIMA Y MANTENIMIENTO
def evaluate_events(current_time, segment, weather, maintenance): 
    events = []
    extra_time = timedelta()  # Additional time added to segment due to events

    # Open json with possible events
    with open('events.json', 'r') as file:
        eventsjson = json.load(file)

    # MANDATORY (prestablished events)
    for event in eventsjson["mandatory_events"]:

        if event["segment"] == segment["segment_id"] and (event["time_window"][0] <= (current_time.hour*60 + current_time.minute) and event["time_window"][1] >= (current_time.hour*60 + current_time.minute)):
            t = st.NormalDist(event["duration"], event["deviation"]).samples(1)[0]
            events.append({
                "event_name": event["name"],
                "event_time": t,
                "time_of_event": 0
            })

            extra_time += timedelta(minutes=t)    

    # RANDOM (regular events)
    for event in eventsjson["random_events"]:

        if event["probability"] >= random.random():
            t = st.NormalDist(event["duration"], event["deviation"]).samples(1)[0]
            events.append({
                "event_name": event["name"],
                "event_time": t,
                "time_of_event": 0
            })

            extra_time += timedelta(minutes=t)

    return events, extra_time

# Run truck's simulation
def simulate_trip(data, start_time):
    current_time = datetime.combine(datetime.today(), start_time)
    total_time = timedelta()  # Initialize total time in 0
    total_events = []

    for segment in data["segment"]:
        weather = data["weather"]
        maintenance = data["maintenance"]
        
        print(f"\nCheckpoint {segment['segment_id']} - Clima: {weather}, Mantenimiento: {maintenance}, Hora actual: {current_time.strftime('%H:%M')}")

        # Calculate segment duration
        segment_duration = (st.NormalDist(segment["regular_duration"][0], segment["regular_duration"][1]).samples(1))[0]
        current_time += timedelta(minutes=segment_duration)
        
        # Evaluate all events
        events, extra_time = evaluate_events(current_time, segment, weather, maintenance)

        # Assign random time within segment for events to happen
        for event in events:
            t = random.randint(0, int(extra_time.days * 24 * 60 + extra_time.seconds // 60))
            time_of_event = current_time + timedelta(minutes=t)
            event.update({"time_of_event": time_of_event.strftime('%H:%M:%S')})
            total_events.append(event)

        current_time += extra_time
        segment["events"] = events  # Append events to corresponding segment in json
        
        total_segment_time = segment_duration + (extra_time.days * 24 * 60 + extra_time.seconds // 60 + extra_time.seconds%60)
        segment["estimated_time"] = total_segment_time  # Write the total segment time in json

        total_time += timedelta(minutes=total_segment_time) # Add segment time to total trip time
        print(f"Tiempo tardado en el checkpoint {segment['segment_id']}: {total_segment_time} minutos")

    end_time = (datetime.combine(datetime.today(), start_time) + total_time).time()
    print(f"\nHora de inicio del tráiler: {start_time.strftime('%H:%M')}")
    print(f"Hora de llegada calculada: {end_time.strftime('%H:%M')}")

    # Write total trip time and end time in json
    data["total_time"] = total_time.days * 24 * 60 + total_time.seconds // 60 + total_time.seconds%60
    data["end_time"] = data["start_time"] + data["total_time"]

    #! WRITE DATA IN AGENTS.JSON FOR DEVELOPMENT ONLY
    with open('agents.json', 'w') as output_file:
        json.dump(data, output_file, indent=4)

    return total_events, data

# Run simulation RETURNS OUTPUT JSON
def start_simulation(data):
    
    # Read starting time
    start_time = datetime.strptime(f"{data['start_time']//60}:{data['start_time']%60}", '%H:%M').time()

    # Run trip simulation
    print("Iniciando la simulacion del trayecto del trailer...\n")
    total_events, data = simulate_trip(data, start_time)

    # Print all events that occured during trip
    print("\nEventos ocurridos durante el trayecto:")
    if total_events:
        for event in total_events:
            print(f"{event['event_name']} a las {event['time_of_event']} (Duración: {event['event_time']} minutos)")
    else:
        print("No hubo eventos durante el trayecto.")

    return data

#! FOR DEVELOPMENT PURPOSES ONLY
# Open input data
with open('agents.json', 'r') as file:
    data = json.load(file)

output = start_simulation(data)
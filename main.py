import copy
import random
import json
import statistics as st
from datetime import datetime, timedelta

#! These are used only for plotting, CAN BE REMOVED
import matplotlib.pyplot as plt
from scipy.stats import norm
import numpy as np

# STATE IMPACT PROBABILITY
WEATHER_PROBABILITY = {"Soleado": 0.01, "Nublado": 0.01, "Llovizna": 0.10, "Lluvia": 0.20, "Tormenta": 0.30}  # Aumenta con la gravedad del clima
MAINTENANCE_PROBABILITY = {0: 0.02, 0.1: 0.03, 0.2: 0.04, 0.3: 0.05, 0.4: 0.06, 0.5: 0.07, 0.6: 0.08, 0.7: 0.09, 0.8: 0.10, 0.9: 0.10, 1: 0.10}  # Probabilidad de ponchadura según el mantenimiento
POPULATION = 100

# Function for managing all possible events
def evaluate_events(current_time, segment, weather, maintenance): 
    events = []
    extra_time = 0  # Additional time added to segment due to events

    # Open json with possible events
    with open('events.json', 'r') as file:
        eventsjson = json.load(file)

    # MANDATORY (prestablished events)
    for event in eventsjson["mandatory_events"]:

        if event["segment"] == segment["segment_id"] and (event["time_window"][0] <= (current_time.hour*60 + current_time.minute) and event["time_window"][1] >= (current_time.hour*60 + current_time.minute)):
            t = abs(st.NormalDist(event["duration"], event["deviation"]).samples(1)[0])
            events.append({
                "event_name": event["name"],
                "event_time": t,
                "time_of_event": 0
            })

            extra_time += t    

    # RANDOM (regular events)
    for event in eventsjson["random_events"]:

        if event["probability"] >= random.random():
            t = abs(st.NormalDist(event["duration"], event["deviation"]).samples(1)[0])
            t *= (1 + WEATHER_PROBABILITY.get(weather)) * (1 + event["weather_impact"]) * (1 + MAINTENANCE_PROBABILITY.get(maintenance)) * (1 + event["maintenance_impact"])    # Impacted by states
            events.append({
                "event_name": event["name"],
                "event_time": t,
                "time_of_event": 0
            })

            extra_time += t

    return events, extra_time

# Run truck's simulation
def simulate_trip(data, start_time):
    current_time = datetime.combine(datetime.today(), start_time)
    total_time = timedelta()  # Initialize total time in 0

    for segment in data["segment"]:
        weather = data["weather"]
        maintenance = data["maintenance"]
        
        # print(f"\nCheckpoint {segment['segment_id']} - Clima: {weather}, Mantenimiento: {maintenance}, Hora actual: {current_time.strftime('%H:%M')}")

        # Calculate segment duration
        segment_duration = abs(st.NormalDist(segment["regular_duration"][0], segment["regular_duration"][1]).samples(1)[0])
        segment_duration *= (1 + WEATHER_PROBABILITY.get(weather) + MAINTENANCE_PROBABILITY.get(maintenance))   # Impact by states
        current_time += timedelta(minutes=segment_duration)
        
        # Evaluate all events
        events, extra_time = evaluate_events(current_time, segment, weather, maintenance)

        # Assign random time within segment for events to happen
        for event in events:
            t = random.randint(0, int(extra_time))
            time_of_event = current_time + timedelta(minutes=t)
            event.update({"time_of_event": time_of_event.strftime('%H:%M:%S')})

        current_time += timedelta(minutes=extra_time)
        segment["events"] = events  # Append events to corresponding segment in json
        
        total_segment_time = segment_duration + extra_time
        segment["estimated_time"] = total_segment_time  # Write the total segment time in json

        total_time += timedelta(minutes=total_segment_time) # Add segment time to total trip time
        # print(f"Tiempo tardado en el checkpoint {segment['segment_id']}: {total_segment_time} minutos")

    end_time = (datetime.combine(datetime.today(), start_time) + total_time).time()
    # print(f"\nHora de inicio del tráiler: {start_time.strftime('%H:%M')}")
    # print(f"Hora de llegada calculada: {end_time.strftime('%H:%M')}")

    # Write total trip time and end time in json
    data["total_time"] = total_time.days * 24 * 60 + total_time.seconds // 60 + total_time.seconds%60
    data["end_time"] = data["start_time"] + data["total_time"]

    # #! WRITE DATA IN AGENTS.JSON FOR DEVELOPMENT ONLY
    # with open('agents.json', 'w') as output_file:
    #     json.dump(data, output_file, indent=4)

    return data

# Run simulation RETURNS OUTPUT JSON
def start_simulation(data):
    agents = []
    
    # Read starting time
    start_time = datetime.strptime(f"{data['start_time']//60}:{data['start_time']%60}", '%H:%M').time()

    # Run trip simulation
    print("Iniciando la simulacion del trayecto del trailer...\n")
    for i in range(0, POPULATION):
        random.seed(datetime.now().timestamp() + i) # Ensure a uniquely random simulation for each one
        data_copy = copy.deepcopy(data)  # Make a deep copy of the data for this simulation
        dataSimulation = simulate_trip(data_copy, start_time)
        agents.append(dataSimulation)
    
    # Calcularte mean and std for total time in each simulation
    total_times = [agent["total_time"] for agent in agents]
    mean_times = st.mean(total_times)
    std_times = st.stdev(total_times)
    
    # Calculate agent with closest time to mean (peak in normal distribution)
    closest_agent = min(agents, key=lambda agent: abs(agent["total_time"] - mean_times))
    print(closest_agent)

    #! Show normal distribution, CAN BE REMOVED
    x_axis = np.arange(240, 700, 0.1) 
    plt.plot(x_axis, norm.pdf(x_axis, mean_times, std_times)) 
    plt.show() 

    return closest_agent

#! FOR DEVELOPMENT PURPOSES ONLY
# Open input data
with open('agents.json', 'r') as file:
    data = json.load(file)

output = start_simulation(data)
import simpy
import random
import json
# import os


def cargar_estados(filepath):
    with open(filepath, 'r') as file:
        datos = json.load(file)
    clima = datos.get("clima", 0)
    mantenimiento = datos.get("mantenimiento", 1.0)
    hora = datos.get("hora", 0)
    return clima, mantenimiento, hora

def determinar_eventos(clima, mantenimiento):
    eventos = []

    #lluvia
    if clima > 2:  
        if clima == 3:
            eventos.append({"evento": "lluvia ligera", "demora": random.randint(10, 30)})
        elif clima == 4:
            eventos.append({"evento": "lluvia intensa", "demora": random.randint(30, 60)})

    #llanta ponchada
    if random.random() > mantenimiento: 
        eventos.append({"evento": "llanta ponchada", "demora": random.randint(15, 45)})

    #policía
    if random.random() > 0.8:
        eventos.append({"evento": "parada por policía", "demora": random.randint(5, 20)})

    #sueño
    if random.random() > 0.9:
        eventos.append({"evento": "conductor duerme", "demora": random.randint(20, 40)})

    return eventos


def simular_ruta(env, clima, mantenimiento, hora):
    checkpoints = ["planta", "granja", "baño", "planta"]
    tiempos = []

    for i in range(len(checkpoints) - 1):
        tiempo_base = random.randint(60, 120)  
        eventos = determinar_eventos(clima, mantenimiento)
        tiempo_eventos = sum(evento["demora"] for evento in eventos)

        tiempo_total = tiempo_base + tiempo_eventos
        tiempos.append({"checkpoint": i + 1, "time_taken_minutes": tiempo_total})

        print(f"De {checkpoints[i]} a {checkpoints[i+1]}: {tiempo_total} minutos (Eventos: {eventos})")
        yield env.timeout(tiempo_total)

    return tiempos


def main(input_filepath):
    clima, mantenimiento, hora = cargar_estados(input_filepath)
    env = simpy.Environment()
    resultado_ruta = env.process(simular_ruta(env, clima, mantenimiento, hora))

    env.run()
    resultado_json = {"route": resultado_ruta.value}

    #Json salida
    output_filename = "resultado_ruta.json"
    with open(output_filename, 'w') as outfile:
        json.dump(resultado_json, outfile, indent=4)

    print(f"Resultado guardado en {output_filename}")

if __name__ == "__main__":
    input_filepath = "/Users/danielagallardocolin/Documents/5to semestre itc/Reto Modelación Agentes/entrada.json" 
    main(input_filepath)

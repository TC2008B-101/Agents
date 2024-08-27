import random
import json
from datetime import datetime, timedelta

# Simulación del trayecto de un tráiler

def trailer_sim_handler(data):
    print("Iniciando la simulación del trayecto del trailer...\n")

    print("Datos de la simulación:")
    print(data)
    
    hora_inicio = datetime.strptime(data["inicio"]["hora_inicio"], '%H:%M').time()
    hora_objetivo = datetime.strptime(data["final"]["hora_llegada_esperada"], '%H:%M').time()
    print(f"Hora objetivo de llegada: {hora_objetivo.strftime('%H:%M')}")
    
    eventos, hora_llegada = simular_trayecto(data,hora_inicio, hora_objetivo)
    
    resultado = {
        "eventos": eventos,
        "hora_llegada": hora_llegada.strftime('%H:%M'),
        "a_tiempo": hora_llegada <= hora_objetivo
    }
    
    print("\nEventos ocurridos durante el trayecto:")
    if eventos:
        for evento in eventos:
            print(evento)
    else:
        print("No hubo eventos durante el trayecto.")
    
    if resultado["a_tiempo"]:
        print(f"\nEl trailer llegó a tiempo o antes de las {hora_objetivo.strftime('%H:%M')}.")
    else:
        print(f"\nEl trailer se retrasó y llegó después de las {hora_objetivo.strftime('%H:%M')}.")
    
    return resultado

# # Leer datos desde input.json
# with open('input.json', 'r') as file:
#     data = json.load(file)

# Probabilidades de eventos
PROBABILIDAD_CLIMA = {0: 0.01, 1: 0.10, 2: 0.20, 3: 0.30}  # Aumenta con la gravedad del clima
PROBABILIDAD_MANTENIMIENTO = {0: 0.02, 1: 0.10}  # Probabilidad de ponchadura según el mantenimiento

# Función para determinar si ocurre una ponchadura
def evaluar_ponchadura(clima, mantenimiento):
    probabilidad_clima = PROBABILIDAD_CLIMA[clima] * 0.1  # El clima aporta un 10% a la probabilidad total
    probabilidad_mantenimiento = PROBABILIDAD_MANTENIMIENTO[mantenimiento] * 0.9  # El mantenimiento aporta un 90%
    probabilidad_total = probabilidad_clima + probabilidad_mantenimiento
    return probabilidad_total >= 0.1

# Función para determinar si se necesita una parada para el baño
def evaluar_parada_baño(hora, checkpoint, checkpoint_para_baño):
    # Forzar la parada en el checkpoint seleccionado
    if checkpoint == checkpoint_para_baño:
        return True
    # Probabilidad normal en otros checkpoints
    probabilidad_base = 0.1 if 360 <= hora <= 720 else 0.05
    return random.random() < probabilidad_base

# Función para determinar si se necesita una parada para desayunar
def evaluar_parada_desayuno(hora_actual, ha_desayunado):
    if ha_desayunado:
        return False  # Si ya ha desayunado, no puede desayunar de nuevo
    hora_minima_desayuno = 7 * 60  # 7:00 AM en minutos
    hora_maxima_desayuno = 10 * 60  # 10:00 AM en minutos
    return hora_minima_desayuno <= hora_actual <= hora_maxima_desayuno

# Función para determinar si se necesita una parada para comer
def evaluar_parada_comida(hora_actual, ha_comido):
    if ha_comido:
        return False  # Si ya ha comido, no puede comer de nuevo
    hora_minima_comida = 14 * 60  # 2:00 PM en minutos
    hora_maxima_comida = 16 * 60  # 4:00 PM en minutos
    return hora_minima_comida <= hora_actual <= hora_maxima_comida

# Función para determinar si se necesita una parada para cenar
def evaluar_parada_cena(hora_actual, ha_cenado):
    if ha_cenado:
        return False  # Si ya ha cenado, no puede cenar de nuevo
    hora_minima_cena = 22 * 60  # 10:00 PM en minutos
    hora_maxima_cena = 1 * 60  # 1:00 AM en minutos
    return (hora_actual >= hora_minima_cena or hora_actual <= hora_maxima_cena)

# Función para determinar si se necesita dormir debido a la fatiga
def evaluar_fatiga(fatiga):
    return fatiga > 70  # Si la fatiga supera el 70%, se necesita dormir

# Función para determinar si el cargamento es robado entre las 2 AM y 4 AM
def evaluar_robo(hora_actual):
    hora_minima_robo = 2 * 60  # 2:00 AM en minutos
    hora_maxima_robo = 4 * 60  # 4:00 AM en minutos
    if hora_minima_robo <= hora_actual <= hora_maxima_robo:
        return random.randint(1, 10) < 5  # Si el número es menor que 5, el cargamento es robado
    return False

# Función para determinar si el cargamento necesita ser bañado
def evaluar_bano_cargamento(hora_actual, checkpoint):
    if checkpoint == 3:
        hora_minima_bano = 7 * 60  # 7:00 AM en minutos
        hora_maxima_bano = 16 * 60  # 4:00 PM en minutos
        return hora_minima_bano <= hora_actual <= hora_maxima_bano
    return False

# Simular el trayecto del tráiler
def simular_trayecto(data,hora_inicio, hora_objetivo):
    eventos = []
    hora_actual = datetime.combine(datetime.today(), hora_inicio)
    duracion_total = timedelta()  # Inicializa la duración total en 0
    ha_desayunado = False  # Bandera para controlar si ya ha desayunado
    ha_comido = False  # Bandera para controlar si ya ha comido
    ha_cenado = False  # Bandera para controlar si ya ha cenado
    fatiga = 0  # Estado inicial de fatiga
    tiempos_checkpoint = {}  # Diccionario para guardar los tiempos de cada checkpoint

    # Seleccionar aleatoriamente un checkpoint para forzar la parada para el baño
    checkpoint_para_baño = random.choice([checkpoint["checkpoint"] for checkpoint in data["checkpoints"]])

    for checkpoint in data["checkpoints"]:
        clima = checkpoint["clima"]
        mantenimiento = checkpoint["mantenimiento"]
        tiempo_por_defecto = checkpoint["tiempo_por_defecto_minutos"]
        inicio_checkpoint = hora_actual
        
        print(f"\nCheckpoint {checkpoint['checkpoint']} - Clima: {clima}, Mantenimiento: {mantenimiento}, Hora actual: {hora_actual.strftime('%H:%M')}")

        # Tiempo por defecto entre checkpoints
        tiempo_entre_checkpoints = timedelta(minutes=tiempo_por_defecto)

        # Evaluar ponchadura
        if evaluar_ponchadura(clima, mantenimiento):
            eventos.append(f"Ponchadura en el checkpoint {checkpoint['checkpoint']}")
            print("¡Ponchadura!")
            tiempo_entre_checkpoints += timedelta(minutes=30)  # Se agregan 30 minutos por la ponchadura

        # Evaluar parada para el baño, forzando en uno de los checkpoints
        if evaluar_parada_baño(hora_actual.hour * 60 + hora_actual.minute, checkpoint["checkpoint"], checkpoint_para_baño):
            eventos.append(f"Parada para baño en el checkpoint {checkpoint['checkpoint']}")
            print("Parada para baño")
            tiempo_entre_checkpoints += timedelta(minutes=15)  # Se agregan 15 minutos por la parada para el baño

        # Evaluar parada para desayunar entre las 7:00 AM y 10:00 AM
        if evaluar_parada_desayuno(hora_actual.hour * 60 + hora_actual.minute, ha_desayunado):
            eventos.append(f"Parada para desayunar en el checkpoint {checkpoint['checkpoint']}")
            print("Parada para desayunar")
            tiempo_entre_checkpoints += timedelta(minutes=30)  # Se agregan 30 minutos por la parada para desayunar
            ha_desayunado = True  # Marcar que ya ha desayunado

        # Evaluar parada para comer entre las 2:00 PM y 4:00 PM
        if evaluar_parada_comida(hora_actual.hour * 60 + hora_actual.minute, ha_comido):
            eventos.append(f"Parada para comer en el checkpoint {checkpoint['checkpoint']}")
            print("Parada para comer")
            tiempo_entre_checkpoints += timedelta(minutes=30)  # Se agregan 30 minutos por la parada para comer
            ha_comido = True  # Marcar que ya ha comido

        # Evaluar parada para cenar entre las 10:00 PM y 1:00 AM
        if evaluar_parada_cena(hora_actual.hour * 60 + hora_actual.minute, ha_cenado):
            eventos.append(f"Parada para cenar en el checkpoint {checkpoint['checkpoint']}")
            print("Parada para cenar")
            tiempo_entre_checkpoints += timedelta(minutes=30)  # Se agregan 30 minutos por la parada para cenar
            ha_cenado = True  # Marcar que ya ha cenado

        # Evaluar si se necesita bañar el cargamento en el checkpoint 3 entre 7:00 AM y 4:00 PM
        if evaluar_bano_cargamento(hora_actual.hour * 60 + hora_actual.minute, checkpoint["checkpoint"]):
            eventos.append(f"Baño de cargamento en el checkpoint {checkpoint['checkpoint']} a las {hora_actual.strftime('%H:%M')}")
            print("¡Baño de cargamento!")
            tiempo_entre_checkpoints += timedelta(minutes=30)  # Se agregan 30 minutos por bañar el cargamento

        # Evaluar fatiga
        fatiga += (tiempo_entre_checkpoints.total_seconds() // 1800) * 20  # Incrementa fatiga 20% cada 30 minutos
        if evaluar_fatiga(fatiga):
            eventos.append(f"Fatiga al {fatiga}%, se detiene a dormir en el checkpoint {checkpoint['checkpoint']}")
            print(f"¡Fatiga al {fatiga}%! Se necesita dormir.")
            tiempo_entre_checkpoints += timedelta(hours=8)  # Se agregan 8 horas por dormir
            fatiga = 0  # Resetea la fatiga después de dormir

        # Evaluar robo de cargamento entre las 2:00 AM y 4:00 AM
        if evaluar_robo(hora_actual.hour * 60 + hora_actual.minute):
            eventos.append(f"¡Robo de cargamento en el checkpoint {checkpoint['checkpoint']} a las {hora_actual.strftime('%H:%M')}!")
            print(f"¡Robo de cargamento en el checkpoint {checkpoint['checkpoint']}!")
            tiempo_entre_checkpoints += timedelta(minutes=60)  # Se agregan 60 minutos por el robo

        # Avanzar tiempo con el tiempo por defecto más cualquier tiempo adicional
        duracion_total += tiempo_entre_checkpoints
        hora_actual += tiempo_entre_checkpoints
        
        # Calcular y guardar el tiempo tardado en el checkpoint
        tiempo_tardado = int(tiempo_entre_checkpoints.total_seconds() // 60)
        tiempos_checkpoint[f"Checkpoint {checkpoint['checkpoint']}"] = tiempo_tardado
        print(f"Tiempo tardado en el checkpoint {checkpoint['checkpoint']}: {tiempo_tardado} minutos")

    hora_llegada = (datetime.combine(datetime.today(), hora_inicio) + duracion_total).time()
    print(f"\nHora de inicio del tráiler: {hora_inicio.strftime('%H:%M')}")
    print(f"Hora esperada de llegada: {hora_objetivo.strftime('%H:%M')}")
    print(f"Hora de llegada calculada: {hora_llegada.strftime('%H:%M')}")

    # Guardar el resultado en un archivo JSON
    output_data = {
        "hora_inicio": hora_inicio.strftime('%H:%M'),
        "tiempos_checkpoint": tiempos_checkpoint,
        "hora_llegada_esperada": hora_objetivo.strftime('%H:%M'),
        "hora_llegada_calculada": hora_llegada.strftime('%H:%M')
    }

    with open('output.json', 'w') as output_file:
        json.dump(output_data, output_file, indent=4)

    return eventos, hora_llegada

# Ejecutar la simulación
if __name__ == "__main__":
    # Parámetros iniciales
    hora_inicio = datetime.strptime(data["inicio"]["hora_inicio"], '%H:%M').time()  # Hora de inicio desde input.json
    hora_objetivo = datetime.strptime(data["final"]["hora_llegada_esperada"], '%H:%M').time()  # Hora objetivo de llegada: 5:00 PM

    print("Iniciando la simulacion del trayecto del trailer...\n")
    eventos, hora_llegada = simular_trayecto(hora_inicio, hora_objetivo)

    print("\nEventos ocurridos durante el trayecto:")
    if eventos:
        for evento in eventos:
            print(evento)
    else:
        print("No hubo eventos durante el trayecto.")

    # Comprobar si llegó a tiempo
    if hora_llegada <= hora_objetivo:
        print("\nEl trailer llego a tiempo o antes de las 5:00 PM.")
    else:
        print("\nEl trailer se retrasó y llego después de las 5:00 PM.")

from collections import deque
import heapq

# Clase Proceso
class Proceso:
    def __init__(self, etiqueta, tiempo_burst, tiempo_llegada, cola, prioridad):
        self.etiqueta = etiqueta
        self.tiempo_burst = tiempo_burst
        self.tiempo_llegada = tiempo_llegada
        self.cola = cola  # Nivel de la cola
        self.prioridad = prioridad  # Prioridad dentro de la cola
        self.tiempo_restante = tiempo_burst
        self.tiempo_inicio = None
        self.tiempo_completado = None
        self.tiempo_respuesta = None
        self.tiempo_espera = 0
        self.tiempo_turnaround = 0

    def __repr__(self):
        return f"{self.etiqueta}(BT={self.tiempo_burst}, AT={self.tiempo_llegada}, Q={self.cola}, Pr={self.prioridad})"

# Clase NivelCola
class NivelCola:
    def __init__(self, nivel, politica_planificacion, tiempo_cuanto=None):
        self.nivel = nivel  # Nivel de prioridad (1 es más alto)
        self.politica_planificacion = politica_planificacion  # 'RR', 'FCFS', 'SJF', 'STCF'
        self.tiempo_cuanto = tiempo_cuanto  # Solo para RR
        self.cola = deque()  # Para FCFS y RR
        self.heap = []  # Para SJF y STCF

    def agregar_proceso(self, proceso):
        if self.politica_planificacion == 'SJF':
            heapq.heappush(self.heap, (proceso.tiempo_burst, proceso.tiempo_llegada, proceso))
        elif self.politica_planificacion == 'STCF':
            heapq.heappush(self.heap, (proceso.tiempo_restante, proceso.tiempo_llegada, proceso))
        else:
            self.cola.append(proceso)

    def obtener_siguiente_proceso(self):
        if self.politica_planificacion == 'FCFS':
            if self.cola:
                return self.cola.popleft()
        elif self.politica_planificacion.startswith('RR'):
            if self.cola:
                return self.cola.popleft()
        elif self.politica_planificacion == 'SJF':
            if self.heap:
                return heapq.heappop(self.heap)[2]
        elif self.politica_planificacion == 'STCF':
            if self.heap:
                return heapq.heappop(self.heap)[2]
        return None

    def esta_vacia(self):
        if self.politica_planificacion in ['FCFS', 'RR']:
            return len(self.cola) == 0
        else:
            return len(self.heap) == 0

# Clase PlanificadorMLQ
class PlanificadorMLQ:
    def __init__(self):
        self.colas = []  # Lista de NivelCola ordenadas por prioridad
        self.procesos = []  # Lista de todos los procesos
        self.tiempo_actual = 0
        self.procesos_completados = []
        self.archivo_entrada = ""
        self.archivo_salida = ""

    def agregar_cola(self, nivel_cola):
        self.colas.append(nivel_cola)
        self.colas.sort(key=lambda q: q.nivel)  # Ordena por nivel de prioridad

    def asignar_proceso_a_cola(self, proceso):
        # Añade a la cola correspondiente según el nivel
        for cola in self.colas:
            if cola.nivel == proceso.cola:
                cola.agregar_proceso(proceso)
                break

    def leer_entrada(self, ruta_archivo):
        self.archivo_entrada = ruta_archivo
        try:
            with open(ruta_archivo, 'r') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea.startswith('#') or not linea:
                        continue  # Ignora comentarios y líneas vacías
                    partes = linea.split(';')
                    if len(partes) != 5:
                        continue  # Ignora líneas mal formateadas
                    etiqueta = partes[0].strip()
                    tiempo_burst = int(partes[1].strip())
                    tiempo_llegada = int(partes[2].strip())
                    cola = int(partes[3].strip())
                    prioridad = int(partes[4].strip())
                    proceso = Proceso(etiqueta, tiempo_burst, tiempo_llegada, cola, prioridad)
                    self.procesos.append(proceso)
        except FileNotFoundError:
            print(f"Error: El archivo '{ruta_archivo}' no fue encontrado.")
        except Exception as e:
            print(f"Error al leer el archivo de entrada: {e}")

    def escribir_salida(self, ruta_archivo):
        self.archivo_salida = ruta_archivo
        try:
            with open(ruta_archivo, 'w') as f:
                f.write(f"# archivo: {self.archivo_entrada}\n")
                f.write("# etiqueta; BT; AT; Q; Pr; WT; CT; RT; TAT\n")
                # Ordena procesos por etiqueta o cualquier otro criterio
                procesos_ordenados = sorted(self.procesos_completados, key=lambda p: p.etiqueta)
                total_wt = total_ct = total_rt = total_tat = 0
                for p in procesos_ordenados:
                    f.write(f"{p.etiqueta};{p.tiempo_burst};{p.tiempo_llegada};{p.cola};{p.prioridad};{p.tiempo_espera};{p.tiempo_completado};{p.tiempo_respuesta};{p.tiempo_turnaround}\n")
                    total_wt += p.tiempo_espera
                    total_ct += p.tiempo_completado
                    total_rt += p.tiempo_respuesta
                    total_tat += p.tiempo_turnaround
                n = len(procesos_ordenados)
                avg_wt = total_wt / n if n > 0 else 0
                avg_ct = total_ct / n if n > 0 else 0
                avg_rt = total_rt / n if n > 0 else 0
                avg_tat = total_tat / n if n > 0 else 0
                f.write(f"WT={avg_wt}; CT={avg_ct}; RT={avg_rt}; TAT={avg_tat};\n")
        except Exception as e:
            print(f"Error al escribir el archivo de salida: {e}")

    def obtener_cola_mayor_prioridad(self):
        for cola in self.colas:
            if not cola.esta_vacia():
                return cola
        return None

    def ejecutar_simulacion(self):
        # Ordena procesos por tiempo de llegada
        self.procesos.sort(key=lambda p: p.tiempo_llegada)
        while self.procesos or any(not cola.esta_vacia() for cola in self.colas):
            # Añade procesos que han llegado al sistema
            procesos_llegados = [p for p in self.procesos if p.tiempo_llegada <= self.tiempo_actual]
            for p in procesos_llegados:
                self.asignar_proceso_a_cola(p)
                self.procesos.remove(p)

            # Obtiene la cola de mayor prioridad que no esté vacía
            cola_actual = self.obtener_cola_mayor_prioridad()
            if cola_actual:
                proceso = cola_actual.obtener_siguiente_proceso()
                if proceso:
                    if proceso.tiempo_inicio is None:
                        proceso.tiempo_inicio = self.tiempo_actual
                        proceso.tiempo_respuesta = proceso.tiempo_inicio - proceso.tiempo_llegada
                        proceso.tiempo_espera = self.tiempo_actual - proceso.tiempo_llegada
                    # Ejecuta el proceso según la política de la cola
                    if cola_actual.politica_planificacion.startswith('RR'):
                        quantum = cola_actual.tiempo_cuanto
                        tiempo_ejecucion = min(quantum, proceso.tiempo_restante)
                        # Simula la ejecución
                        self.tiempo_actual += tiempo_ejecucion
                        proceso.tiempo_restante -= tiempo_ejecucion
                        # Añade procesos que llegan durante la ejecución
                        procesos_durante = [p for p in self.procesos if self.tiempo_actual - tiempo_ejecucion < p.tiempo_llegada <= self.tiempo_actual]
                        for p in procesos_durante:
                            self.asignar_proceso_a_cola(p)
                            self.procesos.remove(p)
                        if proceso.tiempo_restante > 0:
                            cola_actual.agregar_proceso(proceso)  # Reinserta en la cola
                        else:
                            proceso.tiempo_completado = self.tiempo_actual
                            proceso.tiempo_turnaround = proceso.tiempo_completado - proceso.tiempo_llegada
                            self.procesos_completados.append(proceso)
                    elif cola_actual.politica_planificacion == 'FCFS':
                        self.tiempo_actual += proceso.tiempo_restante
                        proceso.tiempo_restante = 0
                        proceso.tiempo_completado = self.tiempo_actual
                        proceso.tiempo_turnaround = proceso.tiempo_completado - proceso.tiempo_llegada
                        self.procesos_completados.append(proceso)
                    elif cola_actual.politica_planificacion == 'SJF':
                        self.tiempo_actual += proceso.tiempo_restante
                        proceso.tiempo_restante = 0
                        proceso.tiempo_completado = self.tiempo_actual
                        proceso.tiempo_turnaround = proceso.tiempo_completado - proceso.tiempo_llegada
                        self.procesos_completados.append(proceso)
                    elif cola_actual.politica_planificacion == 'STCF':
                        # busca el proceso con menor tiempo_restante
                        # Simplificación: Ejecutar hasta que llegue un nuevo proceso que pueda preemptar
                        if self.procesos:
                            proximo_llegada = min(self.procesos, key=lambda p: p.tiempo_llegada).tiempo_llegada
                            tiempo_hasta_proximo = proximo_llegada - self.tiempo_actual
                            tiempo_ejecucion = min(proceso.tiempo_restante, tiempo_hasta_proximo)
                        else:
                            tiempo_ejecucion = proceso.tiempo_restante
                        tiempo_ejecucion = max(1, tiempo_ejecucion)  # Al menos 1 unidad de tiempo
                        self.tiempo_actual += tiempo_ejecucion
                        proceso.tiempo_restante -= tiempo_ejecucion
                        # Añade procesos que llegan durante la ejecución
                        procesos_durante = [p for p in self.procesos if self.tiempo_actual - tiempo_ejecucion < p.tiempo_llegada <= self.tiempo_actual]
                        for p in procesos_durante:
                            self.asignar_proceso_a_cola(p)
                            self.procesos.remove(p)
                        if proceso.tiempo_restante > 0:
                            cola_actual.agregar_proceso(proceso)  # Reinserta en la cola
                        else:
                            proceso.tiempo_completado = self.tiempo_actual
                            proceso.tiempo_turnaround = proceso.tiempo_completado - proceso.tiempo_llegada
                            self.procesos_completados.append(proceso)
            else:
                # No hay procesos listos para ejecutar; avanzar el tiempo
                self.tiempo_actual += 1

# Función para imprimir procesos completados
def imprimir_procesos_completados(planificador):
    for p in sorted(planificador.procesos_completados, key=lambda p: p.etiqueta):
        print(f"{p.etiqueta}: WT={p.tiempo_espera}, CT={p.tiempo_completado}, RT={p.tiempo_respuesta}, TAT={p.tiempo_turnaround}")


if __name__ == "__main__":
    planificador = PlanificadorMLQ()
    
    # Definir las colas según los esquemas proporcionados
    # Ejemplo con RR(2), RR(3), STCF
    planificador.agregar_cola(NivelCola(nivel=1, politica_planificacion='RR', tiempo_cuanto=2))
    planificador.agregar_cola(NivelCola(nivel=2, politica_planificacion='RR', tiempo_cuanto=3))
    planificador.agregar_cola(NivelCola(nivel=3, politica_planificacion='STCF'))
    
    # Lee los procesos desde un archivo de entrada
    planificador.leer_entrada('mlq002.txt') 
    
    # Ejecuta la simulación
    planificador.ejecutar_simulacion()
    
    # Muestra resultados en la consola 
    imprimir_procesos_completados(planificador)
    
    # Escribe los resultados en un archivo de salida
    planificador.escribir_salida('mlq002_salida.txt')


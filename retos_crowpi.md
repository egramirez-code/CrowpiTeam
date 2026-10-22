# BANCO DE RETOS DE INTEGRACIÓN — CrowPi

## Cómo usar este banco

1. Lee el **enunciado** y los **dispositivos** implicados.
2. Aplica el **método de 5 pasos**:
   1. Identificar entradas y salidas.
   2. Buscar la interfaz de cada una (GPIO / I2C / SPI).
   3. Instanciar cada dispositivo con su pin/dirección.
   4. Escribir la lógica de conexión.
   5. Envolver en el esqueleto universal (while + try/except + limpieza).
3. Consulta solo la tabla de API (`API_dispositivos_imprimir.md`) si lo necesitas.
4. Compara con `soluciones/reto_XX_*.py` al terminar.

**Orden ascendente:** Nivel 1 (2 dispositivos) → Nivel 5 (menús y estado).

## Referencia rápida de dispositivos

| Dispositivo | Pin / Dirección |
|-------------|-----------------|
| LED | GPIO 20 |
| Buzzer | GPIO 18 |
| Relé | GPIO 21 |
| Vibrador | GPIO 27 |
| Ventilador | GPIO 26 |
| Botón | GPIO 11 |
| Toque | GPIO 17 |
| Movimiento (PIR) | GPIO 23 |
| Inclinación | GPIO 22 |
| Sonido | GPIO 24 |
| Servo | GPIO 25 |
| Ultrasonido | echo 12 / trigger 16 |
| Stepper | GPIO 5, 6, 13, 19 |
| Matriz de botones | filas 27,22,5,6 / cols 25,26,19,13 |
| DHT20 | I2C 0x38 |
| LCD 16x2 | I2C 0x21 (vía MCP23008) |
| Sensor de luz | I2C 0x5c |
| Display 7 segmentos | I2C (HT16K33) |
| Matriz LED | SPI |

> **Ojo con los pines compartidos.** La matriz de botones usa 27, 22, 5, 6, 25, 19, 13,
> que chocan con vibrador (27), inclinación (22), servo (25) y stepper (5,6,13,19).
> En los retos que usan la matriz de botones, NO uses esos dispositivos a la vez.

---

# NIVEL 1 — Integración básica (2 dispositivos)

## Reto 01 — Botón que enciende el LED
**Objetivo:** leer una entrada digital y accionar una salida.
**Dispositivos:** Botón (11) → LED (20).
**Comportamiento esperado:** mientras el botón está presionado, el LED está encendido; al soltarlo, apagado.
**Pista:** usa `button.is_pressed` dentro del `while True`.
**Criterio de éxito:** el LED sigue exactamente el estado del botón.
**Solución:** `soluciones/reto_01_boton_led.py`

## Reto 02 — Botón que hace sonar el buzzer
**Objetivo:** sustituir la salida del reto anterior por otra.
**Dispositivos:** Botón (11) → Buzzer (18).
**Comportamiento esperado:** al pulsar, suena; al soltar, se calla.
**Pista:** es el ejemplo del manual, pero no lo memorices: aplica el mismo patrón entrada→salida.
**Criterio de éxito:** el buzzer suena solo mientras se pulsa.
**Solución:** `soluciones/reto_02_boton_buzzer.py`

## Reto 03 — Toque que activa el relé
**Objetivo:** entrada táctil con salida de potencia temporizada.
**Dispositivos:** Toque (17) → Relé (21).
**Comportamiento esperado:** al tocar, el relé se activa y se oye un clic; permanece activo 1 segundo y se desactiva.
**Pista:** detecta el toque y usa `time.sleep(1)` antes de apagar.
**Criterio de éxito:** cada toque produce un pulso de relé de ~1 s.
**Solución:** `soluciones/reto_03_toque_rele.py`

## Reto 04 — Movimiento que enciende el LED
**Objetivo:** entrada de presencia con salida visual.
**Dispositivos:** Movimiento (23) → LED (20).
**Comportamiento esperado:** al detectar movimiento, el LED se enciende; se apaga cuando no hay movimiento.
**Pista:** `motion.value == 1` indica movimiento detectado.
**Criterio de éxito:** el LED refleja el estado del PIR.
**Solución:** `soluciones/reto_04_movimiento_led.py`

---

# NIVEL 2 — Lógica con umbral

## Reto 05 — Alarma de proximidad con LED
**Objetivo:** convertir una medida continua (distancia) en una decisión (umbral).
**Dispositivos:** Ultrasonido (12/16) → LED (20).
**Comportamiento esperado:** si la distancia es menor a 20 cm, el LED se enciende; si no, se apaga.
**Pista:** `distance` viene en metros, multiplica por 100 para cm.
**Criterio de éxito:** el LED cambia justo al cruzar los 20 cm.
**Solución:** `soluciones/reto_05_ultrasonido_led.py`

## Reto 06 — Detector de ruido con vibración
**Objetivo:** entrada de sonido con salida táctil temporizada.
**Dispositivos:** Sonido (24) → Vibrador (27).
**Comportamiento esperado:** al detectar un sonido, vibra 0.5 s.
**Pista:** en el sensor de sonido, `value == 0` significa sonido detectado.
**Criterio de éxito:** cada palmada produce una vibración breve.
**Solución:** `soluciones/reto_06_sonido_vibrador.py`

## Reto 07 — Aviso de inclinación con pitido
**Objetivo:** detectar un cambio de estado (inclinación) y avisar.
**Dispositivos:** Inclinación (22) → Buzzer (18).
**Comportamiento esperado:** al inclinar el sensor, suena un pitido corto (una sola vez por inclinación).
**Pista:** guarda el estado anterior y actúa solo cuando cambie.
**Criterio de éxito:** no suena en bucle mientras está inclinado.
**Solución:** `soluciones/reto_07_inclinacion_buzzer.py`

## Reto 08 — Luz de emergencia automática
**Objetivo:** usar un sensor I2C analógico con umbral.
**Dispositivos:** Sensor de luz (0x5c) → LED (20).
**Comportamiento esperado:** si el nivel de luz baja de 50 lx, el LED se enciende; si sube, se apaga.
**Pista:** lee con `bus.read_i2c_block_data(0x5c, 0x20)` y convierte con `(d[1]+256*d[0])/1.2`.
**Criterio de éxito:** tapar el sensor enciende el LED.
**Solución:** `soluciones/reto_08_luz_led.py`

---

# NIVEL 3 — Con pantalla (I2C)

## Reto 09 — Termómetro en el LCD
**Objetivo:** mostrar una medida del DHT20 en pantalla.
**Dispositivos:** DHT20 (0x38) → LCD 16x2 (0x21).
**Comportamiento esperado:** línea 1: `Temp: XX.X C`; línea 2: `Hum: XX.X %`, actualizado cada 2 s.
**Pista:** inicializa el MCP23008 en 0x21 y luego `HD44780MCP.HD44780(...)`.
**Criterio de éxito:** el LCD muestra ambos valores y se refresca.
**Solución:** `soluciones/reto_09_dht20_lcd.py`

## Reto 10 — Temperatura en el display de 7 segmentos
**Objetivo:** mostrar un número del DHT20 en un display numérico.
**Dispositivos:** DHT20 (0x38) → 7 segmentos (HT16K33).
**Comportamiento esperado:** muestra la temperatura entera (p. ej. `0024`) cada 2 s.
**Pista:** `set_number(digito, posicion)` y `update()` al final de cada refresco.
**Criterio de éxito:** el número en pantalla coincide con la temperatura.
**Solución:** `soluciones/reto_10_dht20_segmentos.py`

## Reto 11 — Luxómetro en el LCD
**Objetivo:** combinar un sensor I2C con pantalla.
**Dispositivos:** Luz (0x5c) → LCD (0x21).
**Comportamiento esperado:** muestra `Luz: XXX lx` y una etiqueta (`OSCURO`/`MEDIO`/`CLARO`) según el valor.
**Pista:** define tus propios rangos para las etiquetas.
**Criterio de éxito:** la etiqueta cambia al tapar el sensor.
**Solución:** `soluciones/reto_11_luz_lcd.py`

## Reto 12 — Medidor de distancia en 7 segmentos
**Objetivo:** convertir una medida continua en display numérico.
**Dispositivos:** Ultrasonido (12/16) → 7 segmentos.
**Comportamiento esperado:** muestra la distancia en cm (entero) actualizada ~4 veces por segundo.
**Pista:** redondea `distance * 100` a entero antes de escribir los dígitos.
**Criterio de éxito:** el número sigue el movimiento de la mano.
**Solución:** `soluciones/reto_12_ultrasonido_segmentos.py`

---

# NIVEL 4 — Integración multivariable (3+ actuadores)

## Reto 13 — Sistema de alarma
**Objetivo:** reaccionar a un evento con varios actuadores a la vez.
**Dispositivos:** Inclinación (22) → Matriz LED (SPI) + Buzzer (18) + LCD (0x21).
**Comportamiento esperado:** al inclinar, mensaje `ALERTA` en la matriz, pitido del buzzer y `ALERTA!` en el LCD.
**Pista:** reutiliza las funciones de inicialización de matriz y LCD; muestra el mensaje en un hilo para no bloquear.
**Criterio de éxito:** los 3 avisos se activan juntos con una inclinación.
**Solución:** `soluciones/reto_13_alarma.py`

## Reto 14 — Clima inteligente
**Objetivo:** control automático + información al usuario.
**Dispositivos:** DHT20 (0x38) → Ventilador (26) o Relé (21) + LCD (0x21) + Matriz LED (SPI).
**Comportamiento esperado:** si `temp >= 28 C`, ventilador encendido y mensaje `CALOR`; si no, apagado y mensaje normal. El LCD siempre muestra temp/humedad.
**Pista:** es una versión propia del ejemplo `Tem_matrix.py`; no lo copies, reconstrúyelo por pasos.
**Criterio de éxito:** el ventilador se activa solo al superar el umbral.
**Solución:** `soluciones/reto_14_clima_inteligente.py`

## Reto 15 — Sensor de estacionamiento
**Objetivo:** combinar medida + aviso proporcional.
**Dispositivos:** Ultrasonido (12/16) → 7 segmentos + Buzzer (18) + LED (20).
**Comportamiento esperado:** el 7 seg muestra los cm; cuanto más cerca, el buzzer pita más rápido; a menos de 10 cm el LED se enciende fijo.
**Pista:** usa el valor de distancia para elegir el `sleep` entre pitidos (a menor distancia, menor pausa).
**Criterio de éxito:** la frecuencia del pitido aumenta al acercarse.
**Solución:** `soluciones/reto_15_estacionamiento.py`

## Reto 16 — Contador de eventos en 7 segmentos
**Objetivo:** mantener estado acumulado y reaccionar a un umbral.
**Dispositivos:** Movimiento (23) → 7 segmentos + Matriz LED (SPI).
**Comportamiento esperado:** cada detección nueva suma 1; el 7 seg muestra el total. Al llegar a 10, la matriz muestra `LLENO`.
**Pista:** cuenta solo en el flanco (cuando pasa de sin-movimiento a movimiento).
**Criterio de éxito:** el contador no salta varias veces por una sola persona.
**Solución:** `soluciones/reto_16_contador_eventos.py`

---

# NIVEL 5 — Avanzado (menús y máquinas de estado)

## Reto 17 — Menú con la matriz de botones
**Objetivo:** usar el teclado 4x4 como interfaz de navegación.
**Dispositivos:** Matriz de botones → LCD (0x21) + DHT20 + Luz.
**Comportamiento esperado:** las teclas 1/2/3 seleccionan qué se muestra en el LCD (1=temperatura, 2=humedad, 3=luz); el LCD refleja la vista activa.
**Pista:** separa el escaneo de teclas de la actualización de pantalla; recuerda que la matriz de botones ocupa pines de otros sensores.
**Criterio de éxito:** cambiar de tecla cambia la vista del LCD.
**Solución:** `soluciones/reto_17_menu_botones.py`

## Reto 18 — Estación meteorológica con menú y alarma
**Objetivo:** prueba final: estado, menú, varias salidas y umbral.
**Dispositivos:** Matriz de botones → LCD (0x21) + DHT20 + Luz + Buzzer (18) + Matriz LED (SPI).
**Comportamiento esperado:**
- El menú cicla entre vistas con las teclas 1/2/3 (temp, humedad, luz).
- El LCD muestra la vista activa.
- Si `temp >= 30 C`, el buzzer emite un aviso periódico y la matriz LED muestra `ALERTA`.
- La tecla 4 silencia/reactiva la alarma.
**Pista:** modela el sistema como estados (vista actual + alarma activa/silenciada) y un solo bucle que haga: leer entradas → decidir → mostrar.
**Criterio de éxito:** menú funcional + alarma que respeta el silenciador.
**Solución:** `soluciones/reto_18_estacion_meteorologica.py`

---

## Progresión de dificultad (resumen)

| Nivel | Retos | Habilidad que entrena |
|-------|-------|-----------------------|
| 1 | 01–04 | entrada → salida directa |
| 2 | 05–08 | umbrales y flancos |
| 3 | 09–12 | sensores/actuadores I2C y pantallas |
| 4 | 13–16 | varios actuadores y estado acumulado |
| 5 | 17–18 | menús, máquinas de estado, multitarea |

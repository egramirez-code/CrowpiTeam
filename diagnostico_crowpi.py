#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================
 DIAGNOSTICO COMPLETO CrowPi  --  Sensores y Actuadores
============================================================

QUE ES
  Script interactivo que comprueba, uno a uno, TODOS los
  sensores (entradas) y actuadores (salidas) de la placa CrowPi.
  Sirve a la vez como:
    - GUIA DE PASOS: imprime que hacer y que esperar en cada prueba.
    - METODO: aisla cada dispositivo (evita conflictos de pines).
    - CODIGO: reutiliza la API minima de los ejemplos.

COMO EJECUTAR
  1. Copia este archivo a la CrowPi (junto a la carpeta examples/).
  2. Abre una terminal y ejecuta:
         sudo python3 diagnostico_crowpi.py
     (sudo porque gpiozero / I2C / SPI lo requieren)
  3. Elige del menu el dispositivo a probar, o "A" para probar TODO.

REQUISITOS PREVIOS
  - Habilitar I2C y SPI:   sudo raspi-config
        Interface Options -> I2C -> Enable
        Interface Options -> SPI -> Enable
  - Librerias (segun dispositivos):
        gpiozero, smbus,
        DFRobot_DHT20, MCP230XX, HD44780MCP,
        ht16k33segment_python, luma.led_matrix

ORDEN RECOMENDADO DE PRUEBAS
  1) Salidas simples   : LED, buzzer, rele, vibrador
  2) Entradas simples  : boton, toque, movimiento, inclinacion, sonido, IR
  3) Bus I2C           : DHT20, luz, LCD, 7 segmentos
  4) Bus SPI           : matriz LED
  5) Especiales        : servo, ultrasonido, stepper, matriz de botones

NOTA SOBRE PINES COMPARTIDOS
  Algunos dispositivos reutilizan los mismos GPIO (la matriz de
  botones usa 27,22,5,6 / 25,26,19,13). Por eso cada prueba se
  ejecuta de forma AISLADA y libera sus pines al terminar.
"""

import sys
import time

# ------------------------------------------------------------------
# CONFIGURACION CENTRAL (una sola fuente de verdad para pines)
# ------------------------------------------------------------------
PINES = {
    "led":        20,
    "buzzer":     18,
    "rele":       21,
    "vibrador":   27,
    "boton":      26,
    "toque":      17,
    "movimiento": 23,
    "inclinacion": 22,
    "sonido":     24,
    "ir":         20,          # ojo: comparte pin con LED en los ejemplos
    "servo":      25,
    "ultra_echo": 12,
    "ultra_trig": 16,
    "stepper":    [5, 6, 13, 19],
    "matriz_filas": [27, 22, 5, 6],
    "matriz_cols":  [25, 26, 19, 13],
}

DIRS_I2C = {
    "dht20": 0x38,
    "lcd_mcp": 0x21,
    "luz": 0x5c,
}

TIEMPO_ESPERA = 10   # segundos para que el usuario active un sensor

# Resultados acumulados de todas las pruebas
RESULTADOS = {}


# ------------------------------------------------------------------
# UTILIDADES
# ------------------------------------------------------------------
def banner(titulo):
    print("\n" + "=" * 60)
    print("  " + titulo)
    print("=" * 60)


def instruccion(texto):
    print("  INSTRUCCION: " + texto)


def esperado(texto):
    print("  ESPERADO   : " + texto)


def preguntar(mensaje):
    """Pregunta si/no y devuelve True/False."""
    while True:
        r = input("  " + mensaje + " [s/n]: ").strip().lower()
        if r in ("s", "si", "sí", "y", "yes"):
            return True
        if r in ("n", "no"):
            return False
        print("  Responde 's' o 'n'.")


def esperar_evento(descripcion, detectar, timeout=TIEMPO_ESPERA, intervalo=0.05):
    """
    Espera a que 'detectar()' devuelva True durante 'timeout' segundos.
    Se usa para los SENSORES: el usuario debe activar el sensor.
    """
    print("  -> " + descripcion + " (tienes %d s)" % timeout)
    t0 = time.time()
    while (time.time() - t0) < timeout:
        if detectar():
            print("  [OK] Senal detectada.")
            return True
        time.sleep(intervalo)
    print("  [X]  No se detecto nada en el tiempo dado.")
    return False


def registrar(nombre, ok):
    RESULTADOS[nombre] = ok
    print("  >>> Resultado '%s': %s" % (nombre, "PASA" if ok else "FALLA"))


def limpiar(*dispositivos):
    """Cierra/libera dispositivos de forma segura."""
    for d in dispositivos:
        try:
            d.close()
        except Exception:
            pass


# ------------------------------------------------------------------
# 1. SALIDAS DIGITALES SIMPLES
# ------------------------------------------------------------------
def prueba_led():
    from gpiozero import LED
    pin = PINES["led"]
    led = LED(pin)
    banner("PRUEBA: LED (GPIO %d)" % pin)
    instruccion("Observa el LED conectado al pin %d." % pin)
    esperado("El LED debe parpadear 5 veces (encendido/apagado).")
    try:
        for _ in range(5):
            led.on(); time.sleep(0.3)
            led.off(); time.sleep(0.3)
    finally:
        limpiar(led)
    ok = preguntar("¿Parpadeo el LED?")
    registrar("LED", ok)


def prueba_buzzer():
    from gpiozero import Buzzer
    pin = PINES["buzzer"]
    bz = Buzzer(pin)
    banner("PRUEBA: BUZZER (GPIO %d)" % pin)
    instruccion("Escucha el zumbador.")
    esperado("Debe sonar un pitido corto.")
    try:
        bz.on(); time.sleep(0.5); bz.off()
    finally:
        limpiar(bz)
    ok = preguntar("¿Sonó el buzzer?")
    registrar("Buzzer", ok)


def prueba_rele():
    from gpiozero import OutputDevice as Relay
    pin = PINES["rele"]
    rel = Relay(pin)
    banner("PRUEBA: RELE (GPIO %d)" % pin)
    instruccion("Escucha el rele (hace un 'clic' caracteristico).")
    esperado("Se oyen 2 clics: al activar y al desactivar.")
    try:
        rel.on(); time.sleep(0.5)
        rel.off(); time.sleep(0.5)
        rel.on(); time.sleep(0.5)
        rel.off()
    finally:
        limpiar(rel)
    ok = preguntar("¿Se oyeron los clics del rele?")
    registrar("Rele", ok)


def prueba_vibrador():
    from gpiozero import OutputDevice as Vibration
    pin = PINES["vibrador"]
    vib = Vibration(pin)
    banner("PRUEBA: VIBRADOR (GPIO %d)" % pin)
    instruccion("Toca el motor de vibracion.")
    esperado("Debe vibrar durante 1 segundo.")
    try:
        vib.on(); time.sleep(1.0); vib.off()
    finally:
        limpiar(vib)
    ok = preguntar("¿Vibro el motor?")
    registrar("Vibrador", ok)


# ------------------------------------------------------------------
# 2. ENTRADAS DIGITALES
# ------------------------------------------------------------------
def prueba_boton():
    from gpiozero import Button
    pin = PINES["boton"]
    btn = Button(pin)
    banner("PRUEBA: BOTON (GPIO %d)" % pin)
    instruccion("Presiona el boton ahora.")
    esperado("El script detecta la pulsacion.")
    try:
        ok = esperar_evento("Presiona el boton...", lambda: btn.is_pressed)
    finally:
        limpiar(btn)
    registrar("Boton", ok)


def prueba_toque():
    from gpiozero import DigitalInputDevice as Touch
    pin = PINES["toque"]
    t = Touch(pin)
    banner("PRUEBA: SENSOR DE TOQUE (GPIO %d)" % pin)
    instruccion("Toca la superficie metalica del sensor.")
    esperado("Se detecta el toque.")
    try:
        ok = esperar_evento("Toca el sensor...", lambda: bool(t.value))
    finally:
        limpiar(t)
    registrar("Toque", ok)


def prueba_movimiento():
    from gpiozero import DigitalInputDevice as Motion
    pin = PINES["movimiento"]
    m = Motion(pin)
    banner("PRUEBA: SENSOR DE MOVIMIENTO (GPIO %d)" % pin)
    instruccion("Mueve la mano frente al sensor PIR.")
    esperado("Se detecta el movimiento (value == 1).")
    try:
        ok = esperar_evento("Agita la mano frente al PIR...", lambda: m.value == 1)
    finally:
        limpiar(m)
    registrar("Movimiento", ok)


def prueba_inclinacion():
    from gpiozero import DigitalInputDevice as Tilt
    pin = PINES["inclinacion"]
    t = Tilt(pin)
    banner("PRUEBA: SENSOR DE INCLINACION (GPIO %d)" % pin)
    instruccion("Inclina el sensor hacia un lado y luego al otro.")
    esperado("El valor cambia entre inclinacion izquierda/derecha.")
    valor_inicial = t.value
    try:
        ok = esperar_evento(
            "Inclina el sensor (estado inicial=%s)..." % valor_inicial,
            lambda: t.value != valor_inicial,
        )
    finally:
        limpiar(t)
    registrar("Inclinacion", ok)


def prueba_sonido():
    from gpiozero import DigitalInputDevice as Sound
    pin = PINES["sonido"]
    s = Sound(pin)
    banner("PRUEBA: SENSOR DE SONIDO (GPIO %d)" % pin)
    instruccion("Haz un ruido fuerte (palmada) cerca del microfono.")
    esperado("Se detecta el sonido (value == 0).")
    try:
        ok = esperar_evento("Da una palmada...", lambda: s.value == 0)
    finally:
        limpiar(s)
    registrar("Sonido", ok)


def prueba_ir():
    from gpiozero import DigitalInputDevice as IR
    pin = PINES["ir"]
    ir = IR(pin)
    banner("PRUEBA: RECEPTOR INFRARROJO (GPIO %d)" % pin)
    instruccion("Apunta un mando IR al receptor y pulsa cualquier tecla.")
    esperado("Se detecta una senal IR (value == 0).")
    print("  (La decodificacion completa de teclas esta en examples/IR.py)")
    try:
        ok = esperar_evento("Pulsa una tecla del mando IR...", lambda: ir.value == 0)
    finally:
        limpiar(ir)
    registrar("IR", ok)


# ------------------------------------------------------------------
# 3. BUS I2C
# ------------------------------------------------------------------
def prueba_dht20():
    banner("PRUEBA: DHT20 temperatura/humedad (I2C 0x%02X)" % DIRS_I2C["dht20"])
    try:
        from DFRobot_DHT20 import DFRobot_DHT20
    except ImportError:
        print("  [X] Falta la libreria DFRobot_DHT20. Omite esta prueba.")
        registrar("DHT20", False)
        return
    dht = DFRobot_DHT20(0x01, DIRS_I2C["dht20"])
    instruccion("No hay que hacer nada: se leen 3 muestras.")
    esperado("Temperatura entre -10 y 60 C y humedad entre 0 y 100 %.")
    ok = False
    try:
        if not dht.begin():
            print("  [X] DHT20 no inicializo (revisa I2C habilitado / direccion).")
        else:
            for i in range(3):
                t, h, crc = dht.get_temperature_and_humidity()
                print("   Muestra %d -> %.2f C  |  %.2f %%  | CRC %s"
                      % (i + 1, t, h, "OK" if not crc else "ERROR"))
                if (-10 < t < 60) and (0 <= h <= 100) and not crc:
                    ok = True
                time.sleep(1)
    finally:
        limpiar(dht)
    registrar("DHT20", ok)


def prueba_luz():
    import smbus
    addr = DIRS_I2C["luz"]
    bus = smbus.SMBus(1)
    banner("PRUEBA: SENSOR DE LUZ BH1750 (I2C 0x%02X)" % addr)
    instruccion("Tapa y destapa el sensor con la mano varias veces.")
    esperado("El valor en lux cambia al tapar/destapar.")
    ONE_TIME_HIGH_RES_MODE_1 = 0x20
    valores = []
    try:
        for _ in range(10):
            d = bus.read_i2c_block_data(addr, ONE_TIME_HIGH_RES_MODE_1)
            lux = (d[1] + (256 * d[0])) / 1.2
            valores.append(lux)
            print("   Lux: %.1f" % lux)
            time.sleep(0.5)
    finally:
        bus.close()
    variacion = max(valores) - min(valores)
    ok = variacion > 5
    print("  Variacion detectada: %.1f lux" % variacion)
    registrar("Luz", ok)


def prueba_lcd():
    banner("PRUEBA: LCD 16x2 (I2C 0x%02X via MCP)" % DIRS_I2C["lcd_mcp"])
    try:
        import MCP230XX
        import HD44780MCP
    except ImportError:
        print("  [X] Faltan librerias MCP230XX / HD44780MCP. Omite esta prueba.")
        registrar("LCD", False)
        return
    mcp = None
    instruccion("Mira la pantalla LCD.")
    esperado("Muestra 'CrowPi OK' en la linea 1 y 'Diagnostico' en la linea 2.")
    try:
        mcp = MCP230XX.MCP230XX("MCP23008", DIRS_I2C["lcd_mcp"])
        blPin = 7
        mcp.set_mode(blPin, "output")
        mcp.output(blPin, True)
        lcd = HD44780MCP.HD44780(mcp, 1, -1, 2, [3, 4, 5, 6],
                                 rows=2, characters=16, mode=0, font=0)
        lcd.clear_display()
        lcd.display_string("CrowPi OK")
        lcd.set_cursor(2, 1)
        lcd.display_string("Diagnostico")
        time.sleep(3)
        lcd.clear_display()
    finally:
        if mcp is not None:
            try:
                mcp.output(7, False)
            except Exception:
                pass
    ok = preguntar("¿Se vieron los dos textos en el LCD?")
    registrar("LCD", ok)


def prueba_segmentos():
    import smbus
    banner("PRUEBA: DISPLAY 7 SEGMENTOS (HT16K33, I2C)")
    try:
        from ht16k33segment_python import HT16K33Segment
    except ImportError:
        print("  [X] Falta la libreria ht16k33segment_python. Omite esta prueba.")
        registrar("7 segmentos", False)
        return
    instruccion("Mira el display de 4 digitos.")
    esperado("Cuenta del 0 al 9 en el ultimo digito.")
    i2c = smbus.SMBus(1)
    disp = HT16K33Segment(i2c)
    try:
        disp.set_brightness(15)
        disp.clear()
        disp.update()
        for n in range(10):
            disp.clear()
            disp.set_number(n, 3)
            disp.update()
            time.sleep(0.4)
        disp.clear()
        disp.update()
    finally:
        i2c.close()
    ok = preguntar("¿Conto del 0 al 9?")
    registrar("7 segmentos", ok)


# ------------------------------------------------------------------
# 4. BUS SPI
# ------------------------------------------------------------------
def prueba_matriz_led():
    banner("PRUEBA: MATRIZ LED MAX7219 (SPI)")
    try:
        from luma.led_matrix.device import max7219
        from luma.core.interface.serial import spi, noop
        from luma.core.legacy import show_message
        from luma.core.legacy.font import proportional, CP437_FONT
    except ImportError:
        print("  [X] Falta la libreria luma.led_matrix. Omite esta prueba.")
        registrar("Matriz LED", False)
        return
    instruccion("Mira la matriz LED de 8x32.")
    esperado("Aparece el mensaje 'TEST OK' desplazandose.")
    serial = spi(port=0, device=0, gpio=noop())
    matrix = max7219(serial, width=32, height=8, block_orientation=-90)
    try:
        matrix.clear()
        show_message(matrix, "TEST OK", fill="white",
                     font=proportional(CP437_FONT), scroll_delay=0.1)
        time.sleep(1)
        matrix.clear()
    finally:
        try:
            matrix.clear()
        except Exception:
            pass
    ok = preguntar("¿Se vio el mensaje en la matriz LED?")
    registrar("Matriz LED", ok)


# ------------------------------------------------------------------
# 5. DISPOSITIVOS ESPECIALES
# ------------------------------------------------------------------
def prueba_servo():
    from gpiozero import Servo
    pin = PINES["servo"]
    s = Servo(pin)
    banner("PRUEBA: SERVO (GPIO %d)" % pin)
    instruccion("Observa el brazo del servo.")
    esperado("Va a minimo, medio y maximo, con pausas.")
    try:
        s.min(); time.sleep(1)
        s.mid(); time.sleep(1)
        s.max(); time.sleep(1)
        s.mid()
    finally:
        limpiar(s)
    ok = preguntar("¿Se movio el servo en 3 posiciones?")
    registrar("Servo", ok)


def prueba_ultrasonido():
    from gpiozero import DistanceSensor
    banner("PRUEBA: ULTRASONIDO (echo=%d, trigger=%d)"
            % (PINES["ultra_echo"], PINES["ultra_trig"]))
    d = DistanceSensor(echo=PINES["ultra_echo"],
                       trigger=PINES["ultra_trig"], max_distance=5)
    instruccion("Acerca y aleja la mano frente al sensor.")
    esperado("La distancia en cm cambia segun muevas la mano.")
    lecturas = []
    try:
        for _ in range(15):
            cm = d.distance * 100
            lecturas.append(cm)
            print("   Distancia: %.1f cm" % cm)
            time.sleep(0.3)
    finally:
        limpiar(d)
    variacion = max(lecturas) - min(lecturas)
    ok = variacion > 3
    print("  Variacion detectada: %.1f cm" % variacion)
    registrar("Ultrasonido", ok)


def prueba_stepper():
    from gpiozero import OutputDevice
    pins = PINES["stepper"]
    banner("PRUEBA: MOTOR PASO A PASO (GPIO %s)" % pins)
    instruccion("Observa el eje del motor.")
    esperado("Gira en un sentido y luego en el contrario.")
    pA = OutputDevice(pins[0])
    pB = OutputDevice(pins[1])
    pC = OutputDevice(pins[2])
    pD = OutputDevice(pins[3])
    seq = [
        (pD,), (pD, pC), (pC,), (pB, pC),
        (pB,), (pA, pB), (pA,), (pA, pD),
    ]
    interval = 0.010

    def girar(pasos, orden):
        for _ in range(pasos):
            for grupo in orden:
                for p in grupo:
                    p.on()
                time.sleep(interval)
                for p in grupo:
                    p.off()

    try:
        girar(20, seq)                 # adelante
        time.sleep(0.3)
        girar(20, list(reversed(seq)))  # atras
    finally:
        limpiar(pA, pB, pC, pD)
    ok = preguntar("¿Giro el motor en ambos sentidos?")
    registrar("Stepper", ok)


def prueba_matriz_botones():
    from gpiozero import Button, LED
    from time import sleep
    banner("PRUEBA: MATRIZ DE BOTONES 4x4")
    row_pins = PINES["matriz_filas"]
    col_pins = PINES["matriz_cols"]
    key_map = [
        ["1", "2", "3", "4"],
        ["5", "6", "7", "8"],
        ["9", "10", "11", "12"],
        ["13", "14", "15", "16"],
    ]
    print("  Filas (entradas): %s" % row_pins)
    print("  Columnas (salidas): %s" % col_pins)
    rows = [Button(p, pull_up=True) for p in row_pins]
    cols = [LED(p) for p in col_pins]
    instruccion("Pulsa varias teclas de la matriz (tienes %d s)." % TIEMPO_ESPERA)
    esperado("Cada tecla pulsada se imprime al detectarse.")
    detectadas = set()
    t0 = time.time()
    try:
        # Estado en reposo: si una fila ya aparece activa sin pulsar,
        # suele indicar pin en conflicto (vibrador=27, inclinacion=22, etc.)
        reposo = [r.is_active for r in rows]
        print("  Filas en reposo (se espera [False, False, False, False]): %s" % reposo)
        print("  Escaneando...")

        sig_aviso = 2.0
        while (time.time() - t0) < TIEMPO_ESPERA:
            for col in cols:
                col.off()
                sleep(0.001)          # deja asentar la senal de la columna
                for row in rows:
                    if row.is_active:
                        # espera con LIMITE de tiempo (evita cuelgue si el pin
                        # se queda activo por conflicto o rebote)
                        t_press = time.time()
                        while row.is_active and (time.time() - t_press) < 2:
                            sleep(0.02)
                        tecla = key_map[rows.index(row)][cols.index(col)]
                        detectadas.add(tecla)
                        print("   Tecla presionada: %s" % tecla)
                        break
                col.on()

            # aviso periodico: evita que parezca que el programa se colgo
            transcurrido = time.time() - t0
            if transcurrido >= sig_aviso:
                print("   ... escaneando, quedan %.0f s" % (TIEMPO_ESPERA - transcurrido))
                sig_aviso += 2
            sleep(0.05)
    finally:
        for r in rows:
            r.close()
        for c in cols:
            c.close()
    ok = len(detectadas) >= 1
    print("  Teclas detectadas: %s" % (", ".join(sorted(detectadas)) if detectadas else "ninguna"))
    if not ok:
        print("  SUGERENCIAS si no se detecto nada:")
        print("    - Pulsa las teclas JUSTO durante los %d s de escaneo." % TIEMPO_ESPERA)
        print("    - Revisa pines en conflicto (vibrador=27, inclinacion=22,")
        print("      servo=25, stepper=5,6,13,19) y que no haya otra prueba activa.")
        print("    - Ejecuta con 'sudo'.")
    registrar("Matriz botones", ok)


# ------------------------------------------------------------------
# REGISTRO DE PRUEBAS Y MENU
# ------------------------------------------------------------------
# (grupo, etiqueta menu, funcion)
PRUEBAS = [
    ("SALIDAS SIMPLES",   "LED",              prueba_led),
    ("SALIDAS SIMPLES",   "Buzzer",           prueba_buzzer),
    ("SALIDAS SIMPLES",   "Rele",             prueba_rele),
    ("SALIDAS SIMPLES",   "Vibrador",         prueba_vibrador),
    ("ENTRADAS",          "Boton",            prueba_boton),
    ("ENTRADAS",          "Toque",            prueba_toque),
    ("ENTRADAS",          "Movimiento",       prueba_movimiento),
    ("ENTRADAS",          "Inclinacion",      prueba_inclinacion),
    ("ENTRADAS",          "Sonido",           prueba_sonido),
    ("ENTRADAS",          "IR",               prueba_ir),
    ("I2C",               "DHT20",            prueba_dht20),
    ("I2C",               "Luz",              prueba_luz),
    ("I2C",               "LCD",              prueba_lcd),
    ("I2C",               "7 segmentos",      prueba_segmentos),
    ("SPI",               "Matriz LED",       prueba_matriz_led),
    ("ESPECIALES",        "Servo",            prueba_servo),
    ("ESPECIALES",        "Ultrasonido",      prueba_ultrasonido),
    ("ESPECIALES",        "Stepper",          prueba_stepper),
    ("ESPECIALES",        "Matriz botones",   prueba_matriz_botones),
]


def mostrar_menu():
    print("\n" + "=" * 60)
    print("  DIAGNOSTICO CrowPi - MENU")
    print("=" * 60)
    grupo_actual = None
    for i, (grupo, etiqueta, _) in enumerate(PRUEBAS, start=1):
        if grupo != grupo_actual:
            print("  --- %s ---" % grupo)
            grupo_actual = grupo
        print("   %2d) %s" % (i, etiqueta))
    print("    A) Probar TODO (en orden recomendado)")
    print("    R) Ver resumen de resultados")
    print("    Q) Salir")


def ejecutar_todas():
    for grupo, etiqueta, func in PRUEBAS:
        func()
        if not preguntar("¿Continuar con la siguiente prueba?"):
            print("  Pruebas restantes omitidas.")
            break


def mostrar_resumen():
    banner("RESUMEN DE RESULTADOS")
    if not RESULTADOS:
        print("  Aun no hay resultados.")
        return
    ok_count = sum(1 for v in RESULTADOS.values() if v)
    for nombre, ok in RESULTADOS.items():
        print("   [%s] %s" % ("OK " if ok else "X  ", nombre))
    print("\n  TOTAL: %d/%d dispositivos OK" % (ok_count, len(RESULTADOS)))


def main():
    print("\nDiagnostico CrowPi. Recuerda: sudo python3 diagnostico_crowpi.py")
    while True:
        mostrar_menu()
        opcion = input("\n  Elige una opcion: ").strip().lower()
        if opcion == "q":
            break
        if opcion == "a":
            ejecutar_todas()
            continue
        if opcion == "r":
            mostrar_resumen()
            continue
        if opcion.isdigit() and 1 <= int(opcion) <= len(PRUEBAS):
            PRUEBAS[int(opcion) - 1][2]()
        else:
            print("  Opcion no valida.")
    mostrar_resumen()
    print("\n  Fin del diagnostico.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n  Interrumpido por el usuario.")
        mostrar_resumen()

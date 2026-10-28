#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#Temporizador descendente para CrowPi

import tkinter as tk
from tkinter import font as tkfont

try:
    from gpiozero import Buzzer
except ImportError:
    Buzzer = None

# ----------------------- Configuracion -----------------------
BUZZER_PIN = 18            
DURACION_DEFECTO_MIN = 1   # 
COLOR_FONDO = "#101418"
COLOR_TEXTO = "#39FF14"    # verde fosfo
COLOR_ALERTA = "#FF3B30"   # rojo


class Temporizador:
    def __init__(self, root):
        self.root = root

        
        self.buzzer = None
        if Buzzer is not None:
            try:
                self.buzzer = Buzzer(BUZZER_PIN)
            except Exception as e:
                print("Buzzer no disponible: %s" % e)

        self.total = DURACION_DEFECTO_MIN * 60
        self.restante = self.total
        self.en_marcha = False
        self.after_id = None

        self._construir_ui()
        self._refrescar()

    # -------------------- Interfaz --------------------
    def _construir_ui(self):
        self.root.title("Temporizador CrowPi")
        self.root.configure(bg=COLOR_FONDO)
        self.root.geometry("800x480")

        self.fuente_tiempo = tkfont.Font(family="Helvetica", size=140, weight="bold")
        self.lbl = tk.Label(self.root, text="00:00", font=self.fuente_tiempo,
                            bg=COLOR_FONDO, fg=COLOR_TEXTO)
        self.lbl.pack(expand=True, fill="both")

        controles = tk.Frame(self.root, bg=COLOR_FONDO)
        controles.pack(fill="x", pady=12)

        tk.Label(controles, text="Minutos:", bg=COLOR_FONDO, fg="white",
                 font=("Helvetica", 16)).pack(side="left", padx=(20, 6))
        self.spin = tk.Spinbox(controles, from_=1, to=99, width=4,
                               font=("Helvetica", 16), justify="center")
        self.spin.delete(0, "end")
        self.spin.insert(0, str(DURACION_DEFECTO_MIN))
        self.spin.pack(side="left")

        tk.Button(controles, text="Iniciar/Pausar", font=("Helvetica", 14),
                  command=self.alternar).pack(side="left", padx=10)
        tk.Button(controles, text="Reiniciar", font=("Helvetica", 14),
                  command=self.reiniciar).pack(side="left", padx=10)
        tk.Button(controles, text="Salir", font=("Helvetica", 14),
                  command=self.salir).pack(side="left", padx=10)

        self.root.bind("<space>", lambda e: self.alternar())
        self.root.bind("<r>", lambda e: self.reiniciar())
        self.root.bind("<Escape>", lambda e: self.salir())

    # -------------------- Logica --------------------
    def _formato(self, seg):
        minutos, segundos = divmod(max(0, seg), 60)
        return "%02d:%02d" % (minutos, segundos)

    def _refrescar(self):
        self.lbl.config(text=self._formato(self.restante))

    def alternar(self):
        if self.en_marcha:
            self.pausar()
        else:
            self.iniciar()

    def iniciar(self):
        if self.restante <= 0:      
            self.reiniciar()
        self.en_marcha = True
        self._tick()

    def pausar(self):
        self.en_marcha = False
        if self.after_id is not None:
            self.root.after_cancel(self.after_id)
            self.after_id = None

    def _tick(self):
        if not self.en_marcha:
            return
        self._refrescar()
        if self.restante == 0:
            self.al_finalizar()
            return
        self.restante -= 1
        self.after_id = self.root.after(1000, self._tick)

    def reiniciar(self):
        self.pausar()
        try:
            minutos = int(self.spin.get())
        except ValueError:
            minutos = DURACION_DEFECTO_MIN
        self.total = max(1, minutos) * 60
        self.restante = self.total
        self.lbl.config(fg=COLOR_TEXTO)
        self._refrescar()

    # -------------------- Fin de la cuenta --------------------
    def al_finalizar(self):
        self.en_marcha = False
        self._refrescar()
        self.lbl.config(fg=COLOR_ALERTA)
        self.root.bell()                      
        if self.buzzer is not None:  
            self.buzzer.beep(on_time=0.2, off_time=0.15, n=15, background=True)
        self._parpadear(8)
        print("Temporizador finalizado")

    def _parpadear(self, veces):
        if veces <= 0:
            self.lbl.config(fg=COLOR_ALERTA)
            return
        actual = self.lbl.cget("fg")
        nuevo = COLOR_FONDO if actual == COLOR_ALERTA else COLOR_ALERTA
        self.lbl.config(fg=nuevo)
        self.root.after(300, lambda: self._parpadear(veces - 1))

    # -------------------- Salida --------------------
    def salir(self):
        self.pausar()
        if self.buzzer is not None:
            try:
                self.buzzer.off()
                self.buzzer.close()
            except Exception:
                pass
        self.root.destroy()


def main():
    root = tk.Tk()
    app = Temporizador(root)
    root.protocol("WM_DELETE_WINDOW", app.salir)
    root.mainloop()


if __name__ == "__main__":
    main()

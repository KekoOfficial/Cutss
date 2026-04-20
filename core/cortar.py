import subprocess
import config
import os

def extraer_segmento(path_input, n, total_partes):
    """
    Corta el video en fragmentos de 60s con velocidad máxima
    El último fragmento se nombra como 0000.mp4 tal como pediste
    """
    inicio = (n - 1) * config.CLIP_DURATION
    
    # Nomenclatura: 1.mp4, 2.mp4... y el último 0000.mp4
    if n == total_partes:
        nombre_archivo = "0000.mp4"
    else:
        nombre_archivo = f"{n}.mp4"
    
    path_output = f"{config.TEMP_FOLDER}/{nombre_archivo}"

    # ⚡ VELOCIDAD MÁXIMA - Copia directa sin recodificar
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(inicio),
        '-i', path_input,
        '-t', str(config.CLIP_DURATION),
        '-c', 'copy',
        '-avoid_negative_ts', 'make_zero',
        '-loglevel', 'error', # Sin mensajes innecesarios
        path_output
    ]

    subprocess.run(cmd, capture_output=True, shell=False)
    return path_output

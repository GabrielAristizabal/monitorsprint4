from django.http import JsonResponse
from django.shortcuts import render
import json
import random
import time
from datetime import datetime

from core.mongo import rutas_collection


def home(request):
    return render(request, "index.html")


def generar_ruta(locaciones, pedido_id):
    """
    Genera una ruta 'óptima' (aleatoria en este demo),
    calcula algunas métricas y guarda el resultado en MongoDB.
    """
    inicio_proceso = time.perf_counter()

    # Simula un tiempo de cálculo
    time.sleep(random.uniform(0.05, 0.35))

    # Crea una ruta aleatoria
    locaciones_barajadas = locaciones[:]  # copia para no mutar la lista original
    random.shuffle(locaciones_barajadas)

    ruta = ["Dock de Recepción"] + locaciones_barajadas + ["Zona de Empaque"]

    # Métricas muy simples / simuladas
    distancia_base = 80  # recorrido mínimo desde dock + empaque
    distancia_por_item = random.uniform(15, 55)  # metros promedio por item
    distancia_m = round(distancia_base + len(locaciones_barajadas) * distancia_por_item, 2)

    tiempo_caminar_seg = round(distancia_m / 1.4, 2)  # asumiendo 1.4 m/s

    duracion_ms = round((time.perf_counter() - inicio_proceso) * 1000, 2)

    # Documento a guardar en Mongo
    doc = {
        "pedido_id": pedido_id,
        "locaciones": locaciones_barajadas,
        "ruta": ruta,
        "distancia_m": distancia_m,
        "tiempo_caminar_seg": tiempo_caminar_seg,
        "proceso_ruta_ms": duracion_ms,
        "creado_en": datetime.utcnow(),
    }

    # Insertar en MongoDB
    result = rutas_collection.insert_one(doc)
    doc["_id"] = str(result.inserted_id)

    # Esto es lo que se devuelve al cliente
    return doc


def calcular_ruta(request):
    if request.method != "POST":
        return JsonResponse(
            {"status": "ERROR", "mensaje": "Solo se permite el método POST"},
            status=405,
        )

    try:
        body = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse(
            {"status": "ERROR", "mensaje": "JSON inválido"},
            status=400,
        )

    pedido = body.get("pedido_id")
    locaciones = body.get("locaciones")

    if not pedido or not locaciones or not isinstance(locaciones, list):
        return JsonResponse(
            {
                "status": "ERROR",
                "mensaje": "Debes enviar pedido_id y una lista válida de locaciones",
            },
            status=400,
        )

    resultado = generar_ruta(locaciones, pedido)

    # test_endpoint espera: {"status": "OK", "resultado": { ... }}
    return JsonResponse({"status": "OK", "resultado": resultado}, status=200)

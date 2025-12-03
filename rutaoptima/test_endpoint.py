import requests

response = requests.post("http://127.0.0.1:8000/calcular-ruta/", json={
    "pedido_id": "P-TEST-01",
    "locaciones": ["Pasillo 1", "Estanteria 3", "Pasillo 5", "Estanteria 1"]
})

print("\nStatus code:", response.status_code)
print("\nRespuesta en texto del servidor:\n")
print(response.text) 

if response.status_code == 200:
    try:
        print("\nJSON parseado:\n")
        print(response.json())
        data = response.json()
        duracion_ms = data["resultado"]["proceso_ruta_ms"]
        ruta = data["resultado"]["ruta"]
        print(ruta)
        print("\nEl tiempo que tardo el sistema en encontrar la ruta optima es de ",duracion_ms, " ms, para la ruta: ",ruta)

    except:
        print("\nNo pudo convertirse a JSON, pero esto devolvio el servidor")
else:
    print("\nEl endpoint fallo")

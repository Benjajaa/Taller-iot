Taller 5 IoT
Proyecto de monitoreo en tiempo real usando FastAPI, MongoDB Atlas y JanusGraph.

Instrucciones de ejecución:

Instalar dependencias: pip install fastapi uvicorn pydantic motor gremlinpython

Levantar JanusGraph con Docker: docker run -d -p 8182:8182 janusgraph/janusgraph:latest

Ejecutar backend: uvicorn main:app --reload

Exponer mediante Cloudflare: cloudflared tunnel --url [http://127.0.0.1:8000](http://127.0.0.1:8000)

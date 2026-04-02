# Ejemplo rapido: usar MCP Filesystem con Copilot

Este proyecto ya tiene configurado el servidor MCP `filesystem` en `.vscode/mcp.json`.

## 1) Verifica que MCP esta activo
En Copilot Chat, prueba con:

- "Lista los archivos de la carpeta ejemplo"

Respuesta esperada: deberia mostrar `ejemplo/README_MCP.md` y `ejemplo/notas.txt`.

## 2) Leer un archivo
Prueba:

- "Lee el archivo ejemplo/notas.txt y resumelo en 2 lineas"

## 3) Editar un archivo
Prueba:

- "Agrega una tercera tarea al archivo ejemplo/notas.txt: Revisar logs de red"

## 4) Crear un archivo nuevo
Prueba:

- "Crea ejemplo/resultados.txt con un checklist de 3 puntos para una practica de redes complejas"

## 5) Operacion estructurada
Prueba:

- "En la carpeta ejemplo, crea una subcarpeta data y dentro un archivo nodos.csv con columnas id,label y 3 filas de ejemplo"

## Nota importante
- El servidor filesystem solo puede operar dentro del workspace permitido (`${workspaceFolder}`).
- Si no responde, recarga VS Code (Developer: Reload Window).

# Script básico de Julia para aprender
# ====================================

using Statistics

println("¡Bienvenido a Julia!")
println()

# 1. Variables y tipos básicos
println("=== Variables y Tipos ===")
x = 10
y = 20.5
nombre = "Julia"
booleano = true

println("x = $x (tipo: $(typeof(x)))")
println("y = $y (tipo: $(typeof(y)))")
println("nombre = $nombre (tipo: $(typeof(nombre)))")
println("booleano = $booleano (tipo: $(typeof(booleano)))")
println()

# 2. Operaciones aritméticas
println("=== Operaciones Aritméticas ===")
suma = x + y
resta = x - 5
multiplicacion = x * 2
division = y / 3
potencia = x ^ 2
modulo = x % 3

println("Suma: $x + $y = $suma")
println("Potencia: $x elevado a 2 = $potencia")
println("Módulo: $x % 3 = $modulo")
println()

# 3. Arreglos (Arrays)
println("=== Arreglos ===")
numeros = [1, 2, 3, 4, 5]
flotantes = [1.1, 2.2, 3.3]
matriz = [1 2 3; 4 5 6; 7 8 9]

println("Vector: $numeros")
println("Primer elemento: $(numeros[1])")
println("Última posición: $(numeros[end])")
println("Matriz:\n$matriz")
println()

# 4. Control de flujo - Condicionales
println("=== Condicionales ===")
edad = 25

if edad < 18
    println("Eres menor de edad")
elseif edad < 65
    println("Eres adulto en edad de trabajar")
else
    println("Eres jubilado")
end
println()

# 5. Bucles
println("=== Bucles ===")
println("Bucle for:")
for i in 1:5
    println("  i = $i, i² = $(i^2)")
end
println()

println("Bucle while:")
contador = 0
while contador < 3
    global contador
    contador += 1
    println("  Iteración $contador")
end
println()

# 6. Funciones
println("=== Funciones ===")

# Función simple
function saludar(nombre)
    return "¡Hola, " * nombre * "!"
end

# Función con múltiples argumentos
function sumar(a, b)
    return a + b
end

# Función con valor por defecto
function potenciar(base, exponente=2)
    return base ^ exponente
end

println(saludar("María"))
println("3 + 7 = $(sumar(3, 7))")
println("5 elevado a 2 = $(potenciar(5))")
println("2 elevado a 5 = $(potenciar(2, 5))")
println()

# 7. Comprensión de listas
println("=== Comprensión de Listas ===")
cuadrados = [i^2 for i in 1:10]
println("Cuadrados del 1 al 10: $cuadrados")

pares = [i for i in 1:10 if i % 2 == 0]
println("Números pares del 1 al 10: $pares")
println()

# 8. Operaciones con arreglos
println("=== Operaciones con Arreglos ===")
arr = [5, 2, 8, 1, 9]
println("Arreglo original: $arr")
println("Suma total: $(sum(arr))")
println("Promedio: $(mean(arr))")
println("Máximo: $(maximum(arr))")
println("Mínimo: $(minimum(arr))")
println("Ordenado: $(sort(arr))")
println()

# 9. Diccionarios
println("=== Diccionarios ===")
persona = Dict(
    "nombre" => "Juan",
    "edad" => 30,
    "ciudad" => "Madrid"
)

println("Persona: $persona")
println("Nombre: $(persona["nombre"])")
println("Edad: $(persona["edad"])")
println()

# 10. Resumen
println("=== Resumen ===")
println("¡Estos son los conceptos básicos de Julia!")
println("Continúa explorando con más funciones y librerías.")

# Analisis del paper y replica simplificada

## Paper analizado
- Titulo: Continuous model calibration framework for smart-building digital twin: A generative model-based approach
- Revista: Applied Energy 375 (2024) 124080

## Objetivo del paper
El trabajo propone un marco de calibracion continua para modelos fisicos (white-box) en digital twins de edificios inteligentes, cuando hay variables influyentes no observadas y condiciones reales con ruido/fallas de sensores.

## Idea central
1. Definir el problema de calibracion como inferencia de la distribucion posterior de entradas no observadas $p(x_u | y_o)$.
2. Generar datos de simulacion del modelo fisico para entrenar un calibrador inverso.
3. Aplicar augmentacion tipo VPOA (Virtual-to-Physical Observations Approximation) para emular ruido y faltantes.
4. Entrenar un calibrador generativo (DECI-Net), basado en cINN + denoising autoencoder, para estimar distribuciones de entradas no observadas con incertidumbre.
5. En despliegue continuo, usar el calibrador preentrenado para inferir rapidamente una solucion de calibracion por observacion.

## Datos clave reportados en el paper
Extraido del abstract y secciones de resultados:
- Tiempo promedio de inferencia por problema de calibracion: 0.043 s.
- CVRMSE electricidad (sin ruido / con ruido / ruido+faltantes): 6.33% / 10.18% / 10.97%.
- CVRMSE gas (sin ruido / con ruido / ruido+faltantes): 18.75% / 20.53% / 20.7%.
- El paper reporta cumplimiento de umbrales horarios estandar de calibracion.

## Replica implementada en este directorio
Archivo principal: replica_genphysical.py

La replica no reproduce la arquitectura profunda DECI-Net exacta (cINN + autoencoder), pero replica el flujo metodologico del paper:
- Modelo forward simplificado de edificio (electricidad y gas horarios).
- Entradas no observadas influyentes: ocupacion, iluminacion y carga de enchufes.
- Simulacion para crear dataset de entrenamiento.
- Augmentacion en 3 escenarios:
  - exp1_clean: sin degradacion.
  - exp2_noise: ruido gaussiano 10%.
  - exp3_noise_missing: ruido 10% + 35% faltantes.
- Calibrador inverso probabilistico por vecindad (aproxima una inferencia generativa sobre posterior).
- Seleccion MAP (maxima densidad) y evaluacion de calibracion con CVRMSE.

## Resultados obtenidos de la replica
Fuente: metricas_replicacion.csv

- exp1_clean
  - theta_rmse: 0.2395
  - cvrmse_electricity_pct: 3.6387
  - cvrmse_gas_pct: 4.3118
  - avg_inference_time_sec: 0.0919

- exp2_noise
  - theta_rmse: 0.2567
  - cvrmse_electricity_pct: 4.2260
  - cvrmse_gas_pct: 4.4941
  - avg_inference_time_sec: 0.0888

- exp3_noise_missing
  - theta_rmse: 0.2969
  - cvrmse_electricity_pct: 9.5144
  - cvrmse_gas_pct: 5.8218
  - avg_inference_time_sec: 0.0885

## Comparacion paper vs replica
- Tendencia comun reproducida: al pasar de limpio a ruido y luego ruido+faltantes, el error de calibracion aumenta.
- Componente de incertidumbre: la replica estima muestras posteriores y un punto MAP, alineado con la filosofia probabilistica del paper.
- Diferencia principal: el paper usa una arquitectura deep generative (DECI-Net) sobre un BEM realista (EnergyPlus/DOE), mientras que aqui se usa un simulador sintetico y un inverso no profundo.
- Tiempo: la replica es del mismo orden de magnitud sub-segundo, aunque mas lenta que 0.043 s del paper.

## Limitaciones de esta replica
- No usa cINN real ni autoencoder denoising.
- No usa datos reales ni modelo energetico fisico de alta fidelidad.
- No incluye metricas de calibracion probabilistica como CRPS/curvas de confiabilidad.

## Archivos generados
- replica_genphysical.py: implementacion completa de la replica.
- metricas_replicacion.csv: tabla de metricas por escenario.
- resultados_resumen.json: resumen estructurado en JSON.
- posterior_samples_case0.csv: muestras posteriores de un caso para inspeccion.

## Como ejecutar de nuevo
Desde la raiz del workspace:

```powershell
C:/Users/andsi/AppData/Local/Programs/Python/Python311/python.exe "compact/replica_genphysical.py"
```

# Compresión/Descompresión PySCHC


### Cambios

- Implementado Matching Operator MSB. Número de bits en la string MO de la regla (ej: "MSB(6)").
- Implementados Compression/Decompression Actions LSB, mapping-sent y devIID (aes128_cmac).
- Implementada descompresión con residuo en bits.
- Implementado alineamiento en bits del payload.
- Implementada reconstrucción del paquete IPv6 en el método `decompress`.
- Fix: Ahora método `compress` recibe paquete bruto en lugar de preparseado.
- Fix: Ahora residuo de compresión es armado como array de bits.
- Fix: Problemas varios con la regla por defecto (no compresión).
- Fix: Ahora cuando se descarta una regla por MOs no se termina la iteración por reglas prematuramente.
- Fix: Nombres incorrectos de prefijos e iids.
- Cambio de nombres de variables y comentarios de español a inglés


### Detalles no implementados

- CDA devIID con valores obtenidos del device.
- CDAs/Reglas con headers de largo variable (no requerido para IPv6 + UDP).
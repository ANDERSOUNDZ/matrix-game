# dominio/ — módulo autenticación

Ya hay una implementación de referencia acá: `usuario.py` (entidad `Usuario` con
hash/verificación de contraseña) y `errores.py` (`CredencialesInvalidasError`,
`EmailYaRegistradoError`). Extendela según necesites (validación de formato de
email más estricta, requisitos de fuerza de contraseña, etc.).

Ver `GUIA-ARQUITECTURA-Y-CALIDAD.md`, Nivel 1, sección 1.2 ("Dominio").

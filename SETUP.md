# 🚀 Guía de Configuración - TopicTales Biomédica

## ⚡ Configuración Rápida

### 1. **Clonar y Configurar Entorno**
```bash
git clone https://github.com/sircalch/TopicTalesBiomProyecto.git
cd TopicTalesBiomProyecto
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements-core.txt
```

### 2. **Configurar Base de Datos**
```bash
python manage.py migrate
python manage.py initialize_modules
python manage.py create_sample_data
```

### 3. **Ejecutar Sistema**
```bash
python manage.py runserver
```

## 🔑 Credenciales de Acceso

| Usuario | Contraseña | Rol | Acceso |
|---------|------------|-----|--------|
| `admin` | `admin123` | Administrador | **Todos los módulos del Plan Medio** |
| `dr.martinez` | `doctor123` | Médico | Módulos médicos y expedientes |
| `recepcion` | `recep123` | Recepcionista | Módulos administrativos |

## 🏥 Organización de Ejemplo

- **Nombre**: Clínica Ejemplo TopicTales
- **Plan**: MEDIO (permite especialidades básicas, facturación, equipos)
- **Límites**: 500 pacientes, 10 usuarios
- **Estado**: Activo por 365 días

## 📋 Comandos Disponibles

### Gestión del Sistema
```bash
# Inicializar módulos del sistema
python manage.py initialize_modules

# Crear datos de ejemplo
python manage.py create_sample_data

# Crear superusuario
python manage.py createsuperuser

# Ejecutar migraciones
python manage.py migrate

# Recopilar archivos estáticos (producción)
python manage.py collectstatic
```

### Base de Datos
```bash
# Crear migraciones
python manage.py makemigrations

# Ver migraciones pendientes
python manage.py showmigrations

# Shell interactivo
python manage.py shell
```

## 🎯 URLs Principales

- **Sistema**: http://127.0.0.1:8000/
- **Admin**: http://127.0.0.1:8000/admin/
- **API**: http://127.0.0.1:8000/api/
- **Pacientes**: http://127.0.0.1:8000/patients/
- **Citas**: http://127.0.0.1:8000/appointments/
- **Expedientes**: http://127.0.0.1:8000/medical-records/

## 🔧 Configuración de Producción

### Variables de Entorno (.env)
```env
SECRET_KEY=tu-clave-secreta-muy-segura
DEBUG=False
ALLOWED_HOSTS=tudominio.com,www.tudominio.com

# Base de datos PostgreSQL
DB_ENGINE=django.db.backends.postgresql
DB_NAME=topictales_biomedica
DB_USER=tu_usuario
DB_PASSWORD=tu_password
DB_HOST=localhost
DB_PORT=5432
```

### Configuración NGINX
```nginx
server {
    listen 80;
    server_name tudominio.com www.tudominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static/ {
        alias /path/to/staticfiles/;
    }
    
    location /media/ {
        alias /path/to/media/;
    }
}
```

## 🛡️ Configuración de Seguridad

### Para Producción
1. **Cambiar SECRET_KEY** en settings.py
2. **Configurar ALLOWED_HOSTS** con tu dominio
3. **Usar HTTPS** con certificado SSL
4. **Configurar base de datos PostgreSQL**
5. **Configurar backup automático**
6. **Habilitar logging** para auditoría

### Permisos de Archivos
```bash
# Permisos para media files
chmod 755 media/
chmod 644 media/*

# Permisos para logs
mkdir logs/
chmod 755 logs/
```

## 📊 Estructura de Planes

### 🟢 Plan Básico (Gratis)
- ✅ Dashboard
- ✅ Pacientes (hasta 100)
- ✅ Citas médicas
- ✅ Expedientes básicos
- ✅ 2 usuarios máximo

### 🟡 Plan Medio ($2,500 MXN/mes)
- ✅ Todo lo del Plan Básico
- ✅ Especialidades médicas (3)
- ✅ Sistema de facturación
- ✅ Gestión de equipos
- ✅ Reportes avanzados
- ✅ Telemedicina
- ✅ 500 pacientes, 10 usuarios

### 🟠 Plan Avanzado ($5,000 MXN/mes)
- ✅ Todo lo del Plan Medio
- ✅ Todas las especialidades (6)
- ✅ Business Intelligence
- ✅ Portal del paciente
- ✅ Integraciones API
- ✅ Soporte prioritario
- ✅ Usuarios ilimitados

## 🆘 Soporte y Contacto

- **Repositorio**: https://github.com/sircalch/TopicTalesBiomProyecto
- **Issues**: https://github.com/sircalch/TopicTalesBiomProyecto/issues
- **Documentación**: Ver README.md
- **Email**: support@topictales.com

## 🐛 Troubleshooting

### Error: "No module named 'accounts'"
```bash
# Asegúrate de estar en el directorio correcto
cd TopicTalesBiomProyecto
python manage.py runserver
```

### Error: "no such table: accounts_user"
```bash
# Ejecutar migraciones
python manage.py migrate
python manage.py initialize_modules
```

### Error: "ModuleNotFoundError"
```bash
# Instalar dependencias
pip install -r requirements-core.txt
```

### Sidebar vacío o sin módulos
```bash
# Reinicializar módulos y datos
python manage.py initialize_modules
python manage.py create_sample_data
```

---
**¡Tu sistema médico profesional está listo! 🏥✨**
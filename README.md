# TopicTales Biomédica

## 🏥 Sistema Integral de Gestión Médica

TopicTales Biomédica es un sistema completo de gestión médica desarrollado en Django, diseñado para clínicas y consultorios médicos. Ofrece una plataforma modular con planes de suscripción que se adapta a las necesidades específicas de cada organización médica.

## ✨ Características Principales

### 🎯 **Sidebar Dinámico y Modular**
- **Adaptación por Plan**: Los módulos se muestran según el plan de suscripción (Básico, Medio, Avanzado)
- **Control de Permisos**: Acceso basado en roles (Admin, Médico, Recepcionista, Paciente)
- **Indicadores Visuales**: Badges de plan, tooltips informativos, progreso de uso
- **Gestión de Recursos**: Control de límites de pacientes y usuarios

### 📋 **Módulos Básicos (Plan Básico)**
- **Dashboard**: Panel principal con resumen de actividades
- **Gestión de Pacientes**: Registro completo con expedientes digitales
- **Sistema de Citas**: Calendario avanzado con drag-and-drop
- **Expedientes Médicos**: Historia clínica completa con formato SOAP

### 🩺 **Especialidades Médicas (Plan Medio+)**
- **Cardiología**: Especializada en enfermedades del corazón
- **Pediatría**: Atención médica para niños y adolescentes
- **Ginecología**: Salud reproductiva femenina
- **Dermatología**: Enfermedades de la piel (Plan Avanzado)
- **Nutrición**: Evaluación y planes nutricionales (Plan Avanzado)
- **Psicología**: Evaluaciones y terapias psicológicas (Plan Avanzado)

### ⚙️ **Administración**
- **Facturación**: Sistema de cobranza y pagos (Plan Medio+)
- **Gestión de Equipos**: Inventario y mantenimiento (Plan Medio+)
- **Usuarios**: Control de personal y permisos
- **Organizaciones**: Configuración de clínicas

### 📊 **Reportes y Analytics**
- **Reportes Básicos**: Estadísticas estándar del sistema
- **Analytics Avanzado**: Dashboards ejecutivos y KPIs (Plan Medio+)
- **Business Intelligence**: Análisis predictivo (Plan Avanzado)

### 💬 **Comunicación**
- **Notificaciones**: Centro de alertas del sistema
- **Telemedicina**: Consultas médicas virtuales (Plan Medio+)
- **Portal del Paciente**: Acceso en línea para pacientes (Plan Avanzado)

### 🔌 **Integraciones (Plan Avanzado)**
- **API Externa**: Conectividad con sistemas externos
- **Laboratorios**: Integración con laboratorios externos

## 🛠️ Tecnologías Utilizadas

- **Backend**: Django 4.2.16, Python 3.13
- **Base de Datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **Frontend**: Bootstrap 5, FontAwesome, JavaScript
- **Autenticación**: Sistema personalizado con roles y permisos
- **Calendario**: FullCalendar con funcionalidad drag-and-drop

## 🚀 Instalación y Configuración

### Requisitos Previos
- Python 3.11+
- pip
- Git

### Paso a Paso

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/sircalch/TopicTalesBiomProyecto.git
   cd TopicTalesBiomProyecto
   ```

2. **Crear entorno virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   venv\Scripts\activate     # Windows
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurar base de datos**
   ```bash
   python manage.py migrate
   ```

5. **Inicializar módulos del sistema**
   ```bash
   python manage.py initialize_modules
   ```

6. **Crear datos de ejemplo (opcional)**
   ```bash
   python manage.py create_sample_data
   ```

7. **Ejecutar servidor de desarrollo**
   ```bash
   python manage.py runserver
   ```

8. **Acceder al sistema**
   - URL: http://127.0.0.1:8000/
   - Admin: http://127.0.0.1:8000/admin/

## 👥 Credenciales de Ejemplo

| Usuario | Contraseña | Rol | Descripción |
|---------|------------|-----|-------------|
| `admin` | `admin123` | Administrador | Acceso completo al sistema |
| `dr.martinez` | `doctor123` | Médico | Módulos médicos y expedientes |
| `recepcion` | `recep123` | Recepcionista | Módulos administrativos |

## 📋 Planes de Suscripción

### 🟢 **Plan Básico**
- Dashboard y estadísticas básicas
- Gestión de pacientes (hasta 100)
- Sistema de citas
- Expedientes médicos básicos
- 2 usuarios máximo

### 🟡 **Plan Medio**
- Todo lo del Plan Básico
- Especialidades médicas (Cardiología, Pediatría, Ginecología)
- Sistema de facturación
- Gestión de equipos médicos
- Reportes avanzados y KPIs
- Telemedicina
- Hasta 500 pacientes y 10 usuarios

### 🟠 **Plan Avanzado** 
- Todo lo del Plan Medio
- Todas las especialidades médicas
- Business Intelligence
- Portal del paciente
- Integraciones API
- Soporte prioritario
- Pacientes y usuarios ilimitados

## 🏗️ Arquitectura del Sistema

```
TopicTalesBiomProyecto/
├── accounts/                 # Gestión de usuarios y autenticación
├── patients/                 # Módulo de pacientes
├── appointments/            # Sistema de citas
├── medical_records/         # Expedientes médicos
├── specialties/             # Especialidades médicas
├── equipment/               # Gestión de equipos
├── reports/                 # Reportes y analytics
├── billing/                 # Facturación
├── dashboard/               # Panel principal
├── templates/               # Templates HTML
│   ├── components/          # Componentes reutilizables
│   ├── medical_records/     # Templates de expedientes
│   └── auth/               # Templates de autenticación
├── static/                  # Archivos estáticos
└── media/                  # Archivos subidos
```

## 📚 Documentación de la API

El sistema incluye una API RESTful para integraciones externas (disponible en Plan Avanzado):

### Endpoints Principales
- `/api/patients/` - Gestión de pacientes
- `/api/appointments/` - Sistema de citas
- `/api/medical-records/` - Expedientes médicos
- `/api/specialties/` - Especialidades médicas

## 🤝 Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🆘 Soporte

Para soporte técnico o consultas comerciales:
- **Email**: support@topictales.com
- **Website**: https://topictales.com
- **Documentación**: https://docs.topictales.com

## 🚧 Roadmap

### Próximas Funcionalidades
- [ ] Módulos de especialidades médicas completos
- [ ] Sistema de telemedicina con videollamadas
- [ ] Integración con sistemas de laboratorio
- [ ] App móvil para pacientes
- [ ] Inteligencia artificial para diagnósticos
- [ ] Sistema de backup automático
- [ ] Cumplimiento HIPAA/LOPD

---

**TopicTales Biomédica** - Transformando la gestión médica con tecnología avanzada 🏥✨
# UI System (Django Templates + Tailwind CSS v4)

## 1) Configuración Tailwind v4

1. Instala dependencias front-end:
   ```bash
   npm install
   ```
2. Compila Tailwind para producción:
   ```bash
   npm run tailwind:build
   ```
3. Modo watch para desarrollo:
   ```bash
   npm run tailwind:watch
   ```

Entrada de Tailwind: `static/src/tailwind.css`  
Salida compilada: `static/css/app.css`

## 2) Estructura recomendada

```text
static/
  src/
    tailwind.css
  css/
    app.css

templates/
  components/
    ui/
      button.html
      input.html
      select.html
      card.html
      table.html
      modal.html
      _button_core.html
      _button_element.html
```

## 3) Componentes reutilizables mínimos

- **Button**: variantes `primary`, `secondary`, `outline`, `danger`.
- **Input**: estilos de foco accesibles y estados disabled.
- **Select**: estilo consistente con input.
- **Card**: contenedor con header opcional y body.
- **Table**: envoltorio responsive con bordes/sombras Catalyst-like.
- **Modal**: compatible con Alpine.js (`x-show`, overlay y cierre).

## 4) Ejemplo real aplicado

Se aplicó al dashboard y login:
- `templates/dashboard/dashboard.html`
- `templates/users/login.html`

Ejemplo rápido de botón:

```django
{% include "components/ui/button.html" with label="Guardar" variant="primary" type="submit" %}
```

## 5) Cómo extender el sistema

1. Crear un componente nuevo en `templates/components/ui/`.
2. Mantener tokens visuales en Tailwind (`static/src/tailwind.css`) usando `@theme`.
3. Evitar CSS custom si ya existe utilidad Tailwind.
4. Si agregas una nueva variante, primero extiende `button.html` (o componente base correspondiente).
5. Reutiliza clases compartidas desde `apps/common/form_styles.py` para formularios Django.

## Colores institucionales

Los colores institucionales se mantienen como tokens:
- `--color-brand-primary: #000000`
- `--color-brand-primary-hover: #CC0000`
- `--color-brand-primary-strong: #990000`
- `--color-brand-danger: #CC0000`

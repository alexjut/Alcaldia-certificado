import sass

# Compilar todos los archivos SCSS en un único archivo CSS
sass.compile(
    dirname=('static/scss', 'static/css'),
    output_style='compressed'
)
import ply.lex as lex

# Lista para almacenar errores léxicos
errores_lexicos = []

# Palabras reservadas
reserved = {
    'GetPlane': 'GETPLANE',
    'confTemp': 'CONFTEMP',
    'confWatts': 'CONFWATTS',
    'confLevel': 'CONFLEVEL',
    'ONO_FF': 'ONO_FF',
    'SavePoint': 'SAVEPOINT',
    'mark': 'MARK',
    'GetMeter': 'GETMETER',
    'air': 'AIR',
    'fridge': 'FRIDGE',
    'them': 'THEM',
    'oven': 'OVEN',
    'lights': 'LIGHTS',
    'fan': 'FAN',
    'mesh': 'MESH',
    'route': 'ROUTE',
    'airFryer': 'AIRFRYER',
    'speaker': 'SPEAKER',
    '_smartTV': '_SMARTTV',
    'DEVICE': 'DEVICE'
}

# Lista de tokens
tokens = [
    'NUMERIC',
    'TWOPOINT',
    'BOOLEAN_TRUE',
    'BOOLEAN_FALSE',
    'CHARACTERS',
    'tempFah',
    'tempCel',
    'BOOLEAN',
    'CADENA',
    'PLUS',
    'MINUS',
    'TIMES',
    'DIVIDE',
    'AND',
    'OR',
    'NOT',
    'GREATHAN',
    'LESSTHAN',
    'GRTHOREQ',
    'LSTHOREQ',
    'EQUAL',
    'EQUALCOMP',
    'LPAREN',
    'RPAREN',
    'LBRACE',
    'RBRACE',
    'LBRACKET',
    'RBRACKET',
    'SEMICOLON',
    'TYPE_DEVICE',
    'ID'
] + list(reserved.values())

# Expresiones regulares para tokens
t_PLUS = r'\+'
t_MINUS = r'-'
t_TIMES = r'\*'
t_DIVIDE = r'/'
t_AND = r'\&\&'
t_OR = r'\|\|'
t_NOT = r'!'
t_GREATHAN = r'>'
t_LESSTHAN = r'<'
t_GRTHOREQ = r'>='
t_LSTHOREQ = r'<='
t_EQUALCOMP = r'=='
t_EQUAL = r'='
t_LPAREN = r'\('
t_RPAREN = r'\)'
t_LBRACE = r'\{'
t_RBRACE = r'\}'
t_LBRACKET = r'\['
t_RBRACKET = r'\]'
t_SEMICOLON = r';'
t_TWOPOINT = r':'

# Reporte de errores
def reportar_error(tipo, detalle, linea):
    mensaje = f"Error léxico: {tipo} - {detalle} en la línea {linea}."
    errores_lexicos.append(mensaje)

# Definir tokens especiales
def t_NUMERIC(t):
    r'-?\d+(\.\d+)?'
    t.value = float(t.value) if '.' in t.value else int(t.value)
    if not (-10000 <= t.value <= 10000):
        reportar_error("Valor numérico fuera de rango", f"{t.value}", t.lineno)
        return None
    return t

def t_BOOLEAN_TRUE(t):
    r'true'
    t.value = True
    return t

def t_BOOLEAN_FALSE(t):
    r'false'
    t.value = False
    return t

def t_CADENA(t):
    r'\".*?\"'
    t.value = t.value[1:-1]
    return t

def t_tempFah(t):
    r'[+-]?\d{1,3}(\.\d+)?F'
    t.value = float(t.value[:-1])
    if t.value < -459.67:
        reportar_error("Temperatura fuera de rango", f"{t.value}F", t.lineno)
        return None
    return t

def t_tempCel(t):
    r'[+-]?\d{1,3}(\.\d+)?C'
    t.value = float(t.value[:-1])
    if t.value < -273.15:
        reportar_error("Temperatura fuera de rango", f"{t.value}C", t.lineno)
        return None
    return t

def t_ID(t):
    r'[a-zA-Z_][a-zA-Z_0-9]*'
    t.type = reserved.get(t.value, 'ID')
    return t

# Ignorar comentarios y espacios
def t_COMMENT(t):
    r'\#.*'
    pass

t_ignore = ' \t'

# Manejo de nueva línea
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Manejo de caracteres ilegales
def t_error(t):
    mensaje_error = f"Error léxico: Caracter ilegal '{t.value[0]}' en la línea {t.lineno}, columna {t.lexpos}"
    reportar_error("Caracter ilegal", mensaje_error, t.lineno)
    t.lexer.skip(1)

# Construcción del lexer
lexer = lex.lex()

# Función para analizar el código y devolver tokens y errores
def analizar_codigo(codigo):
    limpiar_errores()
    global errores_lexicos
    lexer.lineno = 1
    lexer.input(codigo)
    tokens_encontrados = []
    while True:
        tok = lexer.token()
        if not tok:
            break
        tokens_encontrados.append(tok)
    return tokens_encontrados, errores_lexicos

def limpiar_errores():
    global errores_lexicos
    errores_lexicos = []
"""The canonical unit enum and the spellings people actually type.

Unparseable quantities are not an error: the row keeps its raw_text and simply
opts out of aggregation. Same degrade-don't-break rule as ingredient matching.
"""

from enum import StrEnum


class Unit(StrEnum):
    GRAMO = "g"
    KILOGRAMO = "kg"
    MILILITRO = "ml"
    LITRO = "l"
    UNIDAD = "unidad"
    CUCHARADA = "cucharada"
    CUCHARADITA = "cucharadita"
    TAZA = "taza"
    PIZCA = "pizca"
    DIENTE = "diente"
    RAMA = "rama"
    HOJA = "hoja"
    REBANADA = "rebanada"
    PAQUETE = "paquete"
    LATA = "lata"
    AL_GUSTO = "al_gusto"


# Keys are accent-stripped, lowercased, singular-insensitive spellings. Both the
# singular and plural forms are listed because normalization runs after this map.
UNIT_SYNONYMS: dict[str, Unit] = {
    "g": Unit.GRAMO,
    "gr": Unit.GRAMO,
    "grs": Unit.GRAMO,
    "gramo": Unit.GRAMO,
    "gramos": Unit.GRAMO,
    "kg": Unit.KILOGRAMO,
    "kilo": Unit.KILOGRAMO,
    "kilos": Unit.KILOGRAMO,
    "kilogramo": Unit.KILOGRAMO,
    "kilogramos": Unit.KILOGRAMO,
    "ml": Unit.MILILITRO,
    "mililitro": Unit.MILILITRO,
    "mililitros": Unit.MILILITRO,
    "cc": Unit.MILILITRO,
    "l": Unit.LITRO,
    "lt": Unit.LITRO,
    "litro": Unit.LITRO,
    "litros": Unit.LITRO,
    "u": Unit.UNIDAD,
    "unidad": Unit.UNIDAD,
    "unidades": Unit.UNIDAD,
    "cucharada": Unit.CUCHARADA,
    "cucharadas": Unit.CUCHARADA,
    "cda": Unit.CUCHARADA,
    "cdas": Unit.CUCHARADA,
    "cucharadita": Unit.CUCHARADITA,
    "cucharaditas": Unit.CUCHARADITA,
    "cdta": Unit.CUCHARADITA,
    "cdtas": Unit.CUCHARADITA,
    "taza": Unit.TAZA,
    "tazas": Unit.TAZA,
    "pizca": Unit.PIZCA,
    "pizcas": Unit.PIZCA,
    "diente": Unit.DIENTE,
    "dientes": Unit.DIENTE,
    "rama": Unit.RAMA,
    "ramas": Unit.RAMA,
    "hoja": Unit.HOJA,
    "hojas": Unit.HOJA,
    "rebanada": Unit.REBANADA,
    "rebanadas": Unit.REBANADA,
    "feta": Unit.REBANADA,
    "fetas": Unit.REBANADA,
    "paquete": Unit.PAQUETE,
    "paquetes": Unit.PAQUETE,
    "lata": Unit.LATA,
    "latas": Unit.LATA,
}

# Trailing phrases that mean "no measurable quantity".
TO_TASTE_PHRASES: tuple[str, ...] = ("a gusto", "al gusto", "c n", "cantidad necesaria")

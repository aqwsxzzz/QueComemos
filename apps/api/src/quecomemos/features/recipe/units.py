"""The canonical unit enum.

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

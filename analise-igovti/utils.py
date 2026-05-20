import re
import numpy as np
import seaborn as sns

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, RegularPolygon
from matplotlib.path import Path
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.spines import Spine
from matplotlib.transforms import Affine2D

def parse_expression(expression):
    tokens = []
    current_token = ''

    for char in expression:            
        if char in {'|', '&', '~', '(', ')'}:
            if current_token:
                tokens.append(current_token.strip())
                current_token = ''
            tokens.append(char)
        else:
            current_token += char

    if current_token:
        tokens.append(current_token.strip())

    return tokens

def infix_to_rpn(tokens):
    precedence = {'~': 3, '&': 2, '|': 1}
    output = []
    stack = []
    
    for token in tokens:
        if token == '(':
            # Abre parêntese
            stack.append(token)
        elif token == ')':
            # Fecha parêntese
            while stack and stack[-1] != '(':
                output.append(stack.pop())
            stack.pop()  # Remove o '('
        elif token in precedence:
            # Operador
            while stack and stack[-1] in precedence and precedence[stack[-1]] >= precedence[token]:
                output.append(stack.pop())
            stack.append(token)
        else:
            output.append(token)

    while stack:
        output.append(stack.pop())
    
    return list(filter(lambda x: x != '', output))

def avalia_expressao(expressao_achado, situacao_encontrada, debug=False):
    # Primeiro tenta se é o caso de um eval
    try:
        if debug:
            print(f"Testando se {situacao_encontrada} {expressao_achado} = {eval(f'{situacao_encontrada} {expressao_achado}')}")
        return eval(f'{situacao_encontrada} {expressao_achado}')
    except Exception as e:        
        parsed_tokens = parse_expression(expressao_achado)
        tokens = infix_to_rpn(parsed_tokens)
        
        #print(tokens)

        pilha = []

        for token in tokens:
            if token == '|':
                # Operador OR
                y = pilha.pop()
                x = pilha.pop()
                pilha.append(x or y)
            elif token == '&':
                # Operador AND
                y = pilha.pop()
                x = pilha.pop()
                pilha.append(x and y)
            elif token == '~':
                x = pilha.pop()
                pilha.append(not x)
            else:            
                # Aqui se remove o '.' no final da string pois não está padronizada as respostas.
                # Assim, encontra-se resposta terminando em '.' como 'Não adota' ou 'Não adota.'
                a = re.sub(r'\.$', '', token)
                b = re.sub(r'\.$', '', situacao_encontrada)
                if debug:
                    print(f"    Checa se {a} == {b} - ", a == b)
                pilha.append(a == b)
       
        if len(pilha) == 1:
            if debug:
                print('        Achado:', pilha[0])

            return pilha[0]
        else:
            raise ValueError("Expressão lógica inválida")


def radar_factory(num_vars, frame='circle'):
    """
    Create a radar chart with `num_vars` axes.

    This function creates a RadarAxes projection and registers it.

    Parameters
    ----------
    num_vars : int
        Number of variables for radar chart.
    frame : {'circle', 'polygon'}
        Shape of frame surrounding axes.

    """
    # calculate evenly-spaced axis angles
    theta = np.linspace(0, 2*np.pi, num_vars, endpoint=False)

    class RadarTransform(PolarAxes.PolarTransform):

        def transform_path_non_affine(self, path):
            # Paths with non-unit interpolation steps correspond to gridlines,
            # in which case we force interpolation (to defeat PolarTransform's
            # autoconversion to circular arcs).
            if path._interpolation_steps > 1:
                path = path.interpolated(num_vars)
            return Path(self.transform(path.vertices), path.codes)

    class RadarAxes(PolarAxes):

        name = 'radar'
        # use 1 line segment to connect specified points
        RESOLUTION = 1
        PolarTransform = RadarTransform

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # rotate plot such that the first axis is at the top
            self.set_theta_zero_location('N')

        def fill(self, *args, closed=True, **kwargs):
            """Override fill so that line is closed by default"""
            return super().fill(closed=closed, *args, **kwargs)

        def plot(self, *args, **kwargs):
            """Override plot so that line is closed by default"""
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            # FIXME: markers at x[0], y[0] get doubled-up
            if x[0] != x[-1]:
                x = np.append(x, x[0])
                y = np.append(y, y[0])
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

        def _gen_axes_patch(self):
            # The Axes patch must be centered at (0.5, 0.5) and of radius 0.5
            # in axes coordinates.
            if frame == 'circle':
                return Circle((0.5, 0.5), 0.5)
            elif frame == 'polygon':
                return RegularPolygon((0.5, 0.5), num_vars,
                                      radius=.5, edgecolor="k")
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

        def _gen_axes_spines(self):
            if frame == 'circle':
                return super()._gen_axes_spines()
            elif frame == 'polygon':
                # spine_type must be 'left'/'right'/'top'/'bottom'/'circle'.
                spine = Spine(axes=self,
                              spine_type='circle',
                              path=Path.unit_regular_polygon(num_vars))
                # unit_regular_polygon gives a polygon of radius 1 centered at
                # (0, 0) but we want a polygon of radius 0.5 centered at (0.5,
                # 0.5) in axes coordinates.
                spine.set_transform(Affine2D().scale(.5).translate(.5, .5)
                                    + self.transAxes)
                return {'polar': spine}
            else:
                raise ValueError("Unknown value for 'frame': %s" % frame)

    register_projection(RadarAxes)
    return theta
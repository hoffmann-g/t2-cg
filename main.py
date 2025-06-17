from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *

import time
import copy
import math

from Objeto3D import *

o:Objeto3D
tempo_antes = time.time()
soma_dt = 0
pausado = True
velocidade_animacao = 1
posicao_atual = 0
historico_posicoes = []

distancia_camera = 8.0
angulo_camera_x = 45.0
angulo_camera_y = 45.0
ultimo_x = 0
ultimo_y = 0
mouse_pressionado = False

def inicializar():
    global o, historico_posicoes
    glClearColor(0, 0, 0, 1.0)
    glClearDepth(1.0)
    glDepthFunc(GL_LESS)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_CULL_FACE)
    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
    o = Objeto3D()
    o.carregar_arquivo('Human_Head.obj')
    historico_posicoes = [copy.deepcopy(o.vertices)]
    configurar_luz()
    posicionar_camera()

def configurar_luz():
    luz_ambiente = [0.4, 0.4, 0.4]
    luz_difusa = [0.7, 0.7, 0.7]
    luz_especular = [0.0, 0.0, 0.0]
    posicao_luz = [2.0, 3.0, 0.0]
    especularidade = [0.0, 0.0, 0.0]

    glEnable(GL_COLOR_MATERIAL)
    glEnable(GL_LIGHTING)
    glLightModelfv(GL_LIGHT_MODEL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_AMBIENT, luz_ambiente)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, luz_difusa)
    glLightfv(GL_LIGHT0, GL_SPECULAR, luz_especular)
    glLightfv(GL_LIGHT0, GL_POSITION, posicao_luz)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glMaterialfv(GL_FRONT, GL_SPECULAR, especularidade)
    glMateriali(GL_FRONT, GL_SHININESS, 0)

def posicionar_camera():
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(60, 16/9, 0.01, 50)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

    x = distancia_camera * math.cos(math.radians(angulo_camera_y)) * math.cos(math.radians(angulo_camera_x))
    y = distancia_camera * math.sin(math.radians(angulo_camera_x))
    z = distancia_camera * math.sin(math.radians(angulo_camera_y)) * math.cos(math.radians(angulo_camera_x))

    gluLookAt(x, y, z, 0, 2, 0, 0, 1.0, 0)

def desenhar_ladrilho():
    glColor3f(0.5, 0.5, 0.5)
    glBegin(GL_QUADS)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

    glColor3f(1, 1, 1)
    glBegin(GL_LINE_STRIP)
    glNormal3f(0, 1, 0)
    glVertex3f(-0.5, 0.0, -0.5)
    glVertex3f(-0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, 0.5)
    glVertex3f(0.5, 0.0, -0.5)
    glEnd()

def desenhar_piso():
    glPushMatrix()
    glTranslated(-20, -1, -10)
    for x in range(-20, 20):
        glPushMatrix()
        for z in range(-20, 20):
            desenhar_ladrilho()
            glTranslated(0, 0, 1)
        glPopMatrix()
        glTranslated(1, 0, 0)
    glPopMatrix()

def desenhar_cubo():
    glPushMatrix()
    glColor3f(1, 0, 0)
    glTranslated(0, 0.5, 0)
    glutSolidCube(1)

    glColor3f(0.5, 0.5, 0)
    glTranslated(0, 0.5, 0)
    glRotatef(90, -1, 0, 0)
    glRotatef(45, 0, 0, 1)
    glutSolidCone(1, 1, 4, 4)
    glPopMatrix()

def atualizar_animacao():
    global soma_dt, tempo_antes, posicao_atual, historico_posicoes

    if pausado:
        return

    tempo_agora = time.time()
    delta_time = tempo_agora - tempo_antes
    tempo_antes = tempo_agora
    soma_dt += delta_time

    if soma_dt > 1.0 / 30:
        soma_dt = 0
        for _ in range(1):
            o.proxima_posicao()
            historico_posicoes.append(copy.deepcopy(o.vertices))
            posicao_atual = len(historico_posicoes) - 1
        glutPostRedisplay()

def desenhar():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glMatrixMode(GL_MODELVIEW)
    o.desenhar_vertices()
    glutSwapBuffers()

def processar_teclado(key, x, y):
    global pausado, velocidade_animacao, posicao_atual, historico_posicoes
    
    if key == b' ':
        pausado = not pausado
        print("Animação", "pausada" if pausado else "reproduzindo")
    elif key == b'a' or key == b'A':
        if not pausado:
            pausado = True
        if posicao_atual > 0:
            posicao_atual -= 1
            o.vertices = copy.deepcopy(historico_posicoes[posicao_atual])
            glutPostRedisplay()
    elif key == b'd' or key == b'D':
        if not pausado:
            pausado = True
        if posicao_atual < len(historico_posicoes) - 1:
            posicao_atual += 1
            o.vertices = copy.deepcopy(historico_posicoes[posicao_atual])
            glutPostRedisplay()
        else:
            o.proxima_posicao()
            historico_posicoes.append(copy.deepcopy(o.vertices))
            posicao_atual = len(historico_posicoes) - 1
            glutPostRedisplay()
    else:
        o.rotacao = (1, 0, 0, o.rotacao[3] + 2)    

    glutPostRedisplay()

def processar_mouse(button, state, x, y):
    global mouse_pressionado, ultimo_x, ultimo_y
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_pressionado = True
            ultimo_x = x
            ultimo_y = y
        else:
            mouse_pressionado = False

def processar_movimento_mouse(x, y):
    global angulo_camera_x, angulo_camera_y, ultimo_x, ultimo_y
    if mouse_pressionado:
        dx = x - ultimo_x
        dy = y - ultimo_y
        angulo_camera_y += dx * 0.5
        angulo_camera_x += dy * 0.5
        angulo_camera_x = max(-89, min(89, angulo_camera_x))
        ultimo_x = x
        ultimo_y = y
        posicionar_camera()
        glutPostRedisplay()

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(400, 400)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"T2 - CG")
    inicializar()
    glutDisplayFunc(desenhar)
    glutIdleFunc(atualizar_animacao)
    glutKeyboardFunc(processar_teclado)
    glutMouseFunc(processar_mouse)
    glutMotionFunc(processar_movimento_mouse)
    glutMainLoop()

if __name__ == '__main__':
    main()
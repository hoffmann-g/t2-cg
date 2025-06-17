from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GL import *
from Ponto import *

import random
import math
import time

class Objeto3D:
    def __init__(self):
        # lista de vértices do objeto 3d
        self.vertices = []
        # lista de faces (triângulos) que formam o objeto
        self.faces = []
        # velocidade de cada vértice
        self.velocidade = []
        # ângulo de cada vértice
        self.angulo = []
        # raio de cada vértice
        self.raio = []
        # posição do objeto no espaço 3d
        self.posicao = Ponto(0,0,0)
        # rotação do objeto (eixo x, y, z, ângulo)
        self.rotacao = (0,0,0,0)
        # velocidade vertical de cada vértice
        self.velocidade_y = []
        # posições originais dos vértices
        self.posicoes_originais = []
        # estado atual da animação
        self.estado_animacao = "queda"
        # variáveis de tempo para controle da animação
        self.tempo_estado = time.time()
        self.tempo_inicio_estado = time.time()
        # variáveis para diferentes efeitos de animação
        self.espiral_t = [0.0 for _ in range(0)]
        self.ponto_alto = None
        self.retorno_t = [0.0 for _ in range(0)]
        self.redemoinho_t = [0.0 for _ in range(0)]
        self.comprimir_t = 0.0
        self.explodir_v = []
        self.vibrar_offset = []
        self.tornado_angulo = 0.0
        self.espiral_delay = []
        self.esfera_t = [0.0 for _ in range(0)]
        self.retorno_cabeca_t = [0.0 for _ in range(0)]

    def carregar_arquivo(self, arquivo:str):
        # carrega um arquivo .obj e extrai vértices e faces
        f = open(arquivo, "r")
        for linha in f:
            valores = linha.split(' ')
            if valores[0] == 'v': 
                # processa vértices
                p = Ponto(float(valores[1]), float(valores[2]), float(valores[3]))
                if random.random() < 0.5:
                    self.vertices.append(p)
                    self.posicoes_originais.append(Ponto(p.x, p.y, p.z))
                    self.velocidade.append((random.random() + 0.1))
                    self.angulo.append(math.atan2(float(valores[3]), float(valores[1])))
                    self.raio.append(math.hypot(float(valores[1]), float(valores[3])))
                    self.velocidade_y.append(0.0)

            if valores[0] == 'f':
                # processa faces
                self.faces.append([])
                for vertice_face in valores[1:]:
                    info_face = vertice_face.split('/')
                    self.faces[-1].append(int(info_face[0]) - 1)
                
        # inicializa variáveis de animação
        self.espiral_t = [0.0 for _ in self.vertices]
        self.retorno_t = [0.0 for _ in self.vertices]
        self.vibrar_offset = [Ponto(0,0,0) for _ in self.vertices]
        self.explodir_v = [Ponto(0,0,0) for _ in self.vertices]
        self.espiral_delay = [0.0 for _ in self.vertices]
        # calcula delay para efeito espiral baseado na altura do vértice
        for i, p in enumerate(self.posicoes_originais):
            self.espiral_delay[i] = (1.0 - (p.y - min(p.y for p in self.posicoes_originais)) / 
                                   (max(p.y for p in self.posicoes_originais) - min(p.y for p in self.posicoes_originais))) * 3.0
        self.ponto_alto = max(self.posicoes_originais, key=lambda p: p.y)

    def desenhar_vertices(self):
        # desenha os vértices como esferas sólidas
        glPushMatrix()
        glTranslatef(self.posicao.x, self.posicao.y, self.posicao.z)
        glRotatef(self.rotacao[3], self.rotacao[0], self.rotacao[1], self.rotacao[2])
        glColor3f(1, 1, 1)
        glPointSize(6)

        for v in self.vertices:
            glPushMatrix()
            glTranslate(v.x, v.y, v.z)
            glutSolidSphere(.03, 16, 16)
            glPopMatrix()
        
        glPopMatrix()

    def desenhar_wireframe(self):
        # desenha o objeto em modo wireframe (apenas linhas)
        glPushMatrix()
        glTranslatef(self.posicao.x, self.posicao.y, self.posicao.z)
        glRotatef(self.rotacao[3], self.rotacao[0], self.rotacao[1], self.rotacao[2])
        glColor3f(0, 0, 0)
        glLineWidth(2)        
        
        for f in self.faces:            
            glBegin(GL_LINE_LOOP)
            for iv in f:
                v = self.vertices[iv]
                glVertex(v.x, v.y, v.z)
            glEnd()
        
        glPopMatrix()

    def desenhar(self):
        # desenha o objeto com faces sólidas
        glPushMatrix()
        glTranslatef(self.posicao.x, self.posicao.y, self.posicao.z)
        glRotatef(self.rotacao[3], self.rotacao[0], self.rotacao[1], self.rotacao[2])
        glColor3f(0.34, .34, .34)
        glLineWidth(2)        
        
        for f in self.faces:            
            glBegin(GL_TRIANGLE_FAN)
            for iv in f:
                v = self.vertices[iv]
                glVertex(v.x, v.y, v.z)
            glEnd()
        
        glPopMatrix()

    def proxima_posicao(self):
        # atualiza a posição dos vértices baseado no estado atual da animação
        agora = time.time()
        dt = min(0.05, agora - self.tempo_estado)
        self.tempo_estado = agora

        # chama o método apropriado baseado no estado atual
        if self.estado_animacao == "queda":
            self._atualizar_queda(agora, dt)
        elif self.estado_animacao == "espiral":
            self._atualizar_espiral(agora, dt)
        elif self.estado_animacao == "retorno":
            self._atualizar_retorno(agora, dt)
        elif self.estado_animacao == "comprimir":
            self._atualizar_comprimir(agora, dt)
        elif self.estado_animacao == "vibrar":
            self._atualizar_vibrar(agora, dt)
        elif self.estado_animacao == "explodir":
            self._atualizar_explodir(agora, dt)
        elif self.estado_animacao == "esfera":
            self._atualizar_esfera(agora, dt)
        elif self.estado_animacao == "retorno_cabeca":
            self._atualizar_retorno_cabeca(agora, dt)

    def _atualizar_queda(self, agora, dt):
        # simula a queda dos vértices com física básica
        gravidade = -0.005
        amortecimento = 0.7
        todos_parados = True
        for i, v in enumerate(self.vertices):
            if v.y > 0 and self.velocidade_y[i] == 0:
                self.velocidade_x = [random.uniform(-0.01, 0.01) for _ in self.vertices]
                self.velocidade_z = [random.uniform(-0.01, 0.01) for _ in self.vertices]
            
            # aplica gravidade e movimento
            self.velocidade_y[i] += gravidade
            v.y += self.velocidade_y[i]
            v.x += self.velocidade_x[i]
            v.z += self.velocidade_z[i]
            
            # verifica colisão com o chão
            if v.y <= 0:
                v.y = 0
                if abs(self.velocidade_y[i]) > 0.01:
                    self.velocidade_y[i] = -self.velocidade_y[i] * amortecimento
                    self.velocidade_x[i] *= amortecimento
                    self.velocidade_z[i] *= amortecimento
                    todos_parados = False
                else:
                    self.velocidade_y[i] = 0
                    self.velocidade_x[i] = 0
                    self.velocidade_z[i] = 0
            else:
                todos_parados = False

        # muda para o próximo estado quando todos os vértices pararem
        if todos_parados and agora - self.tempo_inicio_estado > 1.0:
            self.estado_animacao = "espiral"
            self.tempo_inicio_estado = agora
            self.espiral_t = [0.0 for _ in self.vertices]

    def _atualizar_espiral(self, agora, dt):
        # animação em espiral onde os vértices sobem em movimento circular
        terminou = True
        tempo_espiral = agora - self.tempo_inicio_estado
        
        for i, v in enumerate(self.vertices):
            if tempo_espiral >= self.espiral_delay[i]:
                t = self.espiral_t[i]
                if t < 1.0:
                    terminou = False
                    atual = Ponto(v.x, v.y, v.z)
                    alvo = self.ponto_alto
                    
                    # calcula centro da espiral
                    centro_x = sum(p.x for p in self.posicoes_originais) / len(self.posicoes_originais)
                    centro_z = sum(p.z for p in self.posicoes_originais) / len(self.posicoes_originais)
                    
                    # calcula ângulos e raios para movimento espiral
                    angulo_base = math.atan2(atual.z - centro_z, atual.x - centro_x)
                    angulo_espiral = angulo_base + (t * 4.0 * math.pi) + (i * 0.05)
                    
                    raio_max = math.hypot(atual.x - centro_x, atual.z - centro_z)
                    raio_atual = raio_max * (1.0 - t)
                    
                    altura_atual = atual.y + (alvo.y - atual.y) * (t * t)
                    
                    # atualiza posição do vértice
                    v.x = centro_x + math.cos(angulo_espiral) * raio_atual
                    v.z = centro_z + math.sin(angulo_espiral) * raio_atual
                    v.y = altura_atual
                    
                    self.espiral_t[i] += dt * 0.15
                    if self.espiral_t[i] > 1.0:
                        self.espiral_t[i] = 1.0
                else:
                    v.x = self.ponto_alto.x
                    v.y = self.ponto_alto.y
                    v.z = self.ponto_alto.z
        
        # muda para o próximo estado quando a espiral terminar
        if terminou:
            self.estado_animacao = "retorno"
            self.tempo_inicio_estado = agora
            self.retorno_t = [0.0 for _ in self.vertices]

    def _atualizar_retorno(self, agora, dt):
        # animação de retorno dos vértices às suas posições originais
        terminou = True
        tempo_retorno = agora - self.tempo_inicio_estado
        
        for i, v in enumerate(self.vertices):
            t = self.retorno_t[i]
            if t < 1.0:
                terminou = False
                atual = Ponto(v.x, v.y, v.z)
                alvo = self.posicoes_originais[i]
                
                # interpola suavemente entre posição atual e original
                v.x = atual.x + (alvo.x - atual.x) * 0.15
                v.y = atual.y + (alvo.y - atual.y) * 0.15
                v.z = atual.z + (alvo.z - atual.z) * 0.15
                
                self.retorno_t[i] += dt * 0.75
                if self.retorno_t[i] > 1.0:
                    self.retorno_t[i] = 1.0
            else:
                v.x = self.posicoes_originais[i].x
                v.y = self.posicoes_originais[i].y
                v.z = self.posicoes_originais[i].z
        
        # muda para o próximo estado após o retorno
        if terminou and tempo_retorno > 2.0:
            self.estado_animacao = "comprimir"
            self.tempo_inicio_estado = agora
            self.comprimir_t = 0.0

    def _atualizar_comprimir(self, agora, dt):
        # animação que comprime o objeto em direção ao seu centro
        cx = sum(p.x for p in self.posicoes_originais) / len(self.posicoes_originais)
        cy = sum(p.y for p in self.posicoes_originais) / len(self.posicoes_originais)
        cz = sum(p.z for p in self.posicoes_originais) / len(self.posicoes_originais)
        centro = Ponto(cx, cy, cz)
        
        terminou = True
        for i, v in enumerate(self.vertices):
            alvo = Ponto(centro.x, centro.y, centro.z)
            dist = math.hypot(v.x - alvo.x, v.z - alvo.z)
            forca = 0.2 * (1.0 + 1.0 / (dist + 0.1))
            
            # move vértices em direção ao centro
            v.x += (alvo.x - v.x) * forca
            v.y += (alvo.y - v.y) * forca
            v.z += (alvo.z - v.z) * forca
            
            if dist > 0.01:
                terminou = False
        
        self.comprimir_t += dt * 0.5
        if terminou or self.comprimir_t > 1.0:
            self.estado_animacao = "vibrar"
            self.tempo_inicio_estado = agora
            self.vibrar_offset = [Ponto(0,0,0) for _ in self.vertices]

    def _atualizar_vibrar(self, agora, dt):
        # animação que faz o objeto vibrar
        tempo_vibracao = agora - self.tempo_inicio_estado
        
        for i, v in enumerate(self.vertices):
            if random.random() < 0.1:
                # movimento aleatório ocasional
                ang = random.uniform(0, 2*math.pi)
                elev = random.uniform(-0.2, 0.2)
                v.x += math.cos(ang) * 0.1
                v.y += elev * 0.1
                v.z += math.sin(ang) * 0.1
            else:
                # vibração baseada em funções senoidais
                self.vibrar_offset[i].x = math.sin(tempo_vibracao * 20 + i) * 0.05
                self.vibrar_offset[i].y = math.cos(tempo_vibracao * 15 + i) * 0.05
                self.vibrar_offset[i].z = math.sin(tempo_vibracao * 25 + i) * 0.05
                v.x += self.vibrar_offset[i].x
                v.y += self.vibrar_offset[i].y
                v.z += self.vibrar_offset[i].z
        
        # muda para o próximo estado após a vibração
        if tempo_vibracao > 1.5:
            self.estado_animacao = "explodir"
            self.tempo_inicio_estado = agora
            for i, v in enumerate(self.vertices):
                ang = random.uniform(0, 2*math.pi)
                elev = random.uniform(-0.2, 0.2)
                speed = random.uniform(0.1, 0.3)
                self.explodir_v[i] = Ponto(math.cos(ang)*speed, elev, math.sin(ang)*speed)

    def _atualizar_explodir(self, agora, dt):
        # animação que faz o objeto explodir
        for i, v in enumerate(self.vertices):
            v.x += self.explodir_v[i].x
            v.y += self.explodir_v[i].y
            v.z += self.explodir_v[i].z
        
        # muda para o próximo estado após a explosão
        if agora - self.tempo_inicio_estado > 2.0:
            self.estado_animacao = "esfera"
            self.tempo_inicio_estado = agora
            self.esfera_t = [0.0 for _ in self.vertices]

    def _atualizar_esfera(self, agora, dt):
        # animação que reorganiza os vértices em uma esfera
        terminou = True
        tempo_esfera = agora - self.tempo_inicio_estado
        
        # calcula centro da esfera
        cx = sum(p.x for p in self.posicoes_originais) / len(self.posicoes_originais)
        cy = sum(p.y for p in self.posicoes_originais) / len(self.posicoes_originais)
        cz = sum(p.z for p in self.posicoes_originais) / len(self.posicoes_originais)
        centro = Ponto(cx, cy, cz)
        
        raio = 2.0
        n = len(self.vertices)
        
        for i, v in enumerate(self.vertices):
            t = self.esfera_t[i]
            if t < 1.0:
                terminou = False
                atual = Ponto(v.x, v.y, v.z)
                
                # calcula posição na esfera usando fibonacci sphere
                phi = math.pi * (3.0 - math.sqrt(5.0))
                y = 1.0 - (i / float(n - 1)) * 2.0
                radius = math.sqrt(1.0 - y * y)
                
                theta = phi * i
                
                alvo = Ponto(
                    centro.x + raio * radius * math.cos(theta),
                    centro.y + raio * y,
                    centro.z + raio * radius * math.sin(theta)
                )
                
                # interpola suavemente para a nova posição
                v.x = atual.x + (alvo.x - atual.x) * 0.1
                v.y = atual.y + (alvo.y - atual.y) * 0.1
                v.z = atual.z + (alvo.z - atual.z) * 0.1
                
                self.esfera_t[i] += dt * 0.5
                if self.esfera_t[i] > 1.0:
                    self.esfera_t[i] = 1.0
        
        # muda para o próximo estado após formar a esfera
        if terminou and tempo_esfera > 2.0:
            self.estado_animacao = "retorno_cabeca"
            self.tempo_inicio_estado = agora
            self.retorno_cabeca_t = [0.0 for _ in self.vertices]

    def _atualizar_retorno_cabeca(self, agora, dt):
        # animação final que retorna os vértices às suas posições originais
        terminou = True
        tempo_retorno = agora - self.tempo_inicio_estado
        
        for i, v in enumerate(self.vertices):
            t = self.retorno_cabeca_t[i]
            if t < 1.0:
                terminou = False
                atual = Ponto(v.x, v.y, v.z)
                alvo = self.posicoes_originais[i]
                
                # interpola suavemente para a posição original
                v.x = atual.x + (alvo.x - atual.x) * 0.1
                v.y = atual.y + (alvo.y - atual.y) * 0.1
                v.z = atual.z + (alvo.z - atual.z) * 0.1
                
                self.retorno_cabeca_t[i] += dt * 0.5
                if self.retorno_cabeca_t[i] > 1.0:
                    self.retorno_cabeca_t[i] = 1.0
            else:
                v.x = self.posicoes_originais[i].x
                v.y = self.posicoes_originais[i].y
                v.z = self.posicoes_originais[i].z
        
        # reinicia a animação após o retorno
        if terminou and tempo_retorno > 2.0:
            for i, v in enumerate(self.vertices):
                v.x = self.posicoes_originais[i].x
                v.y = self.posicoes_originais[i].y + random.uniform(2, 4)
                v.z = self.posicoes_originais[i].z
                self.velocidade_y[i] = 0.0
            self.estado_animacao = "queda"
            self.tempo_inicio_estado = agora




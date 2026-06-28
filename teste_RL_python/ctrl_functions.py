import numpy as np
import matplotlib.pyplot as plt
import control as ct
import math
import json
import os


def leitura(caminho):
    try:
        with open(caminho, 'r') as f:
            dados_json = json.load(f)
    except FileNotFoundError:
        print(f"Erro: '{caminho}' não encontrado. Por favor, certifique-se de que o arquivo foi enviado para o Google Drive e a variável 'caminho_arquivo' aponta para o local correto.")
        raise # Relança o erro para parar a execução
    except json.JSONDecodeError:
        print(f"Erro: Não foi possível decodificar o arquivo JSON em '{caminho}'. Verifique a formatação do arquivo.")
        raise # Relança o erro para parar a execução

    t = []
    y = []

    for registro in dados_json:
        t.append(float(registro['tempo_segundos']))
        y.append(float(registro['temperatura']))

    t = np.array(t)
    y = np.array(y)
    return t, y


def tempo_morto(y, y_init):
    for i in range(len(y)):
        if ((y[i] - 1) > y_init):
            t_morto = i - 1
            return t_morto
    return 0


def ft_1_levantamento(t, y, u):
    y_init = y[0]
    t_morto = tempo_morto(y, y_init)

    y_0 = y - y_init
    y_norm = y_0 / u

    # Calculando o ganho de regime permanente (k)
    tam_janela = len(y_norm)//10
    k = np.mean(y_norm[-tam_janela:])

    point_1_tau = 0.632 * k

    idx_tau = np.where(y_norm >=  point_1_tau)[0]
    tau = t[idx_tau[0]] - t_morto
    a = 1/tau

    return k, a, tau, y_init, t_morto

def ZOH(k, a, t_a, t_morto):
    espo= np.exp(-a * t_a)
    num =[]
    num.append(k *(1 - espo))
    if (t_a >= 2):
        for i in range(t_a - 1):
            num.append(0)
    num.append(k * (- 1 + espo))
    den = [1, - 1 - espo, espo]
    if (t_morto != 0):
        num_tm = [1]
        den_tm = [1 if i == 0 else 0 for i in range(t_morto + 1)]
        G_D = ct.series(ct.tf(num, den, dt=t_a), ct.tf(num_tm, den_tm, dt=t_a))
    else:
        G_D = ct.tf(num, den, dt=t_a)
    return G_D


def sind(angulo_graus):
  return math.sin(math.radians(angulo_graus))

def cosd(angulo_graus):
  return math.cos(math.radians(angulo_graus))

def tand(angulo_graus):
  return math.tan(math.radians(angulo_graus))

def arctand(valor):
  return math.degrees(math.atan(valor))


def metodos_disc(kp, ki, t_a, G, G_D, metodo_projeto, pasta_destino):
    num = [kp, ki]
    den = [1, 0]
    C = ct.tf(num, den)

    numCT = [kp + (t_a*ki)/2, (t_a*ki/2) - kp]
    denCT = [1, -1]
    CT = ct.tf(numCT, denCT, dt=t_a)

    numCEP = [kp, + t_a*ki - kp]
    denCEP = [1, -1]
    CEP = ct.tf(numCEP, denCEP, dt=t_a)

    numCER = [kp + t_a*ki, - kp]
    denCER = [1, -1]
    CER = ct.tf(numCER, denCER, dt=t_a)

    # FTMF Continua com controlador
    T = ct.feedback(C * G)
    print(f"FTMF com controlador discretizado por metodo Trapeziodal:\n {T}\n")

    # FTMF com controlador discretizado por metodo Trapeziodal
    T_Trapezoidal = ct.feedback(CT * G_D)
    print(f"FTMF com controlador discretizado por metodo Trapeziodal:\n {T_Trapezoidal}\n")

    # FTMF com controlador discretizado por metodo Euler progressivo
    T_Euler_P = ct.feedback(CEP * G_D)
    print(f"FTMF com controlador discretizado por metodo Euler progressivo:\n {T_Euler_P}\n")

    # FTMF com controlador discretizado por metodo Euler regressivo
    T_Euler_R = ct.feedback(CER * G_D)
    print(f"FTMF com controlador discretizado por metodo Euler regressivo:\n {T_Euler_R}\n")
                                                                            
    t_t, temperatura_t = ct.step_response(T, T=np.arange(0, 4020, 1))
    t_t_trap, temperatura_t_trap = ct.step_response(T_Trapezoidal, T=np.arange(0, 4020, 1))
    t_t_euler_p, temperatura_t_euler_p = ct.step_response(T_Euler_P, T=np.arange(0, 4020, 1))
    t_t_euler_r, temperatura_t_euler_r = ct.step_response(T_Euler_R, T=np.arange(0, 4020, 1))

    # --- CONFIGURAÇÃO GLOBAL DE LAYOUT FINO ---
    plt.rcParams['axes.linewidth'] = 0.5    # Deixa as bordas dos gráficos bem finas
    plt.rcParams['grid.linewidth'] = 0.3    # Deixa as linhas do grid super sutis
    plt.rcParams['lines.linewidth'] = 0.7   # Espessura padrão para qualquer linha plotada

    plt.figure(figsize=(10, 8))

    # 1. Resposta Contínua
    plt.subplot(2, 2, 1)
    plt.plot(t_t, temperatura_t, label='Resposta Continua', color='blue')
    plt.grid(True, linestyle='--', alpha=0.5) # Grid tracejado e sutil
    plt.xlabel('t, s', fontsize=9)
    plt.ylabel('Temperatura, °C', fontsize=9)
    plt.tick_params(axis='both', labelsize=8, width=0.5) # Riscos dos eixos mais finos
    plt.legend(loc='best', fontsize=8, frameon=True, edgecolor='none') # Legenda limpa

    # 2. Trapezoidal
    plt.subplot(2, 2, 2)
    plt.plot(t_t_trap, temperatura_t_trap, label='Trapezoidal', color='orange')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlabel('t, s', fontsize=9)
    plt.ylabel('Temperatura, °C', fontsize=9)
    plt.tick_params(axis='both', labelsize=8, width=0.5)
    plt.legend(loc='best', fontsize=8, frameon=True, edgecolor='none')

    # 3. Euler Progressivo
    plt.subplot(2, 2, 3)
    plt.plot(t_t_euler_p, temperatura_t_euler_p, label='Euler Progressivo', color='green')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlabel('t, s', fontsize=9)
    plt.ylabel('Temperatura, °C', fontsize=9)
    plt.tick_params(axis='both', labelsize=8, width=0.5)
    plt.legend(loc='best', fontsize=8, frameon=True, edgecolor='none')

    # 4. Euler Regressivo
    plt.subplot(2, 2, 4)
    plt.plot(t_t_euler_r, temperatura_t_euler_r, label='Euler Regressivo', color='red')
    plt.grid(True, linestyle='--', alpha=0.5)
    plt.xlabel('t, s', fontsize=9)
    plt.ylabel('Temperatura, °C', fontsize=9)
    plt.tick_params(axis='both', labelsize=8, width=0.5)
    plt.legend(loc='best', fontsize=8, frameon=True, edgecolor='none')

    plt.tight_layout()
    plt.savefig(os.path.join(pasta_destino, f'Comparação do metodos de discretização {metodo_projeto}.png'), dpi=300)
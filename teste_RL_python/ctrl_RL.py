import numpy as np
import matplotlib.pyplot as plt
import control as ct
import math
import json
import os

pasta_destino = "figuras_ctrl_RL"
os.makedirs(pasta_destino, exist_ok=True)

# TRATAMENTO DOS DADOS PARA LEVANTAMENTO DA FTMA

# Buscando o arquivo degral.csv no meu drive
caminho_arquivo = r'C:\Users\wirkl\Documents\PlatformIO\Projects\projeto_CD_wirkley\dados_temperatura_67_minutos.json'

try:
  with open(caminho_arquivo, 'r') as f:
    dados_json = json.load(f)
except FileNotFoundError:
  print(f"Erro: '{caminho_arquivo}' não encontrado. Por favor, certifique-se de que o arquivo foi enviado para o Google Drive e a variável 'caminho_arquivo' aponta para o local correto.")
  raise # Relança o erro para parar a execução
except json.JSONDecodeError:
  print(f"Erro: Não foi possível decodificar o arquivo JSON em '{caminho_arquivo}'. Verifique a formatação do arquivo.")
  raise # Relança o erro para parar a execução

k_in = 127

t_orig = []
temperatura_orig = []

for registro in dados_json:
  t_orig.append(float(registro['tempo_segundos']))
  temperatura_orig.append(float(registro['temperatura']))

t_orig = np.array(t_orig)
temperatura_orig = np.array(temperatura_orig)

# Determina a temperatura inicial
temperatura_inicial = temperatura_orig[0]

# Determinar tempo morto
for i in range(len(temperatura_orig)):
  if ((temperatura_orig[i] - 1) > temperatura_inicial):
    tempo_morto = i - 1
    break
print(f'tempo morto = {tempo_morto}')

# Desloca os dados de temperatura para que comecem em zero para o cálculo dos parâmetros
temperatura_orig_shifted = temperatura_orig - temperatura_inicial
temperatura_orig_shifted = temperatura_orig_shifted / k_in

# Calculando o ganho de regime permanente (k)
tamanho_janela = len(temperatura_orig_shifted)//10
k = np.mean(temperatura_orig_shifted[-tamanho_janela:])
print(f"k = {k:.2f}")

target_value_for_tau = 0.632 * k

idx_for_tau = np.where(temperatura_orig_shifted >= target_value_for_tau)[0]
tau = t_orig[idx_for_tau[0]] - tempo_morto
print(f"tau = {tau:.2f} s\n")

a = 1/tau
print(f"a = {a:.4f} 1/s\n")

t_sim = np.linspace(t_orig.min(), t_orig.max(),len(t_orig))

# FUNÇÃO TRANSFERÊNCIA G(s) - Modelo de Primeira Ordem

numGSTM = [k*a]
denGSTM = [1, a]

G = ct.tf(numGSTM, denGSTM)

numTM, denTM = ct.pade(tempo_morto, 2)
GTM = ct.series(G, ct.tf(numTM, denTM))

print(f"G(s):\n {GTM}\n")

t_g, temperatura_g_response1 = ct.step_response(GTM, T=t_sim)
temperatura_g_response = temperatura_g_response1 * k_in
temperatura_g_adjusted = temperatura_g_response + temperatura_inicial

plt.figure()
plt.plot(t_orig,temperatura_orig, label='Resposta levantada experimentalmente')
plt.plot(t_g, temperatura_g_adjusted, label='Resposta do modelo matemático (1ª Ordem)')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, C°')
plt.legend(loc='best')
plt.grid()
plt.xlim(t_orig.min(), t_orig.max())
plt.title('Resposta ao Degrau')
plt.savefig(os.path.join(pasta_destino, 'resposta_degrau.png'), dpi=300)
plt.show()

# Plotando apenas a resposta do modelo matemático a um degrau unitário
plt.figure()
plt.plot(t_g, temperatura_g_response1, label='Resposta do modelo matemático (1ª Ordem)')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, C°')
plt.legend(loc='best')
plt.grid()
plt.xlim(t_orig.min(), t_orig.max())
plt.title('Resposta ao Degrau')
plt.savefig(os.path.join(pasta_destino, 'resposta_degrau_unitario.png'), dpi=300)


# Plotando a resposta do modelo matemático a um degrau unitário e a resposta discreta
espon_c = np.exp(- 1 / tau)

numZ =  [0, k * (1 - espon_c), k * (- 1 + espon_c)]
denZ = [1, - 1 - espon_c, espon_c]
FTDSTM = ct.tf(numZ, denZ, dt=1)
numTMZ = [1]
denTMZ = [1 if i == 0 else 0 for i in range(tempo_morto + 1)]

FTD = ct.series(FTDSTM, ct.tf(numTMZ, denTMZ, dt=1))


print(f"FTD(z):\n {FTD}\n")

t_d, y_d = ct.step_response(FTD, T=np.arange(0, 4020, 1))

plt.figure()
plt.plot(t_g, temperatura_g_response1, label='Resposta do modelo matemático (1ª Ordem)')
plt.plot(t_d, y_d, '--', label='Discreta')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, C°')
plt.legend()
plt.grid()
plt.xlim(t_orig.min(), t_orig.max())
plt.title('Resposta ao Degrau - Comparação entre modelo contínuo e discreto')
plt.savefig(os.path.join(pasta_destino, 'resposta_degrau_comparacao.png'), dpi=300)

# Controlador: C(z) = 1
C1 = ct.TransferFunction([1],[1], dt=1)
print(f"C(z):\n {C1}\n")

# FTMF: T(z) = C(z)G(z) / (1 + C(z)FTD(z))
T1 = ct.feedback(C1 * FTD)
print(f"FTMF:\n {T1}\n")

t_t1, theta_t1 = ct.step_response(T1, T=np.arange(0, 4020, 1))
step = np.ones_like(t_t1) * 1.0 # Define a reference step signal of amplitude 1.0

#Plotando o gráfico
plt.figure()
plt.plot(t_t1, step, 'b--', label='Referência') # Plot the reference step
plt.plot(t_t1, theta_t1, label='Resposta SEM controlador, C(z) = 1')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, °C')
plt.legend(loc='best')
plt.grid()
plt.xlim(t_orig.min(), t_orig.max())
plt.title('Resposta ao Degrau')
plt.savefig(os.path.join(pasta_destino, 'resposta_degrau_sem_controlador.png'), dpi=300)

# Funções para respostas de funções trigonometricas em graus

def sind(angulo_graus):
  return math.sin(math.radians(angulo_graus))

def cosd(angulo_graus):
  return math.cos(math.radians(angulo_graus))

def tand(angulo_graus):
  return math.tan(math.radians(angulo_graus))

def arctand(valor):
  return math.degrees(math.atan(valor))

# CONTROLADOR

# Variaveis
Mp_ftmf = 0.1
Ts_2_ftmf = 600

# Calculando zeta e wn
zeta_ftmf = -np.log(Mp_ftmf)/np.sqrt(np.pi**2 + np.log(Mp_ftmf)**2)
wn_ftmf = 4/(Ts_2_ftmf*zeta_ftmf)
print(f"zeta_ftmf = {zeta_ftmf:.4f}")
print(f"wn_ftmf = {wn_ftmf:.4f}\n")

# Definir ponto a que o Root Locus deve mapear
sigma_i = - wn_ftmf*zeta_ftmf
w_i = np.sqrt(wn_ftmf**2 - sigma_i**2)
print(f"sigma_i = {sigma_i:.4f}")
print(f"w_i = {w_i:.4f}\n")

# Ponto que o RL precisa mapear
print(f"s = {sigma_i:.4f} + j{w_i:.4f}\n")

# Plotando RL de FTMA G(s)
plt.figure()
ct.root_locus(G)
plt.plot(sigma_i, w_i, 'ro')
plt.title('Root Locus of G(s)')
plt.xlabel('Real Axis')
plt.ylabel('Imaginary Axis')
plt.grid()
plt.savefig(os.path.join(pasta_destino, 'root_locus_G(s).png'), dpi=300)

# CALCULO DO CONTROLADOR PI
# Calcular o polos da G(s)
p0 = - a
# Calcular o polo do controlador PI
ppi = 0

# Separando a parte real (sigma) e imaginária (w) dos polos
sigma_p0 = p0
w_p0 = 0

print(f"s_p0 = {sigma_p0:.4f}\n")

# Condição Angular
# theta_pid
alfa_pi = arctand(w_i/np.abs(sigma_i))
theta_pi = 180 - alfa_pi
print(f"theta_pi = {theta_pi:.4f}")

# theta_p0
alfa_p0 = arctand((w_i - w_p0)/(np.abs(sigma_i) - np.abs(sigma_p0)))
theta_p0 = 180 - alfa_p0
print(f"theta_p0 = {theta_p0:.4f}")


# Calculo de theta_z
theta_z0 = theta_pi + theta_p0 -180

print(f"theta_z0 = {theta_z0:.4f}\n")

# Calculo de z0
if theta_z0 > 90:
  x0 = w_i/tand(180 - theta_z0)
  z0 = sigma_i + x0
elif theta_z0 == 90:
  z0 = sigma_i
else:
  x0 = w_i/tand(theta_z0)
  z0 = sigma_i - x0

print(f"z0 = {z0:.4f}\n")

# calculo kp, ki
Az0 = np.sqrt(w_i**2 + (sigma_i - z0)**2)

Ap0 = np.sqrt((w_i - w_p0)**2 + (sigma_i - sigma_p0)**2)

Api = np.sqrt(w_i**2 + sigma_i**2)

kp = (Ap0*Api)/(numGSTM[0]*Az0) # Ganho propocional
ki = np.abs(z0)*kp # Ganho integral

print(f"kp = {kp:.2f}")
print(f"ki = {ki:.2f}\n")

# Definir numerador e denominador da função transferencia C(s)
numC = [kp, ki] # Representa numerador de C(s)
denC = [1, 0] # Representa denominador de C(s)
C = ct.tf(numC,denC) # Controlador: C(s)
print(f"C(s):\n {C}\n")

# FTMF: T(s) = C(s)G(s) / (1 + C(s)G(s))
T = ct.feedback(C * G)
print(f"FTMF:\n {T}\n")
print(f'Zeros:\ns = {np.roots(numC)[0]:.4f}\n')

# Plotando RL com ponto dejado de mapear
plt.figure()
ct.root_locus(C*G)
plt.plot(sigma_i, w_i, 'ro')
plt.title('Root Locus of G(s)')
plt.xlabel('Real Axis')
plt.ylabel('Imaginary Axis')
plt.grid()
plt.savefig(os.path.join(pasta_destino, 'root_locus_CG(s).png'), dpi=300)

# Calculo das informações da respota ao degrau da T(s)
step_info_T = ct.step_info(T)

# Extraindo e plotando as especifiçãoes da função ct.step_info
print(f"Tr: {step_info_T['RiseTime']:.2f} s")
print(f"Tp: {step_info_T['PeakTime']:.2f} s")
print(f"Mp: {step_info_T['Overshoot']:.2f}%")
print(f"Ts: {step_info_T['SettlingTime']:.2f} s (2% tolerancia)")
print(f"temperatura_rp: {step_info_T['SteadyStateValue']:.2f}")

# Plotando noo gráfico as curvas com controlador PID, sem controlador PID e referncia
t_t, theta_t = ct.step_response(T, T=np.arange(0, 4020, 1))
step = np.ones_like(t_t) * 1.0 # Define a reference step signal of amplitude 1.0

plt.figure()
plt.plot(t_t, step, 'b--', label='Referência') # Plot the reference step
plt.plot(t_t, theta_t, label='Resposta COM controlador PI')
plt.plot(t_t1, theta_t1, label='Resposta SEM controlador PI')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, °C')
plt.legend(loc='lower right')
plt.grid()
plt.xlim(t_orig.min(), t_orig.max())
plt.title('Resposta ao Degrau')
plt.savefig(os.path.join(pasta_destino, 'resposta_degrau_comparacao_controlador.png'), dpi=300)

# DISCRETIZANDO O CONTROLADOR PI
numCT = [2*kp + ki, ki - 2*kp]
denCT = [2, -2]
CT = ct.tf(numCT, denCT, dt=1)

numCEP = [kp + ki, - 1]
denCEP = [1, -1]
CEP = ct.tf(numCEP, denCEP, dt=1)

numCER = [kp, ki - kp]
denCER = [1, -1]
CER = ct.tf(numCER, denCER, dt=1)

# FTMF com controlador discretizado por metodo Trapeziodal
T_Trapezoidal = ct.feedback(CT * FTD)
print(f"FTMF com controlador discretizado por metodo Trapeziodal:\n {T_Trapezoidal}\n")

# FTMF com controlador discretizado por metodo Euler progressivo
T_Euler_P = ct.feedback(CEP * FTD)
print(f"FTMF com controlador discretizado por metodo Euler progressivo:\n {T_Euler_P}\n")

# FTMF com controlador discretizado por metodo Euler regressivo
T_Euler_R = ct.feedback(CER * FTD)
print(f"FTMF com controlador discretizado por metodo Euler regressivo:\n {T_Euler_R}\n")
                                                                         
# Plotando a resposta ao degrau do sistema com controlador PI discretizado por metodo Trapeziodal
t_t_trap, theta_t_trap = ct.step_response(T_Trapezoidal, T=np.arange(0, 4020, 1))
plt.figure()
plt.plot(t_t_trap, theta_t_trap, label='Resposta COM controlador PI discretizado por metodo Trapeziodal')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, °C')
plt.legend(loc='lower right')
plt.grid()
plt.title('Resposta ao Degrau')
plt.savefig(os.path.join(pasta_destino, 'resposta_degrau_Trapezoidal.png'), dpi=300)

# Plotando a resposta ao degrau do sistema com controlador PI discretizado por metodo Euler progressivo
t_t_euler_p, theta_t_euler_p = ct.step_response(T_Euler_P, T=np.arange(0, 4020, 1))
plt.figure()
plt.plot(t_t_euler_p, theta_t_euler_p, label='Resposta COM controlador PI discretizado por metodo Euler progressivo')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, °C')
plt.legend(loc='lower right')
plt.grid()
plt.title('Resposta ao Degrau')
plt.savefig(os.path.join(pasta_destino, 'resposta_degrau_Euler_P.png'), dpi=300)

# Plotando a resposta ao degrau do sistema com controlador PI discretizado por metodo Euler regressivo
t_t_euler_r, theta_t_euler_r = ct.step_response(T_Euler_R, T=np.arange(0, 4020, 1))
plt.figure()
plt.plot(t_t_euler_r, theta_t_euler_r, label='Resposta COM controlador PI discretizado por metodo Euler regressivo')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, °C')
plt.legend(loc='lower right')
plt.grid()
plt.title('Resposta ao Degrau')
plt.savefig(os.path.join(pasta_destino, 'resposta_degrau_Euler_R.png'), dpi=300)

# Comparando as respostas ao degrau dos sistemas com controlador PI discretizado por metodo Trapeziodal e em tempo contínuo
plt.figure()
plt.plot(t_t, theta_t, label='Resposta COM controlador PI em tempo contínuo')
plt.plot(t_t_trap, theta_t_trap, '--', label='Resposta COM controlador PI discretizado por metodo Trapeziodal')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, °C')
plt.legend(loc='lower right')
plt.grid()
plt.title('Resposta ao Degrau')
plt.savefig(os.path.join(pasta_destino, 'resposta_degrau_comparacao_discreto_continuo.png'), dpi=300)
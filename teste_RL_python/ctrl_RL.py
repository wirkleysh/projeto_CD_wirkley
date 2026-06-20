import numpy as np
import matplotlib.pyplot as plt
import control as ct
import math
import json

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
T_initial = temperatura_orig[0]

# Desloca os dados de temperatura para que comecem em zero para o cálculo dos parâmetros
temperatura_orig_shifted = temperatura_orig - T_initial
temperatura_orig_shifted = temperatura_orig_shifted / k_in

# Calculando o ganho de regime permanente (k)
tamanho_janela = len(temperatura_orig_shifted)//10
k = np.mean(temperatura_orig_shifted[-tamanho_janela:])
print(f"k = {k:.2f}")

target_value_for_tau = 0.632 * k

idx_for_tau = np.where(temperatura_orig_shifted >= target_value_for_tau)[0]
tau = t_orig[idx_for_tau[0]]
print(f"tau = {tau:.2f} s\n")

t_sim = np.linspace(t_orig.min(), t_orig.max(),len(t_orig))

# FUNÇÃO TRANSFERÊNCIA G(s) - Modelo de Primeira Ordem

numG = [k]
denG = [tau, 1]

# Criando a função transferencia G
G = ct.TransferFunction(numG, denG)

print(f"G(s):\n {G}\n")


t_g, temperatura_g_response1 = ct.step_response(G, T=t_sim)
temperatura_g_response = temperatura_g_response1 * k_in
temperatura_g_adjusted = temperatura_g_response + T_initial

plt.figure()
plt.plot(t_orig,temperatura_orig, label='Resposta levantada experimentalmente')
plt.plot(t_g, temperatura_g_adjusted, label='Resposta do modelo matemático (1ª Ordem)')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, C°')
plt.legend(loc='best')
plt.grid()
plt.xlim(t_orig.min(), t_orig.max())
plt.title('Resposta ao Degrau')
plt.savefig('resposta_degrau.png', dpi=300)

# Plotando apenas a resposta do modelo matemático a um degrau unitário
plt.figure()
plt.plot(t_g, temperatura_g_response1, label='Resposta do modelo matemático (1ª Ordem)')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, C°')
plt.legend(loc='best')
plt.grid()
plt.xlim(t_orig.min(), t_orig.max())
plt.title('Resposta ao Degrau')
plt.savefig('resposta_degrau_unitario.png', dpi=300)


# Plotando a resposta do modelo matemático a um degrau unitário e a resposta discreta
espon_c = np.exp(- 1 / tau)

numZ =  [0, k * (1 - espon_c), k * (- 1 + espon_c)]
denZ = [1, - 1 - espon_c, espon_c]
FTD = ct.TransferFunction(numZ, denZ, dt=1)
print(f"FTD(z):\n {FTD}\n")

t_d, y_d = ct.step_response(FTD, T=np.arange(0, 4020, 1))

plt.figure()
plt.plot(t_g, temperatura_g_response1, label='Resposta do modelo matemático (1ª Ordem)')
plt.plot(t_d, y_d, '--', label='Discreta')
plt.xlabel('t, s')
plt.ylabel('Resposta')
plt.legend()
plt.grid()
plt.xlim(t_orig.min(), t_orig.max())
plt.title('Resposta ao Degrau - Comparação entre modelo contínuo e discreto')
plt.savefig('resposta_degrau_comparacao.png', dpi=300)

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
plt.ylabel(r'$\Theta$, °')
plt.legend(loc='best')
plt.grid()
plt.xlim(t_orig.min(), t_orig.max())
plt.title('Resposta ao Degrau')
plt.savefig('resposta_degrau_sem_controlador.png', dpi=300)

# Funções para respostas de funções trigonometricas em graus

def sind(angulo_graus):
  return math.sin(math.radians(angulo_graus))

def cosd(angulo_graus):
  return math.cos(math.radians(angulo_graus))

def tand(angulo_graus):
  return math.tan(math.radians(angulo_graus))

def arctand(valor):
  return math.degrees(math.atan(valor))

# CONTROLADOR PI

# Variaveis
Mp_ftmf = 0.2
Ts_2_ftmf = 1000

# Calcular o polos da G(s)
p0 = -1/tau
ppi = 0
# Separando a parte real (sigma) e imaginária (w) dos polos
sigma_p0 = p0
w_p0 = 0

print(f"s_p0 = {sigma_p0:.4f} {w_p0:.4f}j\n")


# Calculando zeta e wn
zeta_ftmf = -np.log(Mp_ftmf)/np.sqrt(np.pi**2 + np.log(Mp_ftmf)**2)
wn_ftmf = 4/(Ts_2_ftmf*zeta_ftmf)
print(f"zeta_ftmf = {zeta_ftmf:.3f}")
print(f"wn_ftmf = {wn_ftmf:.3f}\n")

# Definir ponto a que o Root Locus deve mapear
sigma_i = - wn_ftmf*zeta_ftmf
w_i = np.sqrt(wn_ftmf**2 - sigma_i**2)
print(f"sigma_i = {sigma_i:.2f}")
print(f"w_i = {w_i:.2f}\n")

# Ponto que o RL precisa mapear
print(f"s = {sigma_i:.2f} + j{w_i:.2f}\n")

# Condição Angular
# theta_pid
alfa_pid = arctand(w_i/np.abs(sigma_i))
theta_pid = 180 - alfa_pid
print(f"theta_pid = {theta_pid:.2f}")

# theta_p0
alfa_p0 = arctand((w_i - w_p0)/(np.abs(sigma_i) - np.abs(sigma_p0)))
theta_p0 = 180 - alfa_p0
print(f"theta_p0 = {theta_p0:.2f}")


# Calculo de theta_z0 e theta_z1
theta_z0 = 80 # atribuindo um valor a theta_z0
theta_z1 = theta_pid + theta_p0 - theta_z0 -180
print(f"theta_z0 = {theta_z0:.2f}")
print(f"theta_z1 = {theta_z1:.2f}\n")

# Calculo de z0 e z1
if theta_z0 > 90:
  x0 = w_i/tand(180 - theta_z0)
  z0 = sigma_i + x0
elif theta_z0 == 90:
  z0 = sigma_i
else:
  x0 = w_i/tand(theta_z0)
  z0 = sigma_i - x0

if theta_z1 > 90:
  x1 = w_i/tand(180 - theta_z1)
  z1 = sigma_i + x1
elif theta_z1 == 90:
  z1 = sigma_i
else:
  x1 = w_i/tand(theta_z1)
  z1 = sigma_i - x1

print(f"z0 = {z0:.2f}")
print(f"z1 = {z1:.2f}\n")
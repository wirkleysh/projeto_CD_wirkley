import numpy as np
import matplotlib.pyplot as plt
import control as ct
import math
import os
import ctrl_functions as lc

pasta_planta = "figuras_ctrl_planta"
pasta_RL = "figuras_ctrl_RL"
pasta_CHR = "figuras_ctrl_CHR"
pasta_IMC = "figuras_ctrl_IMC"
pasta_ZN = "figuras_ctrl_ZN"
pasta_DB = "figuras_ctrl_DB"


os.makedirs(pasta_planta, exist_ok=True)
os.makedirs(pasta_RL, exist_ok=True)
os.makedirs(pasta_CHR, exist_ok=True)
os.makedirs(pasta_IMC, exist_ok=True)
os.makedirs(pasta_ZN, exist_ok=True)
os.makedirs(pasta_DB, exist_ok=True)




# TRATAMENTO DOS DADOS PARA LEVANTAMENTO DA FTMA

# Buscando o arquivo degral.csv no meu drive
caminho_arquivo = r'/home/wirkley/Documentos/platformIO/projeto_CD_wirkley/dados_temperatura_67_minutos.json'

u = 127
t_a = 1

t, y = lc.leitura(caminho_arquivo)

k, a, tau, temperatura_inicial, t_morto = lc.ft_1_levantamento(t, y, u)
print(k, a, tau)

t_sim = np.linspace(t.min(), t.max(),len(t))

# FUNÇÃO TRANSFERÊNCIA G(s) - Modelo de Primeira Ordem

numGSTM = [k*a]
denGSTM = [1, a]

G_STM= ct.tf(numGSTM, denGSTM)
print(f"G_STM(s):\n{G_STM}")

numTM, denTM = ct.pade(t_morto, 1)

G = ct.series(G_STM, ct.tf(numTM, denTM))

print(f"G(s):\n {G}\n")

t_g, temperatura_g_degrau_1 = ct.step_response(G, T=t_sim)
temperatura_g_degral_u = temperatura_g_degrau_1 * u
temperatura_g_comp_planta = temperatura_g_degral_u + temperatura_inicial

titulo_1 = 'Comparação - Dados experimentais e Modelo matematico'

plt.figure()
plt.plot(t,y, label='Resposta levantada experimentalmente')
plt.plot(t_g, temperatura_g_comp_planta, label='Resposta do modelo matemático')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, C°')
plt.legend(loc='best')
plt.grid()
plt.xlim(t.min(), t.max())
plt.title(titulo_1)
plt.savefig(os.path.join(pasta_planta, f'{titulo_1}.png'), dpi=300)

titulo_2 = 'Resposta Degrau do Modelo matematico'

plt.figure()
plt.plot(t_g, temperatura_g_degrau_1, label='Resposta do modelo matemático')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, C°')
plt.legend(loc='best')
plt.grid()
plt.xlim(t.min(), t.max())
plt.title(titulo_2)
plt.savefig(os.path.join(pasta_planta, f'{titulo_2}.png'), dpi=300)

# Plotando a resposta do modelo matemático a um degrau unitário e a resposta discreta
G_D = lc.ZOH(k, a, t_a, t_morto)
print(f'G_D(s):\n{G_D}')

t_d, y_d = ct.step_response(G_D, T=np.arange(0, 4020, 1))
titulo_3 = 'Resposta Degrau do Modelos Discreto e Continuo'

plt.figure()
plt.plot(t_g, temperatura_g_degrau_1, label='Resposta Continua')
plt.plot(t_d, y_d, '--', label='Resposta Discreta')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, C°')
plt.legend(loc='best')
plt.grid()
plt.xlim(t.min(), t.max())
plt.title(titulo_3)
plt.savefig(os.path.join(pasta_planta, f'{titulo_3}.png'), dpi=300)


# CONTROLADOR

# Variaveis
Mp_ftmf = 0.01
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
titulo_4 = 'root_locus_G(s)'

plt.figure()
ct.root_locus(G)
plt.plot(sigma_i, w_i, 'ro')
plt.title('Root Locus G(s)')
plt.xlabel('Real Axis')
plt.ylabel('Imaginary Axis')
plt.title(titulo_4)
plt.grid()
plt.savefig(os.path.join(pasta_planta, f'{titulo_4}.png'), dpi=300)


#----------------------------------------Root Locus-------------------------------------------------#

# CALCULO DO CONTROLADOR PI
# Calcular os polos da G(s)
p_0, p_1 = ct.poles(G)

# Calcular o polo do controlador PI
p_pi = 0

# Calculando o zero da G(s)
z_0 = ct.zeros(G)

# Separando a parte real (sigma) e imaginária (w) dos polos
sigma_p0 = p_0.real
w_p0 = p_0.imag

print(f"s_p0 = {sigma_p0:.4f}\n")

sigma_p1 = p_1.real
w_p1 = p_1.imag

print(f"s_p1 = {sigma_p1:.4f}\n")

# Separando a parte real (sigma) e imaginária (w) dos zeros
sigma_z0 = z_0[0].real
w_z0 = z_0[0].imag

print(f"s_z0 = {sigma_z0:.4f}\n")

# Condição Angular
# theta_pi
alfa_pi = lc.arctand(w_i/np.abs(sigma_i))
theta_pi = 180 - alfa_pi
print(f"theta_pi = {theta_pi:.4f}")

# theta_p0
alfa_p0 = lc.arctand((w_i - w_p0)/(np.abs(sigma_i) - np.abs(sigma_p0)))
theta_p0 = 180 - alfa_p0
print(f"theta_p0 = {theta_p0:.4f}")

# theta_p1
alfa_p1 = lc.arctand((w_i - w_p1)/(np.abs(sigma_i) - np.abs(sigma_p1)))
theta_p1 = 180 - alfa_p1
print(f"theta_p1 = {theta_p1:.4f}")

# theta_z0
alfa_z0 = lc.arctand((w_i - w_z0)/(np.abs(sigma_i) - np.abs(sigma_z0)))
theta_z0 = 180 - alfa_z0
print(f"theta_p0 = {theta_p0:.4f}")


# Calculo de theta_zpi
theta_zpi = theta_pi + theta_p0 + theta_p1 - theta_z0 -180

print(f"theta_zpi = {theta_zpi:.4f}\n")

# Calculo de z0
if theta_zpi > 90:
  x_pi = w_i/lc.tand(180 - theta_zpi)
  z_pi = sigma_i + x_pi
elif theta_zpi == 90:
  z_pi = sigma_i
else:
  x_pi = w_i/lc.tand(theta_zpi)
  z_pi = sigma_i - x_pi

print(f"z_pi = {z_pi:.4f}\n")

# calculo kp, ki
Azpi = np.sqrt(w_i**2 + (sigma_i - z_pi)**2)
Az0 = np.sqrt((w_i - w_z0)**2 + (sigma_i - sigma_z0)**2)
Ap0 = np.sqrt((w_i - w_p0)**2 + (sigma_i - sigma_p0)**2)
Ap1 = np.sqrt((w_i - w_p1)**2 + (sigma_i - sigma_p1)**2)
Api = np.sqrt(w_i**2 + sigma_i**2)

kp = (Ap0*Ap1*Api)/(k*a*Azpi*Az0) # Ganho propocional
ki = np.abs(z_pi)*kp # Ganho integral

print(f"kp = {kp:.4f}")
print(f"ki = {ki:.4f}\n")

# Definir numerador e denominador da função transferencia C(s)
numC = np.ravel([kp, ki]) # Representa numerador de C(s)
denC = ([1, 0]) # Representa denominador de C(s)
C = ct.tf(numC,denC) # Controlador: C(s)
print(f"C(s):\n {C}\n")


# FTMF: T(s) = C(s)G(s) / (1 + C(s)G(s))
T = ct.feedback(C * G)
print(f"FTMF:\n {T}\n")
print(f'Zeros:\ns = {np.roots(numC)[0]:.4f}\n')

# Plotando RL com ponto dejado de mapear
titulo_5 = 'root_locus_CG(s)'

plt.figure()
ct.root_locus(C*G)
plt.plot(sigma_i, w_i, 'ro')
plt.title('Root Locus CG(s)')
plt.xlabel('Real Axis')
plt.ylabel('Imaginary Axis')
plt.title(titulo_5)
plt.grid()
plt.savefig(os.path.join(pasta_RL, f'{titulo_5}.png'), dpi=300)

# Calculo das informações da respota ao degrau da T(s)
step_info_T = ct.step_info(T)

# Extraindo e plotando as especifiçãoes da função ct.step_info
print(f"Tr: {step_info_T['RiseTime']:.2f} s")
print(f"Tp: {step_info_T['PeakTime']:.2f} s")
print(f"Mp: {step_info_T['Overshoot']:.2f}%")
print(f"Ts: {step_info_T['SettlingTime']:.2f} s (2% tolerancia)")
print(f"temperatura_rp: {step_info_T['SteadyStateValue']:.2f}")

# Plotando noo gráfico as curvas com controlador PI e referencia
t_t, temperatura_t = ct.step_response(T, T=np.arange(0, 4020, 1))
step = np.ones_like(t_t) * 1.0

titulo_6 = 'Resposta Degrau - Plata com controlador PI - RL'

plt.figure()
plt.plot(t_t, step, 'b--', label='Referência')
plt.plot(t_t, temperatura_t, label='Resposta COM controlador PI')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, C°')
plt.legend(loc='best')
plt.grid()
plt.xlim(t.min(), t.max())
plt.title(titulo_6)
plt.savefig(os.path.join(pasta_RL, f'{titulo_6}.png'), dpi=300)


lc.metodos_disc(kp, ki, t_a, G_D, 'Root Locus', pasta_RL)

#---------------------------------------- CHR -------------------------------------------------#

kp_chr = (0.6 * tau)/(k * t_morto)
ti_chr = 4 * t_morto
ki_chr = kp_chr/ti_chr

print(f"kp_chr = {kp_chr}")
print(f"ki_chr = {ki_chr}")

lc.metodos_disc(kp_chr, ki_chr, t_a, G_D, 'CHR', pasta_CHR)

#---------------------------------------- IMC -------------------------------------------------#

lamb = 2*t_morto
kp_imc = (2*tau - t_morto)/(k*2*lamb)
ti_imc = tau + (lamb/2)
ki_imc = kp_imc/ti_imc

print(f"kp_imc = {kp_imc}")
print(f"ki_imc = {ki_imc}")

lc.metodos_disc(kp_imc, ki_imc, t_a, G_D, 'IMC', pasta_IMC)

#---------------------------------------- DeadBeat -------------------------------------------------#

n = len(ct.poles(G_D)) - len(ct.zeros(G_D))
num_F = [1]
den_F = [1 if i == 0 else (0 if 0 < i < n else - 1) for i in range(n + 1)]

C_DB = ct.series(ct.minreal(1 / G_D), ct.tf(num_F, den_F, dt=t_a))

print(f"C_DB(s):\n {C_DB}\n")

# FTMF: T(s) = C(s)G(s) / (1 + C(s)G(s))
T_DB = ct.feedback(C_DB*G_D)
print(f"FTMF deadbeat:\n {T_DB}\n")

t_db, temperatura_db = ct.step_response(T_DB, T=np.arange(0, 4020, 1))
step = np.ones_like(t_db) * 1.0 # Define a reference step signal of amplitude 1.0

titulo_7 = 'Resposta Degrau - Plata com controle DeadBeat'

plt.figure()
plt.plot(t_t, step, 'b--', label='Referência')
plt.plot(t_db, temperatura_db, label='Resposta COM controle DeadBeat')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, C°')
plt.legend(loc='best')
plt.grid()
plt.xlim(t.min(), t.max())
plt.title(titulo_7)
plt.savefig(os.path.join(pasta_DB, f'{titulo_7}.png'), dpi=300)

#---------------------------------------- ZN -------------------------------------------------#

kp_zn = 28.686
ti_zn = 76.687
ki_zn = kp_zn/ti_zn

print(f"kp_zn = {kp_zn}")
print(f"ki_zn = {ki_zn}")

lc.metodos_disc(kp_zn, ki_zn, t_a, G_D, 'ZN', pasta_ZN)
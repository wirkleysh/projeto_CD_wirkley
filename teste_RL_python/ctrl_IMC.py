import numpy as np
import matplotlib.pyplot as plt
import control as ct
import math
import json
import os
from ctrl_RL import G, FTD, k, tau

pasta_dest_1 = "figuras_ctrl_IMC"
os.makedirs(pasta_dest_1, exist_ok=True)

# Proje
# to pelo metodo IMC
l = 3
kp = tau/(k * l)
ki = tau

print(f"kp = {kp}")
print(f"ki = {ki}")

# FT do Controlador(tempo continuo)
numC = [kp, ki]
demC = [1, 0]
C = ct.tf(numC, demC)
T = ct.feedback(C*G)
print(f'T(s): \n{T}')

# Plotando noo gráfico as curvas com controlador PID, sem controlador PID e referncia
t_t, theta_t = ct.step_response(T, T=np.arange(0, 4020, 1))
step = np.ones_like(t_t) * 1.0 # Define a reference step signal of amplitude 1.0

plt.figure()
plt.plot(t_t, step, 'b--', label='Referência') # Plot the reference step
plt.plot(t_t, theta_t, label='Resposta COM controlador PI')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, °C')
plt.legend(loc='lower right')
plt.grid()
plt.xlim()
plt.title('Resposta ao Degrau')
plt.savefig(os.path.join(pasta_dest_1, 'resposta_degrau.png'), dpi=300)

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
plt.savefig(os.path.join(pasta_dest_1, 'resposta_degrau_Trapezoidal.png'), dpi=300)

# Plotando a resposta ao degrau do sistema com controlador PI discretizado por metodo Euler progressivo
t_t_euler_p, theta_t_euler_p = ct.step_response(T_Euler_P, T=np.arange(0, 4020, 1))
plt.figure()
plt.plot(t_t_euler_p, theta_t_euler_p, label='Resposta COM controlador PI discretizado por metodo Euler progressivo')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, °C')
plt.legend(loc='lower right')
plt.grid()
plt.title('Resposta ao Degrau')
plt.savefig(os.path.join(pasta_dest_1, 'resposta_degrau_Euler_P.png'), dpi=300)

# Plotando a resposta ao degrau do sistema com controlador PI discretizado por metodo Euler regressivo
t_t_euler_r, theta_t_euler_r = ct.step_response(T_Euler_R, T=np.arange(0, 4020, 1))
plt.figure()
plt.plot(t_t_euler_r, theta_t_euler_r, label='Resposta COM controlador PI discretizado por metodo Euler regressivo')
plt.xlabel('t, s')
plt.ylabel(r'Temperatura, °C')
plt.legend(loc='lower right')
plt.grid()
plt.title('Resposta ao Degrau')
plt.savefig(os.path.join(pasta_dest_1, 'resposta_degrau_Euler_R.png'), dpi=300)



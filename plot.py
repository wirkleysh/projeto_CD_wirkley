import json
import sys

try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    print("Erro: matplotlib não está instalado. Instale com: python -m pip install matplotlib")
    sys.exit(1)

# Arquivo gerado pelo coletor
INPUT_FILE = 'dados_temperatura.json'
OUTPUT_FILE = 'grafico_temperatura.png'

try:
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
except FileNotFoundError:
    print(f"Arquivo {INPUT_FILE} não encontrado. Rode primeiro o coletor.")
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"Erro ao ler JSON: {e}")
    sys.exit(1)

# Extrai tempo e temperatura
tempos = []
temps = []
for entry in data:
    # Suporta chaves 'tempo_segundos' ou 'tempo' para compatibilidade
    t = entry.get('tempo_segundos') if 'tempo_segundos' in entry else entry.get('tempo')
    temp = entry.get('temperatura')
    if t is None or temp is None:
        continue
    try:
        tempos.append(float(t))
        temps.append(float(temp))
    except (ValueError, TypeError):
        continue

if not tempos:
    print('Nenhum dado válido encontrado no JSON.')
    sys.exit(1)

# Ordena por tempo caso não esteja ordenado
pairs = sorted(zip(tempos, temps), key=lambda x: x[0])
tempos, temps = zip(*pairs)

plt.figure(figsize=(10, 5))
# Apenas pontos finos (sem linha de conexão)
plt.plot(tempos, temps, linestyle='', marker='o', markersize=2, markeredgewidth=0)
plt.xlabel('Tempo (s)')
plt.ylabel('Temperatura (°C)')
plt.title('Temperatura vs Tempo')
plt.grid(True)
plt.tight_layout()

# Salva e mostra
plt.savefig(OUTPUT_FILE)
print(f'Gráfico salvo em {OUTPUT_FILE}')
plt.show()

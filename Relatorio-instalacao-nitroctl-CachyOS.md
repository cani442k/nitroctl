# Relatório de instalação e adaptações

**Programa:** nitroctl — interface de terminal para controle de hardware de notebooks Acer Nitro.
**Repositórios de origem:** [cani442k/nitroctl](https://github.com/cani442k/nitroctl) e [0x7375646F/Linuwu-Sense](https://github.com/0x7375646F/Linuwu-Sense).
**Data:** 12 de setembro de 2026.
**Autoria:** relatório técnico gerado por assistência automatizada, a pedido do usuário.

---

## 1. Ambiente

| Item | Valor |
| --- | --- |
| Sistema | CachyOS (base Arch), edição contínua |
| Interface gráfica | GNOME, sessão Wayland |
| Kernel | `7.2.4-3-cachyos` |
| Máquina | Acer Nitro ANV15-51 |
| Comprovação do modelo | `/sys/class/dmi/id/product_name` |
| Sessão do shell | `fish` |

---

## 2. Visão geral

O programa verificado é o **nitroctl**, de autoria de terceiros. Ele não controla o hardware diretamente; depende do driver **Linuwu-Sense**, que expõe interfaces no sistema de arquivos virtual do kernel (sysfs), sob `.../nitro_sense/`.

A instalação oficial, no entanto, não era aplicável a este computador por três motivos:

1. o instalador depende das ferramentas gráficas `kdialog` e `qdbus`, próprias do ambiente KDE, ausentes no GNOME;
2. o instalador exige identificação de sistema igual a `arch`; este sistema se identifica como `cachyos`, o que exigiria alteração do arquivo do sistema, decisão que evitei;
3. o driver não compila com GCC, compilador padrão do sistema, porque o kernel CachyOS foi construído com Clang.

O resultado foi uma **instalação adaptada, porém conservadora**: o código-fonte do programa foi mantido intacto, e as adaptações ficaram restritas ao procedimento de instalação, ao comando de compilação do driver e à configuração do serviço de inicialização.

---

## 3. Componentes instalados

O nitroctl é um programa em linguagem Python; o Linuwu-Sense é um módulo de kernel, escrito em linguagem C, carregado diretamente no kernel.

Ambos foram copiados para diretórios administrados pelo sistema, o que os torna acessíveis a qualquer usuário e impede alteração por usuários comuns:

| Componente | Caminho instalado |
| --- | --- |
| Código do programa | `/opt/nitroctl/main/main.py` |
| Licença do programa | `/opt/nitroctl/LICENSE` |
| Comando de abertura | `/usr/local/bin/nitroctl` |
| Código-fonte do driver | `/usr/local/src/linuwu-sense/src/linuwu_sense.c` |
| Compilador do driver | `/usr/local/src/linuwu-sense/Makefile` |
| Módulo compilado | `/usr/lib/modules/7.2.4-3-cachyos/kernel/drivers/platform/x86/linuwu_sense.ko` |
| Bloqueio do driver Acer | `/etc/modprobe.d/blacklist-acer_wmi.conf` |
| Inicialização do driver | `/etc/systemd/system/linuwu_sense.service` |

O registro do módulo no kernel foi atualizado com o comando `depmod -a`, o que permite que o sistema o localize quando necessário.

---

## 4. Adaptação 1 — Bloqueio do driver Acer

O driver Acer fornecido pelo próprio kernel (`acer_wmi`) não oferece o controle de ventoinhas e de perfis térmicos desejado. Para que o Linuwu-Sense assuma essas funções, o driver original precisa permanecer desativado.

A ativação simultânea dos dois drivers geraria conflito no acesso ao hardware; por isso, o bloqueio é uma condição necessária, e não uma preferência.

Arquivo `/etc/modprobe.d/blacklist-acer_wmi.conf`:

```text
blacklist acer_wmi
```

O driver foi removido da memória e substituído durante a instalação. Após a substituição, confirmei que o driver Acer **não** está carregado e que o Linuwu-Sense está ativo com a interface Nitro disponível.

---

## 5. Adaptação 2 — Compilação do driver

### 5.1 Primeira falha: compilador incorreto

A compilação padrão falhou porque o sistema tentou usar o GCC, enquanto o kernel CachyOS foi construído com a suíte LLVM/Clang. Os avisos indicaram essa divergência:

```text
The kernel was built by: clang version 22.1.8
You are using:           gcc (GCC) 16.2.1 20260810
gcc: error: unrecognized command-line option '-mstack-alignment=8'
```

### 5.2 Segunda falha: função ausente

A compilação foi refeita com a opção `LLVM=1`, que instrui o sistema a usar o Clang, mas surgiu um segundo erro, em três trechos do arquivo `linuwu_sense.c`:

```text
error: call to undeclared library function 'strncpy'
ISO C99 and later do not support implicit function declarations
```

A função `strncpy`, usada para copiar um texto para dentro de um espaço de memória, deixou de estar disponível no cabeçalho incluído pelo kernel nesta versão. Isso revela uma incompatibilidade real entre o driver e o kernel atual; portanto, **sem modificação, o driver não compilaria neste sistema**.

### 5.3 Correção aplicada

Nos três trechos, substituí a cópia de texto e acrescentei uma verificação de tamanho antes do acesso ao último caractere:

```diff
- strncpy(input, buf, len);
- if(input[len-1] == '\n'){
+ memcpy(input, buf, len);
+ if(len && input[len-1] == '\n'){
```

Os trechos corrigidos estão nas linhas 3302, 3753 e 3926 do arquivo instalado em `/usr/local/src/linuwu-sense/src/linuwu_sense.c`.

A função `memcpy` copia exatamente a quantidade de bytes indicada, sem regras adicionais de encerramento de texto. O acréscimo `len &&` impede a leitura de uma posição inválida quando o tamanho é zero. **Essas são as únicas alterações feitas no driver.**

Comando final de compilação:

```bash
make LLVM=1 -j4
```

O módulo gerado apresentou a identificação de versão `7.2.4-3-cachyos`, correspondente exata ao kernel em uso, o que confirma a compatibilidade.

---

## 6. Adaptação 3 — Serviço de inicialização

Para que o driver seja carregado automaticamente a cada inicialização, configurei o serviço de sistema em `/etc/systemd/system/linuwu_sense.service`:

```ini
[Unit]
Description=Linuwu-Sense Acer notebook driver
After=systemd-modules-load.service
ConditionPathExists=/usr/lib/modules/%v/kernel/drivers/platform/x86/linuwu_sense.ko

[Service]
Type=oneshot
RemainAfterExit=yes
ExecStartPre=/usr/bin/modprobe -r acer_wmi
ExecStart=/usr/bin/modprobe linuwu_sense
ExecStop=/usr/bin/modprobe -r linuwu_sense

[Install]
WantedBy=multi-user.target
```

**Justificativa:** em vez de usar `modprobe` com a opção `-f`, que força o carregamento, o serviço simplesmente solicita a ativação do módulo com `modprobe`. Assim, o próprio sistema pode recusar o carregamento se o módulo estiver incompatível com o kernel. A verificação de existência do módulo, `ConditionPathExists`, faz com que a inicialização do sistema não falhe caso o arquivo seja removido. Por fim, a remoção do driver Acer ocorre imediatamente antes do carregamento, reforçando que apenas um dos dois permaneça ativo.

### 6.1 O que não foi configurado

O instalador do projeto também configura permissões para que usuários comuns possam ler e escrever nas interfaces do driver, por meio do recurso de arquivos temporários do sistema e do grupo de usuários `linuwu_sense`. **Não repliquei essa configuração.** O motivo é que o nitroctl requer privilégios administrativos de qualquer forma, de modo que essas permissões adicionais seriam uma exposição desnecessária.

Também **não configurei o DKMS**, recurso que recompilaria o driver automaticamente após atualizações do kernel. Essa é a principal limitação desta instalação, explicada na seção 8.

---

## 7. Adaptação 4 — Forma de abertura do programa

### 7.1 Problema

O inicializador do projeto, arquivo `nitroctl.sh`, exibe uma janela de aviso de licença antes de abrir o menu. Para isso, usa as ferramentas `kdialog` e `qdbus`, que **não estão presentes neste sistema**. O programa não abriria.

A função desses comandos é apenas decorativa: mostram a licença do software. O menu em si é exibido no terminal, independentemente delas.

### 7.2 Solução adotada

Criei o comando `/usr/local/bin/nitroctl` com a finalidade única de solicitar autorização administrativa e iniciar o programa:

```sh
#!/bin/sh
exec /usr/bin/sudo -- /usr/bin/python3 -I /opt/nitroctl/main/main.py "$@"
```

Cada parte tem uma razão de ser:

- `sudo` solicita a senha no terminal e executa o programa com privilégios administrativos, algo exigido pelo próprio nitroctl;
- `python3 -I` inicia o programa em modo isolado, sem carregar configurações ou módulos do ambiente do usuário;
- o caminho absoluto do código-fonte impede que outro arquivo, colocado em local menos protegido, seja executado no lugar do original.

O `nitroctl.sh` original foi **preservado no repositório baixado**, mas não foi instalado. Caso o programa seja usado em um ambiente KDE, com `kdialog` disponível, o inicializador original volta a funcionar sem alterações.

### 7.3 Alterações no código do nitroctl

**Nenhuma.** Os três arquivos do repositório do programa — `main/main.py`, `nitroctl.sh` e `setup/install.sh` — encontram-se exatamente como foram baixados, sem qualquer modificação. O arquivo `main.py` instalado em `/opt/nitroctl` é idêntico ao do repositório. Arquivos auxiliares foram acrescentados apenas no diretório de trabalho, sem alterar os originais.

---

## 8. Limitações e avisos

1. **Ausência de DKMS.** O driver foi compilado especificamente para o kernel `7.2.4-3-cachyos`. **Após cada atualização do kernel, o driver precisará ser recompilado**, com os mesmos comandos descritos nas seções 5.3 e 9. Não há automação para isso.
2. **Adaptação não verificada em reinicialização.** O serviço foi habilitado e está ativo, mas sua atuação durante a inicialização do sistema não foi testada, pois isso exigiria reiniciar o computador sem o conhecimento do usuário.
3. **Funcionalidades não testadas.** Foram verificados a instalação, a substituição do driver e a abertura do menu. **Não** foram testados perfis térmicos, controle de ventoinhas, limite de carga da bateria, iluminação do teclado nem a função de LCD.
4. **Origem e autoria.** Os dois programas são de terceiros e usam interfaces de baixo nível do hardware. O nitroctl é fornecido "como está", sem garantia, conforme a licença GPL exibida pelo próprio programa.
5. **Função desaconselhada.** A opção `L`, que carrega a configuração salva, é marcada pelo próprio projeto como não testada e potencialmente capaz de causar problemas ao sistema.
6. **Função ausente.** A configuração de cores do teclado (`6`) está declarada como não implementada pelo próprio projeto.
7. **Finalidade das permissões.** O programa executa com privilégios administrativos por exigência do autor, e não por decisão desta instalação.

---

## 9. Como usar e como remover

### Abrir o programa

```bash
nitroctl
```

Digite a senha de administrador quando solicitada. Use `Q` para sair.

### Acompanhar o driver

```bash
systemctl status linuwu_sense.service
```

### Recompilar após atualização do kernel

```bash
cd /home/elton/.cache/linuwu-sense-install
make LLVM=1 clean
make LLVM=1 -j4
sudo cp src/linuwu_sense.ko /usr/lib/modules/$(uname -r)/kernel/drivers/platform/x86/
sudo depmod -a
```

### Desfazer a instalação

```bash
sudo systemctl disable --now linuwu_sense.service
sudo rm -f /etc/systemd/system/linuwu_sense.service
sudo rm -f /etc/modprobe.d/blacklist-acer_wmi.conf
sudo rm -f /usr/lib/modules/$(uname -r)/kernel/drivers/platform/x86/linuwu_sense.ko
sudo rm -rf /usr/local/src/linuwu-sense
sudo rm -f /usr/local/bin/nitroctl
sudo rm -rf /opt/nitroctl
sudo systemctl daemon-reload
sudo depmod -a
```

Após esses comandos, o driver original Acer volta a ser usado. Convém reiniciar o computador para que a substituição tenha efeito completo.

---

## 10. Resumo das alterações

| # | Componente | Arquivo | Alteração |
| --- | --- | --- | --- |
| 1 | Driver Linuwu-Sense | `src/linuwu_sense.c` | Troca de `strncpy` por `memcpy` e verificação de tamanho, em três trechos, para permitir a compilação no kernel atual |
| 2 | Driver Linuwu-Sense | comando `make` | Uso de `LLVM=1`, por exigência do kernel CachyOS |
| 3 | Driver Linuwu-Sense | `linuwu_sense.service` | Serviço próprio, com verificação de existência do módulo e remoção prévia do driver Acer |
| 4 | Driver Linuwu-Sense | `blacklist-acer_wmi.conf` | Bloqueio do driver Acer |
| 5 | Instalação do nitroctl | `/usr/local/bin/nitroctl` | Comando próprio que dispensa `kdialog` e `qdbus` |
| 6 | Instalação do nitroctl | `/opt/nitroctl` | Instalação em diretório administrado pelo sistema |
| 7 | Código-fonte do nitroctl | `main/main.py` | **Sem alterações** |

---

## 11. Comprovação

| Verificação | Resultado |
| --- | --- |
| Serviço do driver | `active`, `enabled` |
| Identificação do módulo | `7.2.4-3-cachyos` |
| Driver Acer desativado | Confirmado |
| Interface Nitro disponível | Confirmada |
| Abertura do menu e saída | Confirmadas, código de retorno `0` |
| Comparação com os arquivos de origem | Sem diferenças no código do nitroctl |
| Sintaxe do serviço e do comando | Validadas sem erros |

A verificação foi conduzida por conferência independente, com evidências de cada item: comandos executados, saída obtida e código de retorno.
# Questionário de Levantamento de Requisitos: Projeto BuildingOS

## Parte 1: A Visão e o Negócio (Para o Project Charter)

O objetivo desta seção é entender o "porquê" do projeto, alinhando a visão de negócio com os objetivos técnicos.

### 1\. Visão Geral e Problema

\- Qual é o problema principal que este projeto se propõe a resolver?

Este projeto visa gerar um sistema capaz de integrar todas as funcionalidades de um condomínio a um sistema de inteligência artificial, que ajude a todos os envolvidos em suas tarefas diárias.

\- Poderia descrever o cenário atual que motiva a criação do BuildingOS?  
<br/>\- Quem enfrenta esse problema hoje? (Ex: moradores, administradores de condomínio, equipe de manutenção?)  
<br/>\- Qual é a visão de longo prazo para este produto? Onde vocês o veem em 3 ou 5 anos?

2\. Objetivos de Negócio  
<br/>\- Quais são os 3 principais objetivos de negócio que esperam alcançar com este projeto? (Ex: reduzir custos operacionais, criar uma nova fonte de receita, melhorar a satisfação do cliente, etc.)  
<br/>\- Como mediremos o sucesso desses objetivos? Quais números (KPIs) nos dirão que fomos bem-sucedidos? (Ex: "reduzir o tempo de resposta a chamados de manutenção em 50%", "aumentar a taxa de renovação de aluguéis em 10%").

3\. Escopo do Projeto  
<br/>\- Para a primeira versão (MVP), quais são as funcionalidades absolutamente essenciais que o sistema precisa ter?  
<br/>**Resposta:** Para garantir um lançamento focado e que valide as integrações mais críticas, o escopo será dividido em duas fases claras:

**Fase 1: O MVP (Fundação da Confiança e Acesso)** O MVP se concentrará em resolver o problema central de **identidade e acesso**, que é a base para todas as outras operações em um ambiente de uso misto.

* **1. Interface de Chat Conversacional:** O assistente virtual (via web) como o ponto central de interação.
* **2. Agente de Sincronização de Usuários (ERP):**
  * **Integração Core:** Conectar com o ERP da **Superlógica** como a fonte da verdade para proprietários e locatários anuais.
  * **Funcionalidade:** Sincronizar automaticamente a base de usuários (moradores ativos) do ERP para o BuildingOS, garantindo que apenas pessoas autorizadas tenham acesso.
* **3. Agente de Controle de Acesso (PSIM):**
  * **Integração Core:** Conectar com o PSIM **Situator**.
  * **Funcionalidade:** Provisionar os usuários sincronizados do ERP para dentro do PSIM, criando ou atualizando seus perfis para garantir o acesso físico básico.
* **4. Agente de Elevadores (API Neomot):**
  * **Funcionalidade:** Permitir que um usuário autenticado, via chat, possa **chamar o elevador** para o seu andar e receber a **notificação de chegada**.

**Fase 2: A Visão da Versão Final (O Ecossistema de Hospitalidade e Operações)** A versão final expande o MVP para se tornar uma plataforma completa de gestão de operações e hospitalidade, satisfazendo todos os stakeholders.

* **Módulo 1: Gestão de Hospitalidade e Locações Temporárias (Brokers):**
  * Integração com **AirBnB e Booking.com** para receber reservas automaticamente.
  * Automação do fluxo de comunicação com hóspedes via WhatsApp (instruções, lembretes de check-in).
  * Processo de **check-in online** com captura de documentos e foto.
  * Provisionamento **automático e temporário** de credenciais de acesso (facial no PSIM, senhas para fechaduras **TTLock**).
  * Portal para o proprietário/operador visualizar reservas e interações.
* **Módulo 2: Operações Proativas e Inteligentes:**
  * Receber eventos de acesso do **PSIM** em tempo real.
  * **Automação Proativa:** Ao detectar a entrada de um morador ou hóspede autorizado no edifício (via facial ou tag de veículo), o sistema **automaticamente chama o elevador** para o andar de acesso (térreo/garagem) e notifica o usuário.
  * **Manutenção Inteligente:** O sistema irá diferenciar chamados: um problema dentro de um apartamento de locação temporária gera uma tarefa para o **operador**, enquanto um problema em área comum aciona a **equipe de manutenção** do edifício.
  * **Medição e Alertas de Consumo:** Integrar com medidores de água/gás para enviar dados ao ERP, permitir consultas via chat e **alertar sobre consumos anormais**.
* **Módulo 3: Segurança e Conformidade para Uso Misto:**
  * **Visibilidade para a Portaria/Segurança:** A equipe do edifício terá uma visão clara em seu sistema de quem são os hóspedes, em qual unidade estão e o período de sua estadia.
  * **Perfis de Acesso Dinâmicos:** O sistema gerenciará diferentes perfis no PSIM (Morador, Hóspede, Prestador de Serviço), com permissões e validades distintas.
* **Módulo 4: Experiência do Morador Aprimorada:**
  * **Gestão de Recursos Justa:** O sistema de reserva de áreas comuns terá regras para garantir que o uso por hóspedes não prejudique o acesso dos moradores.
  * **Comunicação Direcionada:** O BuildingOS garantirá que as solicitações dos hóspedes sejam sempre direcionadas aos seus operadores, evitando sobrecarregar a administração do condomínio.
* **Módulo 5: Plataforma de Parceiros e Ecossistema:**
  * Desenvolver uma arquitetura de "adaptadores" para integrar facilmente com outros ERPs de mercado.
  * Criar um portal para que empresas parceiras (de segurança, manutenção, etc.) possam vender e gerenciar o BuildingOS para seus próprios clientes.

\- Existe algo que, por enquanto, está explicitamente fora do escopo? (Ex: "Nesta fase, não vamos integrar com sistemas de câmeras de segurança", "Não haverá um aplicativo para iOS, apenas Android e Web").
<br/>**Resposta:** Sim, para manter o foco do **MVP**, os seguintes itens estão explicitamente fora do escopo **inicial**:

* Toda a **Fase 2 (Visão da Versão Final)**, incluindo a integração com brokers (AirBnB, Booking), automação proativa do elevador e medição de consumo.
* Aplicativos nativos (iOS/Android). O foco será em uma interface Web responsiva.
* Integração com sistemas de câmeras (CFTV).
* Módulo de reserva de áreas comuns.
* Integrações financeiras (além da sincronização de usuários).
* Módulo de gestão de correspondências.

### 4\. Stakeholders (Partes Interessadas)

<br/>\- Quem são as pessoas-chave envolvidas neste projeto?
<br/>\- Quem é o Ponto de Contato Principal para decisões de produto (Product Owner)?
<br/>\- Quem é o Ponto de Contato Principal para decisões técnicas (Tech Lead)?
<br/>**Resposta:**
*   **Equipe Principal (Blubrain.ai):**
    *   **Jomil:** Fundador, responsável pela visão de produto (Product Owner) e pela arquitetura técnica (Tech Lead).
    *   **Licca:** Inspiração para a persona da assistente de IA, servindo como um guia para a experiência do usuário.
*   **Grupos de Stakeholders (Usuários e Clientes):**
    *   **Usuários Finais:** Moradores, Locatários (anuais e temporários), Síndicos, Administradores, Zeladores, Porteiros, etc. Suas necessidades e feedback são a principal entrada para o desenvolvimento do produto.
    *   **Clientes e Parceiros:** Construtoras, Administradoras de Condomínios e Empresas Parceiras que irão comercializar a solução. Seus objetivos de negócio direcionam a estratégia de mercado do produto.
*   **Ponto de Contato Principal para Decisões de Produto (Product Owner):**
    *   **Jomil.**
*   **Ponto de Contato Principal para Decisões Técnicas (Tech Lead):**
    *   **Jomil.**

## Parte 2: Requisitos Funcionais e Não-Funcionais (Para o Requirements)

O objetivo desta seção é detalhar o "o quê" e o "como" do sistema.

### 5\. Funcionalidades (User Stories)

A seguir, uma lista abrangente de User Stories que descrevem as necessidades dos diferentes usuários do ecossistema BuildingOS:

#### 5.1. Para o Morador / Locatário Anual
1.  **Como morador, eu quero** que o portão da garagem abra automaticamente (via LPR ou tag) quando meu carro se aproxima **para que** eu tenha um acesso rápido e sem atritos.
2.  **Como morador, eu quero** chamar o elevador para o meu andar enquanto saio do apartamento **para que** ele esteja me esperando quando eu chegar no corredor.
3.  **Como morador, eu quero** ser notificado quando um delivery chegar e o entregador deixar minha encomenda em um Smart Locker **para que** eu possa retirar com um código único com segurança e conveniência.
4.  **Como morador, eu quero** pré-autorizar a entrada de um visitante para o final de semana **para que** ele possa entrar usando reconhecimento facial sem me incomodar.
5.  **Como morador, eu quero** ser notificado quando uma encomenda minha chegar na portaria **para que** eu possa retirá-la.
6.  **Como morador, eu quero** criar uma permissão de acesso recorrente para minha diarista (toda sexta-feira, das 8h às 12h) **para que** eu não precise liberar o acesso dela manualmente toda semana.
7.  **Como morador, eu quero** ver o status do elevador (andar atual e direção) **para que** eu possa decidir se vale a pena esperar ou usar as escadas.
8.  **Como morador, eu quero** ver a disponibilidade e reservar a churrasqueira pelo chat **para que** eu possa planejar meu evento de forma rápida.
9.  **Como morador, eu quero** ser colocado em uma lista de espera para a quadra de tênis **para que** eu seja notificado se um horário vagar.
10. **Como morador, eu quero** pagar a taxa de reserva do salão de festas via Pix pelo sistema **para que** o processo seja 100% digital.
11. **Como morador, eu quero** consultar as regras de uso da academia **para que** eu saiba os horários de pico e as normas.
12. **Como morador, eu quero** receber um lembrete da minha reserva da área comum um dia antes **para que** eu não me esqueça.
13. **Como morador, eu quero** relatar uma infiltração no teto da minha garagem enviando uma foto **para que** a manutenção seja acionada com a localização exata.
14. **Como morador, eu quero** acompanhar o status do meu chamado de manutenção **para que** eu saiba quando o problema será resolvido.
15. **Como morador, eu quero** avaliar o serviço de manutenção após a conclusão **para que** eu possa dar feedback sobre a qualidade.
16. **Como morador, eu quero** acessar um histórico de todos os meus chamados **para que** eu tenha um registro do que já foi solicitado.
17. **Como morador, eu quero** ser notificado quando o técnico de manutenção estiver a caminho do meu apartamento **para que** eu possa me preparar para recebê-lo.
18. **Como morador, eu quero** receber comunicados importantes do síndico (como falta de água) no meu celular **para que** eu esteja sempre informado.
19. **Como morador, eu quero** participar de uma enquete sobre a nova cor da fachada do prédio **para que** minha opinião seja considerada.
20. **Como morador, eu quero** perguntar "onde fica o hidrômetro do meu apartamento?" **para que** eu receba a localização exata.
21. **Como morador, eu quero** acessar a ata da última reunião de condomínio **para que** eu me mantenha atualizado sobre as decisões.
22. **Como morador, eu quero** acessar um "classificados" do condomínio **para que** eu possa vender uma bicicleta para um vizinho.
23. **Como morador, eu quero** ser notificado sobre eventos sociais no condomínio, como a festa junina **para que** eu possa participar.
24. **Como morador, eu quero** solicitar a segunda via do meu boleto de condomínio **para que** eu possa efetuar o pagamento.
25. **Como morador, eu quero** consultar meu consumo de água e gás do último mês **para que** eu possa entender minha conta.
26. **Como morador, eu quero** cadastrar meu novo veículo no sistema **para que** o acesso dele seja liberado na garagem.
27. **Como morador, eu quero** receber um alerta de consumo anormal de água **para que** eu possa verificar um possível vazamento.
28. **Como morador, eu quero** acionar um "botão de pânico" silencoso pelo chat **para que** a equipe de segurança seja notificada discretamente em uma emergência.
29. **Como morador, eu quero** ser notificado se o alarme de incêndio do meu andar for ativado **para que** eu possa evacuar o local com segurança.
30. **Como morador, eu quero** consultar o histórico de acessos ao meu apartamento (se houver fechadura inteligente) **para que** eu saiba quem entrou e quando.

#### 5.2. Para o Hóspede de Locação Temporária
1.  **Como hóspede, eu quero** receber um link para check-in online via WhatsApp assim que minha reserva for confirmada **para que** eu possa adiantar o processo.
2.  **Como hóspede, eu quero** enviar uma foto do meu documento de identidade de forma segura pelo link de check-in **para que** eu cumpra os requisitos de registro.
3.  **Como hóspede, eu quero** receber lembretes automáticos para fazer o check-in **para que** eu não esqueça de completar o processo antes da viagem.
4.  **Como hóspede, eu quero** receber instruções claras de como chegar ao edifício, incluindo o endereço e regras de entrada **para que** minha chegada seja tranquila.
5.  **Como hóspede, eu quero** receber a senha da fechadura do apartamento e do Wi-Fi automaticamente no dia do check-in **para que** eu tenha autonomia total.
6.  **Como hóspede, eu quero** que meu rosto seja minha credencial de acesso às áreas comuns permitidas **para que** eu não precise carregar chaves ou cartões.
7.  **Como hóspede, eu quero** ser recebido com o elevador me esperando no térreo na minha primeira entrada **para que** eu tenha uma experiência "wow" de boas-vindas.
8.  **Como hóspede, eu quero** perguntar ao assistente "qual a voltagem das tomadas?" **para que** eu obtenha informações úteis sobre o apartamento.
9.  **Como hóspede, eu quero** solicitar toalhas limpas ou outros itens de hospitalidade pelo chat **para que** meu anfitrião seja notificado.
10. **Como hóspede, eu quero** relatar que o ar-condicionado não está funcionando **para que** o operador do imóvel possa providenciar o conserto.
11. **Como hóspede, eu quero** receber sugestões de restaurantes e atrações perto do edifício **para que** eu possa aproveitar melhor minha estadia.
12. **Como hóspede, eu quero** que minhas perguntas sobre o apartamento sejam respondidas pelo assistente **para que** eu não precise contatar o anfitrião para coisas simples.
13. **Como hóspede, eu quero** que minhas solicitações de manutenção sejam direcionadas automaticamente ao meu anfitrião **para que** a pessoa certa resolva meu problema.
14. **Como hóspede, eu quero** ter um canal de comunicação direto e registrado com o anfitrião **para que** eu tenha segurança sobre o que foi combinado.
15. **Como hóspede, eu quero** receber instruções de check-out na manhã da minha saída **para que** eu saiba exatamente o que fazer.
16. **Como hóspede, eu quero** solicitar um late check-out pelo chat **para que** o anfitrião possa aprovar ou negar facilmente.
17. **Como hóspede, eu quero** informar que já saí do apartamento **para que** a equipe de limpeza possa ser acionada.
18. **Como hóspede, eu quero** poder avaliar minha estadia diretamente pelo chat **para que** eu possa dar meu feedback de forma simples.
19. **Como hóspede, eu quero** receber um cupom de desconto para uma futura estadia **para que** eu seja incentivado a voltar.
20. **Como hóspede, eu quero** ter a certeza de que meus dados e credenciais de acesso serão automaticamente revogados após o check-out **para que** eu me sinta seguro.

#### 5.3. Para o Proprietário / Operador de Locação
1.  **Como operador, eu quero** que as reservas do AirBnB e Booking sejam importadas automaticamente para o meu painel **para que** eu tenha uma visão centralizada.
2.  **Como operador, eu quero** definir templates de mensagens automáticas (boas-vindas, check-in, check-out) **para que** a comunicação com o hóspede seja padronizada e eficiente.
3.  **Como operador, eu quero** visualizar todos os hóspedes com check-in pendente **para que** eu possa acompanhar quem ainda precisa enviar os documentos.
4.  **Como operador, eu quero** aprovar manualmente um check-in após revisar os documentos **para que** o acesso seja liberado com segurança.
5.  **Como operador, eu quero** ser notificado em tempo real quando meu hóspede fizer o check-in físico (primeira entrada) **para que** eu saiba que ele chegou bem.
6.  **Como operador, eu quero** ter um "super chat" onde posso ver e responder a todas as conversas dos meus hóspedes com o assistente **para que** eu possa intervir quando necessário.
7.  **Como operador, eu quero** poder estender a estadia de um hóspede no sistema **para que** suas credenciais de acesso sejam atualizadas automaticamente.
8.  **Como operador, eu quero** ser o primeiro a ser notificado sobre um problema de manutenção no meu apartamento **para que** eu possa acionar minha equipe de confiança.
9.  **Como operador, eu quero** criar uma ordem de serviço para minha equipe de limpeza assim que o hóspede fizer o check-out **para que** o apartamento seja preparado para o próximo.
10. **Como operador, eu quero** autorizar o acesso de um técnico de ar-condicionado para uma data e hora específicas **para que** ele possa realizar o conserto sem minha presença.
11. **Como operador, eu quero** ter um histórico de manutenção de cada um dos meus imóveis **para que** eu possa controlar os custos e o histórico de reparos.
12. **Como operador, eu quero** visualizar um calendário com a ocupação de todos os meus imóveis **para que** eu possa gerenciar minha disponibilidade.
13. **Como operador, eu quero** receber um resumo financeiro semanal com o faturamento das minhas locações **para que** eu acompanhe meu rendimento.
14. **Como operador, eu quero** que o sistema me alerte sobre o consumo excessivo de água ou energia em um apartamento **para que** eu possa investigar um possível problema.
15. **Como operador, eu quero** ter um log de todos os acessos ao meu apartamento (via fechadura inteligente) **para que** eu tenha um registro de segurança.
16. **Como operador, eu quero** poder revogar o acesso de um hóspede imediatamente em caso de problemas **para que** eu possa garantir a segurança do meu imóvel.
17. **Como operador, eu quero** que as credenciais de acesso (facial, senhas) expirem automaticamente no horário do check-out **para que** eu não tenha que me preocupar em removê-las manualmente.
18. **Como operador, eu quero** cadastrar os membros da minha equipe (limpeza, manutenção) no sistema **para que** eu possa atribuir tarefas a eles.
19. **Como operador, eu quero** receber avaliações e feedbacks dos hóspedes de forma consolidada **para que** eu possa melhorar meu serviço.
20. **Como operador, eu quero** acessar o sistema através de um portal web simples e intuitivo **para que** eu possa gerenciar minhas propriedades de qualquer lugar.

#### 5.4. Para o Administrador / Síndico
1.  **Como síndico, eu quero** enviar comunicados segmentados (por torre, por andar, apenas para proprietários) **para que** a informação seja relevante para quem a recebe.
2.  **Como administrador, eu quero** ter um dashboard com os principais KPIs do condomínio (chamados abertos, inadimplência, ocupação de áreas comuns) **para que** eu tenha uma visão geral da saúde operacional.
3.  **Como síndico, eu quero** criar e enviar enquetes para os moradores sobre decisões importantes **para que** o processo de votação seja mais ágil e documentado.
4.  **Como administrador, eu quero** ter um repositório central de documentos (atas, regimento interno, balancetes) **para que** os moradores possam consultá-los de forma autônoma.
5.  **Como síndico, eu quero** ser notificado sobre incidentes de segurança (botão de pânico acionado, alarme de incêndio) em tempo real **para que** eu possa tomar as ações necessárias.
6.  **Como administrador, eu quero** visualizar todos os chamados de manutenção em um único painel, com status e prioridade **para que** eu possa gerenciar o trabalho da equipe.
7.  **Como administrador, eu quero** atribuir um chamado de manutenção a um membro específico da equipe **para que** a responsabilidade fique clara.
8.  **Como síndico, eu quero** aprovar orçamentos para reparos diretamente pelo sistema **para que** o processo seja mais rápido e rastreável.
9.  **Como administrador, eu quero** gerar relatórios sobre os tipos mais comuns de problemas de manutenção **para que** possamos identificar áreas que precisam de investimento.
10. **Como administrador, eu quero** ser alertado quando um chamado de alta prioridade não for atendido dentro do prazo (SLA) **para que** eu possa intervir.
11. **Como administrador, eu quero** ter um log completo de todos os acessos de prestadores de serviço **para que** eu tenha um registro de auditoria de segurança.
12. **Como síndico, eu quero** ter uma visão clara de quais apartamentos estão sendo usados para locação temporária e quem são os hóspedes **para que** a segurança do condomínio seja mantida.
13. **Como administrador, eu quero** cadastrar um novo prestador de serviço recorrente (ex: jardinagem) e definir suas permissões de acesso **para que** ele tenha autonomia controlada.
14. **Como administrador, eu quero** revogar o acesso de um ex-funcionário de todas as áreas do condomínio com um único comando **para que** a segurança seja garantida.
15. **Como síndico, eu quero** que os dados de consumo individual de água e gás sejam enviados automaticamente para o ERP da administradora **para que** o faturamento seja preciso e sem esforço manual.
16. **Como administrador, eu quero** visualizar um relatório de inadimplência sincronizado com o ERP **para que** eu possa tomar ações de cobrança.
17. **Como síndico, eu quero** ter acesso ao balancete mensal simplificado através do sistema **para que** eu possa acompanhar a saúde financeira do condomínio.
18. **Como administrador, eu quero** manter uma lista de fornecedores homologados no sistema **para que** a equipe de manutenção possa contatá-los facilmente.
19. **Como síndico, eu quero** que o contrato de manutenção do elevador esteja digitalizado e que o sistema me alerte sobre a data de vencimento **para que** eu não perca o prazo de renovação.
20. **Como administrador, eu quero** poder conceder um acesso temporário ao portal para uma empresa parceira (ex: de segurança) **para que** eles possam ter a visibilidade que precisam para realizar seu trabalho.

#### 5.5. Para a Equipe de Manutenção / Zelador
1.  **Como zelador, eu quero** receber notificações de novos chamados de manutenção em um aplicativo simples no meu celular **para que** eu possa agir rapidamente.
2.  **Como técnico, eu quero** ver todos os detalhes de um chamado (unidade, descrição, foto do problema, nome do solicitante) antes de ir ao local **para que** eu chegue preparado.
3.  **Como zelador, eu quero** visualizar uma lista de todos os chamados abertos, priorizados por urgência **para que** eu saiba o que fazer primeiro.
4.  **Como técnico, eu quero** poder mudar o status de um chamado para "Em andamento" **para que** o administrador e o morador saibam que estou trabalhando no problema.
5.  **Como zelador, eu quero** poder adicionar notas internas ou fotos a um chamado **para que** eu possa documentar o trabalho realizado.
6.  **Como técnico, eu quero** marcar um chamado como "Concluído" ao finalizar o serviço **para que** o sistema notifique o morador e encerre a tarefa.
7.  **Como zelador, eu quero** ter um histórico de todos os reparos feitos em um determinado equipamento (ex: bomba da piscina) **para que** eu possa identificar problemas recorrentes.
8.  **Como zelador, eu quero** ter um checklist de tarefas de manutenção preventiva (ex: verificar gerador, limpar calhas) **para que** eu não esqueça de nenhuma rotina importante.
9.  **Como técnico, eu quero** receber um lembrete semanal das tarefas de manutenção preventiva que precisam ser feitas **para que** eu possa me organizar.
10. **Como zelador, eu quero** poder registrar a conclusão de uma tarefa de rotina com um clique **para que** fique documentado que o serviço foi feito.
11. **Como zelador, eu quero** ser alertado pelo sistema se a pressão da bomba de água estiver fora do normal **para que** eu possa verificar antes que se torne um problema maior.
12. **Como técnico, eu quero** poder enviar uma mensagem para o morador através do chamado ("Estou a caminho") **para que** a comunicação seja centralizada.
13. **Como zelador, eu quero** poder solicitar a compra de um material para um reparo diretamente pelo sistema **para que** o administrador possa aprovar.
14. **Como técnico, eu quero** acessar a planta baixa ou o manual de um equipamento pelo sistema **para que** eu tenha a informação técnica que preciso em mãos.
15. **Como zelador, eu quero** ter uma lista de contatos de fornecedores de emergência (bombeiro, eletricista) no sistema **para que** eu possa acioná-los rapidamente.
16. **Como técnico, eu quero** que meu acesso à casa de máquinas seja liberado automaticamente quando eu aceito um chamado relacionado a ela **para que** eu não precise pedir a chave.
17. **Como zelador, eu quero** poder registrar a entrada e saída de ferramentas do almoxarifado **para que** haja um controle de inventário.
18. **Como zelador, eu quero** ver quanto tempo em média minha equipe leva para resolver os chamados **para que** eu possa identificar gargalos.
19. **Como técnico, eu quero** ver um resumo das minhas tarefas concluídas na semana **para que** eu possa ter uma visão do meu trabalho.
20. **Como zelador, eu quero** que o sistema gere um relatório simples de atividades de manutenção para a reunião com o síndico **para que** eu possa mostrar o trabalho realizado pela equipe.

#### 5.6. Para a Equipe de Portaria / Segurança
1.  **Como porteiro, eu quero** ter uma tela com a lista de todos os visitantes e prestadores de serviço pré-autorizados para o dia **para que** eu possa liberar o acesso rapidamente.
2.  **Como segurança, eu quero** que o sistema me mostre a foto do visitante autorizado no momento em que ele se apresenta na portaria **para que** eu possa fazer a verificação visual.
3.  **Como porteiro, eu quero** registrar a entrada de um entregador de delivery com apenas um clique **para que** o processo seja rápido e o morador seja notificado.
4.  **Como segurança, eu quero** que o sistema me alerte se um visitante tentar usar um acesso facial que não foi reconhecido **para que** eu possa abordar a pessoa e verificar sua identidade.
5.  **Como porteiro, eu quero** consultar rapidamente quem são os hóspedes de um apartamento e por quanto tempo eles ficam **para que** eu possa prestar um serviço de recepção informado.
6.  **Como segurança, eu quero** que o sistema bloqueie automaticamente o acesso de um prestador de serviço fora do horário autorizado **para que** as regras sejam cumpridas.
7.  **Como porteiro, eu quero** poder reenviar um link de cadastro facial para um visitante cujo primeiro cadastro não funcionou **para que** o acesso não seja um transtorno.
8.  **Como segurança, eu quero** receber um alerta no meu painel quando o "botão de pânico" de um morador for acionado, com a localização exata **para que** a resposta à emergência seja imediata.
9.  **Como segurança, eu quero** ter um mapa do condomínio que mostre em tempo real as portas que estão abertas há mais tempo que o normal **para que** eu possa verificar.
10. **Como segurança, eu quero** que o sistema inicie a gravação da câmera mais próxima quando um evento de acesso negado ocorrer **para que** tenhamos um registro visual da tentativa.
11. **Como segurança, eu quero** realizar "rondas virtuais" através do sistema, que me guia pelas câmeras em uma sequência pré-definida **para que** a verificação seja mais eficiente.
12. **Como porteiro, eu quero** ser notificado se um carro não cadastrado passar pela cancela da garagem junto com um carro autorizado ("carona") **para que** a segurança possa interceptá-lo.
13. **Como porteiro, eu quero** enviar uma mensagem padronizada para um morador ("Sua encomenda chegou") com um clique **para que** a comunicação seja rápida e sem erros.
14. **Como segurança, eu quero** ter um canal de comunicação direto e registrado com o síndico para reportar incidentes **para que** tudo fique documentado.
15. **Como porteiro, eu quero** registrar no sistema a entrega e a devolução de chaves de áreas comuns que não possuem controle de acesso facial **para que** haja um controle claro.
16. **Como porteiro, eu quero** acessar uma lista de telefones úteis (polícia, bombeiros, síndico, zelador) diretamente no sistema **para que** eu possa agir rápido em emergências.
17. **Como chefe de segurança, eu quero** gerar um relatório de todos os eventos de acesso em uma área restrita no último mês **para que** eu possa realizar uma auditoria.
18. **Como porteiro, eu quero** poder buscar no sistema "quem foi o último a usar a quadra ontem?" **para que** eu possa verificar um item esquecido.
19. **Como segurança, eu quero** ter um livro de ocorrências digital **para que** eu possa registrar eventos importantes (ex: uma discussão entre vizinhos) de forma segura e pesquisável.
20. **Como porteiro, eu quero** que o sistema me mostre um alerta se um morador que deveria estar com o acesso bloqueado (ex: inadimplente) tentar entrar **para que** eu possa seguir o procedimento correto.

### 6\. Requisitos Não-Funcionais (As "Qualidades" do Sistema)

\- Performance: Existe alguma operação que seja crítica em termos de tempo? (Ex: "A abertura de uma porta deve ocorrer em menos de 2 segundos").
<br/>**Resposta:** Sim, a performance é um pilar fundamental para a confiança e usabilidade do sistema. Os requisitos são definidos por domínios de operação e medidos no 95º percentil (p95).

*   **Domínio de Acesso Físico (Latência Ultra-Baixa):**
    *   **SLO:** Resposta do sistema em **< 1.5 segundos**.
    *   **Operações:** Abertura de portões de garagem (via LPR/Tag), portas de pedestres (via facial), cancelas e portas de áreas comuns.
    *   **Justificativa:** A latência deve ser imperceptível para o usuário, equivalente ou melhor que um controle remoto tradicional.

*   **Domínio de Interação com o Usuário (Latência Baixa):**
    *   **SLO:** Resposta do assistente em **< 3 segundos**.
    *   **Operações:** Chamada de elevador via chat, respostas a perguntas factuais.
    *   **Justificativa:** A interação conversacional precisa ser ágil para manter o engajamento.

*   **Domínio de Operações do Portal (Latência Moderada):**
    *   **SLO:** Carregamento de páginas e dashboards em **< 5 segundos**.
    *   **Operações:** Abrir o painel de reservas, visualizar a lista de chamados de manutenção.
    *   **Justificativa:** Operadores e administradores precisam de fluidez para realizar suas tarefas de gestão.

*   **Domínio de Processamento Assíncrono (Não-crítico em tempo real):**
    *   **SLO:** Processamento completo em **< 2 minutos**.
    *   **Operações:** Sincronização de uma nova reserva do AirBnB, provisionamento de um novo usuário no PSIM.
    *   **Justificativa:** Operações em background que precisam ser concluídas em um tempo razoável.

\- Escalabilidade: Qual é o número esperado de usuários (ou apartamentos) para o lançamento? E qual é a projeção de crescimento para o primeiro ano?
<br/>**Resposta:** A estratégia de escalabilidade é dividida em duas fases:

**Fase 1: Lançamento (MVP)**
*   **Escopo:** 1 a 5 edifícios (~100-500 unidades, ~300-1500 usuários).
*   **Concorrência:** Suportar **50 operações de acesso concorrentes** por minuto e **200 usuários de chat simultâneos**.
*   **Arquitetura:** A arquitetura Serverless-first (Lambda, DynamoDB, SNS) deve escalar automaticamente para esta carga.

**Fase 2: Visão Final (Longo Prazo)**
*   **Escopo:** 300 edifícios (~45.000 unidades, ~135.000 usuários).
*   **Concorrência em Pico:**
    *   **Acesso Físico:** Suportar picos de **10.000 operações de acesso concorrentes** por minuto.
    *   **Interações de Chat:** Suportar **15.000 usuários simultâneos**.
    *   **Processamento de Eventos:** Ingerir e processar até **1.000 eventos por segundo** das integrações.
*   **Estratégia de Arquitetura:**
    *   **Multi-Tenancy:** Arquitetura nativamente multi-tenant com isolamento lógico de dados.
    *   **Escalabilidade Regional:** Infraestrutura como código (Terraform) para ser facilmente replicável em múltiplas regiões da AWS.
    *   **Filas e Resiliência:** Uso massivo de SNS/SQS para absorver picos de carga e garantir a durabilidade das mensagens.

\- Disponibilidade: O sistema precisa funcionar 24/7? Qual é a tolerância a uma eventual falha ou tempo de inatividade? (Ex: "É aceitável ter uma janela de manutenção planejada de 1 hora por mês?").
<br/>**Resposta:** Sim, a disponibilidade é um requisito crítico, especialmente para as funcionalidades de acesso e segurança. A estratégia de disponibilidade será baseada em Service Level Objectives (SLOs) claros:

*   **SLO de Uptime:** **99.9%** de disponibilidade mensal.
    *   **Isso se traduz em:** Não mais que **43.8 minutos** de inatividade não planejada por mês.
    *   **Justificativa:** Garante que o sistema esteja operacional na vasta maioria do tempo, o que é essencial para um serviço que controla o acesso físico.

*   **Estratégia de Alta Disponibilidade:**
    *   **Infraestrutura Multi-AZ:** Todos os componentes da arquitetura (Lambdas, DynamoDB, API Gateway, SNS/SQS) serão implantados em múltiplas Zonas de Disponibilidade (AZs) da AWS para garantir que a falha de um único data center não derrube o serviço.
    *   **Banco de Dados Resiliente:** O Amazon DynamoDB oferece replicação síncrona de dados em múltiplas AZs por padrão.
    *   **Computação sem Estado (Stateless):** Nossos agentes (Lambdas) são sem estado, o que significa que se uma instância falhar, outra pode assumir o trabalho instantaneamente.

*   **Política de Manutenção:**
    *   **Zero Downtime Deployments:** As atualizações de software serão realizadas usando estratégias de deploy como Blue/Green ou Canary, que permitem a atualização do sistema sem tirá-lo do ar.
    *   **Janelas de Manutenção:** Para manutenções planejadas que exijam inatividade (ex: migrações de banco de dados), elas serão agendadas para períodos de baixíssimo uso (ex: entre 3h e 4h da manhã) e comunicadas com antecedência.

\- Segurança: - Quais são os dados mais sensíveis que o sistema irá armazenar? (Ex: dados pessoais dos moradores, registros de acesso).
<br/>**Resposta:** A segurança é um pilar inegociável do BuildingOS. A estratégia de segurança abrange a proteção de dados, a conformidade com a legislação e a segurança da infraestrutura.

*   **Dados Sensíveis Armazenados:**
    *   **Dados Pessoais Identificáveis (PII):** Nome completo, CPF, RG, e-mail, telefone de moradores, hóspedes e prestadores de serviço.
    *   **Dados Biométricos:** Fotos para o sistema de reconhecimento facial.
    *   **Registros de Acesso:** Logs detalhados de quem acessou qual área e quando.
    *   **Informações Financeiras:** Status de pagamento de condomínio (via integração com ERP).
    *   **Comunicações Privadas:** Histórico de conversas no chat.

\- Existem requisitos de conformidade com alguma lei, como a LGPD (Lei Geral de Proteção de Dados)?
<br/>**Resposta:** Sim, a conformidade com a **LGPD é um requisito mandatório**. O sistema será desenvolvido desde o início seguindo os princípios de **Privacy by Design**, para garantir a conformidade total.
*   **Consentimento:** Os usuários terão que consentir explicitamente com o uso de seus dados através de termos de serviço claros.
*   **Transparência e Acesso:** Os usuários poderão solicitar um relatório de todos os dados que o sistema armazena sobre eles.
*   **Direito ao Esquecimento:** Haverá um processo para a anonimização ou exclusão completa dos dados de um usuário quando ele deixar o condomínio ou solicitar.
*   **Estratégia de Segurança da Aplicação e Infraestrutura:**
    *   **Criptografia em Trânsito e em Repouso:** Todos os dados serão criptografados. A comunicação entre serviços e com o usuário final usará TLS 1.2+. Os dados em bancos de dados (DynamoDB) e outros armazenamentos (S3) serão criptografados em repouso usando o AWS KMS.
    *   **Princípio do Menor Privilégio:** Cada componente da arquitetura (cada Lambda) terá apenas as permissões estritamente necessárias para realizar sua função.
    *   **Autenticação e Autorização Robustas:** O acesso às APIs será protegido, e a identidade do usuário será validada em todas as requisições.
    *   **Auditoria e Logs:** Todas as ações críticas (especialmente as de acesso e modificação de dados) serão registradas em logs de auditoria para permitir a rastreabilidade.
    *   **Segurança de Credenciais:** Todas as senhas e chaves de API de serviços de terceiros serão armazenadas de forma segura no AWS Secrets Manager, e não no código-fonte.

\- Usabilidade: Quão familiarizados com tecnologia são os usuários finais (moradores e administradores)? O sistema precisa ser extremamente simples e intuitivo?
<br/>**Resposta:** Sim, a usabilidade é um pilar crítico para garantir a adoção e o sucesso do BuildingOS, dado o público-alvo extremamente diverso.

*   **Público-Alvo:** O sistema será utilizado por um espectro amplo de usuários, desde hóspedes estrangeiros e jovens moradores (altamente tecnológicos) até moradores idosos, porteiros e equipes de manutenção (potencialmente com baixa familiaridade tecnológica).

*   **Princípio de Design: "Conversa Primeiro" (Conversation-First):**
    *   A interface principal será o **chat**, pois a conversação em linguagem natural é a forma mais intuitiva de interação humana, minimizando a curva de aprendizado.
    *   O assistente deve ser capaz de compreender intenções variadas, incluindo erros de digitação e gírias comuns.

*   **Diretrizes de Usabilidade por Interface:**
    *   **Interface Conversacional (Chat):** Deve ser tão simples quanto usar o WhatsApp, com sugestões proativas de funcionalidades e total acessibilidade (WCAG 2.1 AA).
    *   **Portal do Operador de Locação (Web):** Deve ser focado em eficiência, com design orientado a tarefas, dashboards visuais e total responsividade para uso em dispositivos móveis.
    *   **Painel da Equipe do Edifício (Portaria/Manutenção):** Deve priorizar a simplicidade radical, com botões grandes, textos claros, alertas visuais/sonoros e baixa carga cognitiva, otimizado para tablets ou totens.

*   **Diretrizes Gerais:**
    *   **Suporte a Múltiplos Idiomas:** Começando com Português e Inglês.
    *   **Onboarding e Ajuda:** Tutoriais interativos para o primeiro uso dos portais e uma seção de "Ajuda" facilmente acessível em todas as telas.
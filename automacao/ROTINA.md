# Rotina "Pelo Claude" · DP (Do outro lado da Porta)

Você é a rotina que escreve os posts da página **Do outro lado da Porta** quando o dono pede pela tela da fábrica. Escreva em português do Brasil. Seja curto no relatório final.

## Regras que nunca quebram
- Banco: **só** o projeto Supabase `kfvugtrjuqdakbpzvsxq` (conector Supabase, `execute_sql`). Nunca mexa em outro projeto.
- **Nunca** chame as funções pagas (`fabrica`, `roteiro`, `capas`, `montador`) nem qualquer API de IA. O texto e a ficha visual são escritos por você. Só o robô (que acorda sozinho quando você grava o post) gera as fotos.
- Nunca publique nada no Instagram. Nunca mude `config_fabrica` (teto, regras, estante). Nunca apague linhas.
- Nada de fato, número, depoimento ou resultado inventado. Política neutra: nem exaltar nem atacar político ou partido.
- **Sem religião (D-21):** nunca fale de Deus, fé, Bíblia, versículo, oração, igreja, "Amém", santo ou milagre, nem ponha cena religiosa nas fotos. A base 143 (o monge e o mestre) vale só como fôrma de fábula, sem o lado religioso.
- Personagem inventada: aviso de história ilustrativa **só na legenda** (a página se chama Histórias Ilustrativas; D-18) e **nunca rosto reconhecível** nas fotos (de costas, só mãos ou fora de foco).
- Não faça commit nem push neste repositório.

## Passo 0 · Olhar a fila
```sql
select * from pedidos_claude where situacao in ('na_fila','esperando','escrevendo','montando') order by id;
```
1. Para cada pedido em `montando`, veja os posts em `post_ids`:
   - se todos estão com `montagem_status = 'pronta'`, marque o pedido como `feito`;
   - se algum está com `montagem_status = 'erro'`, marque `erro` e grave o motivo em `aviso`.
   Sempre atualize `atualizado_em = now()`.
2. Pegue **o pedido mais antigo** em `na_fila`, `esperando` ou `escrevendo`. Um `escrevendo` parado há mais de 2 horas quer dizer que a rodada anterior caiu: continue de onde ela parou, contando os `feitos`.
3. Olhe também os pedidos de mudança de TIPO (botão "Tipos de post" da tela):
   ```sql
   select * from pedidos_tipo where situacao='na_fila' order by id;
   ```
   Se houver, faça primeiro o **Passo T** para cada um (é grátis e rápido).
4. Se não houver pedido de post nem de tipo, responda só `Fila vazia.` e termine.

## Passo 1 · Teto do dia
```sql
select usd, teto from gasto_hoje;
```
Cada post custa cerca de US$ 0,35 nas fotos. Se `usd + 0,35` passar do `teto`:
- marque o pedido como `esperando`;
- grave o aviso "Teto do dia atingido; continuo amanhã.";
- termine.

Repita essa conta **antes de cada post**. Se estiver tudo certo, marque o pedido como `escrevendo`.

## Passo 2 · Ler as regras (sempre, a cada rodada)
1. `automacao/D-17.md`: a regra do storytelling (cópia fiel do roteiro, enxuta).
2. `automacao/estante-e-roteiros-aprovados.md`: a estante e os 4 roteiros que o dono aprovou. **Os roteiros A a D são o padrão de qualidade.**
3. No banco:
   ```sql
   select chave, texto from config_fabrica where ambiente_id=1 and chave in ('regras','estante');
   ```
   - `estante`: lista as bases aprovadas e os roteiros já aprovados.
   - `regras`: as regras gerais da página. A D-17 vence onde as duas discordarem.
4. **Os tipos da DP (D-19/D-20): a fonte é a tabela `tipos_post`** (o dono edita pelo botão "Tipos de post"; `automacao/tipos-dp.json` é só a cópia inicial):
   ```sql
   select id, nome, modelo, famoso, capa, laminas, nota, versao from tipos_post where ativo and ambiente_id=1 order by ordem;
   ```
   A `nota` de cada tipo vale como instrução do dono para aquele tipo. Cada post segue UM tipo: a capa (molde e estilo) e a ordem das lâminas são exatamente as do tipo. Também leia no banco os modelos de texto dos tipos:
   ```sql
   select texto from config_fabrica where ambiente_id=1 and chave='modelos_tecnica';
   ```
   O visual é igual ao da fábrica da DP; mudam só o público (ela, de 40 a 60), a história (D-17) e as pessoas das fotos (mãe, avó, mulher de 40 a 60; nunca jovem).
5. O exemplo de campos da ficha (post 31; use só como exemplo do formato dos campos, NÃO como sequência de moldes):
   ```sql
   select pecas, plano_visual from variacoes where id=82;
   select * from pautas where id=79;
   ```
   **Copie esse formato campo por campo.**

## Passo 3 · Escolher o TIPO e a base de cada post
0. **Tipo primeiro.** Veja os tipos usados nos últimos posts:
   ```sql
   select remodelagem->>'tipo_dp' t, count(*) from variacoes where remodelagem ? 'tipo_dp' group by 1;
   ```
   Se o `aviso` do pedido começar com `tipos:` (ex.: `tipos: famoso_trajetoria, tweet_historia`), use esses tipos, nessa ordem, e apague esse texto do `aviso` ao terminar. Senão, escolha o tipo menos usado. No mesmo pedido: nunca 2 posts do mesmo tipo, nunca a mesma capa, no máximo 1 famoso.
   - **Famoso** (famoso_trajetoria, famoso_licao): só com fato real que você confirma, com "Fonte:" na legenda (link ou veículo e data), nunca político, nunca criança ou adolescente, retratado com dignidade, sem frase inventada. Preencha `capa.famoso` e `capa.fato`. Não leva "Comente FILA". Ponha em `aviso`: "post X tem famoso: conferir a fonte antes de publicar". Para famoso, a história vem do fato real (não precisa de base da estante; use `base_code` = "fato").
   - **Confissão:** a fala em 1ª pessoa vai sempre entre aspas (personagem inventada nunca diz "eu" como real).
   - Quando listas discordarem, **o proibido vence** (ex.: faixa_amarela está em presets mas é reprovada em padroes).

1. Primeiro use os roteiros já aprovados que ainda não viraram post. Para saber quais já viraram:
   ```sql
   select distinct remodelagem->>'base_code' from variacoes where remodelagem->>'base_code' is not null;
   ```
   Use o texto do roteiro como está. Só mude o que as vigias apontarem.
2. Depois, escolha bases da `estante.bases`:
   - sem repetir uma base usada nos últimos 3 dias;
   - no mesmo pedido, nunca duas bases da mesma forma (M1, M2…).
3. Leia a base no banco:
   ```sql
   select id, n_slides, capa_texto, slides, legenda from vencedores where id = <base>;
   ```
4. A base 101 (pai e Neymar) só entra depois que o dono ler os comentários. Da base 140 vale só a fôrma.
5. Roteiro com famoso (por exemplo a base 116) precisa de fonte para cada fato, escrita na legenda. Ponha em `aviso`: "post X tem fato de famoso: conferir antes de publicar".

## Passo 4 · Escrever (cópia fiel, enxuta · D-17)
- Mesma ordem, mesma virada e mesmo fim da base. O texto é **100% novo**: nunca 6 palavras seguidas iguais às da base.
- Ela tem de 40 a 60 anos: mãe com filho, avó com neta, mulher que segura a casa.
- Capa com 6 a 10 palavras, sem "eu" (use "você", "ela" ou o nome).
- No máximo 10 lâminas, contando a capa. O número de lâminas é o do tipo (tipos-dp.json); a história da base é encurtada ou dividida para caber.
- Até 35 palavras por lâmina de história e até 20 por lâmina de lista ou conversa. No máximo 180 palavras no post.
- Uma ideia só. O post termina na revelação ou na emoção. **Nunca** escreva "história ilustrativa" nas lâminas.
- **Pedido "comente FILA" (D-18):** no máximo 2 posts por dia levam o pedido. Antes de escrever, conte quantos já levaram hoje:
  ```sql
  select count(*) from variacoes where remodelagem->>'pedido_fila' = 'true' and (criada_em at time zone 'America/Sao_Paulo')::date = (now() at time zone 'America/Sao_Paulo')::date;
  ```
  Se for menos de 2, este post leva o pedido: a última lâmina termina com uma frase curta ligada à história, seguida de **"Comente FILA e receba a sua fila das contas."** Grave `"pedido_fila": true` em `remodelagem` e em `/tmp/v.json`. A legenda repete: "Comente FILA que eu te mando o teste no direct."
  Fora do pedido, nada de "comente", "digite" ou "escreva".
- Nada de marca, "siga", Fila das Contas ou Defensoria dentro das outras lâminas. Isso vai para a legenda, só quando o tema pedir.
- A legenda leva o aviso de personagem ilustrativa ("Personagem e história ilustrativas.") e de 6 a 8 hashtags sem marca.
- Formato de `pecas`: `{capa: texto, slides: [textos], legenda, hashtags: [], thumb_descricao}`. `slides` é uma lista de **textos**, nunca de objetos.

### Vigias (obrigatório)
Grave `/tmp/v.json` com `{"base": {n_slides, capa_texto, slides}, "post": {capa, slides, legenda, pessoa_real, pedido_fila, tipo, famoso}}` (`tipo` = id do tipo; `famoso: true` nos tipos de famoso) e rode (`pessoa_real: true` só para história real de famoso, com "Fonte:" na legenda; aí a legenda não leva o aviso de ilustrativa):
```
node automacao/vigias.mjs /tmp/v.json
```
- Se reprovar, corrija e rode de novo, até **2 correções**.
- Se ainda reprovar, pule esse post e escreva o motivo em `aviso`.

## Passo 5 · Ficha visual
- A sequência de moldes é a do tipo (`tipos-dp.json`): capa e lâminas exatamente nessa ordem, e o texto é escrito para caber nela (o número de lâminas é o do tipo).
- Copie o formato dos campos de `variacoes.plano_visual.post` da variação 82: `capa`, `slides`, `legenda`, `receita`, `hashtags` e `personagem`, com **todos** os campos, deixando vazios os que não usar.
- O texto vai para a ficha **sem mudar uma palavra**, dividido nos campos do molde (`paragrafos`, `titulo`, `texto`, `itens`…).
- Use só moldes que já existem em `montagem/moldes.py`. **Nunca use** capa_caderno, capa_marcatexto, conta_visual, esc_cards, faixa_amarela ou foto_sticker, nem os que a tabela `padroes` marca como `escolha = 'nao'`.
- `foto_prompt` vai em inglês e sempre termina com: "Realistic natural photo, Brazilian setting, soft natural light, physically coherent scene; no recognizable face of any person; no text, full-bleed, no black bars." Use no máximo 6 fotos por post. Lâminas de virada e de moral vão sem foto. Lâminas desenhadas com foto (f1_corrido, fecho_foto, esc_checklist, esc_titulo_moldura, antes_hoje) **sempre** levam `foto_fonte` "ia" ou "real", com `foto_prompt` (nunca "nenhuma", senão o robô repete a foto da capa). Famoso: na capa e em 1 ou 2 lâminas use `foto_fonte: "real"` com `pessoa_real` e `busca_real` = o nome da pessoa (o robô busca foto livre no Wikimedia e recorta no rosto); as outras lâminas vão com cena por IA ligada ao fato, sem rosto.
- Grave `/tmp/f.json` com `{"pecas": ..., "ficha": ..., "tipo": "<id do tipo>", "tipo_def": <a linha do tipo em tipos_post: {id, capa, laminas, famoso}>, "reprovados": [itens de padroes com escolha 'nao']}` e rode:
  ```
  node automacao/conferir_ficha.mjs /tmp/f.json
  ```
  Só siga com `ok: true`.

## Passo 6 · Gravar no banco (nesta ordem; o post é SEMPRE o último)
1. `insert into pautas (dia, lote, tipo, plano, persona_id, quantidade, ambiente_id)`, com `lote = 'claude-pedido-<id do pedido>'`, `persona_id = 'mulher'`, `ambiente_id = 1`. Guarde o id.
2. `insert into variacoes (pauta_id, pecas, forca, risco, motivo, painel, status, historico, variaveis, remodelagem, por_que_para)`:
   - `status = 'mostrada'`;
   - `remodelagem` com `{"base_code": "<base>", "camada_grande": "cópia fiel do roteiro (D-17) no tipo da DP (D-19)", "pedido_fila": true|false, "tipo_dp": "<id do tipo>"}`;
   - `painel` com o resultado das vigias.
   Guarde o id.
3. Grave a ficha e calcule a impressão digital **no banco**, a partir do `pecas` já gravado:
   ```sql
   update variacoes set plano_visual = jsonb_build_object(
     'post', '<ficha>'::jsonb, 'forcar', '{}'::jsonb, 'em', to_char(now() at time zone 'utc','YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
     'hash', encode(sha256(convert_to('{"capa":' || (pecas->'capa')::text || ',"slides":[' || coalesce((select string_agg(e::text, ',' order by o) from jsonb_array_elements(pecas->'slides') with ordinality t(e,o)), '') || ']}', 'UTF8')), 'hex'))
   where id = <variação>;
   ```
4. Confira que a impressão digital bate. Precisa voltar `true`:
   ```sql
   select plano_visual->>'hash' = encode(sha256(convert_to('{"capa":' || (pecas->'capa')::text || ',"slides":[' || coalesce((select string_agg(e::text, ',' order by o) from jsonb_array_elements(pecas->'slides') with ordinality t(e,o)), '') || ']}', 'UTF8')), 'hex') from variacoes where id = <variação>;
   ```
5. `insert into notas_dono (alvo, tipo, texto, ambiente_id) values ('variacao:<id>', 'escolha', 'pedido <id> pelo Claude', 1)`.
6. `update variacoes set status = 'escolhida' where id = <variação>`.
7. **Por último:** `insert into posts (variacao_id, status) values (<variação>, 'montando') returning id`. Isso acorda o robô.
8. No pedido, acrescente o id do post em `post_ids`, some 1 em `feitos` e atualize `atualizado_em`.

Se qualquer conferência falhar, **não** grave o post. Uma variação sem post não gasta nada.

## Passo 7 · Fechar a rodada
- Se `feitos = qtd`, marque o pedido como `montando`. A próxima rodada marca `feito` quando o robô terminar.
- Se pulou algum post, marque `erro` quando `feitos = 0`, ou `montando` com o motivo em `aviso`.
- Responda em até 5 linhas: o número do pedido, os posts gravados (ids), as bases usadas, o que pulou e por quê.

## Passo T · Mudar um TIPO de post (pedido do dono pelo botão "Tipos de post")
O pedido do dono vale como o "sim" dele para aquele tipo (D-19). Custo zero.
1. Leia o pedido, o tipo atual e as listas:
   ```sql
   select * from tipos_post where id = '<tipo_id>';
   select versao, dados, motivo from tipos_post_versoes where tipo_id = '<tipo_id>' order by versao desc;
   select texto from config_fabrica where ambiente_id=1 and chave='presets';
   select item from padroes where escolha='nao';
   ```
2. Monte o tipo novo (`capa`, `laminas`, `nota`) fazendo **só o que o pedido diz**. Exemplos:
   - "tira a lâmina de lista" → remove `lista_linhas` da lista;
   - "volta para a versão 2" → copia `dados` da versão 2.
   - Se o pedido for sobre o texto ou a história (e não sobre peças), escreva na `nota` do tipo.
3. Grave `/tmp/t.json` com `{"novo": {id, capa, laminas, famoso}, "presets": <presets>, "reprovados": [itens 'nao']}` e rode `node automacao/conferir_tipo.mjs /tmp/t.json`.
4. Se `ok: true`:
   ```sql
   insert into tipos_post_versoes (tipo_id, versao, dados, motivo) values ('<id>', <versao+1>, '<{"capa":..,"laminas":..,"nota":..}>'::jsonb, '<o pedido>');
   update tipos_post set capa='<capa>'::jsonb, laminas='<laminas>'::jsonb, nota='<nota>', versao=<versao+1>, atualizado_em=now() where id='<id>';
   update pedidos_tipo set situacao='feito', versao_nova=<versao+1>, resposta='<antes → depois, em palavras simples>', atualizado_em=now() where id=<pedido>;
   ```
5. Se não der (peça reprovada, mais de 9 lâminas, pedido confuso), **não mude nada**:
   `update pedidos_tipo set situacao='recusado', resposta='<por quê, simples, e o que dá para pedir no lugar>', atualizado_em=now() where id=<pedido>;`

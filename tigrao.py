import streamlit as st
import numpy as np
import random
import time

def criar_tabuleiro(linhas, colunas):
    simbolos = ['🐯', '💎', '🎰', '🍒', '⭐']
    return np.array([[random.choice(simbolos) for _ in range(colunas)] for _ in range(linhas)])

def verificar_combinacoes(tabuleiro):
    linhas, colunas = tabuleiro.shape
    pontos = 0
    combinacoes = np.zeros_like(tabuleiro, dtype=bool)
    
    # Verificar linhas
    for i in range(linhas):
        for j in range(colunas - 2):
            if tabuleiro[i, j] == tabuleiro[i, j+1] == tabuleiro[i, j+2]:
                combinacoes[i, j:j+3] = True
                pontos += 10
                if j+3 < colunas and tabuleiro[i, j] == tabuleiro[i, j+3]:
                    combinacoes[i, j+3] = True
                    pontos += 5
    
    # Verificar colunas
    for i in range(linhas - 2):
        for j in range(colunas):
            if tabuleiro[i, j] == tabuleiro[i+1, j] == tabuleiro[i+2, j]:
                combinacoes[i:i+3, j] = True
                pontos += 10
                if i+3 < linhas and tabuleiro[i, j] == tabuleiro[i+3, j]:
                    combinacoes[i+3, j] = True
                    pontos += 5
    
    return combinacoes, pontos

def verificar_combinacoes_possiveis(tabuleiro):
    linhas, colunas = tabuleiro.shape
    
    # Verificar horizontalmente
    for i in range(linhas):
        for j in range(colunas - 2):
            if tabuleiro[i, j] == tabuleiro[i, j+1] == tabuleiro[i, j+2]:
                return True
    
    # Verificar verticalmente
    for i in range(linhas - 2):
        for j in range(colunas):
            if tabuleiro[i, j] == tabuleiro[i+1, j] == tabuleiro[i+2, j]:
                return True
    
    return False

def aplicar_gravidade(tabuleiro):
    linhas, colunas = tabuleiro.shape
    novo_tabuleiro = tabuleiro.copy()
    
    for j in range(colunas):
        coluna = list(novo_tabuleiro[:, j])
        # Remover espaços vazios
        coluna = [x for x in coluna if x != '⬜']
        # Preencher com novos símbolos
        while len(coluna) < linhas:
            coluna.insert(0, random.choice(['🐯', '💎', '🎰', '🍒', '⭐']))
        # Atualizar coluna no tabuleiro
        novo_tabuleiro[:, j] = coluna
    
    return novo_tabuleiro

def renderizar_tabuleiro(tabuleiro, combinacoes=None):
    html = """
    <style>
        .tabuleiro {
            text-align: center;
            display: inline-block;
        }
        .simbolo {
            font-size: 2.5em;
            margin: 0.1em;
            display: inline-block;
            transition: all 0.3s ease;
        }
        .combinacao {
            animation: pulse 0.5s infinite;
        }
        @keyframes pulse {
            0% { transform: scale(1); }
            50% { transform: scale(1.2); }
            100% { transform: scale(1); }
        }
        @keyframes cair {
            from { transform: translateY(-50px); opacity: 0; }
            to { transform: translateY(0); opacity: 1; }
        }
        .caindo {
            animation: cair 0.3s ease-out;
        }
    </style>
    <div class="tabuleiro">
    """
    
    for i, linha in enumerate(tabuleiro):
        for j, simbolo in enumerate(linha):
            classe = "simbolo"
            if combinacoes is not None and combinacoes[i, j]:
                classe += " combinacao"
            elif simbolo != '⬜':
                classe += " caindo"
            html += f"<span class='{classe}'>{simbolo}</span>"
        html += "<br>"
    
    html += "</div>"
    return html

def main():
    st.set_page_config(
        page_title="🐯 Tigrão",
        page_icon="🐯",
    )
    
    # CSS para o título
    st.markdown("""
        <style>
            .titulo {
                text-align: center;
                color: #FF6B6B;
                font-size: 3em;
                margin-bottom: 1em;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            .placar {
                font-size: 1.5em;
                color: #4A90E2;
            }
            .fim-jogo {
                text-align: center;
                color: #FF6B6B;
                font-size: 2em;
                margin: 1em;
                animation: pulse 1s infinite;
            }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='titulo'>🐯 Tigrão</h1>", unsafe_allow_html=True)
    
    # Inicializar estado do jogo
    if 'tabuleiro' not in st.session_state:
        st.session_state.tabuleiro = criar_tabuleiro(8, 8)
    if 'pontos' not in st.session_state:
        st.session_state.pontos = 0
    if 'rodando' not in st.session_state:
        st.session_state.rodando = False
    if 'velocidade' not in st.session_state:
        st.session_state.velocidade = 1.0
    if 'fim_jogo' not in st.session_state:
        st.session_state.fim_jogo = False
    
    # Layout do jogo
    col1, col2 = st.columns([3, 1])
    
    with col2:
        st.markdown(f"<div class='placar'>Pontos: {st.session_state.pontos}</div>", unsafe_allow_html=True)
        
        # Controles
        if not st.session_state.fim_jogo:
            if st.button("Iniciar" if not st.session_state.rodando else "Pausar"):
                st.session_state.rodando = not st.session_state.rodando
        
        st.session_state.velocidade = st.slider(
            "Velocidade",
            min_value=0.5,
            max_value=2.0,
            value=st.session_state.velocidade,
            step=0.1
        )
        
        if st.button("Novo Jogo"):
            st.session_state.tabuleiro = criar_tabuleiro(8, 8)
            st.session_state.pontos = 0
            st.session_state.fim_jogo = False
            st.session_state.rodando = False
            st.rerun()
    
    with col1:
        # Container para o tabuleiro
        tabuleiro_container = st.empty()
        
        # Loop principal do jogo
        while st.session_state.rodando and not st.session_state.fim_jogo:
            # Verificar se ainda há combinações possíveis
            if not verificar_combinacoes_possiveis(st.session_state.tabuleiro):
                st.session_state.fim_jogo = True
                st.session_state.rodando = False
                break
            
            # Verificar combinações
            combinacoes, pontos = verificar_combinacoes(st.session_state.tabuleiro)
            
            if pontos > 0:
                st.session_state.pontos += pontos
                
                # Mostrar combinações com animação
                tabuleiro_container.markdown(
                    renderizar_tabuleiro(st.session_state.tabuleiro, combinacoes),
                    unsafe_allow_html=True
                )
                
                # Pausa para mostrar a animação
                time.sleep(0.3 / st.session_state.velocidade)
                
                # Marcar combinações
                for x in range(len(combinacoes)):
                    for y in range(len(combinacoes[0])):
                        if combinacoes[x, y]:
                            st.session_state.tabuleiro[x, y] = '⬜'
                
                # Aplicar gravidade e mostrar animação de queda
                st.session_state.tabuleiro = aplicar_gravidade(st.session_state.tabuleiro)
            
            # Renderizar estado atual
            tabuleiro_container.markdown(
                renderizar_tabuleiro(st.session_state.tabuleiro),
                unsafe_allow_html=True
            )
            
            # Pausa entre verificações
            time.sleep(0.5 / st.session_state.velocidade)
        
        # Mostrar tabuleiro quando pausado
        tabuleiro_container.markdown(
            renderizar_tabuleiro(st.session_state.tabuleiro),
            unsafe_allow_html=True
        )
        
        # Mensagem de fim de jogo
        if st.session_state.fim_jogo:
            st.markdown(
                "<div class='fim-jogo'>🎮 Fim de Jogo! Não há mais combinações possíveis!<br>Clique em 'Novo Jogo' para jogar novamente!</div>",
                unsafe_allow_html=True
            )
    
    # Instruções
    with st.expander("📜 Como Jogar"):
        st.write("""
        1. Clique em 'Iniciar' para começar o jogo
        2. O jogo fará combinações automáticas de 3 ou mais símbolos iguais
        3. Pontuação:
           - 3 símbolos = 10 pontos
           - 4 símbolos = 15 pontos
        4. O jogo termina automaticamente quando não houver mais combinações possíveis
        5. Use o controle de velocidade para ajustar a rapidez das combinações
        
        Símbolos:
        - 🐯 Tigrão
        - 💎 Diamante
        - 🎰 Caça-níqueis
        - 🍒 Cereja
        - ⭐ Estrela
        """)

if __name__ == "__main__":
    main()
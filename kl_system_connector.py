"""
KL System Connector - Consulta histórico de manutenção do sistema KL
Usa Selenium pra fazer scraping (web automation)
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from typing import List, Dict, Optional
import logging
import os

logger = logging.getLogger(__name__)

class KLSystemConnector:
    def __init__(self, headless=True):
        """Inicializa driver Selenium (Chrome)"""
        try:
            options = webdriver.ChromeOptions()
            if headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')

            self.driver = webdriver.Chrome(options=options)
            self.base_url = "https://sistema.klrentacar.com.br"
            logger.info("Selenium Chrome inicializado")
        except Exception as e:
            logger.error(f"Erro inicializando Selenium: {e}")
            self.driver = None

    def get_vehicle_maintenance_history(self, placa: str, limit: int = 50) -> List[Dict]:
        """
        Busca histórico de manutenção de uma placa no sistema KL
        Retorna lista de dict com: data, os_numero, km, oficina, servicos, etc
        """
        if not self.driver:
            logger.error("Driver Selenium não disponível")
            return []

        try:
            # Monta URL do sistema KL
            url = f"{self.base_url}/manutencao/listar?status=fechadas&tipo_os=os&placa={placa}&ordem=data_entrada_man&modo_ordem=DESC&page=1&limit={limit}"

            logger.info(f"Buscando histórico de {placa} no sistema KL...")
            self.driver.get(url)

            # Aguarda a página carregar
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "table tbody tr"))
            )

            # Aguarda botão "Ok" e clica (conforme documentação KL)
            try:
                ok_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Ok')]"))
                )
                ok_button.click()

                # Aguarda resultado da busca
                import time
                time.sleep(2.5)
            except:
                logger.warning("Botão 'Ok' não encontrado, continuando...")

            # Extrai dados das linhas da tabela
            rows = self.driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
            history = []

            for row in rows:
                try:
                    # Extrai células (ordem pode variar, tenta extrair o máximo possível)
                    cells = row.find_elements(By.TAG_NAME, "td")

                    if len(cells) < 5:
                        continue

                    # Tenta extrair dados (estrutura pode mudar, faz best-effort)
                    entry = {
                        'data_entrada': cells[1].text if len(cells) > 1 else None,
                        'os_numero': cells[0].text if len(cells) > 0 else None,
                        'placa': placa,
                        'km': cells[4].text if len(cells) > 4 else None,
                        'oficina': cells[5].text if len(cells) > 5 else None,
                        'servicos': cells[6].text if len(cells) > 6 else None,
                        'raw_text': row.text,
                    }

                    if entry['os_numero']:
                        history.append(entry)
                except Exception as e:
                    logger.warning(f"Erro extraindo linha: {e}")
                    continue

            logger.info(f"Histórico extraído: {len(history)} registros de {placa}")
            return history

        except Exception as e:
            logger.error(f"Erro ao buscar histórico em sistema KL: {e}")
            return []

    def parse_maintenance_history(self, history: List[Dict]) -> Dict:
        """
        Processa histórico raw em formatação estruturada
        Retorna dict com padrões e recorrências detectadas
        """
        if not history:
            return {}

        parsed = {
            'total_os': len(history),
            'placa': history[0].get('placa'),
            'recent_services': [],
            'recurring_items': [],
            'last_maintenance': None,
            'maintenance_frequency': None,
        }

        # Ultimas 5 OS
        parsed['recent_services'] = history[:5]

        # Detecta recorrências (mesmo serviço em curto período)
        service_counts = {}
        for record in history:
            servicos = record.get('servicos', '').lower()
            if servicos:
                service_counts[servicos] = service_counts.get(servicos, 0) + 1

        parsed['recurring_items'] = [
            {'servico': k, 'count': v} for k, v in service_counts.items() if v > 1
        ]

        if history:
            parsed['last_maintenance'] = history[0].get('data_entrada')

        logger.info(f"Histórico parseado: {len(parsed['recent_services'])} recentes, {len(parsed['recurring_items'])} recorrências")
        return parsed

    def close(self):
        """Fecha o driver"""
        if self.driver:
            self.driver.quit()
            logger.info("Driver Selenium fechado")

    def __del__(self):
        self.close()

# Fallback: função que simula resposta sem Selenium
def get_history_fallback(placa: str) -> Dict:
    """
    Fallback quando Selenium não está disponível
    Retorna estrutura vazia (será preenchida com dados da planilha)
    """
    logger.warning(f"Usando fallback para {placa} (Selenium indisponível)")
    return {
        'total_os': 0,
        'placa': placa,
        'recent_services': [],
        'recurring_items': [],
        'last_maintenance': None,
        'source': 'fallback_only_spreadsheet'
    }

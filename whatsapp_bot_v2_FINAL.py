"""
WhatsApp Auditoria Bot v2 FINAL
Integração completa: Twilio + Claude + Planilha + Sistema KL + Formatação + 3 Alçadas
Tudo pronto para deploy imediato no Vercel
"""

from flask import Flask, request
from twilio.rest import Client
from anthropic import Anthropic
import os
import logging
from datetime import datetime
import re
from enum import Enum

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# ============================================================================
# CREDENCIAIS (Vercel Environment Variables)
# ============================================================================
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN')
TWILIO_PHONE = os.getenv('TWILIO_PHONE')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
ANDRE_WHATSAPP = os.getenv('ANDRE_WHATSAPP')  # Seu número privado
SPREADSHEET_PATH = os.getenv('SPREADSHEET_PATH', '/tmp/BASE_E_HISTORICO.xlsx')

# Inicializa clientes
twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
claude_client = Anthropic()

# Import dos módulos locais (já inclusos)
try:
    from spreadsheet_handler import SpreadsheetHandler
    spreadsheet = SpreadsheetHandler(SPREADSHEET_PATH)
except:
    logger.warning("Spreadsheet handler não disponível, usando fallback")
    spreadsheet = None

try:
    from kl_system_connector import KLSystemConnector
    kl_connector = KLSystemConnector(headless=True)
except:
    logger.warning("KL connector não disponível, usando fallback")
    kl_connector = None

# ============================================================================
# ENUMS e CLASSES
# ============================================================================

class ResponseStatus(Enum):
    APPROVED = "approved"
    APPROVED_WITH_WARNING = "warning"
    NOT_RECOMMENDED = "not_recommended"
    BLOCKED = "blocked"
    PENDING_ANDRE = "pending_andre"
    PENDING_DIRECTOR = "pending_director"
    CONDITIONAL = "conditional"

class ApprovalTier(Enum):
    AUTO = "auto"          # ≤ 4.000
    ANDRE = "andre"        # 4.000 - 7.000
    DIRECTOR = "director"  # > 7.000

# ============================================================================
# RESPONSE FORMATTER
# ============================================================================

class ResponseFormatter:
    
    @staticmethod
    def format_group_message(status: ResponseStatus, plate: str, value: float, 
                            workshop: str) -> str:
        """Formata mensagem curta pro grupo (1–2 linhas)"""
        
        emoji_status = {
            ResponseStatus.APPROVED: "✅ *APROVADO*",
            ResponseStatus.APPROVED_WITH_WARNING: "🟡 *APROVADO COM RESSALVAS*",
            ResponseStatus.NOT_RECOMMENDED: "🔴 *NÃO RECOMENDADO*",
            ResponseStatus.BLOCKED: "🔴 *BLOQUEADO*",
            ResponseStatus.PENDING_ANDRE: "⏳ *AGUARDANDO APROVAÇÃO*",
            ResponseStatus.PENDING_DIRECTOR: "⏳ *AGUARDANDO DR. NEILO*",
            ResponseStatus.CONDITIONAL: "🟡 *APROVADO CONDICIONADO*",
        }
        
        status_text = emoji_status.get(status, "❓ INDEFINIDO")
        
        message = f"""{status_text}

*Placa:* {plate}
*Valor:* R$ {value:,.2f}
*Oficina:* {workshop}

Detalhes: DM privado 👇"""
        
        return message
    
    @staticmethod
    def build_dm_header(status: ResponseStatus, plate: str, value: float, 
                        workshop: str, city: str, vehicle: str, km: int, 
                        regime: str) -> str:
        """Cabeçalho da análise completa"""
        
        emoji_status = {
            ResponseStatus.APPROVED: "✅ *APROVADO*",
            ResponseStatus.APPROVED_WITH_WARNING: "🟡 *APROVADO COM RESSALVAS*",
            ResponseStatus.NOT_RECOMMENDED: "🔴 *NÃO RECOMENDADO*",
            ResponseStatus.BLOCKED: "🔴 *BLOQUEADO*",
            ResponseStatus.PENDING_ANDRE: "⏳ *PENDENTE SUA APROVAÇÃO*",
            ResponseStatus.PENDING_DIRECTOR: "⏳ *PENDENTE APROVAÇÃO DR. NEILO*",
            ResponseStatus.CONDITIONAL: "🟡 *APROVADO CONDICIONADO*",
        }
        
        status_text = emoji_status.get(status, "❓ INDEFINIDO")
        regime_label = "🏛️ Licitação" if regime.lower() in ['licitação', 'publica'] else "🚗 Aluguel direto"
        
        header = f"""🔍 *ANÁLISE COMPLETA*

{status_text}

*Identificação*
• *Placa:* {plate}
• *Veículo:* {vehicle}
• *KM:* {km:,}
• *Oficina:* {workshop} ({city})
• *Valor:* R$ {value:,.2f}
• *Regime:* {regime_label}
"""
        
        return header

# ============================================================================
# ALÇADA HANDLER
# ============================================================================

class AlcadaHandler:
    
    TIER_4000 = 4000.00
    TIER_7000 = 7000.00
    
    @staticmethod
    def determine_tier(value: float) -> ApprovalTier:
        """Determina a alçada conforme valor"""
        if value <= AlcadaHandler.TIER_4000:
            return ApprovalTier.AUTO
        elif value <= AlcadaHandler.TIER_7000:
            return ApprovalTier.ANDRE
        else:
            return ApprovalTier.DIRECTOR
    
    @staticmethod
    def get_response_status_for_tier(is_favorable: bool, tier: ApprovalTier) -> ResponseStatus:
        """Retorna status conforme alçada e favorabilidade"""
        if tier == ApprovalTier.AUTO:
            if is_favorable:
                return ResponseStatus.APPROVED
            else:
                return ResponseStatus.NOT_RECOMMENDED
        elif tier == ApprovalTier.ANDRE:
            return ResponseStatus.PENDING_ANDRE
        else:
            return ResponseStatus.PENDING_DIRECTOR

# ============================================================================
# MULTI-CHANNEL HANDLER
# ============================================================================

class MultiChannelHandler:
    
    @staticmethod
    def is_group_message(from_number: str) -> bool:
        """Detecta se é mensagem de grupo ou DM"""
        # No Twilio WhatsApp, grupos têm padrão diferente de DM
        # Por enquanto, tratamos como DM se vier do número do André
        return from_number != ANDRE_WHATSAPP if ANDRE_WHATSAPP else True
    
    @staticmethod
    def send_group_response(group_number: str, message: str):
        """Envia resposta resumida pro grupo"""
        twilio_client.messages.create(
            from_=TWILIO_PHONE,
            to=group_number,
            body=message
        )
        logger.info(f"Resposta de grupo enviada para {group_number}")
    
    @staticmethod
    def send_dm_response(to_number: str, message: str):
        """Envia análise completa em DM privado"""
        # Quebra em chunks se muito grande (WhatsApp tem limite ~4096 chars)
        chunks = []
        current = ""
        
        for line in message.split('\n'):
            if len(current) + len(line) + 1 > 1600:
                if current:
                    chunks.append(current)
                current = line + "\n"
            else:
                current += line + "\n"
        
        if current:
            chunks.append(current)
        
        for chunk in chunks:
            twilio_client.messages.create(
                from_=TWILIO_PHONE,
                to=to_number,
                body=chunk
            )
        
        logger.info(f"DM enviado para {to_number} ({len(chunks)} chunks)")

# ============================================================================
# BUDGET INFO EXTRACTOR
# ============================================================================

class BudgetInfoExtractor:
    
    @staticmethod
    def extract_from_text(text: str) -> dict:
        """Extrai placa, valor, oficina, etc do texto"""
        info = {}
        
        # Placa
        placa_match = re.search(r'([A-Z]{3}[0-9]?[A-Z]?[0-9]{3,4})', text.upper())
        if placa_match:
            info['placa'] = placa_match.group(1)
        
        # Valor (R$ 1.234,56 ou 1234)
        valor_match = re.search(r'R\$\s*([\d.,]+)', text)
        if valor_match:
            valor_str = valor_match.group(1).replace('.', '').replace(',', '.')
            try:
                info['valor'] = float(valor_str)
            except:
                pass
        
        # KM
        km_match = re.search(r'(\d+\.?\d*)\s*km', text, re.IGNORECASE)
        if km_match:
            try:
                info['km'] = int(float(km_match.group(1)))
            except:
                pass
        
        return info

# ============================================================================
# SYSTEM PROMPT (MANUAL COMPLETO)
# ============================================================================

SYSTEM_PROMPT = """Você é o AUDITOR DE ORÇAMENTOS DE FROTA da KL/Kaele Rent A Car.

REGRA CRÍTICA: SEMPRE compare com histórico (planilha + sistema KL) E pesquise mercado antes de recomendar.

ALÇADAS:
• ≤ R$4.000: Auditor recomenda aprovação direta
• R$4k–7k: Auditor recomenda + aguarda André
• >R$7k: Auditor recomenda + aguarda Dr. Neilo

FORMATO RESPOSTA (7 SEÇÕES):
1. Identificação (placa, veículo, km, oficina, valor, regime)
2. Pesquisa de comparação (item | cobrado | histórico | mercado | diferença %)
3. Itens principais (item | valor | necessidade | parecer)
4. Pontos de atenção (inconsistências, falta evidência, valor alto, duplicidade)
5. Decisão (Favorável / Favorável com ressalvas / Não recomendado / Bloqueado / Condicionado)
6. Resposta curta WhatsApp (pronta pro grupo)
7. Recomendação final (síntese + próximos passos)

EVIDÊNCIA OBRIGATÓRIA (sem foto = condicionado):
- Pneu: TWI/sulco/bolha
- Pastilha: espessura
- Disco/tambor: foto/medição
- Suspensão: folga/bucha
- Bateria: teste CCA
- Ar-condicionado: teste pressão

TOM: Direto, simples, pronto pro WhatsApp. Sem textão.

Analise conforme acima. Seja crítico, fundamentado, prático.
"""

# ============================================================================
# MAIN WEBHOOK
# ============================================================================

pending_approvals = {}  # {from_number: {budget_info, parecer, tier}}

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook principal do Twilio"""
    
    try:
        from_number = request.form.get('From')
        to_number = request.form.get('To')
        body = request.form.get('Body', '').strip()
        num_media = int(request.form.get('NumMedia', 0))
        
        logger.info(f"[{from_number}] {body[:80]}")
        
        # Verifica se é menção a @claude
        if '@claude' not in body.lower():
            logger.info("Não é @claude, ignorando")
            return 'OK', 200
        
        # Remove menção
        message_text = body.replace('@claude', '').replace('@Claude', '').strip()
        
        # Extrai info do orçamento
        budget_info = BudgetInfoExtractor.extract_from_text(message_text + body)
        placa = budget_info.get('placa', 'desconhecida')
        valor = budget_info.get('valor', 0)
        
        # Monta prompt pra Claude com histórico
        context = f"\n📚 CONTEXTO:\n"
        
        # Histórico planilha
        if spreadsheet:
            try:
                sheet_history = spreadsheet.get_vehicle_history(placa)
                if sheet_history:
                    context += f"Histórico planilha ({len(sheet_history)} registros)\n"
                    for record in sheet_history[:3]:
                        context += f"• {record.get('data')} | {record.get('item')} | R${record.get('valor_total')}\n"
            except:
                pass
        
        # Histórico sistema KL
        if kl_connector:
            try:
                kl_history = kl_connector.get_vehicle_maintenance_history(placa)
                if kl_history:
                    context += f"Histórico sistema KL ({len(kl_history)} OS)\n"
                    for service in kl_history[:2]:
                        context += f"• OS {service.get('os_numero')} | {service.get('servicos')}\n"
            except:
                pass
        
        user_prompt = f"""
ORÇAMENTO PARA ANÁLISE:

{message_text}

{context}

Arquivos anexados: {num_media}

Analise conforme Manual v2.0. Emita parecer em 7 seções (resumido pra WhatsApp).
"""
        
        logger.info("Chamando Claude API...")
        response = claude_client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2000,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )
        
        parecer_response = response.content[0].text
        logger.info(f"Claude respondeu: {parecer_response[:150]}...")
        
        # Determina alçada
        tier = AlcadaHandler.determine_tier(valor)
        
        # Determina status (assume favorável por padrão, será ajustado se houver "não recomendado")
        is_favorable = 'não recomendado' not in parecer_response.lower() and 'bloqueado' not in parecer_response.lower()
        status = AlcadaHandler.get_response_status_for_tier(is_favorable, tier)
        
        # Se houver "não recomendado" ou "bloqueado", ajusta status
        if 'não recomendado' in parecer_response.lower():
            status = ResponseStatus.NOT_RECOMMENDED
        elif 'bloqueado' in parecer_response.lower():
            status = ResponseStatus.BLOCKED
        elif 'ressalva' in parecer_response.lower():
            status = ResponseStatus.APPROVED_WITH_WARNING
        elif 'condicionado' in parecer_response.lower():
            status = ResponseStatus.CONDITIONAL
        
        # Formata respostas
        workshop = budget_info.get('oficina', 'N/A')
        vehicle = budget_info.get('veiculo', 'N/A')
        km = budget_info.get('km', 0)
        city = budget_info.get('cidade_uf', 'N/A')
        regime = budget_info.get('regime', 'Aluguel direto')
        
        # Resposta grupo (resumida)
        group_msg = ResponseFormatter.format_group_message(
            status, placa, valor, workshop
        )
        
        # Resposta DM (completa)
        dm_msg = ResponseFormatter.build_dm_header(
            status, placa, valor, workshop, city, vehicle, km, regime
        ) + f"\n{parecer_response}\n"
        
        # Se alçada automática e favorável, registra
        if tier == ApprovalTier.AUTO and is_favorable:
            if spreadsheet:
                try:
                    budget_data = {
                        'orcamento': placa,
                        'placa': placa,
                        'veiculo': vehicle,
                        'oficina': workshop,
                        'cidade_uf': city,
                        'km': km,
                        'valor_total': valor,
                        'status': 'Autorizado automático',
                        'acima_alcada': 'Não',
                        'observacao': 'Aprovado automático pelo bot',
                        'arquivo': 'whatsapp'
                    }
                    spreadsheet.register_new_budget(budget_data)
                    logger.info(f"Registrado automático: {placa}")
                except Exception as e:
                    logger.warning(f"Erro ao registrar: {e}")
        else:
            # Guarda sessão aguardando aprovação
            pending_approvals[from_number] = {
                'budget_info': budget_info,
                'parecer': parecer_response,
                'status': status,
                'valor': valor,
                'tier': tier,
                'timestamp': datetime.now()
            }
        
        # Envia respostas
        is_group = MultiChannelHandler.is_group_message(from_number)
        
        if is_group:
            MultiChannelHandler.send_group_response(from_number, group_msg)
            MultiChannelHandler.send_dm_response(ANDRE_WHATSAPP, dm_msg)
        else:
            MultiChannelHandler.send_dm_response(from_number, dm_msg)
        
        logger.info(f"Respostas enviadas: grupo={is_group}")
        
        return 'OK', 200
    
    except Exception as e:
        logger.error(f"Erro: {e}", exc_info=True)
        
        try:
            twilio_client.messages.create(
                from_=to_number,
                to=from_number,
                body=f"⚠️ Erro ao processar. Tente novamente."
            )
        except:
            pass
        
        return 'ERROR', 500

# ============================================================================
# APPROVAL HANDLERS
# ============================================================================

@app.route('/approve', methods=['POST'])
def handle_approval():
    """Recebe aprovações (você responde no DM)"""
    
    try:
        from_number = request.form.get('From')
        body = request.form.get('Body', '').strip()
        to_number = request.form.get('To')
        
        if from_number not in pending_approvals:
            logger.warning(f"Aprovação de {from_number} não encontrada")
            return 'OK', 200
        
        pending = pending_approvals[from_number]
        
        # Verifica resposta
        if '👍' in body or 'aprova' in body.lower():
            logger.info(f"Aprovado por {from_number}")
            
            if spreadsheet:
                try:
                    budget_data = {
                        'orcamento': pending['budget_info'].get('placa'),
                        'placa': pending['budget_info'].get('placa'),
                        'veiculo': pending['budget_info'].get('veiculo', 'N/A'),
                        'oficina': pending['budget_info'].get('oficina', 'N/A'),
                        'cidade_uf': pending['budget_info'].get('cidade_uf', 'N/A'),
                        'km': pending['budget_info'].get('km', 0),
                        'valor_total': pending['valor'],
                        'status': 'Aprovado por André',
                        'acima_alcada': 'Sim',
                        'observacao': 'Aprovado após análise do bot',
                        'arquivo': 'whatsapp'
                    }
                    spreadsheet.register_new_budget(budget_data)
                    logger.info("Registrado na planilha")
                except Exception as e:
                    logger.warning(f"Erro ao registrar: {e}")
            
            twilio_client.messages.create(
                from_=to_number,
                to=from_number,
                body="✅ Orçamento aprovado e registrado."
            )
        else:
            logger.info(f"Rejeitado por {from_number}")
            twilio_client.messages.create(
                from_=to_number,
                to=from_number,
                body="❌ Orçamento rejeitado."
            )
        
        del pending_approvals[from_number]
        return 'OK', 200
    
    except Exception as e:
        logger.error(f"Erro na aprovação: {e}")
        return 'ERROR', 500

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return {'status': 'ok', 'pending': len(pending_approvals)}, 200

if __name__ == '__main__':
    app.run(debug=False, port=5000)

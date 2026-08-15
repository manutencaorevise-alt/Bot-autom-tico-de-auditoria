"""
Response Formatter — Formata respostas padronizadas para grupo e DM
WhatsApp: negrito com *texto*
"""

from enum import Enum
from typing import Tuple

class ResponseStatus(Enum):
    APPROVED = "approved"  # ✅ APROVADO
    APPROVED_WITH_WARNING = "warning"  # 🟡 COM RESSALVAS
    NOT_RECOMMENDED = "not_recommended"  # 🔴 NÃO RECOMENDADO
    BLOCKED = "blocked"  # 🔴 BLOQUEADO
    PENDING_ANDRE = "pending_andre"  # ⏳ AGUARDANDO
    PENDING_DIRECTOR = "pending_director"  # ⏳ AGUARDANDO DR. NEILO
    CONDITIONAL = "conditional"  # 🟡 CONDICIONADO

class ResponseFormatter:
    
    @staticmethod
    def format_group_message(
        status: ResponseStatus,
        plate: str,
        value: float,
        workshop: str,
        decision: str = "Ver DM privado"
    ) -> str:
        """
        Formata mensagem curta pro grupo (1–2 linhas)
        Negrito: *texto*
        """
        
        # Emoji + status
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
        
        # Formato
        message = f"""{status_text}

*Placa:* {plate}
*Valor:* R$ {value:,.2f}
*Oficina:* {workshop}

Detalhes: DM privado 👇"""
        
        return message
    
    @staticmethod
    def format_dm_header(
        status: ResponseStatus,
        plate: str,
        value: float,
        workshop: str,
        city: str,
        vehicle: str,
        km: int,
        regime: str
    ) -> str:
        """
        Formata cabeçalho da análise completa pro DM privado
        """
        
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
    
    @staticmethod
    def format_comparison_section(comparisons: list) -> str:
        """
        Formata seção de comparação (histórico + mercado)
        
        Args:
            comparisons: list of dict
            {
                'item': 'Pastilha dianteira',
                'charged': 172.00,
                'internal_history': 172.00,
                'market': '150-180',
                'difference_pct': 0,
                'status': 'OK' | 'WARNING' | 'ERROR'
            }
        """
        
        section = "*📊 Comparação com histórico*\n"
        
        for comp in comparisons:
            item = comp.get('item', '?')
            charged = comp.get('charged', 0)
            history = comp.get('internal_history')
            market = comp.get('market')
            diff = comp.get('difference_pct', 0)
            comp_status = comp.get('status', 'OK')
            
            # Símbolo do status
            if comp_status == 'OK':
                symbol = "✅"
            elif comp_status == 'WARNING':
                symbol = "⚠️"
            else:
                symbol = "❌"
            
            line = f"{symbol} *{item}:* R$ {charged:.2f}"
            
            if history:
                line += f" (histórico: R$ {history:.2f}"
                if diff != 0:
                    line += f" | +{diff:.1f}%"
                line += ")"
            
            if market:
                line += f" [mercado: R$ {market}]"
            
            section += line + "\n"
        
        return section
    
    @staticmethod
    def format_main_items_section(items: list) -> str:
        """
        Formata seção de itens principais
        
        Args:
            items: list of dict
            {
                'item': 'Pastilha dianteira',
                'value': 172.00,
                'necessity': 'Confirmada',
                'opinion': 'Favorável - foto mostra lona fina'
            }
        """
        
        section = "*💡 Itens principais*\n"
        
        for item in items:
            item_name = item.get('item', '?')
            value = item.get('value', 0)
            necessity = item.get('necessity', '?')
            opinion = item.get('opinion', '?')
            
            section += f"• *{item_name}:* R$ {value:.2f}\n"
            section += f"  Necessidade: {necessity} → {opinion}\n"
        
        return section
    
    @staticmethod
    def format_attention_points_section(points: list) -> str:
        """
        Formata seção de pontos de atenção
        """
        
        if not points:
            return ""
        
        section = "*⚠️ Pontos de atenção*\n"
        
        for i, point in enumerate(points, 1):
            section += f"{i}. {point}\n"
        
        return section
    
    @staticmethod
    def format_decision_section(decision: str) -> str:
        """
        Formata seção de decisão
        """
        
        decision_emoji = {
            'FAVORÁVEL': '✅',
            'FAVORÁVEL COM RESSALVAS': '🟡',
            'NÃO RECOMENDADO': '🔴',
            'BLOQUEADO': '🔴',
            'CONDICIONADO': '🟡',
        }
        
        emoji = decision_emoji.get(decision.upper(), '❓')
        
        section = f"*✏️ Decisão*\n{emoji} {decision}\n"
        
        return section
    
    @staticmethod
    def format_recommendation_section(recommendation: str, tier: str = "auto") -> str:
        """
        Formata seção de recomendação final
        
        tier: 'auto' | 'andre' | 'director'
        """
        
        section = f"*📋 Recomendação final*\n{recommendation}\n"
        
        if tier == "auto":
            section += "\n✅ Orçamento registrado automaticamente."
        elif tier == "andre":
            section += "\n⏳ Aguardando sua aprovação (responda aqui):\n👍 para APROVAR\n👎 para REJEITAR"
        elif tier == "director":
            section += "\n⏳ Aguardando aprovação Dr. Neilo."
        
        return section
    
    @staticmethod
    def format_override_prompt() -> str:
        """
        Formata prompt para você responder com override
        """
        
        prompt = """
*💬 Você pode responder aqui:*

Se concordar com a recomendação:
→ Nada (bot já registrou)

Se discordar e quiser aprovar mesmo assim:
→ Responda: "Aprovo mesmo assim"

Bot registrará com flag de override.
"""
        
        return prompt
    
    @staticmethod
    def build_complete_dm(
        status: ResponseStatus,
        plate: str,
        value: float,
        workshop: str,
        city: str,
        vehicle: str,
        km: int,
        regime: str,
        comparisons: list = None,
        main_items: list = None,
        attention_points: list = None,
        decision: str = "Favorável",
        recommendation: str = "Recomendo aprovação",
        tier: str = "auto"
    ) -> str:
        """
        Monta análise COMPLETA pro DM privado (todas as 7 seções)
        """
        
        # 1. Cabeçalho + Identificação
        dm = ResponseFormatter.format_dm_header(
            status, plate, value, workshop, city, vehicle, km, regime
        )
        
        # 2. Comparação
        if comparisons:
            dm += "\n" + ResponseFormatter.format_comparison_section(comparisons)
        
        # 3. Itens principais
        if main_items:
            dm += "\n" + ResponseFormatter.format_main_items_section(main_items)
        
        # 4. Pontos de atenção
        if attention_points:
            dm += "\n" + ResponseFormatter.format_attention_points_section(attention_points)
        
        # 5. Decisão
        dm += "\n" + ResponseFormatter.format_decision_section(decision)
        
        # 6. Recomendação final
        dm += "\n" + ResponseFormatter.format_recommendation_section(recommendation, tier)
        
        # 7. Se não for aprovação automática, adiciona prompt
        if tier in ["andre", "director"]:
            if tier == "andre":
                dm += ResponseFormatter.format_override_prompt()
        
        return dm

# Exemplos de uso
if __name__ == "__main__":
    
    # Teste: Orçamento aprovado automático
    group_msg = ResponseFormatter.format_group_message(
        ResponseStatus.APPROVED,
        plate="TGQ3G92",
        value=2500.00,
        workshop="Auto Kar",
    )
    
    print("=== GRUPO ===")
    print(group_msg)
    print("\n")
    
    # Teste: DM privado completo
    dm_msg = ResponseFormatter.build_complete_dm(
        status=ResponseStatus.APPROVED,
        plate="TGQ3G92",
        value=2500.00,
        workshop="Auto Kar",
        city="Macapá/AP",
        vehicle="Chevrolet S10 Duramax",
        km=40000,
        regime="Aluguel direto",
        comparisons=[
            {
                'item': 'Pastilha dianteira',
                'charged': 172.00,
                'internal_history': 172.00,
                'market': '150-180',
                'difference_pct': 0,
                'status': 'OK'
            },
            {
                'item': 'Disco freio',
                'charged': 286.90,
                'internal_history': 275.00,
                'market': '280-320',
                'difference_pct': 4.3,
                'status': 'OK'
            }
        ],
        main_items=[
            {
                'item': 'Pastilha dianteira',
                'value': 172.00,
                'necessity': 'Confirmada',
                'opinion': 'Favorável - foto mostra lona fina'
            }
        ],
        attention_points=[],
        decision="FAVORÁVEL",
        recommendation="Preços batem com histórico. Desgaste normal. Aprovação recomendada.",
        tier="auto"
    )
    
    print("=== DM PRIVADO ===")
    print(dm_msg)

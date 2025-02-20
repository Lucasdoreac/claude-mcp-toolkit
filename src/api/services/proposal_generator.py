import pdfkit
from jinja2 import Environment, FileSystemLoader
from datetime import datetime

class ProposalGenerator:
    def __init__(self):
        self.env = Environment(
            loader=FileSystemLoader('templates/proposals')
        )
    
    def generate_proposal(self, data):
        """Gera uma proposta em PDF"""
        template = self.env.get_template('proposal_template.html')
        
        # Adiciona dados padrão
        data['generated_at'] = datetime.now()
        
        # Renderiza o template
        html = template.render(**data)
        
        # Configurações do PDF
        options = {
            'page-size': 'A4',
            'margin-top': '0.75in',
            'margin-right': '0.75in',
            'margin-bottom': '0.75in',
            'margin-left': '0.75in',
            'encoding': "UTF-8"
        }
        
        # Gera o PDF
        pdf = pdfkit.from_string(html, False, options=options)
        
        return pdf
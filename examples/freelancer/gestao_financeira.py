"""
Sistema de Gestão Financeira para Freelancers
Controla receitas, despesas, impostos e relatórios
Preço Referência: R$1000-2500
"""

import os
from typing import Dict, Any, List, Optional, Tuple, Callable
from datetime import datetime, timedelta
import asyncio
import pandas as pd
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import plotly.express as px
import plotly.graph_objects as go
from sklearn.linear_model import LinearRegression
from dataclasses import dataclass
import json
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('GestaoFinanceira')

# Classes de dados
@dataclass
class Config:
    """Configurações do sistema"""
    impostos: Dict[str, Dict[str, float]]
    categorias: Dict[str, List[str]]
    limites: Dict[str, float]

@dataclass
class APIConfig:
    """Configurações das APIs"""
    sheets_credentials: str
    banco_token: str
    nfe_token: str
    email_key: str
    sheets_ids: Dict[str, str]

class GestaoFinanceira:
    """
    Sistema completo de gestão financeira
    """
    def __init__(self):
        # Inicializar configurações
        self.config = self._load_config()
        self.api_config = self._load_api_config()
        
        # Inicializar APIs
        self._init_apis()
        
        # Inicializar cache e estado
        self.data_cache = {}
        self.last_update = None
        
        # Inicializar API FastAPI
        self.app = FastAPI(
            title="Sistema de Gestão Financeira",
            description="API para gestão financeira de freelancers",
            version="1.0.0"
        )
        self._setup_api()
        
        logger.info("Sistema de Gestão Financeira inicializado")

[Resto do código mantido como estava...]
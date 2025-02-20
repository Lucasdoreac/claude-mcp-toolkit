"""
Testes para o módulo de redes sociais.
"""
import pytest
from src.social_media.bot import SocialMediaBot
from src.social_media.analyzer import EngagementAnalyzer

@pytest.fixture
def social_bot():
    """Fixture para criar uma instância do bot de redes sociais."""
    config = {
        "platforms": ["twitter", "instagram"],
        "posting_interval": 3600,
        "max_posts_per_day": 5
    }
    return SocialMediaBot(config)

@pytest.fixture
def engagement_analyzer():
    """Fixture para criar uma instância do analisador de engajamento."""
    return EngagementAnalyzer()

@pytest.mark.core
def test_bot_initialization(social_bot):
    """Testa a inicialização correta do bot."""
    assert social_bot.platforms == ["twitter", "instagram"]
    assert social_bot.posting_interval == 3600
    assert social_bot.max_posts_per_day == 5

@pytest.mark.core
def test_post_scheduling(social_bot):
    """Testa o agendamento de posts."""
    post = {
        "content": "Test post",
        "platform": "twitter",
        "schedule_time": "2025-03-01 12:00:00"
    }
    result = social_bot.schedule_post(post)
    assert result["status"] == "scheduled"
    assert result["platform"] == "twitter"

@pytest.mark.core
def test_engagement_calculation(engagement_analyzer):
    """Testa o cálculo de métricas de engajamento."""
    metrics = {
        "likes": 100,
        "comments": 20,
        "shares": 30
    }
    engagement = engagement_analyzer.calculate_engagement_rate(metrics, followers=1000)
    assert 0 <= engagement <= 100
    assert engagement == pytest.approx(15.0)  # (100 + 20 + 30) / 1000 * 100

@pytest.mark.integrations
def test_multi_platform_posting(social_bot):
    """Testa postagem em múltiplas plataformas."""
    post = {
        "content": "Multi-platform test",
        "platforms": ["twitter", "instagram"],
        "media": None
    }
    results = social_bot.post_to_all_platforms(post)
    assert len(results) == 2
    assert all(result["status"] in ["posted", "scheduled"] for result in results)

@pytest.mark.utils
def test_content_validation(social_bot):
    """Testa validação de conteúdo."""
    invalid_post = {
        "content": "!" * 300,  # Conteúdo muito longo
        "platform": "twitter"
    }
    with pytest.raises(ValueError):
        social_bot.validate_post_content(invalid_post)
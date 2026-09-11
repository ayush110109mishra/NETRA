"""
FastAPI dependency providers for NETRA Intelligence Core.
"""

from functools import lru_cache
from fastapi import Depends
from config import NetraConfig, default_config
from entities.repository import EntityRepository
from intelligence.entity_intelligence import EntityIntelligenceEngine
from intelligence.anomaly_intelligence import AnomalyIntelligenceEngine
from intelligence.fusion_intelligence import FusionIntelligenceEngine
from intelligence.predictive_intelligence import PredictiveIntelligenceEngine
from simulation.synthetic_data import seed_entity_repository


def get_config() -> NetraConfig:
    """Dependency provider returning active configuration."""
    return default_config


@lru_cache()
def get_entity_repository() -> EntityRepository:
    """Singleton repository pre-seeded with synthetic scenario entities."""
    repo = EntityRepository(default_config.entity)
    seed_entity_repository(repo)
    return repo


def get_entity_engine(
    config: NetraConfig = Depends(get_config),
    repo: EntityRepository = Depends(get_entity_repository),
) -> EntityIntelligenceEngine:
    """Provide Master EntityIntelligenceEngine instance."""
    return EntityIntelligenceEngine(config=config, repository=repo)


def get_anomaly_engine(
    config: NetraConfig = Depends(get_config),
    repo: EntityRepository = Depends(get_entity_repository),
) -> AnomalyIntelligenceEngine:
    """Provide Master AnomalyIntelligenceEngine instance."""
    return AnomalyIntelligenceEngine(config=config, repository=repo)


def get_fusion_engine(
    config: NetraConfig = Depends(get_config),
    repo: EntityRepository = Depends(get_entity_repository),
    anomaly_engine: AnomalyIntelligenceEngine = Depends(get_anomaly_engine),
) -> FusionIntelligenceEngine:
    """Provide Master FusionIntelligenceEngine instance."""
    return FusionIntelligenceEngine(config=config, repository=repo, anomaly_engine=anomaly_engine)


def get_prediction_engine(
    config: NetraConfig = Depends(get_config),
    repo: EntityRepository = Depends(get_entity_repository),
    anomaly_engine: AnomalyIntelligenceEngine = Depends(get_anomaly_engine),
    fusion_engine: FusionIntelligenceEngine = Depends(get_fusion_engine),
) -> PredictiveIntelligenceEngine:
    """Provide Master PredictiveIntelligenceEngine instance."""
    return PredictiveIntelligenceEngine(
        config=config,
        repository=repo,
        anomaly_engine=anomaly_engine,
        fusion_engine=fusion_engine,
    )



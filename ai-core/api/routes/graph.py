"""
Phase 8 Knowledge Graph & Relationship Intelligence API Routes for NETRA.
ASTRAVEDA Defence Intelligence Platform - ATUL AI/ML Engineering.

Exposes REST endpoints for graph analytics, entity networks, evidence shortest paths,
centrality metrics, community detection, and temporal graph changes.
"""

from datetime import datetime, timezone
import logging
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status

from api.dependencies import get_graph_intelligence_engine
from intelligence.graph_intelligence import GraphIntelligenceEngine
from models.knowledge_graph import (
    CentralityResult,
    CommunityResult,
    EdgeType,
    EntityNetworkResponse,
    GraphAnalyzeRequest,
    GraphAnalyzeResponse,
    GraphChangesResponse,
    GraphEdge,
    GraphNode,
    GraphSnapshotResponse,
    NodeType,
    PathResult,
    RelationshipChange,
)

logger = logging.getLogger("netra.api.graph")

router = APIRouter(prefix="/api/v1/intelligence/graph", tags=["Knowledge Graph & Relationship Intelligence"])


@router.post(
    "/analyze",
    response_model=GraphAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Knowledge Graph Full Analysis",
    description="Constructs or queries active graph state, evaluates multi-factor relationships, detects communities, and provides a 5-tier epistemic assessment.",
)
def analyze_graph(
    request: GraphAnalyzeRequest,
    engine: GraphIntelligenceEngine = Depends(get_graph_intelligence_engine),
) -> GraphAnalyzeResponse:
    try:
        return engine.analyze_graph(request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    except Exception as exc:
        logger.error(f"Graph analysis failed: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Graph processing error: {str(exc)}")


@router.get(
    "/nodes",
    response_model=List[GraphNode],
    status_code=status.HTTP_200_OK,
    summary="List Knowledge Graph Nodes",
    description="Retrieves nodes active in the knowledge graph, optionally filtered by node_type.",
)
def get_nodes(
    node_type: Optional[NodeType] = Query(None, description="Filter by categorical node type"),
    limit: int = Query(500, ge=1, le=1000, description="Maximum nodes returned"),
    engine: GraphIntelligenceEngine = Depends(get_graph_intelligence_engine),
) -> List[GraphNode]:
    if node_type:
        nodes = engine.graph_engine.node_registry.get_nodes_by_type(node_type)
    else:
        nodes = engine.graph_engine.node_registry.get_all_nodes()
    return nodes[:limit]


@router.get(
    "/edges",
    response_model=List[GraphEdge],
    status_code=status.HTTP_200_OK,
    summary="List Knowledge Graph Edges",
    description="Retrieves edges active in the knowledge graph, optionally filtered by edge_type.",
)
def get_edges(
    edge_type: Optional[EdgeType] = Query(None, description="Filter by edge relationship type"),
    limit: int = Query(500, ge=1, le=1000, description="Maximum edges returned"),
    engine: GraphIntelligenceEngine = Depends(get_graph_intelligence_engine),
) -> List[GraphEdge]:
    if edge_type:
        edges = engine.graph_engine.edge_registry.get_edges_by_type(edge_type)
    else:
        edges = engine.graph_engine.edge_registry.get_all_edges()
    return edges[:limit]


@router.get(
    "/entities/{entity_id}/network",
    response_model=EntityNetworkResponse,
    status_code=status.HTTP_200_OK,
    summary="Entity Ego-Network",
    description="Retrieves the multi-hop ego-network, relationships, and cluster membership for a focus entity.",
)
def get_entity_network(
    entity_id: str,
    depth: int = Query(1, ge=1, le=3, description="Traversal hop depth"),
    as_of: Optional[datetime] = Query(None, description="Point-in-time evaluation timestamp"),
    engine: GraphIntelligenceEngine = Depends(get_graph_intelligence_engine),
) -> EntityNetworkResponse:
    try:
        return engine.get_entity_network(entity_id=entity_id, depth=depth, as_of=as_of)
    except Exception as exc:
        logger.error(f"Entity network retrieval failed for {entity_id}: {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get(
    "/entities/{entity_id}/neighbors",
    response_model=List[GraphNode],
    status_code=status.HTTP_200_OK,
    summary="Entity Direct Neighbors",
    description="Retrieves direct 1-hop neighbor nodes for an entity.",
)
def get_entity_neighbors(
    entity_id: str,
    depth: int = Query(1, ge=1, le=3, description="Neighbor hop depth"),
    engine: GraphIntelligenceEngine = Depends(get_graph_intelligence_engine),
) -> List[GraphNode]:
    net = engine.get_entity_network(entity_id=entity_id, depth=depth)
    return net.neighbors


@router.get(
    "/path",
    response_model=PathResult,
    status_code=status.HTTP_200_OK,
    summary="Evidence Shortest Path",
    description="Finds deterministic evidence-supported shortest path between two entities with bottleneck confidence.",
)
def get_path(
    source: str = Query(..., description="Originating entity ID"),
    target: str = Query(..., description="Destination entity ID"),
    max_depth: Optional[int] = Query(None, ge=1, le=6, description="Maximum traversal search hops"),
    as_of: Optional[datetime] = Query(None, description="Point-in-time evaluation timestamp"),
    engine: GraphIntelligenceEngine = Depends(get_graph_intelligence_engine),
) -> PathResult:
    try:
        return engine.get_path(source=source, target=target, max_depth=max_depth, as_of=as_of)
    except Exception as exc:
        logger.error(f"Path query failed ({source} -> {target}): {exc}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


@router.get(
    "/communities",
    response_model=List[CommunityResult],
    status_code=status.HTTP_200_OK,
    summary="Community Detection & Structural Partitions",
    description="Detects connected structural components and network communities (strictly non-allegiance).",
)
def get_communities(
    engine: GraphIntelligenceEngine = Depends(get_graph_intelligence_engine),
) -> List[CommunityResult]:
    return engine.graph_engine.communities()


@router.get(
    "/centrality",
    response_model=List[CentralityResult],
    status_code=status.HTTP_200_OK,
    summary="Network Centrality Metrics",
    description="Calculates degree, weighted degree, and betweenness centrality (strictly structural, non-threat).",
)
def get_centrality(
    engine: GraphIntelligenceEngine = Depends(get_graph_intelligence_engine),
) -> List[CentralityResult]:
    return engine.graph_engine.centrality()


@router.get(
    "/changes",
    response_model=GraphChangesResponse,
    status_code=status.HTTP_200_OK,
    summary="Temporal Relationship Change Detection",
    description="Detects relationship state and strength deltas between start_time and end_time.",
)
def get_changes(
    start_time: datetime = Query(..., description="Starting snapshot evaluation timestamp"),
    end_time: datetime = Query(..., description="Ending snapshot evaluation timestamp"),
    entity_id: Optional[str] = Query(None, description="Optional entity filter"),
    engine: GraphIntelligenceEngine = Depends(get_graph_intelligence_engine),
) -> GraphChangesResponse:
    if start_time >= end_time:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="start_time must be strictly earlier than end_time.",
        )
    return engine.get_changes(start_time=start_time, end_time=end_time, entity_id=entity_id)


@router.get(
    "/snapshot",
    response_model=GraphSnapshotResponse,
    status_code=status.HTTP_200_OK,
    summary="Point-in-Time Graph Snapshot",
    description="Captures a reproducible snapshot of the active graph at as_of.",
)
def get_snapshot(
    as_of: Optional[datetime] = Query(None, description="Snapshot timestamp"),
    engine: GraphIntelligenceEngine = Depends(get_graph_intelligence_engine),
) -> GraphSnapshotResponse:
    return engine.get_snapshot(as_of=as_of)


@router.get(
    "/scenarios",
    response_model=List[Dict[str, Any]],
    status_code=status.HTTP_200_OK,
    summary="List Synthetic Graph Scenarios",
    description="Lists pre-packaged operational test scenarios for graph verification.",
)
def list_scenarios() -> List[Dict[str, Any]]:
    from simulation.graph_scenarios import list_all_graph_scenarios
    return list_all_graph_scenarios()


@router.post(
    "/scenarios/{scenario_id}/analyze",
    response_model=GraphAnalyzeResponse,
    status_code=status.HTTP_200_OK,
    summary="Execute Scenario Graph Analysis",
    description="Ingests a specific synthetic scenario and executes full graph analysis.",
)
def analyze_scenario(
    scenario_id: str,
    engine: GraphIntelligenceEngine = Depends(get_graph_intelligence_engine),
) -> GraphAnalyzeResponse:
    from simulation.graph_scenarios import load_graph_scenario
    scenario = load_graph_scenario(scenario_id)
    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scenario '{scenario_id}' not found.",
        )

    # Ingest scenario into graph
    engine.graph_engine.clear()
    scenario["loader"](engine.graph_engine)
    as_of = scenario.get("as_of", datetime.now(timezone.utc))

    return engine.analyze_graph(GraphAnalyzeRequest(as_of=as_of))

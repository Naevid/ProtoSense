from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.db.repository import ProtocolRepository
from app.models.schemas import AssessmentResponse, ChatRequest, ChatResponse, SimulationRequest, SimulationResponse
from app.services.chat_engine.chat_service import ChatService
from app.services.extraction_engine.extractor import FeatureExtractor
from app.services.protocol_ingestion.pdf_parser import ProtocolIngestionService
from app.services.risk_engine.scorer import RiskScorer
from app.services.section_mapper.mapper import SectionMapper
from app.services.simulation_engine.simulator import SimulationEngine
from app.services.traceability_engine.traceability import TraceabilityEngine

router = APIRouter(prefix="/protocols", tags=["protocols"])
repo = ProtocolRepository()


def require_protocol(protocol_id: str):
    record = repo.get_protocol(protocol_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Protocol not found")
    return record


@router.post("/upload")
async def upload_protocol(file: UploadFile = File(...)):
    if not (file.filename or "").lower().endswith((".pdf", ".txt")):
        raise HTTPException(status_code=400, detail="Upload a PDF or text protocol for the MVP parser")
    service = ProtocolIngestionService()
    protocol_id, filename, pages = await service.ingest_upload(file)
    record = repo.create_protocol(protocol_id, filename, pages)
    return {"protocol_id": record.id, "filename": record.filename, "pages": len(record.pages)}


@router.post("/{protocol_id}/section-map")
async def section_map(protocol_id: str):
    record = require_protocol(protocol_id)
    mapper = SectionMapper()
    sections = await mapper.map_sections(record.pages)
    repo.update_sections(protocol_id, sections)
    return {"protocol_id": protocol_id, "sections": [section.model_dump() for section in sections]}


@router.post("/{protocol_id}/extract")
async def extract(protocol_id: str):
    record = require_protocol(protocol_id)
    sections = record.section_map
    if not sections:
        sections = await SectionMapper().map_sections(record.pages)
        repo.update_sections(protocol_id, sections)
    features = await FeatureExtractor().extract(record.pages, sections)
    repo.update_features(protocol_id, features)
    return {"protocol_id": protocol_id, "features": features.model_dump()}


@router.post("/{protocol_id}/score", response_model=AssessmentResponse)
async def score(protocol_id: str):
    record = require_protocol(protocol_id)
    features = record.features
    if features is None:
        sections = record.section_map or await SectionMapper().map_sections(record.pages)
        repo.update_sections(protocol_id, sections)
        features = await FeatureExtractor().extract(record.pages, sections)
        repo.update_features(protocol_id, features)
    assessment = RiskScorer().build_assessment(protocol_id, features)
    repo.update_scores(protocol_id, assessment.model_dump())
    repo.update_recommendations(protocol_id, assessment.recommendations)
    return assessment


@router.get("/{protocol_id}/assessment", response_model=AssessmentResponse)
async def assessment(protocol_id: str):
    record = require_protocol(protocol_id)
    if record.scores:
        return AssessmentResponse(**record.scores)
    return await score(protocol_id)


@router.post("/{protocol_id}/simulate", response_model=SimulationResponse)
async def simulate(protocol_id: str, request: SimulationRequest):
    record = require_protocol(protocol_id)
    if record.features is None:
        await extract(protocol_id)
        record = require_protocol(protocol_id)
    try:
        return SimulationEngine().simulate(protocol_id, record.features, request.overrides)  # type: ignore[arg-type]
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/{protocol_id}/recommendations")
async def recommendations(protocol_id: str):
    record = require_protocol(protocol_id)
    if not record.recommendations:
        assessment_response = await assessment(protocol_id)
        return {"protocol_id": protocol_id, "recommendations": assessment_response.recommendations}
    return {"protocol_id": protocol_id, "recommendations": record.recommendations}


@router.get("/{protocol_id}/evidence")
async def evidence(protocol_id: str):
    record = require_protocol(protocol_id)
    if record.features is None:
        await extract(protocol_id)
        record = require_protocol(protocol_id)
    return {"protocol_id": protocol_id, "evidence": [item.model_dump() for item in TraceabilityEngine().collect_evidence(record.features)]}  # type: ignore[arg-type]


@router.post("/{protocol_id}/chat", response_model=ChatResponse)
async def chat(protocol_id: str, request: ChatRequest):
    record = require_protocol(protocol_id)
    if record.features is None:
        await extract(protocol_id)
        record = require_protocol(protocol_id)
    assessment_response = await assessment(protocol_id)
    return await ChatService().answer(
        protocol_id=protocol_id,
        message=request.message,
        assessment=assessment_response,
        features=record.features,  # type: ignore[arg-type]
    )

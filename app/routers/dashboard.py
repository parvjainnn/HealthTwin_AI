from fastapi import APIRouter
from datetime import datetime
from app.models.schemas import (
    DashboardInput,
    DashboardAnalysis,
    WatchData,
    HealthLogEntry,
    AdvisorRequest,
    AdvisorResponse,
)
from app.services.dashboard import (
    analyze,
    simulate_watch,
    save_log,
    get_history,
    clear_history,
    get_advisor_response,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.post("/analyze", response_model=DashboardAnalysis)
async def dashboard_analyze(data: DashboardInput):
    """Compute BMI, health score, and risk analysis from vitals."""
    return analyze(data.model_dump())


@router.get("/watch", response_model=WatchData)
async def dashboard_watch(base_hr: int = 72):
    """Return simulated smartwatch readings."""
    return simulate_watch(base_hr)


@router.post("/save-log")
async def dashboard_save_log(data: DashboardInput):
    """Save a health log entry."""
    analysis = analyze(data.model_dump())
    record = {
        **data.model_dump(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "bmi": analysis["bmi"],
        "health_score": analysis["health_score"],
        "obesity_risk": analysis["obesity_risk"],
        "fatigue_risk": analysis["fatigue_risk"],
    }
    save_log(record)
    return {"status": "saved"}


@router.get("/history")
async def dashboard_history(limit: int = 30):
    """Return recent health log entries."""
    return get_history(limit)


@router.delete("/history")
async def dashboard_clear_history():
    """Clear all health log entries."""
    clear_history()
    return {"status": "cleared"}


@router.post("/advisor", response_model=AdvisorResponse)
async def dashboard_advisor(req: AdvisorRequest):
    """Contextual AI health advisor based on user vitals."""
    reply = get_advisor_response(req.question, req.user_data)
    return {"reply": reply}

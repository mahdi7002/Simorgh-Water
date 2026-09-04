"""
API و داشبورد سیستم مدیریت چرخه آب سیمرغ
"""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader

from config.settings import settings
from services.layers import HolisticWaterAwarenessSystem, NaturalCycleService, CityInfrastructureService

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = Path(__file__).resolve().parent.parent
jinja_env = Environment(loader=FileSystemLoader(str(BASE_DIR / "dashboard" / "templates")))

system = HolisticWaterAwarenessSystem()
natural_svc = NaturalCycleService()
city_svc = CityInfrastructureService()


@app.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request):
    view = system.create_holistic_view()
    story = system.connect_the_dots()
    bottlenecks = system.find_bottlenecks()
    footprint = system.calculate_water_footprint()
    plan = system.generate_action_plan()

    template = jinja_env.get_template("index.html")
    html = template.render(
        request=request,
        app_name=settings.APP_NAME,
        version=settings.APP_VERSION,
        city=settings.DEFAULT_CITY,
        view=view,
        story=story,
        bottlenecks=bottlenecks,
        footprint=footprint,
        plan=plan,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    return HTMLResponse(content=html)


@app.get("/api/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "mode": "mock" if settings.MOCK_MODE else "live",
    }


@app.get("/api/natural")
async def api_natural(location: str = Query(default=None)):
    state = natural_svc.get_current_state(location)
    availability = natural_svc.calculate_water_availability(location)
    events = natural_svc.detect_natural_events(location)
    return {
        "location": state.location,
        "timestamp": state.timestamp.isoformat(),
        "weather": state.weather.value,
        "rainfall_mm": state.rainfall,
        "reservoir_percent": state.reservoir_level,
        "soil_moisture": state.soil_moisture,
        "temperature": state.temperature,
        "availability": availability,
        "events": [
            {"type": e.type, "severity": e.severity.value, "message": e.message}
            for e in events
        ],
    }


@app.get("/api/city")
async def api_city(city: str = Query(default=None)):
    status = city_svc.get_city_system_status(city)
    issues = city_svc.detect_network_issues(city)
    return {
        "city": status.city_name,
        "population": status.population,
        "supply_demand_ratio": round(status.supply_demand_ratio, 2),
        "leakage_percent": round(status.network_leakage_rate * 100, 1),
        "per_capita_liters": status.consumption_per_capita,
        "pressure_bar": status.network_pressure,
        "issues": issues,
    }


@app.get("/api/holistic")
async def api_holistic(user_id: str = Query(default="USER-YZD-001")):
    view = system.create_holistic_view(user_id)
    return {
        "user_id": user_id,
        "generated_at": datetime.now().isoformat(),
        "view": view,
        "story": system.connect_the_dots(user_id),
        "bottlenecks": [
            {
                "layer": b.layer,
                "type": b.type,
                "severity": b.severity.value,
                "description": b.description,
                "action": b.action,
            }
            for b in system.find_bottlenecks(user_id)
        ],
        "action_plan": system.generate_action_plan(user_id),
        "water_footprint": system.calculate_water_footprint(user_id),
    }


@app.get("/api/story")
async def api_story(user_id: str = Query(default="USER-YZD-001")):
    return {"story": system.connect_the_dots(user_id)}

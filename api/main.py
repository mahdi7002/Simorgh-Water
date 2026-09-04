"""API و داشبورد سیمرغ — سازگار با layers جدید"""
from __future__ import annotations
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from jinja2 import Environment, FileSystemLoader

from config.settings import settings
from services.layers import (
    HolisticWaterAwarenessSystem,
    NaturalCycleService,
    CityInfrastructureService,
)

app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

BASE = Path(__file__).resolve().parent.parent
jinja = Environment(loader=FileSystemLoader(str(BASE / "dashboard" / "templates")))
system = HolisticWaterAwarenessSystem()
natural_svc = NaturalCycleService()
city_svc = CityInfrastructureService()


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    view = system.create_holistic_view()
    story = system.connect_the_dots()
    plan = system.generate_action_plan()
    html = jinja.get_template("index.html").render(
        request=request,
        app_name=settings.APP_NAME,
        version=getattr(settings, "APP_VERSION", "1.1"),
        city=settings.DEFAULT_CITY,
        view=view,
        story=story,
        plan=plan,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
    )
    return HTMLResponse(html)


@app.get("/api/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME, "version": getattr(settings, "APP_VERSION", "1.1")}


@app.get("/api/natural")
async def api_natural(location: str = Query(default=None)):
    state = natural_svc.get_current_state(location)
    availability = natural_svc.calculate_water_availability(location)
    events = natural_svc.detect_natural_events(location)
    return {
        "location": state.location,
        "weather": state.weather.value,
        "rainfall_mm": state.rainfall,
        "reservoir_percent": state.reservoir_level,
        "soil_moisture": state.soil_moisture,
        "temperature": state.temperature,
        "availability": availability,
        "events": [{"type": e.type, "severity": e.severity.value, "message": e.message} for e in events],
    }


@app.get("/api/city")
async def api_city(city: str = Query(default=None)):
    s = city_svc.get_city_system_status(city)
    return {
        "city": s.city_name,
        "leakage_percent": round(s.network_leakage_rate * 100, 1),
        "pressure_bar": s.network_pressure,
        "per_capita_liters": s.consumption_per_capita,
        "supply_demand_ratio": round(s.supply_demand_ratio, 2),
        "issues": city_svc.detect_network_issues(city),
    }


@app.get("/api/holistic")
async def api_holistic(user_id: str = Query(default="USER-YZD-001")):
    return system.create_holistic_view(user_id)


@app.get("/api/story")
async def api_story(user_id: str = Query(default="USER-YZD-001")):
    return {"story": system.connect_the_dots(user_id)}

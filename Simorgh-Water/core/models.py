"""
مدل‌های داده — لایه هسته
طراحی شده با الهام از مدل‌های داده پلتفرم‌های Digital Twin آب (Bentley, Xylem, Siemens SIWA)
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────
# Enums
# ─────────────────────────────────────────────────────────────

class WeatherCondition(str, Enum):
    CLEAR = "صاف"
    CLOUDY = "ابری"
    RAIN = "بارانی"
    STORM = "طوفانی"
    SNOW = "برفی"
    DUST = "گرد و غبار"  # مخصوص یزد


class Severity(str, Enum):
    INFO = "info"
    NORMAL = "normal"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


class AwarenessLevel(str, Enum):
    UNAWARE = "ناآگاه"
    AWARE = "آگاه"
    CONSCIOUS = "هوشیار"
    WISE = "حکیم"


class UsageType(str, Enum):
    SHOWER = "دوش"
    TOILET = "توالت"
    DISHWASHING = "ظرفشویی"
    LAUNDRY = "لباسشویی"
    IRRIGATION = "آبیاری"
    DRINKING = "شرب"
    UNKNOWN = "نامشخص"


# ─────────────────────────────────────────────────────────────
# لایه ۱: چرخه طبیعی
# ─────────────────────────────────────────────────────────────

@dataclass
class NaturalCycleState:
    location: str
    timestamp: datetime
    cloud_coverage: float          # 0-100 %
    humidity: float                # 0-100 %
    rainfall: float                # mm
    weather: WeatherCondition
    soil_moisture: float           # 0-1
    groundwater_level: float       # متر یا درصد
    river_flow_rate: float         # m³/s
    river_level: float             # متر
    reservoir_level: float         # درصد ظرفیت
    reservoir_capacity: float      # میلیون مترمکعب
    temperature: float = 28.0      # °C — مهم برای یزد

    @property
    def reservoir_percent(self) -> float:
        return self.reservoir_level


# ─────────────────────────────────────────────────────────────
# لایه ۲: زیرساخت شهری
# ─────────────────────────────────────────────────────────────

@dataclass
class CityWaterSystem:
    city_name: str
    population: int
    source_type: str
    daily_supply: float            # لیتر/روز
    treatment_capacity: float
    treatment_efficiency: float    # 0-1
    network_length: float          # km
    network_pressure: float        # bar
    network_leakage_rate: float    # 0-1
    daily_consumption: float
    consumption_per_capita: float  # لیتر/نفر/روز
    wastewater_generated: float
    wastewater_treated: float

    @property
    def non_revenue_water(self) -> float:
        """درصد آب بدون درآمد (NRW) — شاخص کلیدی جهانی"""
        return self.network_leakage_rate

    @property
    def supply_demand_ratio(self) -> float:
        if self.daily_consumption == 0:
            return 1.0
        return self.daily_supply / self.daily_consumption


# ─────────────────────────────────────────────────────────────
# لایه ۳: ساختمان
# ─────────────────────────────────────────────────────────────

@dataclass
class BuildingWaterFlow:
    building_id: str
    timestamp: datetime
    inlet_flow: float              # L/min
    inlet_pressure: float          # bar
    inlet_temperature: float       # °C
    kitchen_flow: float
    bathroom_flow: float
    toilet_flow: float
    washing_flow: float
    garden_flow: float
    wastewater_flow: float
    wastewater_temperature: float
    water_quality: Dict[str, float] = field(default_factory=dict)

    @property
    def total_internal_flow(self) -> float:
        return (self.kitchen_flow + self.bathroom_flow +
                self.toilet_flow + self.washing_flow + self.garden_flow)


# ─────────────────────────────────────────────────────────────
# لایه ۴: انسان
# ─────────────────────────────────────────────────────────────

@dataclass
class HumanHydration:
    user_id: str
    timestamp: datetime
    water_intake_today: float       # لیتر
    last_drink_time: Optional[datetime]
    hydration_level: float         # 0-100
    urine_color: str
    activity_level: str
    sweat_loss: float
    daily_requirement: float
    remaining_need: float
    weight_kg: float = 70.0


# ─────────────────────────────────────────────────────────────
# لایه ۵: آگاهی
# ─────────────────────────────────────────────────────────────

@dataclass
class SpiritualState:
    user_id: str
    awareness_level: AwarenessLevel
    awareness_score: float         # 0-100
    wisdom_message: str
    recommended_action: str
    last_reflection: Optional[datetime] = None


# ─────────────────────────────────────────────────────────────
# رویداد و گلوگاه
# ─────────────────────────────────────────────────────────────

@dataclass
class WaterEvent:
    type: str
    severity: Severity
    layer: str
    message: str
    impact: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Bottleneck:
    layer: str
    type: str
    severity: Severity
    description: str
    action: str
    estimated_saving_liters: Optional[float] = None


# ─────────────────────────────────────────────────────────────
# مدل‌های Pydantic برای API / Dashboard
# ─────────────────────────────────────────────────────────────

class NaturalStateResponse(BaseModel):
    location: str
    timestamp: datetime
    weather: str
    rainfall_mm: float
    reservoir_percent: float
    soil_moisture: float
    status: str
    events: List[Dict[str, Any]] = []


class CityStatusResponse(BaseModel):
    city: str
    population: int
    supply_demand_ratio: float
    leakage_percent: float
    per_capita_liters: float
    pressure_bar: float
    status: str
    issues: List[Dict[str, Any]] = []


class HolisticViewResponse(BaseModel):
    user_id: str
    generated_at: datetime
    natural: Dict[str, Any]
    city: Dict[str, Any]
    building: Dict[str, Any]
    human: Dict[str, Any]
    spirit: Dict[str, Any]
    story: str
    bottlenecks: List[Dict[str, Any]]
    action_plan: List[Dict[str, Any]]
    water_footprint: Dict[str, float]
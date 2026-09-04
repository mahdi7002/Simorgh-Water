"""
سرویس‌های ۵ لایه Simorgh Water Cycle
پیاده‌سازی کامل Mock Mode و قابل اتصال به سنسورهای واقعی
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Any, Optional

from core.models import (
    NaturalCycleState,
    CityWaterSystem,
    BuildingWaterFlow,
    HumanHydration,
    SpiritualState,
    WaterEvent,
    Bottleneck,
    WeatherCondition,
    Severity,
    AwarenessLevel,
)

from mocks.data_providers import (
    weather_api,
    env_sensors,
    water_company_api,
    network_sensors,
    iot_devices,
    quality_sensors,
    wearable_api,
    health_api,
    baaran_ai,
)

from config.settings import settings


# ============================================================
# LAYER 1 — NATURAL CYCLE
# ============================================================

class NaturalCycleService:

    def __init__(self):
        self.weather = weather_api
        self.sensors = env_sensors

    def get_current_state(
        self,
        location: str = None
    ) -> NaturalCycleState:

        location = location or settings.DEFAULT_CITY

        weather = self.weather.get_current(location)
        sensors = self.sensors.get_environmental_data(location)

        return NaturalCycleState(
            location=location,
            timestamp=datetime.now(),
            cloud_coverage=weather["clouds"],
            humidity=weather["humidity"],
            rainfall=weather["rain"],
            weather=weather["condition"],
            soil_moisture=sensors["soil_moisture"],
            groundwater_level=sensors["groundwater"],
            river_flow_rate=sensors["river_flow"],
            river_level=sensors["river_level"],
            reservoir_level=sensors["reservoir_level"],
            reservoir_capacity=sensors["reservoir_capacity"],
            temperature=weather.get("temperature", 30),
        )

    def predict_rain(
        self,
        location: str = None,
        hours_ahead: int = 24
    ) -> Dict[str, Any]:

        location = location or settings.DEFAULT_CITY
        return self.weather.get_forecast(location, hours_ahead)

    def detect_natural_events(
        self,
        location: str = None
    ) -> List[WaterEvent]:

        location = location or settings.DEFAULT_CITY
        state = self.get_current_state(location)

        events: List[WaterEvent] = []

        if (
            state.rainfall > 0
            and state.weather == WeatherCondition.RAIN
        ):
            severity = (
                Severity.NORMAL
                if state.rainfall < 8
                else Severity.HIGH
            )

            events.append(
                WaterEvent(
                    type="rain_started",
                    severity=severity,
                    layer="طبیعت",
                    message=f"باران شروع شد: {state.rainfall:.1f} میلی‌متر",
                )
            )

        if (
            state.reservoir_level
            < settings.RESERVOIR_LOW_THRESHOLD * 100
        ):
            events.append(
                WaterEvent(
                    type="reservoir_low",
                    severity=Severity.WARNING,
                    layer="طبیعت",
                    message=(
                        f"سطح سد پایین است: "
                        f"{state.reservoir_level:.0f}٪"
                    ),
                    impact="نیاز به مدیریت مصرف",
                )
            )

        if (
            state.soil_moisture
            < settings.SOIL_MOISTURE_DROUGHT
            and state.rainfall == 0
        ):
            events.append(
                WaterEvent(
                    type="drought",
                    severity=Severity.CRITICAL,
                    layer="طبیعت",
                    message="شرایط خشکسالی — رطوبت خاک بسیار پایین",
                )
            )

        if state.groundwater_level < 25:
            events.append(
                WaterEvent(
                    type="groundwater_low",
                    severity=Severity.WARNING,
                    layer="طبیعت",
                    message=(
                        f"سطح آب زیرزمینی پایین است: "
                        f"{state.groundwater_level:.1f}"
                    ),
                )
            )

        return events

    def calculate_water_availability(
        self,
        location: str = None
    ) -> Dict[str, Any]:

        location = location or settings.DEFAULT_CITY
        state = self.get_current_state(location)

        sources = {
            "reservoir": state.reservoir_level,
            "groundwater": state.groundwater_level,
            "river": min(100, state.river_flow_rate * 8),
        }

        total = sum(sources.values()) / len(sources)
        status = self._status(total)

        return {
            "total_score": round(total, 1),
            "sources": {
                key: round(value, 1)
                for key, value in sources.items()
            },
            "status": status,
            "days_remaining_estimate": max(
                5,
                int(total * 1.2)
            ),
        }

    def _status(self, total: float) -> str:

        if total > 70:
            return "عالی"

        if total > 50:
            return "خوب"

        if total > 30:
            return "نگران‌کننده"

        return "بحرانی"


# ============================================================
# LAYER 2 — CITY INFRASTRUCTURE
# ============================================================

class CityInfrastructureService:

    def __init__(self):
        self.water_company = water_company_api
        self.network = network_sensors

    def get_city_system_status(
        self,
        city: str = None
    ) -> CityWaterSystem:

        city = city or settings.DEFAULT_CITY

        company = self.water_company.get_real_time_data(city)
        network = self.network.get_network_status(city)

        return CityWaterSystem(
            city_name=city,
            population=company["population"],
            source_type=company["source"],
            daily_supply=company["supply"],
            treatment_capacity=company["treatment_capacity"],
            treatment_efficiency=company["treatment_efficiency"],
            network_length=company["network_length"],
            network_pressure=network["avg_pressure"],
            network_leakage_rate=network["leakage_rate"],
            daily_consumption=company["consumption"],
            consumption_per_capita=company["per_capita"],
            wastewater_generated=company["wastewater"],
            wastewater_treated=company["treated_wastewater"],
        )

    def detect_network_issues(
        self,
        city: str = None
    ) -> List[Dict[str, Any]]:

        city = city or settings.DEFAULT_CITY

        status = self.get_city_system_status(city)
        issues: List[Dict[str, Any]] = []

        leakage = status.network_leakage_rate

        if leakage >= settings.LEAKAGE_CRITICAL_THRESHOLD:
            issues.append({
                "type": "critical_leakage",
                "severity": Severity.CRITICAL.value,
                "message": (
                    f"نرخ نشت شبکه بسیار بالا است: "
                    f"{leakage * 100:.1f}%"
                ),
                "action": "بررسی فوری مناطق پرنشت",
            })

        elif leakage >= settings.LEAKAGE_WARNING_THRESHOLD:
            issues.append({
                "type": "high_leakage",
                "severity": Severity.WARNING.value,
                "message": (
                    f"نرخ نشت شبکه بالاست: "
                    f"{leakage * 100:.1f}%"
                ),
                "action": "اولویت‌بندی نشت‌یابی",
            })

        if status.network_pressure < 2.0:
            issues.append({
                "type": "low_pressure",
                "severity": Severity.WARNING.value,
                "message": (
                    f"فشار متوسط شبکه پایین است: "
                    f"{status.network_pressure:.2f} bar"
                ),
                "action": "بررسی فشار مناطق شبکه",
            })

        if status.supply_demand_ratio < 1.0:
            issues.append({
                "type": "supply_deficit",
                "severity": Severity.CRITICAL.value,
                "message": "عرضه آب کمتر از تقاضای روزانه است",
                "action": "مدیریت تقاضا و منابع تأمین",
            })

        zones = self.network.get_zone_consumption(city)

        for zone in zones:
            if zone["priority"] >= 3:
                issues.append({
                    "type": "high_consumption_zone",
                    "severity": Severity.INFO.value,
                    "message": (
                        f"مصرف بالای منطقه: "
                        f"{zone['name']}"
                    ),
                    "action": "تحلیل مصرف منطقه‌ای",
                })

        return issues


# ============================================================
# LAYER 3 — BUILDING
# ============================================================

class BuildingWaterService:

    def __init__(self):
        self.devices = iot_devices
        self.quality = quality_sensors

    def get_building_flow(
        self,
        building_id: str = "BUILDING-YZD-001"
    ) -> BuildingWaterFlow:

        readings = self.devices.get_all_readings(building_id)
        quality = self.quality.get_measurements(building_id)

        return BuildingWaterFlow(
            building_id=building_id,
            timestamp=datetime.now(),

            inlet_flow=readings["main_inlet"]["flow"],
            inlet_pressure=readings["main_inlet"]["pressure"],
            inlet_temperature=readings["main_inlet"]["temp"],

            kitchen_flow=readings["kitchen"]["flow"],
            bathroom_flow=readings["bathroom"]["flow"],
            toilet_flow=readings["toilet"]["flow"],
            washing_flow=readings["washing"]["flow"],
            garden_flow=readings["garden"]["flow"],

            wastewater_flow=readings["drain"]["flow"],
            wastewater_temperature=readings["drain"]["temp"],

            water_quality=quality,
        )

    def analyze_building(
        self,
        building_id: str = "BUILDING-YZD-001"
    ) -> Dict[str, Any]:

        flow = self.get_building_flow(building_id)

        quality_status = "مناسب"

        if (
            flow.water_quality.get("turbidity", 0) > 1.0
            or flow.water_quality.get("tds", 0) > 600
        ):
            quality_status = "نیازمند بررسی"

        return {
            "building_id": flow.building_id,
            "timestamp": flow.timestamp.isoformat(),
            "inlet_flow_lpm": round(flow.inlet_flow, 2),
            "pressure_bar": round(flow.inlet_pressure, 2),
            "internal_flow_lpm": round(
                flow.total_internal_flow,
                2
            ),
            "wastewater_flow_lpm": round(
                flow.wastewater_flow,
                2
            ),
            "quality": {
                key: round(value, 2)
                for key, value in flow.water_quality.items()
            },
            "quality_status": quality_status,
        }


# ============================================================
# LAYER 4 — HUMAN
# ============================================================

class HumanHydrationService:

    def __init__(self):
        self.wearable = wearable_api
        self.health = health_api

    def get_hydration(
        self,
        user_id: str = "USER-YZD-001"
    ) -> HumanHydration:

        wearable = self.wearable.get_data(user_id)
        health = self.health.get_data(user_id)

        weight = health["weight"]
        intake = health["water_intake"]
        sweat_loss = wearable["sweat_loss"]

        # نیاز پایه تقریبی بر اساس وزن
        daily_requirement = max(
            1.5,
            weight * 0.035
        )

        # اصلاح ساده بر اساس فعالیت و تعریق
        daily_requirement += sweat_loss * 0.35

        remaining = max(
            0,
            daily_requirement - intake
        )

        return HumanHydration(
            user_id=user_id,
            timestamp=datetime.now(),
            water_intake_today=intake,
            last_drink_time=health["last_drink"],
            hydration_level=wearable["hydration"],
            urine_color=health["urine_color"],
            activity_level=wearable["activity_level"],
            sweat_loss=sweat_loss,
            daily_requirement=daily_requirement,
            remaining_need=remaining,
            weight_kg=weight,
        )

    def analyze(
        self,
        user_id: str = "USER-YZD-001"
    ) -> Dict[str, Any]:

        hydration = self.get_hydration(user_id)

        if hydration.hydration_level < 50:
            status = "بحرانی"
        elif hydration.hydration_level < settings.HYDRATION_WARNING:
            status = "نیازمند توجه"
        else:
            status = "مناسب"

        return {
            "user_id": hydration.user_id,
            "hydration_level": round(
                hydration.hydration_level,
                1
            ),
            "status": status,
            "water_intake_liters": round(
                hydration.water_intake_today,
                2
            ),
            "daily_requirement_liters": round(
                hydration.daily_requirement,
                2
            ),
            "remaining_need_liters": round(
                hydration.remaining_need,
                2
            ),
            "activity_level": hydration.activity_level,
            "sweat_loss_liters": round(
                hydration.sweat_loss,
                2
            ),
        }


# ============================================================
# LAYER 5 — AWARENESS
# ============================================================

class AwarenessService:

    def __init__(self):
        self.ai = baaran_ai

    def get_state(
        self,
        user_id: str = "USER-YZD-001",
        context: Optional[Dict[str, Any]] = None
    ) -> SpiritualState:

        analysis = self.ai.analyze_spiritual_state(user_id)
        wisdom = self.ai.generate_wisdom_message(
            user_id,
            context or {}
        )
        action = self.ai.recommend_action(user_id)

        level_map = {
            "ناآگاه": AwarenessLevel.UNAWARE,
            "آگاه": AwarenessLevel.AWARE,
            "هوشیار": AwarenessLevel.CONSCIOUS,
            "حکیم": AwarenessLevel.WISE,
        }

        level = level_map.get(
            analysis["awareness_level"],
            AwarenessLevel.AWARE,
        )

        return SpiritualState(
            user_id=user_id,
            awareness_level=level,
            awareness_score=analysis["awareness_score"],
            wisdom_message=wisdom["title"],
            recommended_action=action,
            last_reflection=datetime.now(),
        )

    def analyze(
        self,
        user_id: str = "USER-YZD-001",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:

        state = self.get_state(user_id, context)

        return {
            "user_id": state.user_id,
            "level": state.awareness_level.value,
            "score": round(state.awareness_score, 1),
            "wisdom": state.wisdom_message,
            "recommended_action": state.recommended_action,
        }


# ============================================================
# HOLISTIC SYSTEM
# ============================================================

class HolisticWaterAwarenessSystem:

    def __init__(self):

        self.natural = NaturalCycleService()
        self.city = CityInfrastructureService()
        self.building = BuildingWaterService()
        self.human = HumanHydrationService()
        self.awareness = AwarenessService()

    def create_holistic_view(
        self,
        user_id: str = "USER-YZD-001"
    ) -> Dict[str, Any]:

        natural_state = self.natural.get_current_state()
        city_state = self.city.get_city_system_status()
        building = self.building.analyze_building()
        human = self.human.analyze(user_id)

        context = {
            "reservoir": natural_state.reservoir_level,
            "soil_moisture": natural_state.soil_moisture,
            "city_leakage": city_state.network_leakage_rate,
            "hydration": human["hydration_level"],
        }

        spirit = self.awareness.analyze(
            user_id,
            context
        )

        return {
            "user_id": user_id,
            "generated_at": datetime.now().isoformat(),

            "natural": {
                "location": natural_state.location,
                "weather": natural_state.weather.value,
                "rainfall_mm": natural_state.rainfall,
                "humidity": natural_state.humidity,
                "soil_moisture": natural_state.soil_moisture,
                "groundwater": natural_state.groundwater_level,
                "river_flow": natural_state.river_flow_rate,
                "reservoir_percent": natural_state.reservoir_level,
                "temperature": natural_state.temperature,
            },

            "city": {
                "city": city_state.city_name,
                "population": city_state.population,
                "supply_demand_ratio": round(
                    city_state.supply_demand_ratio,
                    2
                ),
                "leakage_percent": round(
                    city_state.network_leakage_rate * 100,
                    1
                ),
                "pressure_bar": round(
                    city_state.network_pressure,
                    2
                ),
                "per_capita_liters": round(
                    city_state.consumption_per_capita,
                    1
                ),
            },

            "building": building,
            "human": human,
            "spirit": spirit,
        }

    def connect_the_dots(
        self,
        user_id: str = "USER-YZD-001"
    ) -> str:

        natural = self.natural.get_current_state()
        city = self.city.get_city_system_status()
        human = self.human.get_hydration(user_id)

        return (
            f"در {natural.location}، "
            f"وضعیت طبیعی آب با سطح سد "
            f"{natural.reservoir_level:.0f}٪ و رطوبت خاک "
            f"{natural.soil_moisture:.2f} ثبت شده است. "
            f"در شبکه شهری، نسبت عرضه به تقاضا "
            f"{city.supply_demand_ratio:.2f} و نرخ نشت "
            f"{city.network_leakage_rate * 100:.1f}٪ است. "
            f"در سطح انسان، میزان آب دریافت‌شده امروز "
            f"{human.water_intake_today:.2f} لیتر بوده است. "
            f"این سه مقیاس نشان می‌دهند که آب یک سیستم "
            f"پیوسته از طبیعت تا شهر و بدن انسان است."
        )

    def find_bottlenecks(
        self,
        user_id: str = "USER-YZD-001"
    ) -> List[Bottleneck]:

        bottlenecks: List[Bottleneck] = []

        natural = self.natural.get_current_state()
        city = self.city.get_city_system_status()
        human = self.human.get_hydration(user_id)

        if natural.reservoir_level < (
            settings.RESERVOIR_LOW_THRESHOLD * 100
        ):
            bottlenecks.append(
                Bottleneck(
                    layer="طبیعت",
                    type="reservoir",
                    severity=Severity.WARNING,
                    description="ذخیره سد پایین است",
                    action="کاهش مصرف و پایش منابع",
                    estimated_saving_liters=0,
                )
            )

        if city.network_leakage_rate >= (
            settings.LEAKAGE_CRITICAL_THRESHOLD
        ):
            bottlenecks.append(
                Bottleneck(
                    layer="شهر",
                    type="network_leakage",
                    severity=Severity.CRITICAL,
                    description="نشت شبکه بیش از حد بحرانی است",
                    action="نشت‌یابی و تعمیر مناطق اولویت‌دار",
                    estimated_saving_liters=(
                        city.daily_supply
                        * city.network_leakage_rate
                    ),
                )
            )

        elif city.network_leakage_rate >= (
            settings.LEAKAGE_WARNING_THRESHOLD
        ):
            bottlenecks.append(
                Bottleneck(
                    layer="شهر",
                    type="network_leakage",
                    severity=Severity.WARNING,
                    description="نرخ نشت شبکه بالاست",
                    action="پایش و کاهش NRW",
                    estimated_saving_liters=(
                        city.daily_supply
                        * city.network_leakage_rate
                    ),
                )
            )

        if human.hydration_level < settings.HYDRATION_WARNING:
            bottlenecks.append(
                Bottleneck(
                    layer="انسان",
                    type="hydration",
                    severity=Severity.WARNING,
                    description="سطح آب بدن نیازمند توجه است",
                    action="مصرف آب متناسب با شرایط بدن",
                )
            )

        return bottlenecks

    def calculate_water_footprint(
        self,
        user_id: str = "USER-YZD-001"
    ) -> Dict[str, float]:

        human = self.human.get_hydration(user_id)
        building = self.building.get_building_flow()

        household_daily = (
            building.total_internal_flow * 60
        )

        return {
            "direct_human_liters": round(
                human.water_intake_today,
                2
            ),
            "building_flow_estimate_liters": round(
                household_daily,
                2
            ),
            "combined_daily_estimate_liters": round(
                household_daily
                + human.water_intake_today,
                2
            ),
        }

    def generate_action_plan(
        self,
        user_id: str = "USER-YZD-001"
    ) -> List[Dict[str, Any]]:

        plan: List[Dict[str, Any]] = []

        city = self.city.get_city_system_status()
        natural = self.natural.get_current_state()
        human = self.human.get_hydration(user_id)

        if city.network_leakage_rate >= (
            settings.LEAKAGE_WARNING_THRESHOLD
        ):
            plan.append({
                "priority": "HIGH",
                "layer": "شهر",
                "action": "اولویت دادن به نشت‌یابی شبکه",
            })

        if natural.reservoir_level < (
            settings.RESERVOIR_LOW_THRESHOLD * 100
        ):
            plan.append({
                "priority": "HIGH",
                "layer": "طبیعت",
                "action": "کاهش مصرف و حفاظت از ذخایر",
            })

        if human.hydration_level < settings.HYDRATION_WARNING:
            plan.append({
                "priority": "MEDIUM",
                "layer": "انسان",
                "action": "توجه بیشتر به آب‌رسانی بدن",
            })

        plan.append({
            "priority": "LOW",
            "layer": "آگاهی",
            "action": baaran_ai.recommend_action(user_id),
        })

        return plan

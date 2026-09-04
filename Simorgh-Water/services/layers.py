"""
سرویس‌های ۵ لایه — پیاده‌سازی کامل و قابل اجرا
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Any, Optional

from core.models import (
    NaturalCycleState, CityWaterSystem, BuildingWaterFlow,
    HumanHydration, SpiritualState, WaterEvent, Bottleneck,
    WeatherCondition, Severity, AwarenessLevel, UsageType
)
from mocks.data_providers import (
    weather_api, env_sensors, water_company_api, network_sensors,
    iot_devices, quality_sensors, wearable_api, health_api, baaran_ai
)
from config.settings import settings


class NaturalCycleService:
    def __init__(self):
        self.weather = weather_api
        self.sensors = env_sensors

    def get_current_state(self, location: str = None) -> NaturalCycleState:
        location = location or settings.DEFAULT_CITY
        w = self.weather.get_current(location)
        s = self.sensors.get_environmental_data(location)
        return NaturalCycleState(
            location=location,
            timestamp=datetime.now(),
            cloud_coverage=w["clouds"],
            humidity=w["humidity"],
            rainfall=w["rain"],
            weather=w["condition"],
            soil_moisture=s["soil_moisture"],
            groundwater_level=s["groundwater"],
            river_flow_rate=s["river_flow"],
            river_level=s["river_level"],
            reservoir_level=s["reservoir_level"],
            reservoir_capacity=s["reservoir_capacity"],
            temperature=w.get("temperature", 30),
        )

    def predict_rain(self, location: str = None, hours_ahead: int = 24) -> Dict:
        location = location or settings.DEFAULT_CITY
        return self.weather.get_forecast(location, hours_ahead)

    def detect_natural_events(self, location: str = None) -> List[WaterEvent]:
        location = location or settings.DEFAULT_CITY
        state = self.get_current_state(location)
        events = []

        if state.rainfall > 0 and state.weather == WeatherCondition.RAIN:
            sev = Severity.NORMAL if state.rainfall < 8 else Severity.HIGH
            events.append(WaterEvent(
                type="rain_started", severity=sev, layer="طبیعت",
                message=f"باران شروع شد: {state.rainfall:.1f} میلی‌متر"
            ))

        if state.reservoir_level < settings.RESERVOIR_LOW_THRESHOLD * 100:
            events.append(WaterEvent(
                type="reservoir_low", severity=Severity.WARNING, layer="طبیعت",
                message=f"سطح سد پایین است: {state.reservoir_level:.0f}٪",
                impact="نیاز به مدیریت مصرف"
            ))

        if state.soil_moisture < settings.SOIL_MOISTURE_DROUGHT and state.rainfall == 0:
            events.append(WaterEvent(
                type="drought", severity=Severity.CRITICAL, layer="طبیعت",
                message="شرایط خشکسالی — رطوبت خاک بسیار پایین"
            ))

        return events

    def calculate_water_availability(self, location: str = None) -> Dict:
        location = location or settings.DEFAULT_CITY
        state = self.get_current_state(location)
        sources = {
            "reservoir": state.reservoir_level,
            "groundwater": state.groundwater_level,
            "river": min(100, state.river_flow_rate * 8),
        }
        total = sum(sources.values()) / 3
        status = self._status(total)
        return {
            "total_score": round(total, 1),
            "sources": {k: round(v, 1) for k, v in sources.items()},
            "status": status,
            "days_remaining_estimate": max(5, int(total * 1.2)),
        }

    def _status(self, total: float) -> str:
        if total > 70:
            return "عالی"
        if total > 50:
            return "خوب"
        if total > 30:
            return "نگران‌کننده"
        return "بحرانی"


class CityInfrastructureService:
    def __init__(self):
        self.company = water_company_api
        self.sensors = network_sensors

    def get_city_system_status(self, city: str = None) -> CityWaterSystem:
        city = city or settings.DEFAULT_CITY
        c = self.company.get_real_time_data(city)
        s = self.sensors.get_network_status(city)
        return CityWaterSystem(
            city_name=city,
            population=c["population"],
            source_type=c["source"],
            daily_supply=c["supply"],
            treatment_capacity=c["treatment_capacity"],
            treatment_efficiency=c["treatment_efficiency"],
            network_length=c["network_length"],
            network_pressure=s["avg_pressure"],
            network_leakage_rate=s["leakage_rate"],
            daily_consumption=c["consumption"],
            consumption_per_capita=c["per_capita"],
            wastewater_generated=c["wastewater"],
            wastewater_treated=c["treated_wastewater"],
        )

    def detect_network_issues(self, city: str = None) -> List[Dict]:
        city = city or settings.DEFAULT_CITY
        system = self.get_city_system_status(city)
        issues = []

        if system.network_leakage_rate > settings.LEAKAGE_CRITICAL_THRESHOLD:
            issues.append({
                "type": "high_leakage",
                "severity": "critical",
                "location": "شبکه توزیع",
                "description": f"نشت {system.network_leakage_rate*100:.1f}٪ از آب",
                "impact": f"{system.daily_supply * system.network_leakage_rate:,.0f} لیتر/روز تلف می‌شود",
            })
        elif system.network_leakage_rate > settings.LEAKAGE_WARNING_THRESHOLD:
            issues.append({
                "type": "elevated_leakage",
                "severity": "high",
                "location": "شبکه توزیع",
                "description": f"نشت بالاتر از حد مطلوب ({system.network_leakage_rate*100:.1f}٪)",
            })

        if system.network_pressure < 2.0:
            issues.append({
                "type": "low_pressure",
                "severity": "medium",
                "location": "شبکه توزیع",
                "description": "فشار آب پایین است",
                "impact": "کاربران طبقات بالا مشکل دارند",
            })

        if system.daily_consumption > system.daily_supply * 0.98:
            issues.append({
                "type": "supply_shortage",
                "severity": "critical",
                "location": "کل شهر",
                "description": "مصرف نزدیک یا بیشتر از عرضه",
                "impact": "احتمال قطعی یا جیره‌بندی",
            })

        return issues

    def optimize_distribution(self, city: str = None) -> Dict:
        city = city or settings.DEFAULT_CITY
        system = self.get_city_system_status(city)
        zones = self.sensors.get_zone_consumption(city)
        total_demand = sum(z["consumption"] for z in zones) or 1
        optimized = {}
        for zone in zones:
            allocation = (zone["consumption"] / total_demand) * system.daily_supply
            optimized[zone["name"]] = {
                "current": zone["consumption"],
                "allocated": round(allocation, 0),
                "priority": zone["priority"],
            }
        return {
            "zones": optimized,
            "total_allocated": sum(z["allocated"] for z in optimized.values()),
            "efficiency_note": "تخصیص بر اساس اولویت و مصرف واقعی",
        }


class BuildingMonitoringService:
    def __init__(self):
        self.devices = iot_devices
        self.quality = quality_sensors

    def track_water_flow(self, building_id: str = "BLD-YZD-001") -> BuildingWaterFlow:
        d = self.devices.get_all_readings(building_id)
        q = self.quality.get_measurements(building_id)
        return BuildingWaterFlow(
            building_id=building_id,
            timestamp=datetime.now(),
            inlet_flow=d["main_inlet"]["flow"],
            inlet_pressure=d["main_inlet"]["pressure"],
            inlet_temperature=d["main_inlet"]["temp"],
            kitchen_flow=d["kitchen"]["flow"],
            bathroom_flow=d["bathroom"]["flow"],
            toilet_flow=d["toilet"]["flow"],
            washing_flow=d["washing"]["flow"],
            garden_flow=d["garden"]["flow"],
            wastewater_flow=d["drain"]["flow"],
            wastewater_temperature=d["drain"]["temp"],
            water_quality=q,
        )

    def detect_usage_type(self, building_id: str = "BLD-YZD-001") -> Dict:
        flow = self.track_water_flow(building_id)
        types = []
        if flow.bathroom_flow > 7 and flow.inlet_temperature > 32:
            types.append(UsageType.SHOWER.value)
        if flow.toilet_flow > 0.5:
            types.append(UsageType.TOILET.value)
        if flow.kitchen_flow > 1:
            types.append(UsageType.DISHWASHING.value)
        if flow.washing_flow > 2:
            types.append(UsageType.LAUNDRY.value)
        if flow.garden_flow > 1:
            types.append(UsageType.IRRIGATION.value)
        primary = types[0] if types else UsageType.UNKNOWN.value
        return {"types": types, "primary": primary}

    def suggest_improvements(self, building_id: str = "BLD-YZD-001") -> List[Dict]:
        history = self.devices.get_historical_data(building_id)
        avg = sum(h["total_liters"] for h in history) / len(history)
        suggestions = []
        if avg > 320:
            suggestions.append({
                "type": "behavior",
                "title": "کاهش مصرف خانگی",
                "description": f"میانگین مصرف روزانه شما {avg:.0f} لیتر است. با کاهش ۲۰٪ حدود {avg*0.2*30:.0f} لیتر در ماه صرفه‌جویی می‌شود.",
                "priority": "high",
            })
        suggestions.append({
            "type": "maintenance",
            "title": "بررسی نشت توالت",
            "description": "حتی یک نشت کوچک می‌تواند صدها لیتر در ماه هدر دهد.",
            "priority": "medium",
        })
        return suggestions


class HumanHydrationService:
    def __init__(self):
        self.wearable = wearable_api
        self.health = health_api

    def get_hydration_status(self, user_id: str = "USER-YZD-001") -> HumanHydration:
        w = self.wearable.get_data(user_id)
        h = self.health.get_data(user_id)
        req = self._calc_requirement(h["weight"], w["activity_level"], w["ambient_temp"])
        return HumanHydration(
            user_id=user_id,
            timestamp=datetime.now(),
            water_intake_today=h["water_intake"],
            last_drink_time=h["last_drink"],
            hydration_level=w["hydration"],
            urine_color=h["urine_color"],
            activity_level=w["activity_level"],
            sweat_loss=w["sweat_loss"],
            daily_requirement=req,
            remaining_need=max(0, req - h["water_intake"]),
            weight_kg=h["weight"],
        )

    def _calc_requirement(self, weight: float, activity: str, temp: float) -> float:
        base = weight * 0.035
        factors = {"sedentary": 1.0, "moderate": 1.25, "high": 1.5}
        base *= factors.get(activity, 1.1)
        if temp > 32:
            base *= 1.25
        elif temp > 28:
            base *= 1.1
        return round(base, 2)


class HolisticWaterAwarenessSystem:
    """
    سیستم جامع آگاهی آبی
    اتصال تمام لایه‌ها — قلب پروژه سیمرغ
    """

    def __init__(self):
        self.natural = NaturalCycleService()
        self.city = CityInfrastructureService()
        self.building = BuildingMonitoringService()
        self.human = HumanHydrationService()
        self.ai = baaran_ai

    def create_holistic_view(self, user_id: str = "USER-YZD-001",
                             city: str = None, building_id: str = "BLD-YZD-001") -> Dict:
        city = city or settings.DEFAULT_CITY
        natural_state = self.natural.get_current_state(city)
        availability = self.natural.calculate_water_availability(city)
        events = self.natural.detect_natural_events(city)
        city_sys = self.city.get_city_system_status(city)
        issues = self.city.detect_network_issues(city)
        flow = self.building.track_water_flow(building_id)
        usage = self.building.detect_usage_type(building_id)
        suggestions = self.building.suggest_improvements(building_id)
        hydration = self.human.get_hydration_status(user_id)
        spirit_raw = self.ai.analyze_spiritual_state(user_id)
        wisdom = self.ai.generate_wisdom_message(user_id)
        action = self.ai.recommend_action(user_id)

        view = {
            "۱_آسمان": {
                "باران": self.natural.predict_rain(city),
                "منابع": availability,
                "رویدادها": [{"type": e.type, "severity": e.severity.value, "message": e.message} for e in events],
                "وضعیت_فعلی": {
                    "weather": natural_state.weather.value,
                    "reservoir": natural_state.reservoir_level,
                    "soil": natural_state.soil_moisture,
                    "temp": natural_state.temperature,
                },
            },
            "۲_شهر": {
                "وضعیت_شبکه": {
                    "pressure": city_sys.network_pressure,
                    "leakage": round(city_sys.network_leakage_rate * 100, 1),
                    "per_capita": city_sys.consumption_per_capita,
                    "ratio": round(city_sys.supply_demand_ratio, 2),
                },
                "مشکلات": issues,
            },
            "۳_خانه": {
                "جریان_فعلی": {
                    "inlet": round(flow.inlet_flow, 1),
                    "pressure": round(flow.inlet_pressure, 1),
                    "quality_tds": flow.water_quality.get("tds"),
                },
                "نوع_استفاده": usage,
                "پیشنهادات": suggestions,
            },
            "۴_بدن": {
                "وضعیت": {
                    "hydration": round(hydration.hydration_level, 0),
                    "intake": round(hydration.water_intake_today, 1),
                    "need": round(hydration.remaining_need, 1),
                    "requirement": hydration.daily_requirement,
                },
            },
            "۵_روح": {
                "سطح_آگاهی": spirit_raw,
                "حکمت_امروز": wisdom,
                "عمل_پیشنهادی": action,
            },
        }
        return view

    def connect_the_dots(self, user_id: str = "USER-YZD-001") -> str:
        view = self.create_holistic_view(user_id)
        parts = []

        rain = view["۱_آسمان"]["باران"]
        if rain["rain_probability"] > 0.45:
            parts.append(f"🌧️ باران امروز محتمل است ({rain['rain_probability']*100:.0f}٪)")
            parts.append(f"   ↓ سد و منابع طبیعی تقویت می‌شوند")
        else:
            parts.append("☀️ امروز باران قابل‌توجهی پیش‌بینی نمی‌شود")
            parts.append(f"   ↓ وضعیت منابع: {view['۱_آسمان']['منابع']['status']}")

        city = view["۲_شهر"]["وضعیت_شبکه"]
        parts.append(f"🏙️ شبکه شهر با فشار {city['pressure']:.1f} بار و نشت {city['leakage']:.1f}٪ کار می‌کند")
        if view["۲_شهر"]["مشکلات"]:
            parts.append(f"   ⚠️ {len(view['۲_شهر']['مشکلات'])} مشکل شناسایی شد")

        home = view["۳_خانه"]["جریان_فعلی"]
        parts.append(f"🏠 آب با دبی {home['inlet']:.1f} لیتر/دقیقه به خانه می‌رسد")
        usage = view["۳_خانه"]["نوع_استفاده"]["primary"]
        if usage != "نامشخص":
            parts.append(f"   → استفاده فعلی: {usage}")

        body = view["۴_بدن"]["وضعیت"]
        parts.append(f"🧑 آبرسانی بدن: {body['hydration']:.0f}٪")
        if body["hydration"] < 70:
            parts.append(f"   💧 نیاز به نوشیدن حدود {body['need']:.1f} لیتر دیگر")

        spirit = view["۵_روح"]["سطح_آگاهی"]
        parts.append(f"✨ سطح آگاهی: {spirit['awareness_level']} ({spirit['awareness_score']:.0f}/100)")
        parts.append(f"🌊 حکمت امروز: {view['۵_روح']['حکمت_امروز']['title']}")

        parts.append("\n" + "═" * 50)
        parts.append("همه چیز به هم متصل است:")
        parts.append("آسمان → زمین → شهر → خانه → بدن → روح")
        parts.append("═" * 50)
        return "\n".join(parts)

    def find_bottlenecks(self, user_id: str = "USER-YZD-001") -> List[Bottleneck]:
        view = self.create_holistic_view(user_id)
        bns = []

        if view["۱_آسمان"]["منابع"]["status"] == "بحرانی":
            bns.append(Bottleneck(
                layer="طبیعت", type="منابع کم", severity=Severity.CRITICAL,
                description="منابع طبیعی در حد بحران",
                action="صرفه‌جویی شدید و مدیریت تقاضا ضروری است"
            ))

        for issue in view["۲_شهر"]["مشکلات"]:
            if issue["type"] in ("high_leakage", "supply_shortage"):
                bns.append(Bottleneck(
                    layer="زیرساخت", type=issue["type"],
                    severity=Severity.CRITICAL if issue["severity"] == "critical" else Severity.HIGH,
                    description=issue["description"],
                    action="اقدام فوری توسط شرکت آب و مدیریت شهری"
                ))

        for s in view["۳_خانه"]["پیشنهادات"]:
            if s["priority"] in ("critical", "high"):
                bns.append(Bottleneck(
                    layer="ساختمان", type=s["type"], severity=Severity.HIGH,
                    description=s["description"], action=s["title"]
                ))

        if view["۴_بدن"]["وضعیت"]["hydration"] < 50:
            bns.append(Bottleneck(
                layer="بدن", type="کم‌آبی", severity=Severity.HIGH,
                description="بدن شما کم‌آب است", action="فوراً آب بنوشید"
            ))

        if view["۵_روح"]["سطح_آگاهی"]["awareness_score"] < 45:
            bns.append(Bottleneck(
                layer="آگاهی", type="غفلت", severity=Severity.MEDIUM,
                description="سطح آگاهی نسبت به آب پایین است",
                action="تأمل روزانه و ثبت عادت‌های آبی"
            ))

        return bns

    def calculate_water_footprint(self, user_id: str = "USER-YZD-001") -> Dict[str, float]:
        # تقریبی بر اساس میانگین‌های جهانی + داده شبیه‌سازی
        direct = random_monthly()
        virtual_food = direct * 2.8      # آب مجازی غذا
        network_loss = direct * 0.18
        energy = direct * 0.35
        total = direct + virtual_food + network_loss + energy
        return {
            "direct_home": round(direct, 0),
            "virtual_food": round(virtual_food, 0),
            "network_loss_share": round(network_loss, 0),
            "energy_related": round(energy, 0),
            "total_monthly_liters": round(total, 0),
        }

    def generate_action_plan(self, user_id: str = "USER-YZD-001") -> List[Dict]:
        bns = self.find_bottlenecks(user_id)
        plan = []
        for bn in bns:
            if bn.severity in (Severity.CRITICAL, Severity.HIGH):
                plan.append({
                    "priority": 1,
                    "layer": bn.layer,
                    "action": bn.action,
                    "deadline": "امروز / این هفته",
                })
        plan.append({
            "priority": 2,
            "layer": "آگاهی",
            "action": "هر روز یک جمله کوتاه درباره آب بنویس یا به اشتراک بگذار",
            "deadline": "۳۰ روز",
        })
        plan.append({
            "priority": 3,
            "layer": "جامعه",
            "action": "مشکلات شبکه را در شورای محله یا اپلیکیشن شهری گزارش کن",
            "deadline": "۱ ماه",
        })
        return plan


def random_monthly() -> float:
    import random
    return random.uniform(4500, 9500)
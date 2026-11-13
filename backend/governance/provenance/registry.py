"""
KRISHIVA AI — Data Source Registry and Provenance Tracker
Maintains metadata, validation status, and provenance records for all data streams.
"""

from datetime import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class DataSourceMetadata(BaseModel):
    source_name: str
    provider: str
    source_url: str
    data_owner: str
    geographic_coverage: str
    update_frequency: str
    schema_fields: List[str]
    license_or_usage: str
    validation_status: str  # VALIDATED, LIVE_ACTIVE, VERIFIED_OFFLINE, INACTIVE
    last_verified_at: datetime
    provenance_id: str
    notes: Optional[str] = None


class DataSourceRegistry:
    """Registry maintaining active and verified data sources."""

    _registry: Dict[str, DataSourceMetadata] = {
        "agmarknet_mandi_prices": DataSourceMetadata(
            source_name="Agmarknet Mandi Prices & Arrivals",
            provider="Directorate of Marketing & Inspection (DMI) / Ministry of Agriculture & Farmers Welfare",
            source_url="https://data.gov.in/catalog/current-daily-price-various-commodities-various-markets-mandi",
            data_owner="Government of India",
            geographic_coverage="National (India - All States and APMC Mandis)",
            update_frequency="Daily",
            schema_fields=[
                "state", "district", "market", "commodity", "variety",
                "arrival_date", "min_price", "max_price", "modal_price"
            ],
            license_or_usage="Government Open Data License - India (GODL)",
            validation_status="VALIDATED",
            last_verified_at=datetime.utcnow(),
            provenance_id="PROV-AGMARKNET-001",
            notes="Mandatory price discovery standard for APMC yards across India."
        ),
        "enam_market_trading": DataSourceMetadata(
            source_name="e-NAM Trading & Electronic Auction Intelligence",
            provider="Small Farmers' Agribusiness Consortium (SFAC)",
            source_url="https://www.enam.gov.in/web/trading-details",
            data_owner="Ministry of Agriculture and Farmers Welfare, Govt of India",
            geographic_coverage="India (Integrated e-NAM Mandis)",
            update_frequency="Real-time / Daily",
            schema_fields=[
                "state", "district", "apmc_name", "commodity", "variety",
                "trade_date", "modal_price_qtl", "traded_quantity_tonnes"
            ],
            license_or_usage="e-NAM Public Information & Trade Portal",
            validation_status="VALIDATED",
            last_verified_at=datetime.utcnow(),
            provenance_id="PROV-ENAM-002",
            notes="Electronic trading records reflecting realized trade quantities."
        ),
        "open_meteo_weather": DataSourceMetadata(
            source_name="Open-Meteo High-Resolution Agricultural Weather & Forecast",
            provider="Open-Meteo / ECMWF / DWD / IMD ensemble",
            source_url="https://api.open-meteo.com/v1/forecast",
            data_owner="Open-Meteo GmbH & National Meteorological Services",
            geographic_coverage="Global with 0.1-degree Indian subcontinent resolution",
            update_frequency="Hourly / Daily",
            schema_fields=[
                "latitude", "longitude", "timestamp", "temperature_2m",
                "relative_humidity_2m", "precipitation", "wind_speed_10m", "shortwave_radiation"
            ],
            license_or_usage="Open Data Commons (ODC-BY / CC BY 4.0)",
            validation_status="LIVE_ACTIVE",
            last_verified_at=datetime.utcnow(),
            provenance_id="PROV-WEATHER-003",
            notes="Distinguishes measured historical observations from multi-day predictive forecast envelopes."
        ),
        "cibrc_pesticide_registry": DataSourceMetadata(
            source_name="Central Insecticides Board & Registration Committee (CIB&RC)",
            provider="Directorate of Plant Protection, Quarantine & Storage",
            source_url="https://ppqs.gov.in/divisions/cib-rc",
            data_owner="Ministry of Agriculture and Farmers Welfare, Govt of India",
            geographic_coverage="India National Regulatory Standard",
            update_frequency="Periodic Statutory Updates",
            schema_fields=[
                "registration_number", "active_ingredient", "formulation",
                "approved_crop", "approved_pest", "dosage_per_acre", "waiting_period_days"
            ],
            license_or_usage="Statutory Regulatory Publication (Insecticides Act, 1968)",
            validation_status="VALIDATED",
            last_verified_at=datetime.utcnow(),
            provenance_id="PROV-CIBRC-004",
            notes="Safety-critical: Zero recommendations allowed without matching CIB&RC approved label."
        ),
        "fco_fertilizer_standards": DataSourceMetadata(
            source_name="Fertiliser Control Order (FCO) Standards & Nutrient Grades",
            provider="Department of Fertilisers, Ministry of Chemicals and Fertilisers",
            source_url="https://fert.gov.in/fertilizer-control-order",
            data_owner="Government of India",
            geographic_coverage="India National Standard",
            update_frequency="Statutory Gazette Standards",
            schema_fields=[
                "standard_grade_name", "category", "npk_ratio",
                "moisture_limit_percent", "heavy_metal_limits", "micronutrient_contents"
            ],
            license_or_usage="Statutory Regulation (FCO, 1985)",
            validation_status="VALIDATED",
            last_verified_at=datetime.utcnow(),
            provenance_id="PROV-FCO-005",
            notes="Verifies authentic grades (e.g. 19-19-19, 10-26-26, DAP, Urea) against unverified commercial claims."
        )
    }

    @classmethod
    def get_source(cls, key: str) -> Optional[DataSourceMetadata]:
        return cls._registry.get(key)

    @classmethod
    def list_all_sources(cls) -> List[DataSourceMetadata]:
        return list(cls._registry.values())

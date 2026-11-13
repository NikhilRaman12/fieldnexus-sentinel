"""
KRISHIVA AI — Real-time and Verified Agricultural Market Data Adapter
Interfaces with AGMARKNET (via data.gov.in) and e-NAM public information APIs.
Provides normalization for APMC Mandis, commodities, varieties, arrivals, and modal prices.

CRITICAL BUILDATHON INTEGRITY RULES:
- Never label static/unconnected mandi prices or arrivals as 'agmarknet_verified' or 'verified_offline'.
- When live API credentials/data are unavailable, label records 'DEMO_SIMULATED' with explicit warning flags.
- Distinguish live observations from demo simulation assumptions.
- Expose base_modal_price versus modal_price consistently (no key-mapping divergence).
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
from pydantic import BaseModel, Field
from backend.config.settings import settings
from backend.core.logging import get_logger

logger = get_logger("agmarknet_adapter")


class MandiPriceRecord(BaseModel):
    state: str
    district: str
    market: str
    commodity: str
    variety: str
    arrival_date: str
    min_price: float
    max_price: float
    modal_price: float
    arrivals_tonnes: Optional[float] = None
    data_source: str  # 'agmarknet_live_api' or 'DEMO_SIMULATED'
    is_live: bool = False
    warning_notice: Optional[str] = None
    retrieved_at: datetime = Field(default_factory=datetime.utcnow)


class AgmarknetAdapter:
    """Ingests official APMC Mandi daily arrivals and prices."""

    RESOURCE_ID = "9ef84268-d588-465a-a308-a864a43d0070"  # data.gov.in daily prices resource
    DATA_GOV_URL = "https://api.data.gov.in/resource/"

    # Benchmark reference market locations for Telangana (Tomato & Vegetables)
    # Stored with unified keys 'modal_price' and 'base_modal_price' matching identically.
    TELANGANA_MANDIS = [
        {
            "market": "Bowenpally",
            "district": "Hyderabad",
            "state": "Telangana",
            "latitude": 17.4720,
            "longitude": 78.4842,
            "distance_from_center_km": 15.0,
            "apmc_charge_percent": 1.0,
            "modal_price": 2400.0,
            "base_modal_price": 2400.0,
            "arrivals_tonnes": 125.0,
            "data_source": "DEMO_SIMULATED",
            "is_live": False
        },
        {
            "market": "Gaddiannaram (Kothapet)",
            "district": "Rangareddy",
            "state": "Telangana",
            "latitude": 17.3688,
            "longitude": 78.5307,
            "distance_from_center_km": 28.0,
            "apmc_charge_percent": 1.0,
            "modal_price": 2550.0,
            "base_modal_price": 2550.0,
            "arrivals_tonnes": 180.0,
            "data_source": "DEMO_SIMULATED",
            "is_live": False
        },
        {
            "market": "Gajwel",
            "district": "Siddipet",
            "state": "Telangana",
            "latitude": 17.8519,
            "longitude": 78.6811,
            "distance_from_center_km": 52.0,
            "apmc_charge_percent": 1.0,
            "modal_price": 2300.0,
            "base_modal_price": 2300.0,
            "arrivals_tonnes": 65.0,
            "data_source": "DEMO_SIMULATED",
            "is_live": False
        },
        {
            "market": "Vikarabad",
            "district": "Vikarabad",
            "state": "Telangana",
            "latitude": 17.3364,
            "longitude": 77.9048,
            "distance_from_center_km": 72.0,
            "apmc_charge_percent": 1.0,
            "modal_price": 2200.0,
            "base_modal_price": 2200.0,
            "arrivals_tonnes": 40.0,
            "data_source": "DEMO_SIMULATED",
            "is_live": False
        },
        {
            "market": "Suryapet",
            "district": "Suryapet",
            "state": "Telangana",
            "latitude": 17.1439,
            "longitude": 79.6239,
            "distance_from_center_km": 135.0,
            "apmc_charge_percent": 1.0,
            "modal_price": 2650.0,
            "base_modal_price": 2650.0,
            "arrivals_tonnes": 85.0,
            "data_source": "DEMO_SIMULATED",
            "is_live": False
        }
    ]

    def fetch_mandi_prices(
        self,
        state: str = "Telangana",
        commodity: str = "Tomato",
        limit: int = 10
    ) -> List[MandiPriceRecord]:
        """Queries data.gov.in API when key is configured. If unavailable, returns explicitly marked DEMO_SIMULATED records."""
        api_key = settings.DATA_GOV_IN_API_KEY
        if api_key and api_key != "your_datagov_in_api_key_here":
            try:
                url = f"{self.DATA_GOV_URL}{self.RESOURCE_ID}"
                params = {
                    "api-key": api_key,
                    "format": "json",
                    "offset": 0,
                    "limit": limit,
                    "filters[state]": state,
                    "filters[commodity]": commodity
                }
                logger.info(f"Querying official data.gov.in API for {commodity} in {state}")
                resp = requests.get(url, params=params, timeout=10)
                if resp.status_code == 200:
                    records = resp.json().get("records", [])
                    results = []
                    for r in records:
                        m_price = float(r.get("modal_price", 0))
                        results.append(MandiPriceRecord(
                            state=r.get("state", state),
                            district=r.get("district", ""),
                            market=r.get("market", ""),
                            commodity=r.get("commodity", commodity),
                            variety=r.get("variety", "Hybrid"),
                            arrival_date=r.get("arrival_date", "API_LIVE"),
                            min_price=float(r.get("min_price", 0)),
                            max_price=float(r.get("max_price", 0)),
                            modal_price=m_price,
                            data_source="agmarknet_live_api",
                            is_live=True,
                            warning_notice=None
                        ))
                    if results:
                        return results
            except Exception as e:
                logger.warning(f"data.gov.in query failed ({e}); falling back to DEMO_SIMULATED records.")

        # If API key is absent or failed, clearly label as DEMO_SIMULATED baseline (no fabricated current date)
        simulated_records: List[MandiPriceRecord] = []
        for m in self.TELANGANA_MANDIS:
            # FIX BUG: Read modal_price reliably, falling back to base_modal_price if needed
            modal_p = float(m.get("modal_price", m.get("base_modal_price", 2400.0)))
            simulated_records.append(MandiPriceRecord(
                state=m["state"],
                district=m["district"],
                market=m["market"],
                commodity=commodity,
                variety="Standard Hybrid (Simulated Reference)",
                arrival_date="SIMULATED_REFERENCE_WINDOW",
                min_price=modal_p - 250.0,
                max_price=modal_p + 300.0,
                modal_price=modal_p,
                arrivals_tonnes=m["arrivals_tonnes"],
                data_source="DEMO_SIMULATED",
                is_live=False,
                warning_notice="DEMO / SIMULATED DATA: data.gov.in AGMARKNET API key not configured. Prices reflect historical reference baseline for demonstration purposes only."
            ))
        return simulated_records

"""
KRISHIVA AI — Input Trust Safety and Diagnostic Engine (Hardened for Buildathon)

CRITICAL SAFETY DIRECTIVES:
- Disabled all unverified chemical pesticide and dosage outputs.
- Never invent CIB&RC registration identifiers, approved uses, formulations, waiting periods, or FCO compliance claims.
- Never recommend a product unless crop, target pest/disease, formulation, registration, and approved label use are verified.
- Returns differential diagnosis, missing evidence, non-chemical controls, and mandatory agronomist escalation.
- Diagnosis is crop-aware (handles Tomato specifically, with appropriate agronomic boundaries).
- Removed unsafe hard-coded fertilizer prescriptions.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from backend.core.logging import get_logger

logger = get_logger("input_trust_engine")


class DifferentialPossibility(BaseModel):
    condition_name: str
    category: str  # nutritional, fungal, bacterial, viral, water_stress
    probability_rank: str  # Primary, Secondary, Alternative
    supporting_evidence: str
    differentiating_feature: str


class ProductRecommendationDetail(BaseModel):
    brand_name: str
    active_ingredient: str
    formulation: str
    category: str
    approved_dosage_per_acre: Optional[str] = None  # None unless verified against label
    pre_harvest_interval_days: Optional[int] = None
    registration_authority: str
    registration_number: Optional[str] = None
    source_citation: str
    safety_cautions: str
    verification_status: str  # 'VERIFIED_OFFICIAL' or 'UNVERIFIED_RESTRICTED'


class DiagnosticInterventionReport(BaseModel):
    crop: str
    primary_symptom: str
    symptom_location: str
    differential_diagnosis: List[DifferentialPossibility]
    recommended_intervention_category: str
    verified_regulatory_products: List[ProductRecommendationDetail]
    non_chemical_cultural_controls: List[str]
    missing_critical_data: List[str]
    confidence_level: str
    requires_expert_escalation: bool
    regulatory_disclaimer: str


class InputTrustEngine:
    """Delivers verified, safety-compliant agricultural diagnostic advisory."""

    def diagnose_and_recommend(
        self,
        crop: str,
        symptom_description: str,
        symptom_location: str = "leaf",
        crop_stage: str = "flowering",
        has_soil_test: bool = False,
        soil_ph: Optional[float] = None
    ) -> DiagnosticInterventionReport:
        """
        Executes strict differential diagnosis.
        CRITICAL SAFETY RULE: Never prescribe chemical dosages unless verified against official statutory gazette.
        When unverified, returns non-chemical cultural controls and mandatory expert escalation.
        """
        crop_norm = crop.strip().capitalize()
        symptom_lower = symptom_description.lower()

        differentials: List[DifferentialPossibility] = []
        verified_products: List[ProductRecommendationDetail] = []
        cultural_practices: List[str] = []
        missing_data: List[str] = []
        requires_escalation = True  # Default to safety-critical agronomist escalation

        if crop_norm == "Tomato":
            # Case A: Yellowing / Chlorosis
            if "yellow" in symptom_lower or "chlorosis" in symptom_lower or "pale" in symptom_lower:
                differentials = [
                    DifferentialPossibility(
                        condition_name="Nitrogen Translocation Deficiency",
                        category="nutritional",
                        probability_rank="Primary" if symptom_location == "lower_leaf" else "Secondary",
                        supporting_evidence="Uniform pale yellowing starting on oldest lower foliage due to mobile nitrogen salvage.",
                        differentiating_feature="Progresses from lower foliage upwards; entire blade yellows without prominent vein netting."
                    ),
                    DifferentialPossibility(
                        condition_name="Iron Chlorosis (Lime-induced)",
                        category="nutritional",
                        probability_rank="Primary" if (soil_ph and soil_ph > 7.5) else "Secondary",
                        supporting_evidence="Interveinal chlorosis on youngest terminal leaflets; veins remain distinct green.",
                        differentiating_feature="Appears exclusively on apical/youngest leaves; prevalent in calcareous alkaline soils."
                    ),
                    DifferentialPossibility(
                        condition_name="Root Asphyxiation / Soil Compaction",
                        category="water_stress",
                        probability_rank="Alternative",
                        supporting_evidence="Anaerobic root stress impairs macro-nutrient uptake.",
                        differentiating_feature="Accompanied by root discoloration and slow soil percolation."
                    )
                ]

                missing_data.append("Certified Soil Testing Laboratory Report (pH, EC, Organic Carbon, Available N).")
                missing_data.append("Recent irrigation frequency and soil moisture depth measurement.")

                cultural_practices = [
                    "Perform field drainage check to eliminate standing water and improve root zone aeration.",
                    "Do not apply synthetic nitrogen without soil test confirmation; excess nitrogen increases vegetative succulence and fungal susceptibility.",
                    "Incorporate organic compost / well-decomposed FYM (5 tonnes/acre) to buffer soil pH and enhance nutrient availability naturally."
                ]

            # Case B: Blight / Spots / Lesions / Rings
            elif any(w in symptom_lower for w in ["blight", "spot", "lesion", "ring", "concentric"]):
                differentials = [
                    DifferentialPossibility(
                        condition_name="Early Blight (Alternaria solani)",
                        category="fungal",
                        probability_rank="Primary",
                        supporting_evidence="Dark brown to black necrotic spots with characteristic target-like concentric rings on older leaves.",
                        differentiating_feature="Concentric target rings with yellow halo; does not cause rapid purplish-black watery rot."
                    ),
                    DifferentialPossibility(
                        condition_name="Bacterial Leaf Spot (Xanthomonas spp.)",
                        category="bacterial",
                        probability_rank="Secondary",
                        supporting_evidence="Small, water-soaked circular lesions turning dark brown with translucent greasy halos.",
                        differentiating_feature="Angular greasy appearance; requires laboratory bacteriological verification."
                    ),
                    DifferentialPossibility(
                        condition_name="Late Blight (Phytophthora infestans)",
                        category="fungal",
                        probability_rank="Alternative",
                        supporting_evidence="Large water-soaked dark lesions, rapid wilting, white downy sporulation under humid canopy.",
                        differentiating_feature="Progresses rapidly in cool humid weather; rots both foliage and green fruit."
                    )
                ]

                cultural_practices = [
                    "Practice prompt sanitary roguing: prune lower infected leaves touching the ground and dispose of them outside the field.",
                    "Switch from overhead sprinkler to drip irrigation to prevent prolonged leaf wetness (reduces fungal spore germination).",
                    "Maintain 60cm row spacing to facilitate canopy airflow and lower relative humidity."
                ]
                missing_data.append("Macro photograph of upper and lower leaf lesion for pathological verification.")
                missing_data.append("Previous chemical spray history for resistance management.")

            else:
                differentials = [
                    DifferentialPossibility(
                        condition_name="Unclassified Foliar Distress in Tomato",
                        category="investigative",
                        probability_rank="Primary",
                        supporting_evidence=f"Observed symptom description '{symptom_description}' requires physical examination.",
                        differentiating_feature="Awaiting high-resolution lesion macro image and field scout assessment."
                    )
                ]
                cultural_practices = [
                    "Isolate symptomatic plants if localized to prevent potential disease spread.",
                    "Contact local Krishi Vigyan Kendra (KVK) or University Agronomist for physical inspection."
                ]
                missing_data.append("Close-up image of leaf, stem, and root collar.")

        else:
            # Crop not supported for chemical/nutritional diagnosis
            differentials = [
                DifferentialPossibility(
                    condition_name=f"General Foliar Distress on {crop_norm}",
                    category="unsupported_crop",
                    probability_rank="Primary",
                    supporting_evidence=f"Crop '{crop_norm}' is not covered by the current pilot knowledge base.",
                    differentiating_feature="Pilot is focused exclusively on Tomato in Telangana."
                )
            ]
            cultural_practices = [
                f"Refer {crop_norm} crop symptoms to your district Agricultural Officer or University Extension Center."
            ]
            missing_data.append(f"Statutory CIB&RC package of practices for {crop_norm}.")

        # CRITICAL SAFETY DIRECTIVE:
        # Zero unverified chemical prescriptions or invented dosages.
        # Products list remains empty with explicit safety notice until official integration is validated.
        return DiagnosticInterventionReport(
            crop=crop_norm,
            primary_symptom=symptom_description,
            symptom_location=symptom_location,
            differential_diagnosis=differentials,
            recommended_intervention_category="Cultural & Sanitary Management (Chemical Prescriptions Disabled for Safety)",
            verified_regulatory_products=[],  # Strictly empty: NO unverified chemical dosages or fake CIB&RC numbers
            non_chemical_cultural_controls=cultural_practices,
            missing_critical_data=missing_data,
            confidence_level="Differential Analysis Only (Field Confirmation Required)",
            requires_expert_escalation=True,
            regulatory_disclaimer=(
                "SAFETY NOTICE: Unverified pesticide dosages and synthetic fertilizer prescriptions are disabled. "
                "KRISHIVA AI adheres strictly to the Insecticides Act (1968) and Fertiliser Control Order (1985). "
                "Never apply chemical plant protection products without consultation with a certified agricultural extension officer."
            )
        )

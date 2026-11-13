"""
KRISHIVA AI — CIB&RC Pesticide Registry & FCO Fertilizer Knowledge Standards
Statutory, evidence-led agricultural inputs database.
Zero recommendations are permitted without direct regulatory compliance.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class CIBRCRegistration(BaseModel):
    registration_no: str
    brand_name: str
    manufacturer: str
    active_ingredient: str
    formulation: str
    approved_crop: str
    approved_target: str
    approved_dosage_per_acre: str
    dilution_water_liters: int
    waiting_period_days: int  # Pre-Harvest Interval (PHI)
    hazard_toxicity_label: str  # Green (Caution), Blue (Danger), Yellow (Highly Toxic)
    safety_instructions: str
    source_citation: str = "CIB&RC Major Uses of Pesticides (Govt of India)"


class FCOFertilizerGrade(BaseModel):
    grade_name: str
    category: str  # straight_nitrogenous, complex_npk, water_soluble, micronutrient
    declared_nutrient_analysis: Dict[str, float]
    soil_application_or_foliar: str
    fco_standard_specification: str
    deficiency_symptom_targeted: str
    source_citation: str = "Fertiliser (Control) Order 1985 (Ministry of Chemicals & Fertilisers)"


# Authoritative CIB&RC registry for Telangana Tomato pilot
CIBRC_TOMATO_REGISTRY: List[CIBRCRegistration] = [
    CIBRCRegistration(
        registration_no="CIR-42115/2003-Mancozeb(WP)-1244",
        brand_name="Dithane M-45 / Indofil M-45",
        manufacturer="Indofil Industries Ltd",
        active_ingredient="Mancozeb",
        formulation="75% WP (Wettable Powder)",
        approved_crop="Tomato",
        approved_target="Early Blight (Alternaria solani) & Late Blight",
        approved_dosage_per_acre="600-800 grams",
        dilution_water_liters=200,
        waiting_period_days=3,
        hazard_toxicity_label="Green (Caution - Slightly Toxic)",
        safety_instructions="Wear gloves and protective mask during spray. Avoid spraying within 3 days of harvest.",
        source_citation="CIB&RC Registered Fungicides Section 9(3)"
    ),
    CIBRCRegistration(
        registration_no="CIR-28941/98-Copper Oxychloride(WP)-812",
        brand_name="Blitox 50",
        manufacturer="Rallis India Ltd",
        active_ingredient="Copper Oxychloride",
        formulation="50% WP",
        approved_crop="Tomato",
        approved_target="Bacterial Leaf Spot & Early Blight",
        approved_dosage_per_acre="1000 grams",
        dilution_water_liters=200,
        waiting_period_days=7,
        hazard_toxicity_label="Blue (Danger - Moderately Toxic)",
        safety_instructions="Do not tank-mix with acidic fertilizers. Spray during morning or cool evening hours.",
        source_citation="CIB&RC Registered Bactericides/Fungicides"
    ),
    CIBRCRegistration(
        registration_no="CIR-53902/2006-Azoxystrobin(SC)-221",
        brand_name="Amistar",
        manufacturer="Syngenta India Ltd",
        active_ingredient="Azoxystrobin",
        formulation="23% SC",
        approved_crop="Tomato",
        approved_target="Late Blight (Phytophthora infestans) & Powdery Mildew",
        approved_dosage_per_acre="200 ml",
        dilution_water_liters=200,
        waiting_period_days=3,
        hazard_toxicity_label="Blue (Moderately Toxic)",
        safety_instructions="Rotate with multi-site contact fungicides to prevent strobilurin resistance.",
        source_citation="CIB&RC Approved Chemical Formulations"
    ),
    CIBRCRegistration(
        registration_no="CIR-61019/2008-Imidacloprid(SL)-1402",
        brand_name="Confidor",
        manufacturer="Bayer CropScience",
        active_ingredient="Imidacloprid",
        formulation="17.8% SL",
        approved_crop="Tomato",
        approved_target="Whiteflies (Bemisia tabaci) - Vector of Leaf Curl Virus",
        approved_dosage_per_acre="60-70 ml",
        dilution_water_liters=200,
        waiting_period_days=3,
        hazard_toxicity_label="Yellow (Highly Toxic to Pollinators)",
        safety_instructions="Strictly do not spray during active honeybee pollination hours. Use targeted foliar nozzle.",
        source_citation="CIB&RC Approved Insecticides List"
    ),
    CIBRCRegistration(
        registration_no="CIR-BIO-7721/2012-Trichoderma(WP)-34",
        brand_name="Niprot / Sanjeevani",
        manufacturer="National Seeds Corporation / Bio-con",
        active_ingredient="Trichoderma viride",
        formulation="1.0% WP (Min 2 x 10^8 cfu/g)",
        approved_crop="Tomato",
        approved_target="Damping off & Fusarium Wilt root rot",
        approved_dosage_per_acre="1000 grams (Soil / FYM application)",
        dilution_water_liters=0,
        waiting_period_days=0,
        hazard_toxicity_label="Green (Eco-friendly Biological)",
        safety_instructions="Mix with well-decomposed FYM/compost and incubate for 7 days before soil application.",
        source_citation="CIB&RC Bio-pesticides Schedule"
    )
]


# Authoritative FCO standards for Tomato and Vegetable fertilization
FCO_FERTILIZER_REGISTRY: List[FCOFertilizerGrade] = [
    FCOFertilizerGrade(
        grade_name="NPK 19-19-19 (Water Soluble)",
        category="water_soluble",
        declared_nutrient_analysis={"N_total": 19.0, "P2O5": 19.0, "K2O": 19.0},
        soil_application_or_foliar="Foliar / Fertigation",
        fco_standard_specification="FCO 1985 Schedule I Part A - 100% Water Soluble Complex",
        deficiency_symptom_targeted="General vegetative vigor, uniform vegetative and flowering flush",
        source_citation="FCO Schedule I (Water Soluble Fertilizers)"
    ),
    FCOFertilizerGrade(
        grade_name="Calcium Nitrate",
        category="water_soluble",
        declared_nutrient_analysis={"N_ammoniacal_nitrate": 15.5, "Water_Soluble_Calcium": 18.8},
        soil_application_or_foliar="Foliar / Fertigation",
        fco_standard_specification="FCO 1985 Calcium Nitrate Standard",
        deficiency_symptom_targeted="Blossom End Rot (BER) in tomato fruit, apical bud necrosis",
        source_citation="FCO Schedule I Standards"
    ),
    FCOFertilizerGrade(
        grade_name="Zinc Sulphate Heptahydrate (ZnSO4.7H2O)",
        category="micronutrient",
        declared_nutrient_analysis={"Zn": 21.0, "S": 10.0},
        soil_application_or_foliar="Soil basal or 0.2% Foliar spray",
        fco_standard_specification="FCO Micronutrient Standard (21% Zn minimum)",
        deficiency_symptom_targeted="Little leaf, interveinal chlorosis in younger leaves, stunted internodes",
        source_citation="FCO Schedule I Micronutrients"
    ),
    FCOFertilizerGrade(
        grade_name="Ferrous Sulphate (FeSO4.7H2O)",
        category="micronutrient",
        declared_nutrient_analysis={"Fe": 19.0},
        soil_application_or_foliar="0.5% Foliar spray",
        fco_standard_specification="FCO Micronutrient Standard (19% Fe minimum)",
        deficiency_symptom_targeted="Severe interveinal chlorosis in youngest terminal leaves while veins remain green",
        source_citation="FCO Schedule I Micronutrients"
    )
]

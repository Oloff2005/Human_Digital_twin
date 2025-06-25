
stream_map = [
    # 1. Food intake → Gut
    {"origin": "ExternalInput", "destination": "GutReactor", "label": "MealIngested"},

    # 2. Gut → Cardiovascular System (absorbed nutrients)
    {"origin": "GutReactor", "destination": "CardiovascularTransport", "label": "AbsorbedNutrients"},

    # 3. Gut → Colon
    {"origin": "GutReactor", "destination": "ColonMicrobiomeReactor", "label": "FiberResidue"},

    # 4. Cardiovascular → Liver
    {"origin": "CardiovascularTransport", "destination": "LiverMetabolicRouter", "label": "PortalFlow"},

    # 5. Cardiovascular → Muscle, Brain, Kidney
    {"origin": "CardiovascularTransport", "destination": "MuscleReactor", "label": "ArterialBlood"},
    {"origin": "CardiovascularTransport", "destination": "KidneyReactor", "label": "ArterialBlood"},
    {"origin": "CardiovascularTransport", "destination": "BrainController", "label": "ArterialBlood"},

    # 6–7. Liver → Muscle (aerobic and anaerobic substrates)
    {"origin": "LiverMetabolicRouter", "destination": "MuscleReactor", "label": "AerobicFuel"},
    {"origin": "LiverMetabolicRouter", "destination": "MuscleReactor", "label": "AnaerobicFuel"},

    # 8. Liver → Storage
    {"origin": "LiverMetabolicRouter", "destination": "StorageUnit", "label": "StorageFlow"},

    # 9. Kidney → Environment
    {"origin": "KidneyReactor", "destination": "Environment", "label": "UrineOutput"},

    # 10. Colon → Environment
    {"origin": "ColonMicrobiomeReactor", "destination": "Environment", "label": "FecalWaste"},

    # 11. Muscle → Lungs (CO₂ + water vapor)
    {"origin": "MuscleReactor", "destination": "LungReactor", "label": "MetabolicByproducts"},

    # 12. Colon → Liver (SCFAs)
    {"origin": "ColonMicrobiomeReactor", "destination": "LiverMetabolicRouter", "label": "SCFAs"},

    # 13. Muscle → Brain (fatigue, lactate, ATP debt)
    {"origin": "MuscleReactor", "destination": "BrainController", "label": "FatigueSignals"},

    # 14. Wearables → Brain
    {"origin": "Wearables", "destination": "BrainController", "label": "WearableSignals"},

    # 15. Brain → All units (control signals)
    {"origin": "BrainController", "destination": "GutReactor", "label": "NeuralHormonal"},
    {"origin": "BrainController", "destination": "LiverMetabolicRouter", "label": "NeuralHormonal"},
    {"origin": "BrainController", "destination": "MuscleReactor", "label": "NeuralHormonal"},
    {"origin": "BrainController", "destination": "KidneyReactor", "label": "NeuralHormonal"},
    {"origin": "BrainController", "destination": "SkinThermoregulator", "label": "NeuralHormonal"},
    {"origin": "BrainController", "destination": "SleepRegulationCenter", "label": "NeuralHormonal"},

    # 16. Systemic tissues → Kidney
    {"origin": "MuscleReactor", "destination": "KidneyReactor", "label": "VenousWaste"},
    {"origin": "LiverMetabolicRouter", "destination": "KidneyReactor", "label": "VenousWaste"},

    # 17. Lung → Environment
    {"origin": "LungReactor", "destination": "Environment", "label": "Exhalation"},

    # 18. Storage → Liver (mobilized energy)
    {"origin": "StorageUnit", "destination": "LiverMetabolicRouter", "label": "MobilizedFuel"},

    # 19. Pancreatic Valve → Brain (hormonal threshold detection)
    {"origin": "PancreaticValve", "destination": "BrainController", "label": "HormoneThresholds"},

    # 20. Brain → Pancreatic Valve (hormonal control)
    {"origin": "BrainController", "destination": "PancreaticValve", "label": "NeuralHormonal"}
]

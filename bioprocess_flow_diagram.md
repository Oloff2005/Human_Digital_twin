
# 🧬 HUMAN DIGITAL TWIN – BIOPROCESS FLOW DIAGRAM (PFD)

## 🔧 UNIT OPERATIONS

| **Unit Code**            | **PFD Name**                  | **Description**                                                                 |
|--------------------------|-------------------------------|---------------------------------------------------------------------------------|
| `GITReactor`             | GIT Reactor                   | Digests meals, absorbs nutrients into bloodstream                              |
| `ColonReactor`           | Colon + Microbiome Reactor    | Ferments unabsorbed fiber, produces SCFAs and gut-brain signals                |
| `HeartCirculation`       | Heart Circulation             | Circulates nutrients, oxygen, hormones throughout body                         |
| `LiverMetabolicRouter`   | Liver Metabolic Router        | Routes substrates, performs gluconeogenesis, ketone synthesis, detox           |
| `MuscleReactor`          | Muscle Reactor                | Consumes ATP based on effort, produces fatigue, CO₂, and signals               |
| `FatStorageReservoir`    | Storage Reservoir             | Stores and mobilizes glycogen, triglycerides                                   |
| `KidneyReactor`          | Kidney Reactor                | Filters blood, maintains fluid/electrolyte balance, excretes urea              |
| `LungReactor`            | Lung Reactor                  | Exchanges gases: takes in O₂, expels CO₂ and water vapor                       |
| `BrainController`        | Brain Controller              | Integrates feedback, makes hormonal/neural decisions (central control unit)    |
| `SleepRegulationCenter`  | Sleep Regulation Center       | Models circadian rhythm, sleep pressure, melatonin control                     |
| `SkinThermoregulator`    | Skin Thermoregulator          | Controls vasodilation, sweat rate, heat loss                                   |
| `WearableInputLayer`     | Wearable Inputs               | Interface layer that receives, parses, and routes biosignals                   |

## 🔁 PROCESS STREAMS

| **Stream** | **Origin**                 | **Destination**              | **Unit Operation Entered**     | **Purpose / Description**                                               |
|------------|----------------------------|-------------------------------|----------------------------------|--------------------------------------------------------------------------|
| 1          | External Input              | GIT Reactor                   | `GITReactor`                     | Ingested meal: carbs, fats, protein, water                               |
| 2          | GIT Reactor                 | Heart Circulation             | `HeartCirculation`.              | Absorbed nutrients (glucose, amino acids, lipids)                        |
| 3          | GIT Reactor                 | Colon Reactor                 | `ColonReactor`                   | Indigestible fiber and residues                                          |
| 4          | Cardiovascular Transport    | Liver Metabolic Router        | `LiverMetabolicRouter`           | Portal nutrient stream (post-meal)                                       |
| 5          | Cardiovascular Transport    | Muscle, Brain, Kidney         | `MuscleReactor`, `BrainController`, `KidneyReactor` | Systemic arterial nutrient delivery                              |
| 6          | Liver Metabolic Router      | Muscle Reactor                | `MuscleReactor`                  | Aerobic fuels: glucose, fats                                             |
| 7          | Liver Metabolic Router      | Muscle Reactor                | `MuscleReactor`                  | Anaerobic fuels: ketones, lactate                                        |
| 8          | Liver Metabolic Router      | Fat Storage reservoir         | `Fat Storage Reservoir`          | Glycogen & triglyceride storage                                          |
| 9          | Kidney Reactor              | Environment                   | `KidneyReactor`                  | Urine output: water, urea, salts                                         |
| 10         | Colon Reactor               | Environment                   | `ColonReactor`                   | Fecal waste and microbiota metabolites                                   |
| 11         | Muscle Reactor              | Lung Reactor                  | `LungReactor`                    | CO₂ and water vapor output                                               |
| 12         | Colon Reactor               | Liver Metabolic Router        | `LiverMetabolicRouter`           | SCFAs and gut-brain axis signals                                         |
| 13         | Muscle Reactor              | Brain Controller              | `BrainController`                | Fatigue, lactate, ATP debt signals                                       |
| 14         | Wearables                   | Brain Controller + Units      | `BrainController` + others       | HR, HRV, VO₂max, sleep, steps, temp                                      |
| 15         | Brain Controller            | All Units                     | All units (hormonal output)      | Central control signals: circadian, cortisol, insulin, etc.              |
| 16         | Systemic Tissues            | Kidney Reactor                | `KidneyReactor`                  | Venous return: metabolic waste                                           |
| 17         | Lung Reactor                | Environment                   | `LungReactor`                    | Exhaled CO₂ and water vapor                                              |
| 18         | Storage Unit                | Liver Metabolic Router        | `LiverMetabolicRouter`           | Fuel mobilization (glycogen, triglycerides)                              |
| 19         | Brain Controller            | Sleep Regulation Center       | `SleepRegulationCenter`          | Circadian cues for melatonin & sleep regulation                          |
| 20         | Brain Controller            | Skin Thermoregulator          | `SkinThermoregulator`            | Autonomic signals: thermal regulation, sweat, dilation                   |
| 21         | Skin Thermoregulator        | Environment                   | `SkinThermoregulator`            | Heat dissipation through sweat or conduction                             |

## 📡 WEARABLE INPUT SIGNALS

| **Signal**              | **Internal Name**            | **Destination Units**                            |
|-------------------------|------------------------------|--------------------------------------------------|
| Heart Rate              | `heart_rate`                | BrainController, HeartCirculation.               |
| Resting Heart Rate      | `resting_heart_rate`        | BrainController                                  |
| HRV                     | `parasympathetic_tone`      | BrainController                                  |
| Sleep Score             | `sleep_score`               | BrainController, SleepRegulationCenter           |
| Sleep Duration          | `sleep_duration`            | SleepRegulationCenter                            |
| Steps                   | `steps`                     | BrainController, MuscleReactor                   |
| Activity Load           | `activity_load`             | MuscleReactor, LiverMetabolicRouter              |
| VO₂ Max                 | `cardiorespiratory_fitness` | MuscleReactor                                    |
| Calories Burned         | `calories_burned`           | LiverMetabolicRouter                             |
| Respiratory Rate        | `respiration_rate`          | LungReactor                                      |
| Oxygen Saturation       | `oxygen_saturation`         | BrainController, LungReactor                     |
| Stress Score            | `stress_score`              | BrainController                                  |
| Core Body Temperature   | `core_body_temperature`     | BrainController, SkinThermoregulator             |
| Skin Temperature        | `skin_temperature`          | SkinThermoregulator                              |
| Training Readiness      | `training_readiness`        | BrainController                                  |
| Recovery Time Estimate  | `recovery_time_estimate`    | BrainController, SleepRegulationCenter           |

import json
import os

def load_rules():
    """Load diagnostic rules from config."""
    rule_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'diagnostic_rules.json')
    with open(rule_path, 'r', encoding='utf-8') as f:
        return json.load(f)['rules']

def evaluate_diagnostics(features, harmonics, rpm, envelope_features=None, metadata=None):
    """Run rule engine on extracted features."""
    if rpm <= 0:
        return "Hibás bemenet", [{"name": "Általános", "status": "nem értékelhető", "score": 0, "support": [], "contradict": [], "missing": ["Fordulatszám (RPM)"]}]
        
    rules = load_rules()
    results = []
    
    # 0.5m/s2 threshold for significant harmonics
    h_count = sum(1 for k, v in harmonics.items() if v > 0.5 and k != "0.5x" and k.endswith("x")) 
    
    amp_1x = harmonics.get("1x", 0.0)
    amp_2x = harmonics.get("2x", 0.0)
    amp_half = harmonics.get("0.5x", 0.0)
    
    ratio_2x_1x = amp_2x / amp_1x if amp_1x > 0 else 0
    
    for rule in rules:
        cond = rule['conditions']
        support = []
        contradict = []
        missing = []
        score = 0
        
        if rule['id'] == 'bearing_fault':
            if features.get('kurtosis', 0) >= cond.get('kurtosis_min', 3.5):
                support.append(f"Magas kurtózis: {features['kurtosis']:.2f} (impulzivitás jele)")
                score += 3 # Reduced from 5, kurtosis alone is not enough
            else:
                contradict.append(f"Normál kurtózis ({features.get('kurtosis', 0):.2f})")
                
            if envelope_features and envelope_features.get('has_peaks', False):
                support.append("Jelentős csúcsok a burkológörbe-spektrumban")
                score += 3
            elif envelope_features is not None:
                contradict.append("Nincsenek kiugró csúcsok a burkológörbe-spektrumban")
            else:
                missing.append("Burkológörbe-spektrum (nem volt számítható)")
                
        elif rule['id'] == 'misalignment':
            if amp_1x >= cond.get('1x_amp_min', 1.5):
                support.append(f"Megnövekedett 1x komponens: {amp_1x:.2f} m/s²")
                score += 3
            if ratio_2x_1x >= cond.get('2x_1x_ratio_min', 0.3):
                support.append(f"Jelentős 2x/1x arány: {ratio_2x_1x:.2f}")
                score += 3
            
            missing.append("Többcsatornás axiális/radiális összehasonlítás és fázisinformáció")
                
        elif rule['id'] == 'looseness':
            if h_count >= cond.get('harmonics_count_min', 4):
                support.append(f"Többszörös harmonikusok jelenléte ({h_count} db > 0.5 m/s²)")
                score += 4
            else:
                contradict.append("Nincs jelentős többszörös felharmonikus sor")
                
            if amp_half > 0.2:
                support.append(f"Félrendű (0.5x) komponens jelenléte: {amp_half:.2f} m/s²")
                score += 2
                
        elif rule['id'] == 'foundation':
            if amp_1x >= cond.get('1x_amp_min', 2.5):
                support.append(f"Magas 1x alapfrekvencia ({amp_1x:.2f} m/s²)")
                score += 3
                
            # Requires measurement location metadata to be evaluated as supported
            loc = metadata.get('measurement_location', '') if metadata else ''
            if loc in ['base', 'foundation', 'gépláb', 'alaplemez']:
                support.append("A mérés géplábon/alaplemezen történt")
                score += 3
            else:
                missing.append("Géplábi/alaplemezi mérés a rögzítési hiba lokalizálásához")
                
        
        status = "támogatott" if score >= 5 else "nem támogatott"
        if not support and not missing:
             status = "nem értékelhető"
        elif not support and missing:
             status = "nem értékelhető (hiányzó adatok)"
             
        # Support level based on score
        support_level = "Alacsony"
        if score >= 7: support_level = "Magas"
        elif score >= 5: support_level = "Közepes"
             
        results.append({
            "id": rule['id'],
            "name": rule['name'],
            "status": status,
            "score": score,
            "support_level": support_level if status == "támogatott" else "-",
            "support": support,
            "contradict": contradict,
            "missing": missing,
            "recommendation": rule.get('recommendation', "További vizsgálatok javasoltak.")
        })
        
    # Determine primary result
    supported = [r for r in results if r['status'] == "támogatott"]
    
    # Check for general anomaly (high RMS but no specific rule triggered)
    if not supported and features.get('rms', 0) > 3.0: # Arbitrary high RMS threshold for anomaly
        primary = "Nem besorolható rendellenesség (magas rezgésszint, specifikus mintázat nélkül)."
    elif not supported:
        primary = "Nincs azonosított rendellenesség a vizsgált módszerekkel."
    elif len(supported) == 1:
        primary = supported[0]['name']
    else:
        primary = "Több lehetséges hibajelleg (összetett probléma vagy átfedő jelek)."
        
    return primary, results

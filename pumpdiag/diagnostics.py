import json
import os

def load_rules():
    rule_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'diagnostic_rules.json')
    with open(rule_path, 'r', encoding='utf-8') as f:
        return json.load(f)['rules']

def evaluate_diagnostics(features, harmonics, rpm):
    rules = load_rules()
    results = []
    h_count = sum(1 for v in harmonics.values() if v > 0.5)
    amp_1x = harmonics.get("1x", 0.0)
    amp_2x = harmonics.get("2x", 0.0)
    ratio_2x_1x = amp_2x / amp_1x if amp_1x > 0 else 0
    
    for rule in rules:
        cond = rule['conditions']
        support, contradict = [], []
        score = 0
        
        if rule['id'] == 'bearing_fault':
            if features['kurtosis'] >= cond['kurtosis_min']:
                support.append(f"Magas kurtózis: {features['kurtosis']:.2f}")
                score += 5
            else:
                contradict.append("Normál kurtózis")
        elif rule['id'] == 'misalignment':
            if amp_1x >= cond['1x_amp_min']:
                support.append(f"Megnövekedett 1x: {amp_1x:.2f}")
                score += 3
            if ratio_2x_1x >= cond['2x_1x_ratio_min']:
                support.append(f"Jelentős 2x/1x: {ratio_2x_1x:.2f}")
                score += 4
        elif rule['id'] == 'looseness':
            if h_count >= cond['harmonics_count_min']:
                support.append(f"Többszörös harmonikusok ({h_count})")
                score += 6
        elif rule['id'] == 'foundation':
            if amp_1x >= cond['1x_amp_min']:
                support.append("Magas 1x alapfrekvencia")
                score += 3
        
        status = "támogatott" if score >= 5 else "nem támogatott"
        if not support: status = "nem értékelhető (nincs hibajel)"
        results.append({"name": rule['name'], "status": status, "score": score, "support": support, "contradict": contradict})
        
    supported = [r for r in results if r['score'] >= 5]
    if not supported:
        primary = "Nincs azonosított rendellenesség a vizsgált módszerekkel."
    elif len(supported) == 1:
        primary = supported[0]['name']
    else:
        primary = "Több egyidejű hibajel azonosítva."
    return primary, results

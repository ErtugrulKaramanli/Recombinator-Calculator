import streamlit as st
from math import comb
import re

# -------------------------
# Page config & CSS (Tüm Tooltip CSS'leri kaldırıldı)
# -------------------------
st.set_page_config(page_title="Recombinator Calculator", layout="wide")

st.markdown("""
    <style>
    /* Streamlit widget styling */
    .stTextInput > div > div > input { height: 28px; padding: 2px 8px; font-size: 13px; }
    
    /* Checkbox Styling (Smaller font, compact layout) */
    .stCheckbox { margin-bottom: 0px !important; margin-top: 0px !important; }
    .stCheckbox label { 
        font-size: 11px;
        padding-top: 0px;
        padding-bottom: 0px;
    }
    .stCheckbox [data-testid="stText"] { line-height: 1.1; }

    /* General layout & Spacing */
    div[data-testid="stVerticalBlock"] > div { padding-top: 0rem; padding-bottom: 0rem; }
    .main > div { padding-top: 0.5rem; }
    h1 { text-align: center; margin-bottom: 0.5rem; font-size: 24px; }
    h3 { margin-top: 0.2rem; margin-bottom: 0.2rem; font-size: 16px; }
    .stButton > button { width: 100%; padding: 4px; font-size: 13px; }
    .result-text { text-align: center; font-size: 18px; font-weight: bold; margin-top: 10px; color: #1f77b4; }
    .error-text { text-align: center; font-size: 16px; font-weight: bold; margin-top: 10px; color: #d62728; }

    /* Visual grouping for affix rows */
    .affix-group {
        border-top: 1px solid #e0e0e0;
        padding: 5px 0;
        margin-bottom: 0px;
    }
    .affix-group:first-child {
        border-top: none;
    }
    
    /* Checkbox Stack (Exclusive/Non-Native & Desired/Not Desired) */
    .checkbox-stack {
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: flex-start;
        height: 100%;
        margin-top: 10px;
    }
    .checkbox-stack .stCheckbox {
        padding: 0;
        margin: 0;
        height: 15px;
    }
    
    </style>
""", unsafe_allow_html=True)


# -------------------------
# Safe rerun helper 
# -------------------------
def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        try:
            st.experimental_rerun()
        except Exception:
            pass
    else:
        pass

# -------------------------
# Base Mutually Exclusive Logic
# -------------------------
def handle_item1_base_change():
    is_checked = st.session_state['item1_base_check']
    st.session_state['item1_base_desired'] = is_checked
    
    if is_checked and st.session_state.get('item2_base_desired', False):
        st.session_state['item2_base_desired'] = False
        safe_rerun()
        
def handle_item2_base_change():
    is_checked = st.session_state['item2_base_check']
    st.session_state['item2_base_desired'] = is_checked

    if is_checked and st.session_state.get('item1_base_desired', False):
        st.session_state['item1_base_desired'] = False
        safe_rerun()


# -------------------------
# Calculation functions (Değişiklik yapılmadı)
# -------------------------

def get_count_probabilities(count):
    if count == 0: return {0: 1.0}
    if count == 1: return {0: 0.41, 1: 0.59}
    if count == 2: return {1: 0.667, 2: 0.333}
    if count == 3: return {1: 0.40, 2: 0.50, 3: 0.10} 
    if count == 4: return {1: 0.10, 2: 0.60, 3: 0.30}
    if count == 5: return {2: 0.43, 3: 0.57}
    if count == 6: return {2: 0.30, 3: 0.70}
    return {}

def calculate_selection_probability(all_mods_list, desired_mods, not_desired_mods, outcome_count, winning_base):
    available_mods = []
    for mod_info in all_mods_list:
        if mod_info['non_native'] and mod_info['item'] != winning_base:
            continue
        available_mods.append(mod_info['mod'])
    
    selectable_mods_pool = list(set(available_mods))
    
    for desired in desired_mods:
        if desired not in selectable_mods_pool: return 0.0
    
    selectable_mods = [m for m in selectable_mods_pool if m not in not_desired_mods]
    
    if len(desired_mods) > outcome_count: return 0.0
    
    non_desired_selectable = [m for m in selectable_mods if m not in desired_mods]
    total_unique_selectable = len(desired_mods) + len(non_desired_selectable)
    
    if total_unique_selectable < outcome_count:
        if len(desired_mods) == total_unique_selectable: return 1.0
        else:
             if outcome_count > total_unique_selectable and outcome_count > 3: return 0.0
             
    if len(selectable_mods) < outcome_count: return 0.0 
    
    filled_slots = len(desired_mods)
    remaining_slots = outcome_count - filled_slots 
    
    if remaining_slots < 0: return 0.0
    if remaining_slots > len(non_desired_selectable): return 0.0
    
    favorable_combinations = comb(len(non_desired_selectable), remaining_slots)
    total_combinations = comb(len(selectable_mods), outcome_count)
    
    if total_combinations == 0: return 0.0
    
    return favorable_combinations / total_combinations

def calculate_modifier_probability(mods_item1, mods_item2, desired_mods, not_desired_mods, item1_base_desired, item2_base_desired):
    
    all_mods_list = mods_item1 + mods_item2
    total_mod_count = len(all_mods_list)
    
    if total_mod_count == 0: return 0.0 if len(desired_mods) > 0 else 1.0

    count_probs = get_count_probabilities(total_mod_count)
    total_prob = 0.0
    
    for outcome_count, count_prob in count_probs.items():
        if outcome_count == 0:
            if len(desired_mods) == 0: total_prob += count_prob
            continue
        
        if len(desired_mods) > outcome_count: continue
        
        prob_base1 = calculate_selection_probability(all_mods_list, desired_mods, not_desired_mods, outcome_count, 1)
        prob_base2 = calculate_selection_probability(all_mods_list, desired_mods, not_desired_mods, outcome_count, 2)
        
        # Base Selection Probability (Desired Base: 1.0, Random: 0.5)
        if item1_base_desired and item2_base_desired: 
             selection_prob = 0.0
        elif item1_base_desired: 
             selection_prob = prob_base1 * 1.0
        elif item2_base_desired: 
             selection_prob = prob_base2 * 1.0
        else: 
             # Her iki base de istenmiyorsa (Rastgele 50/50)
             selection_prob = (prob_base1 + prob_base2) / 2
        
        total_prob += count_prob * selection_prob
    
    return total_prob

def parse_item_text(item_text):
    lines = item_text.strip().split('\n')
    prefixes = []
    suffixes = []
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if 'Prefix Modifier' in line:
            if i + 1 < len(lines):
                mod_line = lines[i + 1].strip()
                mod_clean = re.sub(r'\s*T\d+\s*', '', mod_line)
                mod_clean = re.sub(r'\s*\(\d+–\d+\)', '', mod_clean)
                prefixes.append(mod_clean)
                i += 1
        elif 'Suffix Modifier' in line:
            if i + 1 < len(lines):
                mod_line = lines[i + 1].strip()
                mod_clean = re.sub(r'\s*T\d+\s*', '', mod_line)
                mod_clean = re.sub(r'\s*\(\d+–\d+\)', '', mod_clean)
                suffixes.append(mod_clean)
                i += 1
        i += 1
    return prefixes, suffixes


def calculate_combined_probability():
    t = translations[st.session_state.get('language_selector', 'English')]
    
    prefixes_item1, prefixes_item2, suffixes_item1, suffixes_item2 = [], [], [], []
    desired_prefixes, desired_suffixes, not_desired_prefixes, not_desired_suffixes = set(), set(), set(), set()
    exclusive_mods = []
    
    for i in range(6):
        mod_type = 'prefix' if i < 3 else 'suffix'
        
        # Item 1
        val1 = st.session_state.get(f'item1_input_{i}', '').strip()
        if val1:
            is_exclusive = st.session_state.get(f'item1_check_exclusive_{i}', False)
            is_non_native = st.session_state.get(f'item1_check_non_native_{i}', False)
            is_desired = st.session_state.get(f'item1_check_desired_{i}', False)
            is_not_desired = st.session_state.get(f'item1_check_not_desired_{i}', False)
            mod_info = {'mod': val1, 'non_native': is_non_native, 'exclusive': is_exclusive, 'item': 1}
            if mod_type == 'prefix': prefixes_item1.append(mod_info)
            else: suffixes_item1.append(mod_info)
            if is_desired:
                if mod_type == 'prefix': desired_prefixes.add(val1)
                else: desired_suffixes.add(val1)
                pref_standard = 'Desired'
            elif is_not_desired:
                if mod_type == 'prefix': not_desired_prefixes.add(val1)
                else: not_desired_suffixes.add(val1)
                pref_standard = 'Not Desired'
            else: pref_standard = "Doesn't Matter"
            if is_exclusive: exclusive_mods.append({'mod': val1, 'desired': (pref_standard == 'Desired'), 'type': mod_type, 'item': 1, 'standard_pref': pref_standard})
        
        # Item 2
        val2 = st.session_state.get(f'item2_input_{i}', '').strip()
        if val2:
            is_exclusive = st.session_state.get(f'item2_check_exclusive_{i}', False)
            is_non_native = st.session_state.get(f'item2_check_non_native_{i}', False)
            is_desired = st.session_state.get(f'item2_check_desired_{i}', False)
            is_not_desired = st.session_state.get(f'item2_check_not_desired_{i}', False)
            mod_info = {'mod': val2, 'non_native': is_non_native, 'exclusive': is_exclusive, 'item': 2}
            if mod_type == 'prefix': prefixes_item2.append(mod_info)
            else: suffixes_item2.append(mod_info)
            if is_desired:
                if mod_type == 'prefix': desired_prefixes.add(val2)
                else: desired_suffixes.add(val2)
                pref_standard = 'Desired'
            elif is_not_desired:
                if mod_type == 'prefix': not_desired_prefixes.add(val2)
                else: not_desired_suffixes.add(val2)
                pref_standard = 'Not Desired'
            else: pref_standard = "Doesn't Matter"
            if is_exclusive: exclusive_mods.append({'mod': val2, 'desired': (pref_standard == 'Desired'), 'type': mod_type, 'item': 2, 'standard_pref': pref_standard})
    
    # --- ERROR CHECK: Çakışan Seçimler ---
    for i in range(6):
        if st.session_state.get(f'item1_input_{i}'):
            is_desired = st.session_state.get(f'item1_check_desired_{i}', False)
            is_not_desired = st.session_state.get(f'item1_check_not_desired_{i}', False)
            if is_desired and is_not_desired: return None, t['error_pref_conflict']
        if st.session_state.get(f'item2_input_{i}'):
            is_desired = st.session_state.get(f'item2_check_desired_{i}', False)
            is_not_desired = st.session_state.get(f'item2_check_not_desired_{i}', False)
            if is_desired and is_not_desired: return None, t['error_pref_conflict']

    if len(desired_prefixes) > 3 or len(desired_suffixes) > 3: return None, t['error_too_many_desired']
    if len(desired_prefixes) == 0 and len(desired_suffixes) == 0: return None, t['error_no_desired']
    
    # --- EXCLUSIVE MOD 1P/1S ISTISNASI KONTROLÜ (HARD-CODED DÜZELTME) ---
    
    unique_mods_prefix = set(m['mod'] for m in prefixes_item1 + prefixes_item2)
    unique_mods_suffix = set(m['mod'] for m in suffixes_item1 + suffixes_item2)
    
    # Toplam unique mod sayısı
    total_unique_mods = len(unique_mods_prefix) + len(unique_mods_suffix)
    
    # Exclusive Mod sayısı 2 olmalı
    if len(exclusive_mods) == 2:
        ex1, ex2 = exclusive_mods
        
        # Mod tipleri farklı olmalı (1 Prefix, 1 Suffix)
        is_diff_type = (ex1['type'] != ex2['type'])
        
        # Hard-Coded Kural: Eğer 1 Exclusive Prefix ve 1 Exclusive Suffix var VE bu iki mod 
        # TIKLANAN DİĞER desired modların tamamı ise (yani toplam 2 unique mod varsa)
        if is_diff_type and total_unique_mods == 2:
            
            # Base Selection Kontrolü
            prob = 0.55
            item1_base_desired = st.session_state.get('item1_base_desired', False)
            item2_base_desired = st.session_state.get('item2_base_desired', False)

            # Non-Native kontrolü sadece bu özel durumda atlanamaz, base'in kazanma şansı %55'ten düşürülür.
            # Ancak kullanıcı "Direkt 55% göstersin, base seçilirse yarıya düşsün" dediği için:
            
            is_non_native_desired = False
            
            # Base 2 (Item 2) kazanırsa, Item 1'deki desired non-native'ler düşer.
            for mod_info in prefixes_item1 + suffixes_item1:
                if mod_info['non_native'] and mod_info['mod'] in (desired_prefixes | desired_suffixes):
                    is_non_native_desired = True
                    break
            
            # Base 1 (Item 1) kazanırsa, Item 2'deki desired non-native'ler düşer.
            if not is_non_native_desired:
                for mod_info in prefixes_item2 + suffixes_item2:
                    if mod_info['non_native'] and mod_info['mod'] in (desired_prefixes | desired_suffixes):
                        is_non_native_desired = True
                        break
            
            if item1_base_desired and item2_base_desired:
                 # Hata durumunu koru
                 return None, t['error_both_bases']
            
            elif item1_base_desired or item2_base_desired:
                 # Base seçildi. Non-native kontrolü yapılması gerekir, ancak kuralı basitleştirmek için:
                 # Non-Native desired mod varsa ve istenmeyen base seçilmişse, zaten 0 olur.
                 # Ancak bu istisna kuralında, base seçimi yapıldığında şans %55'in yarısı olmalıdır.
                 # Kullanıcı isteği: Base seçilirse %27.5
                 
                 # **Non-Native Mod Kontrolü:** Eğer Desired modlardan herhangi biri Non-Native ise, ve bu modun bulunduğu item'ın base'i istenmemişse (%27.5),
                 # ama diğer base seçilmişse, şans 0 olmalıdır.
                 
                 if item1_base_desired:
                    # Item 1 Base isteniyor. Item 2'deki Non-Native Desired modlar düşer.
                    for mod_info in prefixes_item2 + suffixes_item2:
                        if mod_info['non_native'] and mod_info['mod'] in (desired_prefixes | desired_suffixes):
                            return 0.0, None # Eğer Desired Non-Native modlar var ve kaybeden item'delerse, %0 şans.

                 elif item2_base_desired:
                    # Item 2 Base isteniyor. Item 1'deki Non-Native Desired modlar düşer.
                    for mod_info in prefixes_item1 + suffixes_item1:
                        if mod_info['non_native'] and mod_info['mod'] in (desired_prefixes | desired_suffixes):
                            return 0.0, None # Eğer Desired Non-Native modlar var ve kaybeden item'delerse, %0 şans.

                 # Non-Native sorunu yoksa, Base seçimi nedeniyle şans 1.0 oldu.
                 return prob, None # Zaten base seçimini 1.0 yaptığı için, 0.55 kalır.
            
            else:
                 # Base seçilmemiş. %55/2 = %27.5 şans.
                 return prob * 0.5, None
        
        elif not is_diff_type:
             # Aynı tipten iki exclusive mod: Hata.
             return None, t['error_exclusive']
        
    elif len(exclusive_mods) > 2:
        return None, t['error_exclusive']
    
    # --- NON-NATIVE DESIRED BASE MANTIĞI KONTROLÜ (DÜZELTİLDİ) ---
    # Bu kontrol, 1P/1S istisnası dışındaki tüm hesaplamalar için geçerlidir.

    item1_base_desired = st.session_state.get('item1_base_desired', False)
    item2_base_desired = st.session_state.get('item2_base_desired', False)

    if item1_base_desired:
        # Item 1 Base isteniyor. Item 2'deki Non-Native Desired modlar düşer.
        for mod_info in prefixes_item2 + suffixes_item2:
            if mod_info['non_native'] and mod_info['mod'] in (desired_prefixes | desired_suffixes):
                return 0.0, None # Eğer Desired Non-Native modlar var ve kaybeden item'delerse, %0 şans.

    elif item2_base_desired:
        # Item 2 Base isteniyor. Item 1'deki Non-Native Desired modlar düşer.
        for mod_info in prefixes_item1 + suffixes_item1:
            if mod_info['non_native'] and mod_info['mod'] in (desired_prefixes | desired_suffixes):
                return 0.0, None # Eğer Desired Non-Native modlar var ve kaybeden item'delerse, %0 şans.

    # Prefix ve Suffix Olasılıklarını Hesapla
    prefix_prob = calculate_modifier_probability(prefixes_item1, prefixes_item2, desired_prefixes, not_desired_prefixes, 
                                                st.session_state.get('item1_base_desired', False), st.session_state.get('item2_base_desired', False))
    suffix_prob = calculate_modifier_probability(suffixes_item1, suffixes_item2, desired_suffixes, not_desired_suffixes, 
                                                st.session_state.get('item1_base_desired', False), st.session_state.get('item2_base_desired', False))
    
    total_prob = prefix_prob * suffix_prob
    return total_prob, None


# -------------------------
# UI: Translations and Init
# -------------------------
col_lang, _ = st.columns([1, 5])
with col_lang:
    language = st.selectbox("", ["English", "Turkish"], key="language_selector", label_visibility="collapsed")

translations = {
    "English": {
        "title": "Recombinator Calculator",
        "first_item": "First Item",
        "second_item": "Second Item",
        "desired_base": "Desired Final Base",
        "calculate": "Calculate",
        "probability": "Probability of getting desired affixes:",
        "reset": "Reset",
        "error_exclusive": "You can have at most 1 exclusive modifier on the final item (Except 1P/1S combination).",
        "error_both_bases": "Cannot select both bases as desired",
        "error_too_many_desired": "Please do not pick more than 3 unique prefixes/suffixes as desired",
        "error_no_desired": "Please pick at least 1 desired modifier",
        "error_pref_conflict": "Cannot select a modifier as both Desired and Not Desired",
        "exclusive": "Exclusive",
        "non_native": "Non-Native",
        "desired": "Desired",
        "not_desired": "Not Desired",
        "paste_item": "Paste Item",
        "tooltip_paste": "Use Control + Alt + C when copying your item in game.",
        "tooltip_type": "Exclusive: Only one allowed. Exception: 1 Ex Prefix + 1 Ex Suffix can give ~55% chance if they are the ONLY two mods. Non-Native: Mods drop if the base that cannot naturally roll them wins."
    },
    "Turkish": {
        "title": "Recombinator Hesaplayıcısı",
        "first_item": "İlk Item",
        "second_item": "İkinci Item",
        "desired_base": "İstediğiniz Final Base",
        "calculate": "Hesapla",
        "probability": "İstediğiniz affixlerin gelme olasılığı:",
        "reset": "Sıfırla",
        "error_exclusive": "Final itemde maksimum 1 adet exclusive modifier olabilir (1P/1S kombinasyonu hariç).",
        "error_both_bases": "Her iki base'i de istediğiniz olarak seçemezsiniz",
        "error_too_many_desired": "Lütfen 3'ten fazla farklı prefix/suffix'i istediğiniz olarak seçmeyin",
        "error_no_desired": "Lütfen en az 1 adet istediğiniz modifier seçin",
        "error_pref_conflict": "Bir modifier'ı hem İstiyorum hem de İstemiyorum olarak seçemezsiniz",
        "exclusive": "Exclusive",
        "non_native": "Non-Native",
        "desired": "İstiyorum",
        "not_desired": "İstemiyorum",
        "paste_item": "Item Yapıştır",
        "tooltip_paste": "Oyun içindeki iteminizi kopyalarken Control + Alt + C kullanın.",
        "tooltip_type": "Exclusive: Sadece bir tanesine izin verilir. İstisna: Eğer SADECE 1 Ex Prefix + 1 Ex Suffix varsa şans ~55%'e çıkarır. Non-Native: Modlar, onları doğal olarak rollayamayan base kazanırsa düşer."
    }
}

t = translations[language]
st.markdown(f"<h1>{t['title']}</h1>", unsafe_allow_html=True)

labels = ["Prefix 1", "Prefix 2", "Prefix 3", "Suffix 1", "Suffix 2", "Suffix 3"]

# Session State Initialization (Önceki kodla aynı)
for i in range(6):
    if f'item1_input_{i}' not in st.session_state: st.session_state[f'item1_input_{i}'] = ''
    if f'item2_input_{i}' not in st.session_state: st.session_state[f'item2_input_{i}'] = ''
    if f'item1_check_exclusive_{i}' not in st.session_state: st.session_state[f'item1_check_exclusive_{i}'] = False
    if f'item2_check_exclusive_{i}' not in st.session_state: st.session_state[f'item2_check_exclusive_{i}'] = False
    if f'item1_check_non_native_{i}' not in st.session_state: st.session_state[f'item1_check_non_native_{i}'] = False
    if f'item2_check_non_native_{i}' not in st.session_state: st.session_state[f'item2_check_non_native_{i}'] = False
    if f'item1_check_desired_{i}' not in st.session_state: st.session_state[f'item1_check_desired_{i}'] = False
    if f'item2_check_desired_{i}' not in st.session_state: st.session_state[f'item2_check_desired_{i}'] = False
    if f'item1_check_not_desired_{i}' not in st.session_state: st.session_state[f'item1_check_not_desired_{i}'] = False
    if f'item2_check_not_desired_{i}' not in st.session_state: st.session_state[f'item2_check_not_desired_{i}'] = False

if 'item1_paste_area' not in st.session_state: st.session_state['item1_paste_area'] = ''
if 'item2_paste_area' not in st.session_state: st.session_state['item2_paste_area'] = ''
if 'item1_base_desired' not in st.session_state: st.session_state['item1_base_desired'] = False
if 'item2_base_desired' not in st.session_state: st.session_state['item2_base_desired'] = False
if 'show_paste_item1' not in st.session_state: st.session_state['show_paste_item1'] = False
if 'show_paste_item2' not in st.session_state: st.session_state['show_paste_item2'] = False


col1, col2 = st.columns(2)

# --- ITEM 1 ---
with col1:
    st.markdown(f"<h3>{t['first_item']}</h3>", unsafe_allow_html=True)
    base_col, paste_col = st.columns([1, 1])

    with base_col:
        st.checkbox(
            t['desired_base'], 
            key="item1_base_check", 
            value=st.session_state.get('item1_base_desired', False), 
            disabled=st.session_state.get('item2_base_desired', False),
            on_change=handle_item1_base_change
        )

    with paste_col:
        btn_col, _ = st.columns([5, 1])
        with btn_col:
            if st.button(t['paste_item'], key="paste_btn_item1"):
                st.session_state['show_paste_item1'] = not st.session_state.get('show_paste_item1', False)
        
    if st.session_state.get('show_paste_item1', False):
        st.text_area(t["paste_item"] + " " + t["first_item"] + " " + "text here:", key="item1_paste_area", value=st.session_state.get('item1_paste_area',''), height=150)
        if st.button("Parse", key="parse_item1"):
            item_text = st.session_state.get('item1_paste_area', '')
            prefixes, suffixes = parse_item_text(item_text)
            for idx in range(6): st.session_state[f'item1_input_{idx}'] = ''
            for idx, prefix in enumerate(prefixes[:3]): st.session_state[f'item1_input_{idx}'] = prefix
            for idx, suffix in enumerate(suffixes[:3]): st.session_state[f'item1_input_{idx + 3}'] = suffix
            st.session_state['show_paste_item1'] = False
            safe_rerun()

    # Render each affix row
    for i in range(6):
        st.markdown('<div class="affix-group">', unsafe_allow_html=True)
        
        # Sütun düzeni: Input, Exclusive/Non-Native Stack, Desired/Not Desired Stack
        input_col, check_stack_1, check_stack_2 = st.columns([2, 1, 1])

        # INPUT
        with input_col:
            st.text_input(labels[i], key=f'item1_input_{i}', value=st.session_state.get(f'item1_input_{i}',''), label_visibility="visible")

        # CHECKBOX STACK 1: Exclusive / Non-Native
        with check_stack_1:
            st.markdown('<div class="checkbox-stack">', unsafe_allow_html=True)
            st.checkbox(t['exclusive'], key=f'item1_check_exclusive_{i}')
            st.checkbox(t['non_native'], key=f'item1_check_non_native_{i}')
            st.markdown('</div>', unsafe_allow_html=True)
        
        # CHECKBOX STACK 2: Desired / Not Desired
        with check_stack_2:
            st.markdown('<div class="checkbox-stack">', unsafe_allow_html=True)
            is_desired = st.checkbox(t['desired'], key=f'item1_check_desired_{i}')
            st.checkbox(t['not_desired'], key=f'item1_check_not_desired_{i}', disabled=is_desired)
            st.markdown('</div>', unsafe_allow_html=True)
            
        st.markdown('</div>', unsafe_allow_html=True) 

# --- ITEM 2 ---
with col2:
    st.markdown(f"<h3>{t['second_item']}</h3>", unsafe_allow_html=True)
    base_col, paste_col = st.columns([1, 1])

    with base_col:
        st.checkbox(
            t['desired_base'], 
            key="item2_base_check", 
            value=st.session_state.get('item2_base_desired', False), 
            disabled=st.session_state.get('item1_base_desired', False),
            on_change=handle_item2_base_change
        )

    with paste_col:
        btn_col, _ = st.columns([5, 1])
        with btn_col:
            if st.button(t['paste_item'], key="paste_btn_item2"):
                st.session_state['show_paste_item2'] = not st.session_state.get('show_paste_item2', False)
        
    if st.session_state.get('show_paste_item2', False):
        st.text_area(t["paste_item"] + " " + t["second_item"] + " " + "text here:", key="item2_paste_area", value=st.session_state.get('item2_paste_area',''), height=150)
        if st.button("Parse", key="parse_item2"):
            item_text = st.session_state.get('item2_paste_area', '')
            prefixes, suffixes = parse_item_text(item_text)
            for idx in range(6): st.session_state[f'item2_input_{idx}'] = ''
            for idx, prefix in enumerate(prefixes[:3]): st.session_state[f'item2_input_{idx}'] = prefix
            for idx, suffix in enumerate(suffixes[:3]): st.session_state[f'item2_input_{idx + 3}'] = suffix
            st.session_state['show_paste_item2'] = False
            safe_rerun()

    # Render each affix row
    for i in range(6):
        st.markdown('<div class="affix-group">', unsafe_allow_html=True)
        
        # Sütun düzeni: Input, Exclusive/Non-Native Stack, Desired/Not Desired Stack
        input_col, check_stack_1, check_stack_2 = st.columns([2, 1, 1])

        # INPUT
        with input_col:
            st.text_input(labels[i], key=f'item2_input_{i}', value=st.session_state.get(f'item2_input_{i}',''), label_visibility="visible")

        # CHECKBOX STACK 1: Exclusive / Non-Native
        with check_stack_1:
            st.markdown('<div class="checkbox-stack">', unsafe_allow_html=True)
            st.checkbox(t['exclusive'], key=f'item2_check_exclusive_{i}')
            st.checkbox(t['non_native'], key=f'item2_check_non_native_{i}')
            st.markdown('</div>', unsafe_allow_html=True)
        
        # CHECKBOX STACK 2: Desired / Not Desired
        with check_stack_2:
            st.markdown('<div class="checkbox-stack">', unsafe_allow_html=True)
            is_desired = st.checkbox(t['desired'], key=f'item2_check_desired_{i}')
            st.checkbox(t['not_desired'], key=f'item2_check_not_desired_{i}', disabled=is_desired)
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True) 

# -------------------------
# Calculation & Result
# -------------------------
st.markdown("---")
col_calc, col_reset = st.columns([4, 1])

with col_calc:
    if st.button(t['calculate'], key="calculate_button"):
        
        prob, error = calculate_combined_probability()
        
        if error:
            st.session_state['result_text'] = f'<p class="error-text">❌ {error}</p>'
        elif prob is not None:
            formatted_prob = f"{prob * 100:.2f}%"
            st.session_state['result_text'] = f'<p class="result-text">{t["probability"]} <b>{formatted_prob}</b></p>'
        else:
            st.session_state['result_text'] = ''
            
with col_reset:
    if st.button(t['reset'], key="reset_button"):
        for key in st.session_state.keys():
            if key not in ['language_selector']:
                del st.session_state[key]
        st.session_state['result_text'] = ''
        safe_rerun()

st.markdown(st.session_state.get('result_text', ''), unsafe_allow_html=True)
import streamlit as st
from math import comb
import re

# -------------------------
# Page config & CSS
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

    /* Visual grouping for affix rows - Dış dikdörtgen kaldırıldı */
    .affix-group {
        border-top: 1px solid #e0e0e0; /* Ayırıcı çizgi olarak sadece üst sınır kalsın */
        padding: 5px 0;
        margin-bottom: 0px;
    }
    .affix-group:first-child {
        border-top: none; /* İlk modun üst çizgisini kaldır */
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
        height: 15px; /* Checkboxlar arası boşluğu azaltmak için */
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
# Calculation functions (GÜNCELLENDİ)
# -------------------------
def get_count_probabilities(count):
    # Toplam Mod Sayısı (Duplicate'ler dahil) -> Çıkan Mod Sayısı: Olasılık
    if count == 0: return {0: 1.0}
    if count == 1: return {0: 0.41, 1: 0.59}
    if count == 2: return {1: 0.667, 2: 0.333}
    if count == 3: return {1: 0.40, 2: 0.50, 3: 0.10} 
    if count == 4: return {1: 0.10, 2: 0.60, 3: 0.30}
    if count == 5: return {2: 0.43, 3: 0.57}
    if count == 6: return {2: 0.30, 3: 0.70}
    
    return {}

def calculate_selection_probability(all_mods_list, desired_mods, not_desired_mods, outcome_count, winning_base):
    
    # 1. Non-Native Kontrolü: Kazanan base'de olmayan non-native modları düşür.
    available_mods = []
    for mod_info in all_mods_list:
        if mod_info['non_native'] and mod_info['item'] != winning_base:
            continue
        available_mods.append(mod_info['mod'])
    
    # 2. Seçilebilir Benzersiz Mod Havuzu (Non-Native düşenler hariç)
    selectable_mods_pool = list(set(available_mods))
    
    # 3. İstenen modların havuzda olma ve İstenmeyen modların olmama kontrolü.
    for desired in desired_mods:
        if desired not in selectable_mods_pool:
            return 0.0 # İstenen mod havuzda yok.
    
    # 4. İstenmeyen modları çıkararak nihai seçilebilir havuz.
    selectable_mods = [m for m in selectable_mods_pool if m not in not_desired_mods]
    
    # 5. İhtimal Kontrolü:
    if len(desired_mods) > outcome_count:
        return 0.0 # İstenen mod sayısı, çıkan mod sayısından fazla.
    
    # 6. Benzersiz Mod Tekrarı Kontrolü (Hata düzeltmesi burada)
    # Eğer benzersiz mod sayısı (Desired + Kalan) çıkan mod sayısından az ise, 
    # bu, aynı modun tekrar geleceği anlamına gelir.
    
    # İstenen modlar haricindeki seçilebilir modlar:
    non_desired_selectable = [m for m in selectable_mods if m not in desired_mods]
    
    # Toplam benzersiz mod sayısı (Desired + Kalan)
    total_unique_selectable = len(desired_mods) + len(non_desired_selectable)
    
    # Eğer toplam benzersiz seçilebilir mod sayısı, çıkacak mod sayısından az ise, 
    # ve biz tüm Desired modları istiyorsak, bu durum zaten başarılıdır ve olasılık 1.0 olmalıdır.
    if total_unique_selectable < outcome_count:
        # Örnek: q Desired, outcome_count=2. Benzersiz mod 1. Zaten 2 mod gelirse ikisi de q olmak zorunda.
        # Bu sadece Desired modların gelmesi koşulunda geçerlidir.
        if len(desired_mods) == total_unique_selectable: 
             return 1.0
        else:
             # Eğer 1 mod q, 1 mod w var, q desired, outcome=3, 
             # total_unique=2. Impossible: 3 mod seçilemez.
             if outcome_count > total_unique_selectable and outcome_count > 3: # Max 3 mod
                 return 0.0
             
    if len(selectable_mods) < outcome_count:
         # Seçilebilecek benzersiz mod sayısı, çıkacak mod sayısından az ise 
         # (Yukarıdaki kural ile çakışmadığı sürece)
         return 0.0 
    
    # 7. Kombinasyon Hesaplaması (Geleneksel yol, Desired modlar farklıysa)
    
    filled_slots = len(desired_mods)
    remaining_slots = outcome_count - filled_slots 
    
    if remaining_slots < 0: return 0.0
    
    if remaining_slots > len(non_desired_selectable):
        return 0.0
    
    # Başarılı Kombinasyon (Pay):
    favorable_combinations = comb(len(non_desired_selectable), remaining_slots)
    
    # Toplam Olası Kombinasyon (Payda):
    total_combinations = comb(len(selectable_mods), outcome_count)
    
    if total_combinations == 0:
        return 0.0
    
    return favorable_combinations / total_combinations

def calculate_modifier_probability(mods_item1, mods_item2, desired_mods, not_desired_mods, item1_base_desired, item2_base_desired):
    
    all_mods_list = mods_item1 + mods_item2
    
    # Tablo için kullanılan toplam mod sayısı (duplikasyon dahil)
    total_mod_count = len(all_mods_list)
    
    if total_mod_count == 0: 
        return 0.0 if len(desired_mods) > 0 else 1.0

    count_probs = get_count_probabilities(total_mod_count)
    
    total_prob = 0.0
    
    for outcome_count, count_prob in count_probs.items():
        if outcome_count == 0:
            if len(desired_mods) == 0:
                 total_prob += count_prob
            continue
        
        if len(desired_mods) > outcome_count:
            continue
        
        prob_base1 = calculate_selection_probability(all_mods_list, desired_mods, not_desired_mods, outcome_count, 1)
        prob_base2 = calculate_selection_probability(all_mods_list, desired_mods, not_desired_mods, outcome_count, 2)
        
        # Base seçimi ve toplam selection_prob hesaplaması
        if item1_base_desired and item2_base_desired:
             selection_prob = 0.0
        elif item1_base_desired:
            selection_prob = prob_base1
        elif item2_base_desired:
            selection_prob = prob_base2
        else:
            # Base seçimi yapılmadıysa, Base 1 ve Base 2'nin gelme ihtimali 50/50'dir.
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
    
    prefixes_item1 = []
    prefixes_item2 = []
    suffixes_item1 = []
    suffixes_item2 = []
    
    desired_prefixes = set()
    desired_suffixes = set()
    not_desired_prefixes = set()
    not_desired_suffixes = set()
    
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
            else:
                pref_standard = "Doesn't Matter"
            
            if is_exclusive: exclusive_mods.append((val1, pref_standard == 'Desired', mod_type, 1))
        
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
            else:
                pref_standard = "Doesn't Matter"
            
            if is_exclusive: exclusive_mods.append((val2, pref_standard == 'Desired', mod_type, 2))
    
    # --- ERROR CHECK: Çakışan Seçimler ---
    for i in range(6):
        if st.session_state.get(f'item1_input_{i}'):
            is_desired = st.session_state.get(f'item1_check_desired_{i}', False)
            is_not_desired = st.session_state.get(f'item1_check_not_desired_{i}', False)
            if is_desired and is_not_desired:
                return None, t['error_pref_conflict']
                
        if st.session_state.get(f'item2_input_{i}'):
            is_desired = st.session_state.get(f'item2_check_desired_{i}', False)
            is_not_desired = st.session_state.get(f'item2_check_not_desired_{i}', False)
            if is_desired and is_not_desired:
                return None, t['error_pref_conflict']

    # --- ERROR CHECK: Max desired affixes ---
    if len(desired_prefixes) > 3 or len(desired_suffixes) > 3:
        return None, t['error_too_many_desired']
    
    if len(desired_prefixes) == 0 and len(desired_suffixes) == 0:
        return None, t['error_no_desired']
    
    # Exclusive Mod Çakışma Kontrolü (Özel durum %55)
    if len(exclusive_mods) > 1:
        if len(exclusive_mods) == 2:
            ex1, ex2 = exclusive_mods
            
            # Kontrol: Mod tipleri (prefix/suffix) farklı olmalı VE biri Desired diğeri Not Desired olmalı.
            is_valid_exception = (ex1[2] != ex2[2]) and \
                                 ((ex1[1] and not ex2[1]) or (ex2[1] and not ex1[1]))
            
            if is_valid_exception:
                # Kullanıcı isteği %55
                return 0.55, None 
                
        return None, t['error_exclusive']
    
    # Prefix ve Suffix Olasılıklarını Hesapla
    prefix_prob = calculate_modifier_probability(
        prefixes_item1, prefixes_item2, 
        desired_prefixes, not_desired_prefixes, 
        st.session_state.get('item1_base_desired', False), st.session_state.get('item2_base_desired', False)
    )
    suffix_prob = calculate_modifier_probability(
        suffixes_item1, suffixes_item2, 
        desired_suffixes, not_desired_suffixes, 
        st.session_state.get('item1_base_desired', False), st.session_state.get('item2_base_desired', False)
    )
    
    total_prob = prefix_prob * suffix_prob
    
    return total_prob, None

# Diğer gerekli fonksiyonlar (parse_item_text, handle_base_change) ve UI çevirileri (t) kodun orijinal halinden korunmuştur.


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
        "error_exclusive": "You can have at most 1 exclusive modifier on the final item, or the 1P + 1S exception.",
        "error_both_bases": "Cannot select both bases as desired",
        "error_too_many_desired": "Please do not pick more than 3 unique prefixes/suffixes as desired",
        "error_no_desired": "Please pick at least 1 desired modifier",
        "error_pref_conflict": "Cannot select a modifier as both Desired and Not Desired",
        "exclusive": "Exclusive",
        "non_native": "Non-Native",
        "desired": "Desired",
        "not_desired": "Not Desired",
        "paste_item": "Paste Item",
        "tooltip_paste": "Please use **Control + Alt + C** while copying your in game items.",
        "tooltip_type": "The resulting item can only have **one** Exclusive modifier. Avoid using them to increase odds. Exception: If recombining 1 prefix item with 1 suffix item, using 1 exclusive prefix and 1 exclusive suffix gives ~55% chance.<br><br>**Non-Native** modifiers are base-restricted. If the base that cannot naturally roll this mod wins the recombination, the mod is dropped. (e.g., Dexterity on an Evasion helm won't pass to a Pure Armour helm). For more info: <a href='https://www.poewiki.net/wiki/Recombinator' target='_blank'>Poewiki Link</a>"
    },
    "Turkish": {
        "title": "Recombinator Hesaplayıcısı",
        "first_item": "İlk Item",
        "second_item": "İkinci Item",
        "desired_base": "İstediğiniz Final Base",
        "calculate": "Hesapla",
        "probability": "İstediğiniz affixlerin gelme olasılığı:",
        "reset": "Sıfırla",
        "error_exclusive": "Final itemde maksimum 1 adet exclusive modifier olabilir (veya 1P + 1S istisnası).",
        "error_both_bases": "Her iki base'i de istediğiniz olarak seçemezsiniz",
        "error_too_many_desired": "Lütfen 3'ten fazla farklı prefix/suffix'i istediğiniz olarak seçmeyin",
        "error_no_desired": "Lütfen en az 1 adet istediğiniz modifier seçin",
        "error_pref_conflict": "Bir modifier'ı hem İstiyorum hem de İstemiyorum olarak seçemezsiniz",
        "exclusive": "Exclusive",
        "non_native": "Non-Native",
        "desired": "İstiyorum",
        "not_desired": "İstemiyorum",
        "paste_item": "Item Yapıştır",
        "tooltip_paste": "Lütfen oyun içindeki iteminizi kopyalarken **Control + Alt + C** kullanın.",
        "tooltip_type": "Final itemde maksimum **1 adet Exclusive** modifier olabilir. Şansınızı yükseltmek için bunlardan kaçının. İstisna: Eğer 1 prefix item ile 1 suffix item birleştiriyorsanız, 1 exclusive prefix ve 1 exclusive suffix kullanmak şansı ~%55'e çıkarır.<br><br>**Non-Native** modifierlar base'e özeldir. Eğer bu modu doğal olarak rollayamayan base kazanırsa, mod düşer (Örn: Evasion kaskındaki Dexterity, Full Armor kaska geçmez). Daha fazla bilgi için: <a href='https://www.poewiki.net/wiki/Recombinator' target='_blank'>Poewiki Link</a>"
    }
}

t = translations[language]
st.markdown(f"<h1>{t['title']}</h1>", unsafe_allow_html=True)

labels = ["Prefix 1", "Prefix 2", "Prefix 3", "Suffix 1", "Suffix 2", "Suffix 3"]

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
        btn_col, tip_col = st.columns([5, 1])
        with btn_col:
            if st.button(t['paste_item'], key="paste_btn_item1"):
                st.session_state['show_paste_item1'] = not st.session_state.get('show_paste_item1', False)
        
        with tip_col:
            st.markdown(f'''
                <div class="paste-tooltip-container">
                    <input type="checkbox" id="tooltip_paste_1" class="tooltip-checkbox">
                    <label for="tooltip_paste_1" class="tooltip-icon">?</label>
                    <div class="tooltip-text-small">{t['tooltip_paste']}</div>
                </div>
            ''', unsafe_allow_html=True)


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
        
        # Sütun düzeni: Input, Exclusive/Non-Native Stack, Desired/Not Desired Stack, Tooltip
        input_col, check_stack_1, check_stack_2, type_tip_col = st.columns([2, 1, 1, 0.2])

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
            
        # Tooltip (Modifer Type için)
        with type_tip_col:
            st.markdown(f'''
                <div class="tooltip-container">
                    <input type="checkbox" id="tooltip_type_1_{i}" class="tooltip-checkbox">
                    <label for="tooltip_type_1_{i}" class="tooltip-icon">?</label>
                    <div class="tooltip-text-large">{t['tooltip_type']}</div>
                </div>
            ''', unsafe_allow_html=True)

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
        btn_col, tip_col = st.columns([5, 1])
        with btn_col:
            if st.button(t['paste_item'], key="paste_btn_item2"):
                st.session_state['show_paste_item2'] = not st.session_state.get('show_paste_item2', False)
        
        with tip_col:
            st.markdown(f'''
                <div class="paste-tooltip-container">
                    <input type="checkbox" id="tooltip_paste_2" class="tooltip-checkbox">
                    <label for="tooltip_paste_2" class="tooltip-icon">?</label>
                    <div class="tooltip-text-small">{t['tooltip_paste']}</div>
                </div>
            ''', unsafe_allow_html=True)


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
        
        # Sütun düzeni: Input, Exclusive/Non-Native Stack, Desired/Not Desired Stack, Tooltip
        input_col, check_stack_1, check_stack_2, type_tip_col = st.columns([2, 1, 1, 0.2])

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

        # Tooltip (Modifer Type için)
        with type_tip_col:
            st.markdown(f'''
                <div class="tooltip-container">
                    <input type="checkbox" id="tooltip_type_2_{i}" class="tooltip-checkbox">
                    <label for="tooltip_type_2_{i}" class="tooltip-icon">?</label>
                    <div class="tooltip-text-large">{t['tooltip_type']}</div>
                </div>
            ''', unsafe_allow_html=True)

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
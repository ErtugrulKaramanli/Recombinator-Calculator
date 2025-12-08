import streamlit as st
from math import comb

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
        font-size: 11px; /* Font boyutu düşürüldü */
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
        background-color: #f7f7f7; 
        border: 1px solid #e0e0e0;
        padding: 5px;
        border-radius: 5px;
        margin-bottom: 8px;
    }
    
    /* Consolidated Tooltip Styling (Mevcut stiller korundu) */
    .tooltip-container { position: relative; display: block; text-align: center; width: 100%; margin-top: -10px; margin-bottom: 5px; }
    .paste-tooltip-container { position: relative; display: inline-block; margin-left: 0px; padding-top: 13px; }
    .paste-tooltip-container .tooltip-icon { margin: 0; display: inline; }
    .paste-tooltip-container .tooltip-text-small { left: 0; transform: translateX(0%); }
    .tooltip-checkbox { opacity: 0; pointer-events: none; }
    .tooltip-icon { cursor: pointer; color: #007bff; display: block; font-weight: bold; font-size: 16px; line-height: 1; width: fit-content; margin: 0 auto; }
    .tooltip-text-large { visibility: hidden; width: 500px; background-color: #333; color: #fff; text-align: left; padding: 15px; border-radius: 8px; position: absolute; z-index: 1000; bottom: 110%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; white-space: normal; font-size: 13px; line-height: 1.4; }
    .tooltip-text-small { visibility: hidden; width: 300px; background-color: #333; color: #fff; text-align: left; padding: 10px; border-radius: 5px; position: absolute; z-index: 1000; bottom: 110%; left: 50%; transform: translateX(-50%); opacity: 0; transition: opacity 0.3s; white-space: normal; font-size: 13px; }

    .tooltip-checkbox:checked ~ .tooltip-icon + .tooltip-text-small,
    .tooltip-checkbox:checked ~ .tooltip-icon + .tooltip-text-large { visibility: visible; opacity: 1; }
    
    /* General label styling */
    label { font-size: 13px; }
    .stTextArea label { font-size: 13px; }
    .stCheckbox [disabled] { opacity: 0.6; }
    </style>
""", unsafe_allow_html=True)


# -------------------------
# Safe rerun helper 
# -------------------------
def safe_rerun():
    """Call a rerun function if available, but avoid AttributeError in older/newer Streamlit builds."""
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
    """Sets item 1 base and enforces mutual exclusivity."""
    is_checked = st.session_state['item1_base_check']
    st.session_state['item1_base_desired'] = is_checked
    
    if is_checked and st.session_state.get('item2_base_desired', False):
        st.session_state['item2_base_desired'] = False
        safe_rerun()
        
def handle_item2_base_change():
    """Sets item 2 base and enforces mutual exclusivity."""
    is_checked = st.session_state['item2_base_check']
    st.session_state['item2_base_desired'] = is_checked

    if is_checked and st.session_state.get('item1_base_desired', False):
        st.session_state['item1_base_desired'] = False
        safe_rerun()


# -------------------------
# Calculation functions (Düzeltildi)
# -------------------------
def get_count_probabilities(count):
    # Düzeltilen olasılık tablosu (Örnek: 2 mod alırken 2 modun aynı olma durumunda birinin seçilme ihtimali,
    # bu tabloda zaten 'outcome_count' olarak yansıtılmamalı. Seçim olasılığı ayrı hesaplanacak.)
    
    # Prefix/Suffix sayısı (Total_Count) -> Çıkan mod sayısı (Outcome_Count): Olasılık
    if count == 0: return {0: 1.0}
    # 1/2 mod, 2 moddan 1 mod alma ihtimali 66.7, 2 mod alma ihtimali 33.3.
    # Bu tabloda kaç **farklı** mod geleceği değil, kaç **adet** mod geleceği var.
    # Yani 2 farklı moddan 1 adet veya 2 adet mod seçilir. 
    # Ancak burada "total_count" 1 adet modun bulunması durumunu temsil ediyor olmalı.
    
    # Kullanıcıdan gelen listeye göre düzenlenmiş olasılıklar:
    if count == 1: return {0: 0.41, 1: 0.59} # 1 moddan 0 veya 1 mod
    if count == 2: return {1: 0.667, 2: 0.333} # 2 moddan 1 veya 2 mod
    if count == 3: return {1: 0.50, 2: 0.40, 3: 0.10} # 3 moddan 1, 2, 3 mod
    if count == 4: return {1: 0.10, 2: 0.60, 3: 0.30} # 4 moddan 1, 2, 3 mod (Max 3 alınabilir)
    if count == 5: return {2: 0.43, 3: 0.57} # 5 moddan 2 veya 3 mod (Max 3 alınabilir)
    if count == 6: return {2: 0.30, 3: 0.70} # 6 moddan 2 veya 3 mod (Max 3 alınabilir)
    
    # Not: 4, 5, 6 modun 1 adet gelme ihtimali yok kabul edilmiştir.
    # Bu olasılıkların kaynağına göre değişiklik gösterebilir, buradaki değerler korundu.
    return {}

def calculate_selection_probability(all_mods_list, unique_mods, desired_mods, not_desired_mods, outcome_count, winning_base):
    available_mods = []
    # 1. Non-Native Kontrolü: Yalnızca kazanan base'de bulunan non-native modlar seçime girer.
    for mod_info in all_mods_list:
        # Non-native İtem 1'de ise ve Base 2 kazanırsa, bu mod seçime dahil edilmez.
        # Non-native İtem 2'de ise ve Base 1 kazanırsa, bu mod seçime dahil edilmez.
        if mod_info['non_native'] and mod_info['item'] != winning_base:
            continue
        available_mods.append(mod_info['mod'])
    
    # Seçim havuzundaki benzersiz modlar
    available_unique = list(set(available_mods))
    
    # 2. Zorunlu Kontrol: İstenen modlar havuzda mevcut olmalı.
    for desired in desired_mods:
        if desired not in available_unique:
            return 0.0 # İstenen mod havuzda yoksa, olasılık 0.
    
    # 3. Seçilebilir Modlar Havuzu: İstenmeyen modlar hariç, havuzdaki tüm modlar.
    selectable_mods = [m for m in available_unique if m not in not_desired_mods]
    
    # 4. İstenen modlar (desired) seçilebilir havuzda olmalı (Zaten 2. adımda kontrol edildi, burası fazladan koruma).
    for desired in desired_mods:
        if desired not in selectable_mods:
            return 0.0
            
    # 5. İhtimal Kontrolü:
    if len(selectable_mods) < outcome_count:
        return 0.0 # Seçim havuzundaki mod sayısı, çıkacak mod sayısından azsa imkansız.
    
    if len(desired_mods) > outcome_count:
        return 0.0 # İstenen mod sayısı, çıkacak mod sayısından fazlaysa imkansız.
    
    # 6. Kombinasyon Hesaplaması:
    
    # Toplam Olası Kombinasyon (Payda):
    # Seçilebilir modlar arasından (istenmeyenler çıkarılmış), çıkacak mod sayısı kadar seçim.
    total_combinations = comb(len(selectable_mods), outcome_count)
    if total_combinations == 0:
        # Total kombinasyon 0 ise, tek bir istenen modun bile seçilme ihtimali yok demektir (len(selectable_mods) < outcome_count durumu bu yukarıda zaten kontrol edilmişti).
        return 0.0
        
    # Başarılı Kombinasyon (Pay):
    
    # Kaç slotun Desired modlar tarafından doldurulduğu:
    filled_slots = len(desired_mods)
    
    # Geriye kalan slot sayısı (Başarılı kombinasyonu tamamlamak için gerekli olan, 'Doesn't Matter' modlardan seçilecek mod sayısı)
    remaining_slots = outcome_count - filled_slots 
    
    # İstenen modlar haricindeki (ve istenmeyenler zaten çıkarılmış) modlar havuzu.
    non_desired_selectable = [m for m in selectable_mods if m not in desired_mods]
    
    # Geriye kalan slotların doldurulabileceği mod sayısı, kalan slot sayısından azsa imkansız.
    if remaining_slots > len(non_desired_selectable):
        return 0.0
    
    # Kalan slotları, kalan mod havuzundan seçme kombinasyonu
    favorable_combinations = comb(len(non_desired_selectable), remaining_slots)
    
    # Sonuç: (Favorable Kombinasyonlar) / (Total Kombinasyonlar)
    return favorable_combinations / total_combinations

def calculate_modifier_probability(mods_item1, mods_item2, desired_mods, not_desired_mods, item1_base_desired, item2_base_desired):
    # Eğer hiç istenen/istenmeyen mod yoksa, ihtimal %100'dür.
    if len(desired_mods) == 0:
        # İstenmeyen modlar kontrolü burada yok, çünkü desired_mods 0 ise ve not_desired_mods > 0 ise 
        # yine de selection_probability içinde kontrol edilmeli. Ancak bu fonksiyon, desired modların
        # *hepsinin* gelme ihtimalini hesaplar. 
        # Eğer desired mod yoksa ve istenmeyen modlar gelmezse (ki bu 0 mod gelebilir demek),
        # selection_probability içinde 0 mod durumu ele alınacaktır. Basitçe:
        if len(not_desired_mods) == 0:
            return 1.0

    all_mods_list = mods_item1 + mods_item2
    # Benzersiz modlar (mod adı bazında)
    unique_mods_only = list(set([m['mod'] for m in all_mods_list]))
    total_unique_count = len(unique_mods_only)
    
    # Max 3 prefix/suffix kısıtlamasına rağmen 6'ya kadar mod girilebilmesi nedeniyle 
    # kombinasyonları toplam mod sayısına (all_mods_list'in boyutu) göre değil, 
    # **benzersiz mod sayısına** göre alacağız. (PoE Recombinator mantığına göre)
    if total_unique_count == 0: 
        return 0.0 if len(desired_mods) > 0 else 1.0 # İstenen mod yoksa ve havuz boşsa başarılı.
    
    # Olasılık tablosunu benzersiz mod sayısına göre çek:
    count_probs = get_count_probabilities(total_unique_count)
    
    total_prob = 0.0
    
    # Her bir çıkan mod sayısı (outcome_count) için olasılığı hesapla:
    for outcome_count, count_prob in count_probs.items():
        if outcome_count == 0:
            # 0 mod gelmesi durumunda, eğer desired mod yoksa, bu da başarılıdır.
            if len(desired_mods) == 0:
                 total_prob += count_prob
            continue
        
        # Base 1 kazanma ve Base 2 kazanma olasılıkları
        prob_base1 = calculate_selection_probability(all_mods_list, unique_mods_only, desired_mods, not_desired_mods, outcome_count, 1)
        prob_base2 = calculate_selection_probability(all_mods_list, unique_mods_only, desired_mods, not_desired_mods, outcome_count, 2)
        
        # Base seçimi ve toplam selection_prob hesaplaması
        if item1_base_desired and item2_base_desired:
             selection_prob = 0.0 # Zaten UI'da engelleniyor
        elif item1_base_desired:
            selection_prob = prob_base1
        elif item2_base_desired:
            selection_prob = prob_base2
        else:
            # Base seçimi yapılmadıysa, Base 1 ve Base 2'nin gelme ihtimali 50/50'dir.
            selection_prob = (prob_base1 + prob_base2) / 2
        
        # Total olasılığa ekle: (Mod Sayısı Olasılığı) * (Seçim Olasılığı)
        total_prob += count_prob * selection_prob
    
    return total_prob

def parse_item_text(item_text):
    # Modifiers: Eklenen bir satır: "--------------------" ile başlayan satırları atlamak için
    lines = item_text.strip().split('\n')
    prefixes = []
    suffixes = []
    
    # PoE item kopyalama formatına göre: Prefix ve Suffix olarak etiketlenen satırları bulur.
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Modifiers:
        if 'Prefix Modifier' in line:
            if i + 1 < len(lines):
                # Bir sonraki satır modun kendisidir.
                mod_line = lines[i + 1].strip()
                # Tier (örn: "T1") kısmını ve değer aralıklarını (örn: "(20–30)") temizle
                import re
                mod_clean = re.sub(r'\s*T\d+\s*', '', mod_line)
                mod_clean = re.sub(r'\s*\(\d+–\d+\)', '', mod_clean)
                prefixes.append(mod_clean)
                i += 1 # Mod satırını atla
        
        elif 'Suffix Modifier' in line:
            if i + 1 < len(lines):
                mod_line = lines[i + 1].strip()
                import re
                mod_clean = re.sub(r'\s*T\d+\s*', '', mod_line)
                mod_clean = re.sub(r'\s*\(\d+–\d+\)', '', mod_clean)
                suffixes.append(mod_clean)
                i += 1 # Mod satırını atla
        
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
    
    # 6 mod için döngü (3 prefix, 3 suffix)
    for i in range(6):
        mod_type = 'prefix' if i < 3 else 'suffix'
        
        # Item 1
        val1 = st.session_state.get(f'item1_input_{i}', '').strip()
        if val1:
            # Dropdown yerine onay kutularından state çek
            is_exclusive = st.session_state.get(f'item1_check_exclusive_{i}', False)
            is_non_native = st.session_state.get(f'item1_check_non_native_{i}', False)
            is_desired = st.session_state.get(f'item1_check_desired_{i}', False)
            is_not_desired = st.session_state.get(f'item1_check_not_desired_{i}', False)
            
            # Modifier Info listesi için
            mod_info = {'mod': val1, 'non_native': is_non_native, 'exclusive': is_exclusive, 'item': 1}
            if mod_type == 'prefix': prefixes_item1.append(mod_info)
            else: suffixes_item1.append(mod_info)
            
            # Preference kümeleri için
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
            # Dropdown yerine onay kutularından state çek
            is_exclusive = st.session_state.get(f'item2_check_exclusive_{i}', False)
            is_non_native = st.session_state.get(f'item2_check_non_native_{i}', False)
            is_desired = st.session_state.get(f'item2_check_desired_{i}', False)
            is_not_desired = st.session_state.get(f'item2_check_not_desired_{i}', False)
            
            # Modifier Info listesi için
            mod_info = {'mod': val2, 'non_native': is_non_native, 'exclusive': is_exclusive, 'item': 2}
            if mod_type == 'prefix': prefixes_item2.append(mod_info)
            else: suffixes_item2.append(mod_info)
            
            # Preference kümeleri için
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
    # Not: Öncelik Desired'a verildiği için, hem Desired hem Not Desired seçilmişse Desired olarak kabul edilir.
    for i in range(6):
        # Item 1
        if st.session_state.get(f'item1_input_{i}'):
            is_desired = st.session_state.get(f'item1_check_desired_{i}', False)
            is_not_desired = st.session_state.get(f'item1_check_not_desired_{i}', False)
            if is_desired and is_not_desired:
                return None, t['error_pref_conflict']
                
        # Item 2
        if st.session_state.get(f'item2_input_{i}'):
            is_desired = st.session_state.get(f'item2_check_desired_{i}', False)
            is_not_desired = st.session_state.get(f'item2_check_not_desired_{i}', False)
            if is_desired and is_not_desired:
                return None, t['error_pref_conflict']

    # --- ERROR CHECK: Max desired affixes ---
    # Aynı mod iki itemde de isteniyorsa, kümeye (set) bir kere ekleneceği için sorun olmaz.
    if len(desired_prefixes) > 3 or len(desired_suffixes) > 3:
        return None, t['error_too_many_desired']
    
    # En az 1 desired mod seçilmiş olmalı
    if len(desired_prefixes) == 0 and len(desired_suffixes) == 0:
        return None, t['error_no_desired']
    
    # Exclusive Mod Çakışma Kontrolü (Özel durum dahil)
    if len(exclusive_mods) > 1:
        # İzin verilen tek istisna: (1p itemden desired exclusive prefix) + (1s itemden NOT desired exclusive suffix) VEYA tam tersi
        # Not: Bu kontrol, modların gerçekten 1p ve 1s itemler olup olmadığını garanti etmiyor. 
        # Sadece 1 Desired Exclusive ve 1 Not Desired Exclusive varsa 0.5 ihtimali verir.
        if len(exclusive_mods) == 2:
            ex1, ex2 = exclusive_mods
            is_valid_exception = (ex1[2] != ex2[2]) and \
                                 ((ex1[1] and not ex2[1]) or (ex2[1] and not ex1[1]))
            
            if is_valid_exception:
                # İhtimal %50'dir, çünkü bu özel durum Base'in %50 gelme olasılığını simgeler.
                # Mod olasılıkları 1.0 olarak kabul edilir.
                return 0.5, None 
        return None, t['error_exclusive']
    
    # Base Olasılığı
    base_prob = 1.0
    item1_base_desired = st.session_state.get('item1_base_desired', False)
    item2_base_desired = st.session_state.get('item2_base_desired', False)
    
    if item1_base_desired and item2_base_desired:
        return None, t['error_both_bases'] # Zaten on_change ile engelleniyor.
    elif item1_base_desired or item2_base_desired:
        base_prob = 0.5
    
    # Prefix ve Suffix Olasılıklarını Hesapla
    prefix_prob = calculate_modifier_probability(
        prefixes_item1, prefixes_item2, 
        desired_prefixes, not_desired_prefixes, 
        item1_base_desired, item2_base_desired
    )
    suffix_prob = calculate_modifier_probability(
        suffixes_item1, suffixes_item2, 
        desired_suffixes, not_desired_suffixes, 
        item1_base_desired, item2_base_desired
    )
    
    # Genel Olasılık = Base Olasılığı * Prefix Olasılığı * Suffix Olasılığı
    total_prob = base_prob * prefix_prob * suffix_prob
    
    return total_prob, None


# -------------------------
# UI: Translations and Init
# -------------------------
col_lang, _ = st.columns([1, 5])
with col_lang:
    language = st.selectbox("", ["English", "Turkish"], key="language_selector", label_visibility="collapsed")

# **GÜNCELLENMİŞ ÇEVİRİLER**
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
        "tooltip_type": "The resulting item can only have **one** Exclusive modifier. Avoid using them to increase odds. Exception: If recombining 1 prefix item with 1 suffix item, using 1 exclusive prefix and 1 exclusive suffix gives ~50% chance.<br><br>**Non-Native** modifiers are base-restricted. If the base that cannot naturally roll this mod wins the recombination, the mod is dropped. (e.g., Dexterity on an Evasion helm won't pass to a Pure Armour helm). For more info: <a href='https://www.poewiki.net/wiki/Recombinator' target='_blank'>Poewiki Link</a>"
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
        "tooltip_type": "Final itemde maksimum **1 adet Exclusive** modifier olabilir. Şansınızı yükseltmek için bunlardan kaçının. İstisna: Eğer 1 prefix item ile 1 suffix item birleştiriyorsanız, 1 exclusive prefix ve 1 exclusive suffix kullanmak şansı ~%50'ye çıkarır.<br><br>**Non-Native** modifierlar base'e özeldir. Eğer bu modu doğal olarak rollayamayan base kazanırsa, mod düşer (Örn: Evasion kaskındaki Dexterity, Full Armor kaska geçmez). Daha fazla bilgi için: <a href='https://www.poewiki.net/wiki/Recombinator' target='_blank'>Poewiki Link</a>"
    }
}

t = translations[language]
st.markdown(f"<h1>{t['title']}</h1>", unsafe_allow_html=True)

labels = ["Prefix 1", "Prefix 2", "Prefix 3", "Suffix 1", "Suffix 2", "Suffix 3"]

# Session state initialization (Checkbox'lar için güncellendi)
for i in range(6):
    if f'item1_input_{i}' not in st.session_state: st.session_state[f'item1_input_{i}'] = ''
    if f'item2_input_{i}' not in st.session_state: st.session_state[f'item2_input_{i}'] = ''
    
    # Checkbox'lar için yeni state'ler
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

# -------------------------
# Layout: two item columns
# -------------------------
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
        
        # Sütun düzeni: Input, Checkboxlar (3 adet), Tooltip (Modifer Type için)
        input_col, check_col_1, check_col_2, check_col_3, type_tip_col = st.columns([2, 1, 1, 1, 0.2])

        # INPUT
        with input_col:
            st.text_input(labels[i], key=f'item1_input_{i}', value=st.session_state.get(f'item1_input_{i}',''), label_visibility="visible")

        # CHECKBOXLAR (Alt alta sığdırmak için küçük sütunlar)
        # Exclusive
        with check_col_1:
            st.checkbox(t['exclusive'], key=f'item1_check_exclusive_{i}')

        # Non-Native
        with check_col_2:
            st.checkbox(t['non_native'], key=f'item1_check_non_native_{i}')

        # Desired/Not Desired (Radio butonu gibi çalışması için Desired ve Not Desired aynı anda seçilirse Desired kazanır)
        with check_col_3:
            # Desired (İstiyorum)
            is_desired = st.checkbox(t['desired'], key=f'item1_check_desired_{i}')
            # Not Desired (İstemiyorum)
            # Eğer desired seçili ise Not Desired disable edilsin
            st.checkbox(t['not_desired'], key=f'item1_check_not_desired_{i}', disabled=is_desired)
            
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

    for i in range(6):
        st.markdown('<div class="affix-group">', unsafe_allow_html=True) 
        
        # Sütun düzeni: Input, Checkboxlar (3 adet), Tooltip (Modifer Type için)
        input_col, check_col_1, check_col_2, check_col_3, type_tip_col = st.columns([2, 1, 1, 1, 0.2])
        
        # INPUT
        with input_col:
            st.text_input(labels[i], key=f'item2_input_{i}', value=st.session_state.get(f'item2_input_{i}',''), label_visibility="visible")
        
        # CHECKBOXLAR
        # Exclusive
        with check_col_1:
            st.checkbox(t['exclusive'], key=f'item2_check_exclusive_{i}')

        # Non-Native
        with check_col_2:
            st.checkbox(t['non_native'], key=f'item2_check_non_native_{i}')

        # Desired/Not Desired
        with check_col_3:
            # Desired (İstiyorum)
            is_desired = st.checkbox(t['desired'], key=f'item2_check_desired_{i}')
            # Not Desired (İstemiyorum)
            st.checkbox(t['not_desired'], key=f'item2_check_not_desired_{i}', disabled=is_desired)

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
# Buttons: Calculate and Reset 
# -------------------------
st.write("")
col_calc, col_reset = st.columns([1, 1])

with col_calc:
    if st.button(t['calculate'], type="primary"):
        prob, error = calculate_combined_probability()
        if error:
            st.markdown(f'<div class="error-text">⚠️ {error}</div>', unsafe_allow_html=True)
        elif prob is not None:
            st.markdown(f'<div class="result-text">{t["probability"]} {prob*100:.2f}%</div>', unsafe_allow_html=True)

def reset_preserve_language():
    saved_lang = st.session_state.get('language_selector', 'English')
    current_t = translations[saved_lang]
    st.session_state.clear()
    
    # Dil seçimini koru
    st.session_state['language_selector'] = saved_lang
    
    # Tüm diğer state'leri sıfırla
    st.session_state['item1_base_desired'] = False
    st.session_state['item2_base_desired'] = False
    st.session_state['show_paste_item1'] = False
    st.session_state['show_paste_item2'] = False
    st.session_state['item1_paste_area'] = ''
    st.session_state['item2_paste_area'] = ''
    
    for i in range(6):
        st.session_state[f'item1_input_{i}'] = ''
        st.session_state[f'item2_input_{i}'] = ''
        
        # Checkbox state'lerini False yap
        st.session_state[f'item1_check_exclusive_{i}'] = False
        st.session_state[f'item2_check_exclusive_{i}'] = False
        st.session_state[f'item1_check_non_native_{i}'] = False
        st.session_state[f'item2_check_non_native_{i}'] = False
        st.session_state[f'item1_check_desired_{i}'] = False
        st.session_state[f'item2_check_desired_{i}'] = False
        st.session_state[f'item1_check_not_desired_{i}'] = False
        st.session_state[f'item2_check_not_desired_{i}'] = False

    safe_rerun()

with col_reset:
    if st.button(t['reset'], type="secondary"):
        reset_preserve_language()
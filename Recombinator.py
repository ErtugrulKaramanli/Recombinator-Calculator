import streamlit as st
from math import comb
from itertools import combinations
import re 
from collections import Counter

# -------------------------
# Translation Data (Basit İngilizce/Türkçe çevirileri)
# -------------------------
translations = {
    "en": {
        "title": "PoE Recombinator Probability Calculator",
        "item1_header": "Item 1 Modifiers (Source 1)",
        "item2_header": "Item 2 Modifiers (Source 2)",
        "desired_mods_header": "Desired Modifiers (One per line)",
        "not_desired_mods_header": "Not Desired Modifiers (One per line)",
        "result_header": "Calculation Result 📊",
        "enter_mods": "Enter modifiers (e.g., 't1 crit', 't2 life') one per line.",
        "calculate_button": "Calculate Probability",
        "reset_button": "Reset All",
        "prob_text": "Probability of getting **all desired** mods (and **no undesired** mods) is: **{prob:.2f}%**",
        "base_text": "Base Item Preference:",
        "base1_only": "Base 1 Only",
        "base2_only": "Base 2 Only",
        "anybase": "Any Base (50/50)",
        "mods_note": "Prefixes (P) and Suffixes (S) are assumed non-native unless specified.",
        "error_parse": "Error parsing mods. Ensure format is correct (e.g., 't1 crit', 'p t1 life').",
        "error_desired": "Desired mods must be unique.",
        "error_overlap": "Desired and Not Desired mods overlap: {overlap}",
    },
    "tr": {
        "title": "PoE Recombinator Olasılık Hesaplayıcısı",
        "item1_header": "Eşya 1 Modları (Kaynak 1)",
        "item2_header": "Eşya 2 Modları (Kaynak 2)",
        "desired_mods_header": "İstenen Modlar (Her satıra bir tane)",
        "not_desired_mods_header": "İstenmeyen Modlar (Her satıra bir tane)",
        "result_header": "Hesaplama Sonucu 📊",
        "enter_mods": "Modları girin (örn: 't1 crit', 't2 life'). Her satıra bir tane.",
        "calculate_button": "Olasılığı Hesapla",
        "reset_button": "Tümünü Sıfırla",
        "prob_text": "Tüm **istenen** modları (ve **istenmeyen** modların **hiçbirini** almama) olasılığı: **{prob:.2f}%%**",
        "base_text": "Temel Eşya Tercihi:",
        "base1_only": "Sadece Temel Eşya 1",
        "base2_only": "Sadece Temel Eşya 2",
        "anybase": "Herhangi Bir Temel Eşya (50/50)",
        "mods_note": "Prefixler (P) ve Suffixler (S) belirtilmedikçe Non-Native (Yerel Olmayan) varsayılır.",
        "error_parse": "Modlar ayrıştırılırken hata oluştu. Biçimin doğru olduğundan emin olun (örn: 't1 crit', 'p t1 life').",
        "error_desired": "İstenen modlar benzersiz olmalıdır.",
        "error_overlap": "İstenen ve İstenmeyen modlar çakışıyor: {overlap}",
    },
}

# -------------------------
# Helper Functions
# -------------------------

def get_translation(key):
    lang = st.session_state.get('language', 'tr')
    return translations[lang].get(key, translations['en'][key])

def parse_item_text(item_text, item_num):
    """
    Kullanıcı girdisini mod listesine dönüştürür.
    Her mod: {'mod': 'mod_name', 'item': item_num, 'non_native': True/False}
    Non-Native: Prefix veya Suffix olarak belirtilmemişse Non-Native kabul edilir.
    """
    mods = []
    lines = [line.strip().lower() for line in item_text.split('\n') if line.strip()]
    
    for line in lines:
        match = re.match(r"^(p|s)\s+(.*)$", line)
        
        if match:
            # Örn: "p t1 life" -> non_native: False
            mod_name = match.group(2).strip()
            non_native = False
        else:
            # Örn: "t1 life" -> non_native: True
            mod_name = line
            non_native = True

        if mod_name:
            mods.append({
                'mod': mod_name,
                'item': item_num,
                'non_native': non_native
            })
    return mods

def get_count_probabilities(count):
    """
    Toplam mod sayısına (duplicates dahil) göre seçilecek mod sayısını döndürür.
    Bu tablo, oyun içi mekaniği yansıtır (total_count -> outcome_count).
    """
    if count == 0: return {0: 1.0}
    if count == 1: return {0: 0.41, 1: 0.59}
    if count == 2: return {1: 0.667, 2: 0.333}
    if count == 3: return {1: 0.50, 2: 0.40, 3: 0.10}
    if count == 4: return {1: 0.10, 2: 0.60, 3: 0.30}
    if count == 5: return {2: 0.43, 3: 0.57}
    if count == 6: return {2: 0.30, 3: 0.70}
    return {}

def calculate_selection_probability(all_mods_list, desired_mods, not_desired_mods, outcome_count, winning_base):
    """
    Belirli bir çıkan mod sayısı (outcome_count) ve kazanan base (winning_base) için
    istenen modların gelme olasılığını hesaplar.
    Bu fonksiyonda, kombinasyonlar duplicates içeren havuz üzerinden yapılır ve 
    finalde benzersizlik kontrol edilir.
    """
    
    # 1. Seçim Havuzunu Oluşturma (Duplicates dahil ve Non-Native'ler hariç)
    selection_pool = []
    
    for mod_info in all_mods_list:
        # Non-Native Kontrolü: Yalnızca kazanan base'de bulunan non-native modlar seçime girer.
        if mod_info['non_native'] and mod_info['item'] != winning_base:
            continue
        selection_pool.append(mod_info['mod']) # Mod adını ekle (Duplicates dahil)
        
    # 2. İstenmeyen Mod Kontrolü: İstenmeyen modlar, seçim havuzundan kaldırılır.
    filtered_pool = [mod for mod in selection_pool if mod not in not_desired_mods]
    
    # İstenen mod sayısı çıkan mod sayısından fazlaysa, başarı imkansızdır.
    if len(desired_mods) > outcome_count:
        return 0.0

    # Havuzda istenen modların tamamı benzersiz olarak bulunmuyorsa, başarı imkansızdır.
    if not desired_mods.issubset(set(filtered_pool)):
        return 0.0

    # Toplam mod havuzu sayısı, çıkan mod sayısından azsa imkansız.
    if len(filtered_pool) < outcome_count:
        return 0.0

    # 3. Kombinasyon Hesaplaması:

    # Toplam Olası Kombinasyon (Payda):
    # Filterelenmiş havuzdan (tekrar edenler dahil) çıkan mod sayısı kadar seçim.
    # Bu, 'itertools.combinations' ile hesaplanır.
    # NOT: Aynı mod isimleri farklı itemlerden gelse bile distinct olarak sayılır.
    
    # Counter kullanımı, kombinasyonları hesaplarken aynı isimli öğelerin
    # farklı kaynaklardan gelmesini doğru şekilde ele almak için gereklidir.
    
    # Eğer outcome_count ve len(filtered_pool) küçükse, combinations listesi oluşturulabilir.
    # Büyük sayılar için daha karmaşık hesaplama gerekir.
    
    total_combinations = list(combinations(filtered_pool, outcome_count))
    if not total_combinations:
        return 0.0
    
    total_combinations_count = len(total_combinations)
    
    # Başarılı Kombinasyon (Pay):
    favorable_combinations_count = 0
    
    # Filterelenmiş havuzdan (tekrar edenler dahil) outcome_count kadar tüm kombinasyonları dene.
    for combo in total_combinations:
        # Seçilen modların benzersiz (deduplicated) hali
        final_mods = set(combo)
        
        # Seçilen modlar, istenen modların tamamını içeriyor mu?
        if desired_mods.issubset(final_mods):
            favorable_combinations_count += 1
            
    # Sonuç: (Favorable Kombinasyonlar) / (Total Kombinasyonlar)
    return favorable_combinations_count / total_combinations_count

def calculate_modifier_probability(mods_item1, mods_item2, desired_mods, not_desired_mods, base_preference):
    """
    Ana olasılık hesaplama fonksiyonu.
    """
    
    all_mods_list = mods_item1 + mods_item2
    
    # 1. Toplam Mod Sayısını Al (Duplicates dahil)
    total_count = len(all_mods_list)
    
    if total_count == 0: 
        return 0.0 if len(desired_mods) > 0 else 1.0 
    
    # Olasılık tablosunu toplam mod sayısına göre çek:
    count_probs = get_count_probabilities(total_count)
    
    total_prob = 0.0
    
    # 2. Her bir çıkan mod sayısı (outcome_count) için döngü
    for outcome_count, count_prob in count_probs.items():
        if outcome_count == 0:
            # 0 mod gelmesi durumunda, eğer desired mod yoksa, bu da başarılıdır.
            if len(desired_mods) == 0:
                 total_prob += count_prob
            continue
        
        # 3. Base seçimi ve selection_prob hesaplaması
        
        prob_base1 = 0.0
        prob_base2 = 0.0
        
        # Base 1 kazanma olasılığı
        if base_preference in ["Base1Only", "AnyBase"]:
            prob_base1 = calculate_selection_probability(all_mods_list, desired_mods, not_desired_mods, outcome_count, 1)
        
        # Base 2 kazanma olasılığı
        if base_preference in ["Base2Only", "AnyBase"]:
            prob_base2 = calculate_selection_probability(all_mods_list, desired_mods, not_desired_mods, outcome_count, 2)
        
        # Final Selection Probability
        if base_preference == "Base1Only":
            selection_prob = prob_base1
        elif base_preference == "Base2Only":
            selection_prob = prob_base2
        else: # AnyBase (50/50 şans)
            selection_prob = (prob_base1 + prob_base2) / 2.0
            
        total_prob += count_prob * selection_prob
    
    return total_prob

# -------------------------
# Streamlit UI
# -------------------------

# Session State Initialization
if 'language' not in st.session_state:
    st.session_state.language = 'tr'
if 'base_preference' not in st.session_state:
    st.session_state.base_preference = 'AnyBase'

def handle_base_change():
    st.session_state.base_preference = st.session_state.base_select

def safe_rerun():
    # Streamlit'in beklenmedik yeniden çalıştırmalarını önlemek için boş bir fonksiyon
    pass

def reset_preserve_language():
    # Sadece girdileri sıfırlar, dil ayarını korur
    st.session_state.item1_mods = ""
    st.session_state.item2_mods = ""
    st.session_state.desired_mods = ""
    st.session_state.not_desired_mods = ""
    st.session_state.result_prob = None
    st.session_state.base_preference = 'AnyBase'
    st.experimental_rerun()

## UI: Language Selector and Title
st.set_page_config(layout="wide")

col_lang, col_title = st.columns([1, 6])
with col_lang:
    if st.button("English") and st.session_state.language != 'en':
        st.session_state.language = 'en'
        st.experimental_rerun()
    if st.button("Türkçe") and st.session_state.language != 'tr':
        st.session_state.language = 'tr'
        st.experimental_rerun()

st.title(get_translation("title"))

st.markdown("---")

## Mod Girdileri

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader(get_translation("item1_header"))
    st.text_area(
        get_translation("enter_mods"),
        key="item1_mods",
        height=150,
        placeholder="p t1 life\ns t2 res\nt1 crit"
    )

with col2:
    st.subheader(get_translation("item2_header"))
    st.text_area(
        get_translation("enter_mods"),
        key="item2_mods",
        height=150,
        placeholder="p t1 mana\ns t1 crit\nt2 life"
    )

with col3:
    st.subheader(get_translation("desired_mods_header"))
    st.text_area(
        "t1 life\nt1 crit",
        key="desired_mods",
        height=150,
        help=get_translation("mods_note")
    )
    
    st.subheader(get_translation("not_desired_mods_header"))
    st.text_area(
        "t2 res\nt1 mana",
        key="not_desired_mods",
        height=150
    )

st.markdown("---")

## ⚙️ Base Tercihi ve Hesaplama

col_base, col_buttons = st.columns([2, 1])

with col_base:
    st.write(get_translation("base_text"))
    st.radio(
        "", 
        options=["AnyBase", "Base1Only", "Base2Only"],
        format_func=lambda x: translations[st.session_state.language][x.lower().replace("1", "1_").replace("2", "2_")],
        key="base_select",
        on_change=handle_base_change,
        horizontal=True
    )
    
with col_buttons:
    if st.button(get_translation("calculate_button"), type="primary"):
        try:
            # 1. Modları Ayrıştırma
            mods_item1 = parse_item_text(st.session_state.item1_mods, 1)
            mods_item2 = parse_item_text(st.session_state.item2_mods, 2)
            
            desired_mods_list = [m.strip().lower() for m in st.session_state.desired_mods.split('\n') if m.strip()]
            not_desired_mods_list = [m.strip().lower() for m in st.session_state.not_desired_mods.split('\n') if m.strip()]
            
            desired_mods_set = set(desired_mods_list)
            not_desired_mods_set = set(not_desired_mods_list)
            
            # 2. Hata Kontrolü
            if len(desired_mods_list) != len(desired_mods_set):
                st.error(get_translation("error_desired"))
                st.session_state.result_prob = None
            
            overlap = desired_mods_set.intersection(not_desired_mods_set)
            if overlap:
                st.error(get_translation("error_overlap").format(overlap=", ".join(overlap)))
                st.session_state.result_prob = None
                
            # 3. Hesaplama
            if not overlap and len(desired_mods_list) == len(desired_mods_set):
                probability = calculate_modifier_probability(
                    mods_item1, 
                    mods_item2, 
                    desired_mods_set, 
                    not_desired_mods_set, 
                    st.session_state.base_preference
                )
                st.session_state.result_prob = probability
                
        except Exception as e:
            st.error(get_translation("error_parse"))
            # st.exception(e) # Debugging için açılabilir
            st.session_state.result_prob = None

    if st.button(get_translation("reset_button")):
        reset_preserve_language()

st.markdown("---")

## Hesaplama Sonucu

if st.session_state.get('result_prob') is not None:
    prob = st.session_state.result_prob * 100
    st.success(get_translation("result_header"))
    st.markdown(get_translation("prob_text").format(prob=prob))
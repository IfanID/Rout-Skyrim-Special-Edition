#!/usr/bin/env python3
"""
Skyrim Strings Translator v7.5 — CLEAN SPINNER + CHECKPOINT INFO + FILTER INTEGRATION
Translate source.txt ke Bahasa Indonesia.

Features:
- BACKGROUND SAVE: Auto-save setiap 10 detik (anti-lag)
- ATOMIC WRITE: Anti-corrupt saat mati lampu / Ctrl+C
- BATCH 100: Cepat + Auto-Fallback ke 50/25/1 jika limit, lalu naik balik otomatis
- Resume otomatis dari checkpoint terakhir
- ANIMASI LOADING: Spinner + overall progress + elapsed time (TANPA progress bar batch)
- INFO CHECKPOINT LENGKAP saat Ctrl+C
- PROPER NOUN: Menggabungkan daftar dari filters/npc.py, items.py, armor.py, jewelry.py

Usage:
  python translate.py                                            # Default paths
  python translate.py output/source.txt output/translated.txt   # Custom paths
"""

import sys
import re
import time
import json
import os
import threading
from deep_translator import GoogleTranslator

# ============================================
# Tambahkan path ke subfolder filters
# ============================================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FILTERS_DIR = os.path.join(SCRIPT_DIR, 'filters')
if os.path.exists(FILTERS_DIR):
    sys.path.insert(0, FILTERS_DIR)

# ============================================
# DEFAULT PATHS
# ============================================
DEFAULT_INPUT = "output/source.txt"
DEFAULT_OUTPUT = "output/source_translated.txt"
CHECKPOINT_DIR = "cache"
CHECKPOINT_FILE = "source_checkpoint.json"

# ============================================
# DAFTAR PROPER NOUN SKYRIM (MANUAL + DARI FILTER)
# ============================================
# Daftar manual awal
BASE_PROPER_NOUNS = [
    "Whiterun", "Dragonsreach", "Windhelm", "Solitude", "Markarth",
    "Riften", "Falkreath", "Morthal", "Dawnstar", "Winterhold",
    "Helgen", "Riverwood", "Rorikstead", "Ivarstead", "Kynesgrove",
    "Mixwater Mill", "Darkwater Crossing", "Shor's Stone",
    "Karthwasten", "Kolskeggr Mine", "Left Hand Mine",
    "Fort Greymoor", "Fort Dunstad", "Fort Kastav",
    "Bleak Falls Barrow", "Dustman's Cairn", "Saarthal",
    "Labyrinthian", "Ustengrav", "Forelhost", "Valthume",
    "Volunruud", "Korvanjund", "High Hrothgar", "Throat of the World",
    "Skuldafn", "Sovngarde", "Sky Haven Temple", "Alftand",
    "Blackreach", "Dwemer Museum", "Nchuand-Zel",
    "Dwemer Ruins", "Bromjunaar Sanctuary",
    "Alduin", "Paarthurnax", "Odahviing", "Durnehviir",
    "Ulfric Stormcloak", "General Tullius", "Elisif",
    "Jarl Balgruuf", "Irileth", "Proventus",
    "Farengar Secret-Fire", "Farengar",
    "Lydia", "Serana", "Delphine", "Esbern",
    "Brynjolf", "Mercer Frey", "Karliah",
    "Arngeir", "Einarth", "Borri", "Wulfgar",
    "Savos Aren", "Ancano", "Mirabelle Ervine",
    "Enthir", "Sergius Turrianus", "Urag gro-Shub",
    "Vilkas", "Farkas", "Aela the Huntress", "Aela",
    "Kodlak Whitemane", "Kodlak",
    "Maven Black-Briar", "Maven",
    "Astrid", "Babette", "Veezara", "Nazir",
    "Cicero", "Night Mother",
    "Galmar Stone-Fist", "Galmar",
    "Legate Rikke", "Rikke",
    "Miraak", "Neloth", "Frea", "Storn",
    "Hermaeus Mora", "Azura", "Boethiah", "Clavicus Vile",
    "Hircine", "Malacath", "Mehrunes Dagon", "Meridia",
    "Molag Bal", "Namira", "Nocturnal", "Peryite",
    "Sanguine", "Sheogorath", "Vaermina",
    "Nord", "Imperial", "Redguard", "Breton",
    "Altmer", "Bosmer", "Dunmer", "Orsimer", "Khajiit", "Argonian",
    "Falmer", "Dwemer", "Daedra", "Dremora",
    "Companions", "Thieves Guild", "Dark Brotherhood",
    "College of Winterhold", "Stormcloaks", "Imperial Legion",
    "Blades", "Greybeards", "Dawnguard", "Volkihar",
    "Vigilants of Stendarr", "Vigilants",
    "Silver Hand", "Forsworn",
    "Dragonborn", "Dovahkiin", "Harbinger", "Arch-Mage",
    "Guild Master", "Listener", "Nightingale",
    "Fus Ro Dah", "Wuld Nah Kest", "Yol Toor Shul",
    "Zul Mey Gut", "Lok Vah Koor",
    "Ebony Blade", "Mace of Molag Bal", "Wabbajack",
    "Sanguine Rose", "Skull of Corruption", "Ring of Namira",
    "Oghma Infinium", "Rueful Axe", "Savior's Hide",
    "Masque of Clavicus Vile", "Spellbreaker", "Volendrung",
    "Dawnbreaker", "Mehrunes' Razor",
    "Skeleton Key", "Thieves Guild Armor",
    "Ancient Nord Armor", "Dragonscale Armor",
    "Daedric Armor", "Nightingale Armor",
    "Daedric", "Ebony", "Elven", "Dwarven", "Orcish",
    "Glass", "Dragonscale", "Dragonbone",
    "Ancient Nord", "Steel", "Iron", "Leather", "Hide",
    "Falmer", "Stalhrim",
    "Skooma", "Moon Sugar", "Canis Root", "Jarrin Root",
    "Crimson Nirnroot", "Nirnroot",
    "Tamriel", "Skyrim", "Cyrodiil", "Morrowind", "Hammerfell",
    "High Rock", "Valenwood", "Elsweyr", "Black Marsh",
    "Summerset Isles", "Oblivion", "Aetherius", "Mundus",
    "Sovngarde", "Apocrypha",
    "Divines", "Aedra", "Nine Divines", "Talos",
    "Akatosh", "Arkay", "Dibella", "Julianos",
    "Kynareth", "Mara", "Stendarr", "Zenithar",
    "Dawnguard", "Hearthfire", "Dragonborn",
    "Solstheim", "Castle Volkihar", "Fort Dawnguard",
    "Tel Mithryn",
]

# Muat daftar dari filters/ (jika ada)
filter_names = []
try:
    from npc import NPC_NAMES
    filter_names.extend(NPC_NAMES)
except ImportError:
    pass
try:
    from items import ITEM_NAMES
    filter_names.extend(ITEM_NAMES)
except ImportError:
    pass
try:
    from armor import ARMOR_NAMES
    filter_names.extend(ARMOR_NAMES)
except ImportError:
    pass
try:
    from jewelry import JEWELRY_NAMES
    filter_names.extend(JEWELRY_NAMES)
except ImportError:
    pass

# Gabungkan dengan manual, hilangkan duplikat, urutkan dari terpanjang
combined = set(BASE_PROPER_NOUNS) | set(filter_names)
SKYRIM_PROPER_NOUNS = sorted(combined, key=len, reverse=True)

# Tampilkan info
print(f"ℹ️  Memuat proper noun dari filters/...")
print(f"   Total proper noun: {len(SKYRIM_PROPER_NOUNS):,} kata")

# ============================================
# Fungsi proteksi
# ============================================
def protect_proper_nouns(text):
    found = []
    modified = text
    for noun in SKYRIM_PROPER_NOUNS:
        pattern = r'\b' + re.escape(noun) + r'\b'
        if re.search(pattern, modified):
            idx = len(found)
            found.append(noun)
            modified = re.sub(pattern, f'[[PN{idx}]]', modified)
    return modified, found

def restore_proper_nouns(text, nouns):
    for i, noun in enumerate(nouns):
        text = re.sub(r'\[\[PN' + str(i) + r'\]\]', noun, text)
    return text

# ============================================
# Parser, Checkpoint, dan lainnya (tidak berubah)
# ============================================
def parse_source_file(file_path):
    entries = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"❌ Error membaca file: {e}")
        return entries
    
    blocks = content.split('\n-\n')
    for block in blocks:
        block = block.strip()
        if not block or block == '-':
            continue
        lines = block.split('\n')
        entry = {}
        for line in lines:
            line = line.strip()
            if line.startswith('sID='):
                match = re.search(r'sID="([^"]*)"', line)
                if match: entry['sid'] = match.group(1)
            elif line.startswith('<REC>'):
                match = re.search(r'<REC>([^<]*)</REC>', line)
                if match: entry['rec'] = match.group(1).strip()
            elif line.startswith('<Source>'):
                match = re.search(r'<Source>(.*?)</Source>', line)
                if match: entry['source'] = match.group(1)
            elif line.startswith('<Dest>'):
                match = re.search(r'<Dest>(.*?)</Dest>', line)
                if match: entry['dest'] = match.group(1)
        if all(k in entry for k in ['sid', 'rec', 'source', 'dest']):
            entries.append(entry)
    return entries

def load_checkpoint(checkpoint_file):
    if not os.path.exists(checkpoint_file): return None
    try:
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"⚠️  Warning: Gagal load checkpoint: {e}")
        return None

def atomic_save_checkpoint(data, checkpoint_file):
    temp_file = checkpoint_file + ".tmp"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(temp_file, checkpoint_file)
    except Exception:
        pass

def background_auto_saver(translated_entries, checkpoint_file, stop_event):
    while not stop_event.is_set():
        time.sleep(10)
        if len(translated_entries) > 0:
            atomic_save_checkpoint(translated_entries, checkpoint_file)
    if len(translated_entries) > 0:
        atomic_save_checkpoint(translated_entries, checkpoint_file)

class Spinner:
    def __init__(self):
        self.spinner_chars = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
        self.idx = 0
        self.running = False
        self.thread = None
        self.last_line_len = 0
        self.batch_size = 0
        self.overall_progress = 0
        self.batch_start_time = 0
    
    def _spin(self):
        while self.running:
            spin_char = self.spinner_chars[self.idx % len(self.spinner_chars)]
            elapsed = time.time() - self.batch_start_time
            line = f"\r  {spin_char} Menerjemahkan {self.batch_size} string | Overall: {self.overall_progress:.1f}% | ⏱ {elapsed:.0f}s"
            sys.stdout.write('\r' + ' ' * self.last_line_len + '\r')
            sys.stdout.write(line)
            sys.stdout.flush()
            self.last_line_len = len(line)
            self.idx += 1
            time.sleep(0.1)
    
    def start(self, batch_size, overall_progress):
        self.batch_size = batch_size
        self.overall_progress = overall_progress
        self.batch_start_time = time.time()
        self.running = True
        self.thread = threading.Thread(target=self._spin)
        self.thread.daemon = True
        self.thread.start()
    
    def stop(self, message=None):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.3)
        sys.stdout.write('\r' + ' ' * self.last_line_len + '\r')
        if message:
            sys.stdout.write(message + '\n')
        sys.stdout.flush()
        self.last_line_len = 0

def format_time(seconds):
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        m, s = divmod(seconds, 60)
        return f"{int(m)}m {int(s)}s"
    else:
        h, r = divmod(seconds, 3600)
        m, s = divmod(r, 60)
        return f"{int(h)}h {int(m)}m {int(s)}s"

# ============================================
# MAIN
# ============================================
def main():
    if len(sys.argv) == 1:
        input_file = DEFAULT_INPUT
        output_file = DEFAULT_OUTPUT
        print("ℹ️  Menggunakan path default:")
        print(f"   Input  : {input_file}")
        print(f"   Output : {output_file}")
        print()
    elif len(sys.argv) == 3:
        input_file = sys.argv[1]
        output_file = sys.argv[2]
    else:
        print("Usage:")
        print("  python translate.py                                        # Default paths")
        print("  python translate.py <source.txt> <source_translated.txt>   # Custom paths")
        print()
        sys.exit(1)
    
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    checkpoint_file = os.path.join(CHECKPOINT_DIR, CHECKPOINT_FILE)
    
    if not os.path.exists(input_file):
        print(f"❌ File tidak ditemukan: {input_file}")
        sys.exit(1)
    
    print(f"📖 Membaca: {input_file}")
    entries = parse_source_file(input_file)
    if not entries:
        print("❌ Tidak ada entries yang valid di source.txt")
        sys.exit(1)
    print(f"✓ Loaded {len(entries):,} entries")
    
    translated_entries = load_checkpoint(checkpoint_file)
    start_idx = 0
    if translated_entries:
        start_idx = len(translated_entries)
        print(f"📌 Checkpoint ditemukan: {start_idx:,} entries sudah diterjemahkan")
        print(f"🔄 Resume dari entry {start_idx + 1}")
        print(f"⏳ Sisa: {len(entries) - start_idx:,} entries")
    else:
        print("🆕 Tidak ada checkpoint, mulai dari awal")
        translated_entries = []
    
    print()
    print("=" * 80)
    print("  SKYRIM STRINGS TRANSLATOR v7.5 (dengan filter NPC/Item/Armor/Jewelry)")
    print("=" * 80)
    print(f"  Total entries          : {len(entries):,}")
    print(f"  Sudah diterjemahkan    : {start_idx:,}")
    print(f"  Sisa                   : {len(entries) - start_idx:,}")
    print(f"  Proper noun protection : {len(SKYRIM_PROPER_NOUNS):,} kata (termasuk dari filters/)")
    print(f"  Animasi loading        : AKTIF")
    print("-" * 80)
    print()
    
    stop_event = threading.Event()
    saver_thread = threading.Thread(
        target=background_auto_saver,
        args=(translated_entries, checkpoint_file, stop_event),
        daemon=True
    )
    saver_thread.start()
    
    translator = GoogleTranslator(source='auto', target='id')
    BATCH_MAX_SIZE = 100
    stats = {'total': len(entries), 'translated': start_idx}
    idx = start_idx
    current_batch_size = BATCH_MAX_SIZE
    batch_number = 0
    start_time = time.time()
    spinner = Spinner()
    
    try:
        while idx < len(entries):
            batch = entries[idx : idx + current_batch_size]
            batch_texts = []
            batch_nouns = []
            for entry in batch:
                source = entry['source']
                protected, nouns = protect_proper_nouns(source)
                batch_texts.append(protected)
                batch_nouns.append(nouns)
            
            batch_number += 1
            overall_pct = (idx / len(entries)) * 100
            print(f"\n┌─ BATCH #{batch_number} ──────────────────────────────────────────────┐")
            print(f"│  Ukuran batch : {current_batch_size} string")
            print(f"│  Range        : Entry {idx + 1} - {min(idx + current_batch_size, len(entries)):,}")
            print(f"│  Progress     : {stats['translated']}/{len(entries):,} ({overall_pct:.1f}%)")
            elapsed = time.time() - start_time
            if stats['translated'] > start_idx:
                entries_done = stats['translated'] - start_idx
                rate = entries_done / elapsed
                remaining = (len(entries) - stats['translated']) / rate if rate > 0 else 0
                print(f"│  Kecepatan    : {rate:.1f} string/detik")
                print(f"│  Estimasi     : {format_time(remaining)} lagi")
            print(f"└──────────────────────────────────────────────────────────────────┘")
            
            spinner.start(current_batch_size, overall_pct)
            batch_start_time = time.time()
            
            try:
                if current_batch_size > 1:
                    translated_texts = translator.translate_batch(batch_texts)
                    if not translated_texts or len(translated_texts) != len(batch_texts):
                        raise Exception("Batch result invalid/None")
                else:
                    res = translator.translate(batch_texts[0])
                    translated_texts = [res if res else batch_texts[0]]
                
                batch_elapsed = time.time() - batch_start_time
                spinner.stop(f"  ✅ Batch #{batch_number} selesai dalam {format_time(batch_elapsed)} | {len(batch)} string diterjemahkan")
                
                for i, (entry, translated, nouns) in enumerate(zip(batch, translated_texts, batch_nouns)):
                    if translated is None:
                        translated = batch_texts[i]
                    result = restore_proper_nouns(translated, nouns)
                    entry['dest'] = result
                    translated_entries.append(entry)
                    stats['translated'] += 1
                    
                    current = idx + i + 1
                    progress = (current / len(entries)) * 100
                    src = (entry['source'][:45] + '...') if len(entry['source']) > 45 else entry['source']
                    dst = (result[:45] + '...') if len(result) > 45 else result
                    print(f"[{current:6d}/{len(entries)}] {progress:5.1f}% | {entry['rec']:12s} | {src:50s} → {dst:50s}")
                
                if current_batch_size < BATCH_MAX_SIZE:
                    old_batch = current_batch_size
                    current_batch_size = min(BATCH_MAX_SIZE, current_batch_size * 2)
                    print(f"📈 AUTO-RECOVER: Batch {old_batch} → {current_batch_size} (kecepatan ditingkatkan)")
                
                idx += len(batch)
                time.sleep(0.5)
                
            except Exception as e:
                spinner.stop(f"  ⚠️  Batch #{batch_number} GAGAL ({str(e)[:60]}...)")
                if current_batch_size > 1:
                    old_batch = current_batch_size
                    current_batch_size = max(1, current_batch_size // 2)
                    print(f"📉 AUTO-FALLBACK: Batch {old_batch} → {current_batch_size} (kecepatan diturunkan)")
                    time.sleep(1)
                else:
                    print(f"💡 FALLBACK: Menggunakan teks asli (English) untuk {len(batch)} string")
                    for i, (entry, nouns) in enumerate(zip(batch, batch_nouns)):
                        result = restore_proper_nouns(batch_texts[i], nouns)
                        entry['dest'] = result
                        translated_entries.append(entry)
                        stats['translated'] += 1
                        current = idx + i + 1
                        progress = (current / len(entries)) * 100
                        print(f"[{current:6d}/{len(entries)}] {progress:5.1f}% | FALLBACK (EN) | {entry['source'][:50]}...")
                    idx += len(batch)
                    time.sleep(1)

    except KeyboardInterrupt:
        print("\n")
        print("=" * 80)
        print("  🛑 DIHENTIKAN OLEH USER (Ctrl+C)")
        print("=" * 80)
        if len(translated_entries) > 0:
            atomic_save_checkpoint(translated_entries, checkpoint_file)
            print(f"  💾 Checkpoint tersimpan : {len(translated_entries):,} entries")
            print(f"  📁 Lokasi checkpoint    : {checkpoint_file}")
        print(f"  📊 Progress terakhir    : {stats['translated']:,}/{stats['total']:,} ({stats['translated']/stats['total']*100:.1f}%)")
        print("=" * 80)
        print("  🔄 Jalankan ulang tl.bat untuk melanjutkan")
        print("=" * 80)
        stop_event.set()
        saver_thread.join(timeout=3)
        sys.exit(0)
    
    except Exception as e:
        print(f"\n[!] Fatal Error: {e}")
        if len(translated_entries) > 0:
            atomic_save_checkpoint(translated_entries, checkpoint_file)
            print(f"💾 Checkpoint tersimpan: {len(translated_entries):,} entries")
        stop_event.set()
        saver_thread.join(timeout=3)
        sys.exit(1)
    
    stop_event.set()
    saver_thread.join(timeout=3)
    total_time = time.time() - start_time
    
    print()
    print("=" * 80)
    print(f"  Menulis {len(translated_entries):,} entries hasil terjemahan...")
    print("=" * 80)
    
    output_lines = []
    for entry in translated_entries:
        output_lines.append('-')
        output_lines.append(f'sID="{entry["sid"]}"')
        output_lines.append(f'<REC>{entry["rec"]}</REC>')
        output_lines.append(f'<Source>{entry["source"]}</Source>')
        output_lines.append(f'<Dest>{entry["dest"]}</Dest>')
        output_lines.append('-')
        output_lines.append('')
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(output_lines))
        print(f"✓ File tersimpan: {output_file}")
        if os.path.exists(checkpoint_file):
            os.remove(checkpoint_file)
            print(f"🗑️  Checkpoint dibersihkan (terjemahan selesai)")
    except Exception as e:
        print(f"❌ Error menulis file: {e}")
        sys.exit(1)
    
    print()
    print("=" * 80)
    print("  STATISTIK TERJEMAHAN")
    print("=" * 80)
    print(f"  Total entries          : {stats['total']:,}")
    print(f"  ✓ Diterjemahkan        : {stats['translated']:,}")
    print(f"  ⏱️  Total waktu         : {format_time(total_time)}")
    if stats['translated'] > start_idx:
        entries_done = stats['translated'] - start_idx
        rate = entries_done / total_time if total_time > 0 else 0
        print(f"  ⚡ Kecepatan rata-rata  : {rate:.1f} string/detik")
    print("-" * 80)
    success_rate = (stats['translated'] / stats['total'] * 100) if stats['total'] > 0 else 0
    print(f"  Success rate: {success_rate:.1f}%")
    print("=" * 80)
    print()
    print("  ✓ Langkah selanjutnya: jalankan im.bat untuk import ke XML")
    print("=" * 80)

if __name__ == '__main__':
    main()
import os
import csv
from itertools import combinations
from typing import List, Tuple, Dict

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ConversationHandler,
    filters, ContextTypes
)

# =========================
# KONFIGURASI
# =========================
BOT_TOKEN = os.getenv("BOT_TOKEN") or "8265856945:AAGLtpVtH4RVzBTEfTT4ZK_GI8nD2z8FQN0"
MIN_SUPPORT_1_4 = 0.30
MIN_SUPPORT_5 = 0.35
MIN_CONFIDENCE = 0.80

GROUPS = [
    ("TOTAL",),
    ("JK1", "JK2"),
    ("UMR1", "UMR2", "UMR3", "UMR4", "UMR5"),
    ("PT1", "PT2", "PT3", "PT4"),
    ("FBJ1", "FBJ2", "FBJ3", "FBJ4"),
    ("JJ1", "JJ2", "JJ3", "JJ4"),
    ("PDB1", "PDB2", "PDB3", "PDB4"),
    ("KJO1", "KJO2"),
    ("PJO1", "PJO2"),
    ("ABJ1", "ABJ2", "ABJ3", "ABJ4", "ABJ5"),
]

DETAILED_LABELS = {
    "JK1": "👩 Jumlah Perempuan (JK1): {JK1}",
    "JK2": "👨 Jumlah Laki-Laki (JK2): {JK2}",
    "UMR1": "🎂 Jumlah usia < 20 Tahun (UMR1): {UMR1}",
    "UMR2": "🧑‍💼 Jumlah usia 20-30 Tahun (UMR2): {UMR2}",
    "UMR3": "👨‍👩‍👧‍👦 Jumlah usia 31-40 Tahun (UMR3): {UMR3}",
    "UMR4": "👴 Jumlah usia 41-50 Tahun (UMR4): {UMR4}",
    "UMR5": "👵 Jumlah usia > 50 Tahun (UMR5): {UMR5}",
    "PT1": "📚 Tamatan SD/Sederajat (PT1): {PT1}",
    "PT2": "🏫 Tamatan SMP/Sederajat (PT2): {PT2}",
    "PT3": "🎓 Tamatan SMA/Sederajat (PT3): {PT3}",
    "PT4": "🎓🎓 Tamatan Diploma/Sarjana (PT4): {PT4}",
    "FBJ1": "📅🔥 Frekuensi Bermain Hampir Setiap Hari (FBJ1): {FBJ1}",
    "FBJ2": "📅 Frekuensi Bermain 2-3 kali/minggu (FBJ2): {FBJ2}",
    "FBJ3": "📆 Frekuensi Bermain 1 kali/minggu (FBJ3): {FBJ3}",
    "FBJ4": "⏳ Frekuensi Bermain <1 kali/minggu (FBJ4): {FBJ4}",
    "JJ1": "🎲 Jenis Judi Togel/Lotere Online (JJ1): {JJ1}",
    "JJ2": "⚽ Jenis Judi Taruhan Olahraga (JJ2): {JJ2}",
    "JJ3": "🃏 Jenis Judi Kasino Online (JJ3): {JJ3}",
    "JJ4": "❓ Jenis Judi Lainnya (JJ4): {JJ4}",
    "PDB1": "💸 Pengeluaran < Rp 500Rb (PDB1): {PDB1}",
    "PDB2": "💰 Pengeluaran Rp 500Rb - Rp 2 Jt (PDB2): {PDB2}",
    "PDB3": "💵 Pengeluaran 2 Jt - 5 Jt (PDB3): {PDB3}",
    "PDB4": "🏦 Pengeluaran > Rp 5 Jt (PDB4): {PDB4}",
    "MK1": "❗ Masalah Keuangan YA (MK1): {MK1}",
    "MK2": "✔️ Masalah Keuangan TIDAK (MK2): {MK2}",
    "FB1": "🙅‍♂️ Frekuensi Bertengkar Tidak Pernah (FB1): {FB1}",
    "FB2": "🤏 Frekuensi Bertengkar Jarang 1-2 Kali/bln (FB2): {FB2}",
    "FB3": "🔥 Frekuensi Bertengkar Sering 1-2 Kali/bln (FB3): {FB3}",
    "FB4": "💥 Frekuensi Bertengkar Hampir Setiap Hari (FB4): {FB4}",
    "KJO1": "🎰❗ Kecanduan Judi Online YA (KJO1): {KJO1}",
    "KJO2": "✔️ Kecanduan Judi Online TIDAK (KJO2): {KJO2}",
    "PJO1": "💔 Perceraian YA (PJO1): {PJO1}",
    "PJO2": "💖 Perceraian TIDAK (PJO2): {PJO2}",
    "ABJ1": "🎰 Kecanduan Bermain Judi Online (ABJ1): {ABJ1}",
    "ABJ2": "❗ Masalah Keuangan dalam Pernikahan (ABJ2): {ABJ2}",
    "ABJ3": "🗣️ Pertengkaran/Komunikasi yang Buruk (ABJ3): {ABJ3}",
    "ABJ4": "⚠ Konflik dan Kekerasan dalam Pernikahan (ABJ4): {ABJ4}",
    "ABJ5": "🕵 Ketidakjujuran Pasangan Akibat Judi Online (ABJ5): {ABJ5}",
}




ITEM_LABELS = {
    "JK1": "👩 JK1", "JK2": "👨 JK2",
    "UMR1": "🧒 UMR1", "UMR2": "👦 UMR2", "UMR3": "👧 UMR3", "UMR4": "🧑 UMR4", "UMR5": "🧓 UMR5",
    "PT1": "📚 PT1", "PT2": "📖 PT2", "PT3": "🎓 PT3", "PT4": "🎓 PT4",
    "FBJ1": "🎲 FBJ1", "FBJ2": "🎰 FBJ2", "FBJ3": "🃏 FBJ3", "FBJ4": "🎯 FBJ4",
    "JJ1": "🎴 JJ1", "JJ2": "⚽ JJ2", "JJ3": "🎰 JJ3", "JJ4": "🎲 JJ4",
    "PDB1": "💰 PDB1", "PDB2": "💵 PDB2", "PDB3": "💸 PDB3", "PDB4": "🤑 PDB4",
    "MK1": "❌ MK1", "MK2": "✔ MK2",
    "FB1": "🤝 FB1", "FB2": "🗨 FB2", "FB3": "💢 FB3", "FB4": "🔥 FB4",
    "KJO1": "🎰 KJO1", "KJO2": "✔ KJO2",
    "PJO1": "💔 PJO1", "PJO2": "❤️ PJO2",
    "ABJ1": "🎰 ABJ1", "ABJ2": "💸 ABJ2", "ABJ3": "💢 ABJ3", "ABJ4": "⚠ ABJ4", "ABJ5": "🕵 ABJ5",
}

FIELD_PROMPTS = {k: f"{ITEM_LABELS.get(k, k)} ➡ Masukkan nilai (angka ≥0):" for g in GROUPS for k in g}
ASKING = 1
# =========================
# UTILITAS CSV/TXT
# =========================
def export_rows_to_csv(filename: str, header: List[str], rows: List[List[str]]):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)

def export_text(filename: str, content: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)

# =========================
# VALIDASI INPUT
# =========================
def is_int_nonneg(text: str) -> bool:
    try:
        return int(text) >= 0
    except:
        return False

def validate_group(data: Dict[str, int], group_idx: int) -> Tuple[bool, str]:
    group = GROUPS[group_idx]
    if group == ("TOTAL",):
        return True, ""
    total = data.get("TOTAL", None)
    if total is None:
        return False, "TOTAL belum diisi"
    vals = [data.get(k) for k in group]
    if any(v is None for v in vals):
        return False, "Ada nilai yang belum diisi di grup ini"
    s = sum(vals)

    # ABJ
    if group == GROUPS[-1]:
        pjo1 = data.get("PJO1")
        if pjo1 is None:
            return False, "PJO1 belum diisi"
        if s != pjo1:
            return False, f"❌ ABJ1–ABJ5 harus = PJO1 ({pjo1}), sekarang={s}"
        return True, ""

    # PJO juga total
    if group == GROUPS[8]:
        if s != total:
            return False, f"❌ PJO1+PJO2 harus = TOTAL ({total}), sekarang={s}"
        return True, ""

    if s != total:
        return False, f"❌ Jumlah {', '.join(group)} harus = TOTAL ({total}), sekarang={s}"
    return True, ""

def clear_group(user_data: dict, group_idx: int):
    for k in GROUPS[group_idx]: user_data.pop(k, None)

def group_start_index(group_idx: int) -> int:
    idx = 0
    for i in range(group_idx):
        idx += len(GROUPS[i])
    return idx  
    
# =========================
# FORMAT REKAP
# =========================
def format_rekap_text(data: dict) -> str:
    text = "📊 Rekap Data:\n\n"
    for group in GROUPS:
        for key in group:
            if key in DETAILED_LABELS:
                try:
                    text += DETAILED_LABELS[key].format(**data) + "\n"
                except KeyError:
                    text += f"{key}: Data tidak tersedia\n"
            else:
                text += f"{key}: {data.get(key, 'Data tidak tersedia')}\n"
        text += "\n"  # spasi antar grup
    return text

def rekap_rows_csv(d: Dict[str, int]) -> List[List[str]]:
    rows = []
    for g in GROUPS[1:]:
        for k in g:
            rows.append([ITEM_LABELS[k], str(d.get(k, 0))])
    return rows

# =========================
# APRIORI
# =========================
def one_itemset(data: Dict[str, int], min_support: float) -> List[Tuple[Tuple[str, ...], int, float]]:
    total = data["TOTAL"]
    items = [(k, v) for k, v in data.items() if k != "TOTAL"]
    out = []
    for k, v in items:
        s = v / total if total > 0 else 0
        if s >= min_support:
            out.append(((k,), v, s))
    return out

def k_itemset_from_candidates(data: Dict[str, int], candidates: List[Tuple[str, ...]], min_support: float):
    total = data["TOTAL"]
    out = []
    for combo in candidates:
        freq = min(data[c] for c in combo)
        support = freq / total if total > 0 else 0
        if support >= min_support:
            out.append((combo, freq, support))
    return out

def apriori_generate_candidates(prev_frequents: List[Tuple[str, ...]], k: int):
    prev_sorted = [tuple(sorted(x)) for x in prev_frequents]
    candidates = set()
    for i in range(len(prev_sorted)):
        for j in range(i + 1, len(prev_sorted)):
            a, b = prev_sorted[i], prev_sorted[j]
            if a[:k - 2] == b[:k - 2]:
                new = tuple(sorted(set(a).union(b)))
                if len(new) == k:
                    all_subfreq = True
                    for sub in combinations(new, k - 1):
                        if tuple(sorted(sub)) not in prev_sorted:
                            all_subfreq = False
                            break
                    if all_subfreq:
                        candidates.add(new)
    return sorted(candidates)

def apriori(data: Dict[str, int], k: int) -> List[Tuple[Tuple[str, ...], int, float]]:
    min_support = MIN_SUPPORT_1_4 if k < 5 else MIN_SUPPORT_5
    if k == 1:
        return one_itemset(data, min_support)
    prev = apriori(data, k - 1)
    prev_freq = [x[0] for x in prev]
    candidates = apriori_generate_candidates(prev_freq, k)
    return k_itemset_from_candidates(data, candidates, min_support)


# =========================
# RULE MINING (Pola Asosiasi)
# =========================
def generate_rules(frequent_itemsets: List[Tuple[Tuple[str, ...], int, float]], data: Dict[str, int], target: str) -> List[Tuple[str, str, float, float]]:
    rules = []
    target_count = data.get(target, 0)
    for combo, freq, support in frequent_itemsets:
        if target in combo:
            antecedent = [c for c in combo if c != target]
            if not antecedent:
                continue
            # Minimum transaksi yang mengandung antecedent dihitung sebagai min dari masing-masing item
            ant_count = min(data.get(a, 0) for a in antecedent)
            confidence = freq / ant_count if ant_count > 0 else 0
            if confidence >= MIN_CONFIDENCE:
                rules.append((
                    " + ".join([ITEM_LABELS[a] for a in antecedent]),
                    ITEM_LABELS[target],
                    support,
                    confidence
                ))
    return rules

def interpret_rule(antecedent: str, consequent: str, support: float, confidence: float) -> str:
    return (
        f"📘 Jika seseorang memiliki karakteristik: {antecedent}, maka kemungkinan besar mereka juga memiliki karakteristik {consequent}. "
        f"(Support: {support * 100:.2f}%, Confidence: {confidence * 100:.2f}%)"
    )


# =========================
# HANDLER UTAMA
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Halo! Perintah:\n"
        "/input\n"
        "/rekap\n"
        "/apriori1\n"
        "/apriori2\n"
        "/apriori3\n"
        "/apriori4\n"
        "/apriori5\n"
        "/rules [kode_target]\n"
        "/reset"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("🗑 Data direset. Ketik /input untuk mulai lagi.")

def ensure_data(context: ContextTypes.DEFAULT_TYPE) -> Dict[str, int]:
    d = {k: 0 for g in GROUPS for k in g}
    if "data" in context.user_data:
        for k, v in context.user_data["data"].items():
            d[k] = v
    return d

async def rekap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = ensure_data(context)
    text = format_rekap_text(d)
    await update.message.reply_text(text)

    export_text("rekap.txt", text)
    await update.message.reply_document(open("rekap.txt", "rb"))

    rows = rekap_rows_csv(d)
    export_rows_to_csv("rekap.csv", ["Item", "Jumlah"], rows)
    await update.message.reply_document(open("rekap.csv", "rb"))
    
async def input_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["idx"] = 0
    context.user_data["data"] = {}
    fields = [k for g in GROUPS for k in g]
    await update.message.reply_text("📝 Mulai input data step-by-step.\nKetik angka ≥0")
    await update.message.reply_text(FIELD_PROMPTS[fields[0]])
    return ASKING

async def input_ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if not is_int_nonneg(text):
        await update.message.reply_text("❌ Masukkan angka bulat ≥0!")
        return ASKING

    value = int(text)
    fields = [k for g in GROUPS for k in g]
    idx = context.user_data.get("idx", 0)
    key = fields[idx]
    context.user_data["data"][key] = value

    # Cek apakah masih ada field selanjutnya
    idx += 1
    if idx >= len(fields):
        await update.message.reply_text("✅ Input selesai! Ketik /rekap untuk lihat hasil.")
        return ConversationHandler.END
    else:
        context.user_data["idx"] = idx
        next_key = fields[idx]
        await update.message.reply_text(FIELD_PROMPTS[next_key])
        return ASKING

    # validasi grup
    cumulative = 0
    for gi, g in enumerate(GROUPS):
        if idx < cumulative + len(g):
            group_idx = gi
            in_group_pos = idx - cumulative
            group_len = len(g)
            break
        cumulative += len(g)

    if in_group_pos == group_len - 1:
        ok, msg = validate_group(context.user_data["data"], group_idx)
        if not ok:
            clear_group(context.user_data["data"], group_idx)
            context.user_data["idx"] = group_start_index(group_idx)
            await update.message.reply_text(msg)
            first_key = GROUPS[group_idx][0]
            await update.message.reply_text(FIELD_PROMPTS[first_key])
            return ASKING

    # next
    idx += 1
    context.user_data["idx"] = idx
    if idx >= len(fields):
        await update.message.reply_text("✅ Input selesai. Gunakan /rekap untuk melihat ringkasan")
        return ConversationHandler.END
    next_key = fields[idx]
    await update.message.reply_text(FIELD_PROMPTS[next_key])
    return ASKING

async def input_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Dibatalkan. Ketik /input untuk mulai lagi.")
    return ConversationHandler.END
# =========================
# APRIORI & RULES HANDLER
# =========================

async def apriori_handler(update: Update, context: ContextTypes.DEFAULT_TYPE, k: int):
    d = ensure_data(context)
    rows = []
    freq_itemsets = apriori(d, k)
    for combo, freq, support in freq_itemsets:
        rows.append([
            " + ".join([ITEM_LABELS[c] for c in combo]),
            f"{freq}/{d['TOTAL']} = {support:.2f}"
        ])
    text = "\n".join([f"{r[0]} → {r[1]}" for r in rows[:30]]) or "Tidak ada"
    await update.message.reply_text(f"📊 {k}-Itemset:\n{text}")

    export_rows_to_csv(f"apriori{k}.csv", ["Itemset", "Support"], rows)
    export_text(f"apriori{k}.txt", "\n".join([f"{r[0]} | {r[1]}" for r in rows]))
    await update.message.reply_document(open(f"apriori{k}.csv", "rb"))
    await update.message.reply_document(open(f"apriori{k}.txt", "rb"))

    # Jika k=5, tampilkan rules
    if k == 5:
        rules = generate_rules(freq_itemsets, d, target="PJO1")
        if rules:
            text_rules = "\n".join([
                f"Jika {r[0]} → Maka {r[1]} (Support={r[2]:.2f}, Confidence={r[3]:.2f})\n{interpret_rule(r[0], r[1], r[2], r[3])}"
                for r in rules
            ])
            await update.message.reply_text("📊 Rule Mining (Confidence ≥80%):\n" + text_rules)
        else:
            await update.message.reply_text("📊 Rule Mining: Tidak ditemukan aturan dengan confidence ≥80%.")

# Wrapper command handlers
async def apriori1(update, context): await apriori_handler(update, context, 1)
async def apriori2(update, context): await apriori_handler(update, context, 2)
async def apriori3(update, context): await apriori_handler(update, context, 3)
async def apriori4(update, context): await apriori_handler(update, context, 4)
async def apriori5(update, context): await apriori_handler(update, context, 5)

# Command /rules [target]
async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    d = ensure_data(context)
    args = context.args
    target = args[0].upper() if args else "PJO1"

    if target not in d or target == "TOTAL":
        await update.message.reply_text("❌ Target tidak valid. Contoh: /rules PJO1")
        return

    freq_itemsets = apriori(d, 5)
    rules = generate_rules(freq_itemsets, d, target)

    if not rules:
        await update.message.reply_text(f"📊 Tidak ditemukan aturan asosiasi untuk target {target} dengan confidence ≥80%.")
        return

    # =======================
    # Export ke TXT
    # =======================
    text_rules = "\n\n".join([
        f"Jika {r[0]} → Maka {r[1]} (Support={r[2]:.2f}, Confidence={r[3]:.2f})\n{interpret_rule(r[0], r[1], r[2], r[3])}"
        for r in rules
    ])
    export_text("rules.txt", f"📊 Rules untuk target {ITEM_LABELS.get(target, target)}:\n\n{text_rules}")

    # =======================
    # Export ke CSV
    # =======================
    csv_rows = [[r[0], r[1], f"{r[2]:.4f}", f"{r[3]:.4f}"] for r in rules]
    export_rows_to_csv("rules.csv", ["Antecedent", "Consequent", "Support", "Confidence"], csv_rows)

    # =======================
    # Kirim sebagian ke chat
    # =======================
    preview_rules = rules[:10]  # maksimal 10 aturan ditampilkan langsung
    preview_text = "\n\n".join([
        f"Jika {r[0]} → Maka {r[1]} (Support={r[2]:.2f}, Confidence={r[3]:.2f})"
        for r in preview_rules
    ])
    if len(rules) > 10:
        preview_text += f"\n\n📄 {len(rules) - 10} aturan lainnya ada di file terlampir."

    await update.message.reply_text(f"📊 Aturan Asosiasi untuk {ITEM_LABELS.get(target, target)}:\n\n{preview_text}")

    await update.message.reply_document(open("rules.txt", "rb"))
    await update.message.reply_document(open("rules.csv", "rb"))



# =========================
# MAIN
# =========================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("input", input_start)],
        states={ASKING: [MessageHandler(filters.TEXT & ~filters.COMMAND, input_ask)]},
        fallbacks=[CommandHandler("cancel", input_cancel)],
        name="input_conversation",
        persistent=False
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(conv)
    app.add_handler(CommandHandler("rekap", rekap))
    app.add_handler(CommandHandler("apriori1", apriori1))
    app.add_handler(CommandHandler("apriori2", apriori2))
    app.add_handler(CommandHandler("apriori3", apriori3))
    app.add_handler(CommandHandler("apriori4", apriori4))
    app.add_handler(CommandHandler("apriori5", apriori5))
    app.add_handler(CommandHandler("rules", rules))

    app.run_polling()

if __name__ == "__main__":
    main()

                          

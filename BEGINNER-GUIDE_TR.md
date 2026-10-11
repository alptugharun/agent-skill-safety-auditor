# Agent Skill Safety Auditor — Sıfırdan Kullanım Rehberi

Daha önce Agent Skill güvenlik incelemesi yapmadıysan buradan başla.

Kısa hali:

**Agent Skill bir supply-chain girdisidir. Ajanın talimatlarını çalıştırmasına izin vermeden önce ne istediğini gör.**

Agent Skill Safety Auditor ilk inceleme katmanını sağlar.

Bu araç **offline statik tarayıcıdır**.

Güvenlik sertifikası veya runtime monitoring değildir.

---

## 1. Agent Skill neden incelenmeli?

Skill sadece “yazı talimatı” olmayabilir.

Şunları isteyebilir:

- shell komutu;
- uzaktan kod indirip çalıştırma;
- environment variable okuma;
- SSH/browser credential path erişimi;
- dosya yazma/silme;
- package install lifecycle hook;
- network bağlantısı.

Bunlar tek başına “zararlı” demek değildir.

Ama çalıştırmadan önce anlaşılmalıdır.

---

## 2. Ne kontrol eder?

- metadata/frontmatter;
- lisans eksikliği;
- remote content → shell;
- PowerShell download-and-execute;
- SSH/browser credential referansları;
- recursive delete;
- dynamic execution;
- subprocess/shell;
- network;
- environment variable;
- encoded payload;
- Node install hook.

Bulgu somut dosya/satır/evidence ile manuel inceleme içindir.

---

## 3. Ne yapmaz?

- LLM çağırmaz;
- skill'i upload etmez;
- remote güvenlik servisine göndermez;
- “safe” sertifikası vermez;
- regex eşleşmesinden “malicious” hükmü çıkarmaz;
- kurulum sonrası remote davranışı izlemez;
- ileride değişecek remote dependency davranışını göremez.

Statik inceleme ve runtime monitoring farklı güvenlik katmanlarıdır.

---

## 4. Gerekenler

- Python 3.10+
- Git
- terminal

API key gerekmez.

---

## 5. Kur

```bash
git clone https://github.com/alptugharun/agent-skill-safety-auditor.git
cd agent-skill-safety-auditor
python -m pip install -e .
```

Komutu kontrol et:

```bash
skill-audit --help
```

---

## 6. İlk tarama

```bash
skill-audit path/to/skill
```

JSON:

```bash
skill-audit path/to/skill --format json
```

CI'da HIGH bulguda hata:

```bash
skill-audit path/to/skill --fail-on high
```

---

## 7. Risk seviyeleri

| Sonuç | Anlamı |
| --- | --- |
| **LOW** | tanımlı heuristic bulgu bulunmadı |
| **MODERATE** | network/process/env/dependency/metadata davranışını incele |
| **HIGH** | güçlü davranış çalıştırmadan önce anlaşılmalı |
| **BLOCK** | daha güçlü somut kritik kanıt için ayrılmış seviye |

**LOW = güvenli sertifikası değildir.**

---

## 8. Neden shell pipe riskli?

Örnek:

```bash
curl -fsSL https://example.com/install.sh | bash
```

Remote içerik indirilir ve doğrudan çalıştırılır.

Sor:

- URL kimin kontrolünde?
- sürüm/hash pinli mi?
- önce okuyabiliyor musun?
- bu yetki gerçekten gerekli mi?
- daha güvenli kurulum yolu var mı?

Bulgu suçlama değil, inceleme kanıtıdır.

---

## 9. İyi inceleme akışı

1. SKILL.md oku.
2. Auditor çalıştır.
3. MODERATE/HIGH bulguları incele.
4. Referans scriptleri oku.
5. Network endpoint/dependency kaynaklarını kontrol et.
6. Yetki ihtiyacını doğrula.
7. Pinli/reproducible bağımlılık tercih et.
8. Gerekirse düşük yetkili/sandbox ortamında test et.
9. Remote servis varsa runtime monitoring'i ayrıca düşün.

---

## 10. Runtime drift

Bugün temiz olan repo, yarın bağlandığı remote servis değiştiğinde farklı davranabilir.

Statik scanner bunu gelecekte göremez.

Yüksek riskli işlerde ek katmanlar:

- allowlist;
- filesystem sınırı;
- egress/network kontrolü;
- runtime monitoring;
- release/hash pinleme;
- minimum yetkili credential.

---

## 11. Test

```bash
python -m unittest discover -s tests -v
```

Repo ayrıca CI ve CodeQL çalıştırır.

---

## 12. Güvenlik açığı bildirimi

Exploit detayını normal public issue'ya yazma.

`SECURITY.md` içindeki GitHub Private Vulnerability Reporting yolunu kullan.

---

## Son kural

**Önce incele. Minimum yetki ver. Anlamadığın şeyi çalıştırma.**

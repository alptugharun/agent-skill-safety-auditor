# Agent Skill Safety Auditor

[![English](https://img.shields.io/badge/English-0D1117?style=flat-square)](README.md) [![Türkçe](https://img.shields.io/badge/Türkçe-E30A17?style=flat-square)](README_TR.md)

**Bir Agent Skill'i kurmadan önce ne istediğini gör.**

Agent Skills yalnızca metin değildir. Bir skill; script çalıştırabilir, environment variable okuyabilir, dış servislere bağlanabilir veya beklemediğin dosyalara erişim isteyebilir.

Agent Skill Safety Auditor, bir skill klasörünü **yerel ve offline** olarak inceler. Kodu bir LLM'e göndermez ve tek bir regex eşleşmesi yüzünden projeye "zararlı" etiketi yapıştırmaz.

## Kontrol edilenler

- SKILL.md frontmatter alanları;
- lisans bilgisinin eksikliği;
- uzaktan indirilen içeriğin doğrudan shell'e pipe edilmesi;
- PowerShell download-and-execute kalıpları;
- SSH anahtarı / browser credential path referansları;
- recursive silme komutları;
- dynamic code execution;
- subprocess / shell çalıştırma;
- network erişimi;
- environment-variable okuma;
- encoded payload çözme;
- Node package install lifecycle hook'ları.

## Kurulum

```bash
python -m pip install -e .
```

## Kullanım

```bash
skill-audit path/to/skill
```

JSON çıktısı:

```bash
skill-audit path/to/skill --format json
```

CI içinde yüksek riskte hata döndürmek için:

```bash
skill-audit path/to/skill --fail-on high
```

## Risk seviyeleri

| Seviye | Anlamı |
| --- | --- |
| **LOW** | Tanımlı heuristic kontrollerde bulgu çıkmadı |
| **MODERATE** | Network, process, environment, dependency veya metadata tarafı incelenmeli |
| **HIGH** | Güçlü çalıştırma/yetki davranışı manuel olarak anlaşılmalı |
| **BLOCK** | Gelecekte yalnız somut kritik kanıt için kullanılacak |

Temiz sonuç güvenlik sertifikası değildir. Yıldız sayısı, popülerlik veya geliştirici itibarı da güvenlik garantisi değildir.

Repo içindeki `skill/agent-skill-safety-auditor/SKILL.md` dosyası insan/agent inceleme prosedürünü; Python CLI ise deterministik kontrolleri sağlar.

## Test

```bash
python -m unittest discover -s tests -v
```

**Prensip:** Önce incele. Minimum yetki ver. Anlamadığın şeyi çalıştırma.

Bu proje [AI Social Media Toolkit](https://github.com/alptugharun/ai-social-media-toolkit) içindeki güvenlik çalışmalarından doğdu.

## Lisans

MIT.

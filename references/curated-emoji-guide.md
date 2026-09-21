# Curated emoji selection guide

## Table of contents

- [minimal_navigation](#minimal-navigation)
- [status_alerts](#status-alerts)
- [commerce](#commerce)
- [ai_tech](#ai-tech)
- [news_metrics](#news-metrics)
- [iran_culture](#iran-culture)

47 unique IDs; entries shared across sets refer to the same canonical record. Fallback glyphs below are Unicode alternatives, **not previews of custom artwork**. All are source-mapped; none was live-verified in this audit. Read `usage_notes` from JSON before implementation.

Use `scripts/search_emoji.py --curated SET --format json --limit 50` to retrieve full metadata.

## minimal navigation

Menus, settings, navigation, support and account UI

Style policy: `single_source_family_not_visually_verified`.

| Key / Persian label | ID (string) | Fallback | UI category | Recommended use | Caution |
| --- | --- | --- | --- | --- | --- |
| settings_bw / تنظیمات | `5877260593903177342` | ⚙️ | navigation | Open preferences, language, or notification settings. | Do not use for a completed save. |
| search / جستجو | `5874960879434338403` | 🔍 | navigation | Open search or filter a product, order, or help list. | Keep the search target in the label. |
| copy / کپی | `5877301185639091664` | 📋 | navigation | Copy an order number, address, or reference to the clipboard. | Use only when the implementation actually copies; callbacks alone do not copy. |
| trash / حذف | `5879896690210639947` | 🗑 | navigation | Delete or remove an item from a list. | Keep an explicit delete label and confirm irreversible actions. |
| profile / حساب کاربری | `5879770735999717115` | 👤 | account | Open the user account, profile details, or account preferences. | Does not establish identity verification. |
| support / پشتیبانی | `5884510167986343350` | 💬 | support | Open help, support chat, or a contact-support action. | Distinguish human support from an AI assistant in the label. |
| link_bw / پیوند | `5877465816030515018` | 🔗 | navigation | Open a related website, document, or external resource. | Show the destination clearly for sensitive actions. |
| back / بازگشت | `5875082500023258804` | ↩️ | navigation | Return to the parent menu or previous view. | Keep the Persian label; do not infer RTL direction from artwork. |
| forward / بعدی | `5877468380125990242` | ↗️ | navigation | Continue to the next view or open the next step. | Its source fallback is an up-right arrow; do not claim it is an RTL arrow. |
| updates / به‌روزرسانی | `5877410604225924969` | 🔄 | navigation | Refresh displayed data or open an updates view. | Label refresh separately from a software upgrade. |
| verified / تأییدشده | `5805532930662996322` | ✅ | status | Mark a check that your application has actually completed. | Never imply Telegram verification, official status, or a completed payment without evidence. |

## status alerts

Success, warning, error, notification and verification states

Style policy: `mixed_families_filter_by_style_or_preview`.

| Key / Persian label | ID (string) | Fallback | UI category | Recommended use | Caution |
| --- | --- | --- | --- | --- | --- |
| checkmark / موفق | `5206607081334906820` | ✅ | status | Show successful completion after the operation is confirmed. | A queued request is not a completed operation. |
| warning_yellow / هشدار | `5447644880824181073` | ⚠️ | status | Flag a recoverable issue or an action requiring attention. | Explain the issue in text and retain an accessible label. |
| cross / ناموفق | `5210952531676504517` | ❌ | status | Mark a failed operation, rejected input, or unavailable result. | Keep failure distinct from a destructive delete action. |
| info_bw / اطلاعات | `5879785854284599288` | ℹ️ | status | Introduce explanatory details, help text, or a nonurgent notice. | Use warning for actionable risks. |
| bell / اعلان | `5458603043203327669` | 🔔 | status | Open notifications or mark a new alert. | Do not imply notifications are enabled unless confirmed. |
| verified / تأییدشده | `5805532930662996322` | ✅ | status | Mark a check that your application has actually completed. | Never imply Telegram verification, official status, or a completed payment without evidence. |
| fire / پرطرفدار | `5424972470023104089` | 🔥 | status | Highlight a popular item or a prominent editorial cue. | Popularity must be supported; this is not an error-severity indicator. |

## commerce

Shop, wallet, card, price, discount and checkout surfaces

Style policy: `mixed_families_filter_by_style_or_preview`.

| Key / Persian label | ID (string) | Fallback | UI category | Recommended use | Caution |
| --- | --- | --- | --- | --- | --- |
| wallet / کیف پول | `5769403330761593044` | 👛 | commerce | Open a wallet, balance view, or account-credit history. | Display the actual currency and available balance in text. |
| card / پرداخت | `5927169041595634481` | 💳 | commerce | Open card payment or display a payment-method choice. | The icon is not payment confirmation; use trusted transaction state. |
| magazin / فروشگاه | `5983399041197675256` | 🏪 | commerce | Open the storefront, product catalog, or shop categories. | Keep separate from cart and checkout actions. |
| discount / تخفیف | `5406683434124859552` | 🏷 | commerce | Mark a discount, coupon entry, or an offer label. | State expiry and terms in text; do not imply an unverified discount. |
| dollar / دلار | `5409048419211682843` | 💵 | commerce | Label US-dollar prices or a currency-specific money view. | Do not use as a rial/toman currency symbol; use wallet/card for generic Iranian payments. |
| star / امتیاز | `5438496463044752972` | ⭐ | commerce | Mark a rating, favorite, or featured product. | Do not represent Telegram Stars payments without an explicit Stars label and correct payment flow. |

## ai tech

AI assistants, developer tools and technical bot UI

Style policy: `mixed_families_filter_by_style_or_preview`.

| Key / Persian label | ID (string) | Fallback | UI category | Recommended use | Caution |
| --- | --- | --- | --- | --- | --- |
| bot_ai / دستیار هوشمند | `5931415565955503486` | 🤖 | ai | Open an AI assistant or identify an automated response. | Does not itself indicate an active thinking or streaming state. |
| chatgpt / چت‌جی‌پی‌تی | `5945217417591397712` | 💬 | ai | Identify a ChatGPT-related provider choice or integration. | Use only for the named integration; no endorsement or model-version claim. |
| claude / کلاد | `5945210167686601730` | 🌥 | ai | Identify a Claude-related provider choice or integration. | The stored cloud fallback is source-mapped, not a generic weather instruction. |
| gemini / جمینای | `5944955909917646080` | ♊ | ai | Identify a Gemini-related provider choice or integration. | The zodiac fallback does not establish the rendered brand artwork. |
| github / گیت‌هاب | `4999005636604723783` | 🐙 | developer | Open a GitHub repository, issue, or source-code integration. | Label the target repository or action. |
| python / پایتون | `5260480440971570446` | 💻 | developer | Label Python code, a Python runtime, or a language filter. | Do not infer a runtime version from the icon. |
| docker / داکر | `5301137237050663843` | 👩‍💻 | developer | Label a container image, Docker integration, or container task. | Does not indicate that a deployment is healthy. |
| terminal / ترمینال | `5301233981189005137` | 👩‍💻 | developer | Open command output or identify a shell task. | Distinguish viewing logs from executing commands. |

## news metrics

News, analytics, market/status dashboards

Style policy: `single_source_family_not_visually_verified`.

| Key / Persian label | ID (string) | Fallback | UI category | Recommended use | Caution |
| --- | --- | --- | --- | --- | --- |
| breaking / خبر فوری | `5456140674028019486` | 🚨 | news_metrics | Mark a breaking-news item or a high-priority incident update. | Use only when urgency is justified by the content. |
| urgent / فوری | `5224607267797606837` | ⚡ | news_metrics | Highlight a time-sensitive action or urgent notice. | State the deadline or consequence in text. |
| stats / آمار | `5231200819986047254` | 📊 | news_metrics | Open a statistics summary or metrics dashboard. | Include units and measurement period. |
| chart_up / روند صعودی | `5449683594425410231` | 📈 | news_metrics | Indicate an increase in the displayed metric. | An increase is not automatically good; name the metric and period. |
| chart_down / روند نزولی | `5447183459602669338` | 📉 | news_metrics | Indicate a decrease in the displayed metric. | A decrease is not automatically bad; name the metric and period. |
| announcement / اطلاعیه | `5424818078833715060` | 📢 | news_metrics | Introduce a broadcast update or public announcement. | Keep promotional notices distinct from service incidents. |
| bell / اعلان | `5458603043203327669` | 🔔 | status | Open notifications or mark a new alert. | Do not imply notifications are enabled unless confirmed. |

## iran culture

General source-mapped cultural vocabulary suitable for Persian UI; not proof of Iranian origin or visually verified Nowruz/Yalda artwork

Style policy: `single_source_family_not_visually_verified`.

| Key / Persian label | ID (string) | Fallback | UI category | Recommended use | Caution |
| --- | --- | --- | --- | --- | --- |
| unicode_1F1EE_1F1F7 / ایران | `5271878966347601947` | 🇮🇷 | culture | Label Iran as a country or region selection. | A country flag does not mean Persian language or Iranian authorship. |
| unicode_1F349 / یلدا | `5305336095863485125` | 🍉 | culture | Use a watermelon cue for Yalda greetings or seasonal offers. | Yalda is a project-assigned use case, not a verified pack theme. |
| unicode_1F331 / نوروز | `5449885771420934013` | 🌱 | culture | Use a seedling cue for spring, growth, or Nowruz greetings. | Do not claim the artwork depicts a specific Haft-sin item. |
| unicode_1F337 / لاله | `5404835520150773707` | 🌷 | culture | Use a tulip cue for flowers, gifts, or spring greetings. | Not evidence of an Iranian creator or a Nowruz-specific pack. |
| unicode_1F338 / شکوفه | `5440354006335495210` | 🌸 | culture | Use a blossom cue for spring greetings or seasonal sections. | This is general floral vocabulary suitable for Persian UI. |
| unicode_1FABB / سنبل | `5375282786489880721` | 🪻 | culture | Use a hyacinth cue for a Nowruz or spring greeting. | The cultural association is editorial; preview the actual artwork before branding. |
| unicode_2615_FE0F / نوشیدنی گرم | `5359370246190801956` | ☕️ | culture | Open hot drinks, a cafe menu, or a hospitality greeting. | The fallback does not distinguish tea from coffee; use a clear label. |
| unicode_1F389 / جشن | `5436040291507247633` | 🎉 | culture | Celebrate a milestone, holiday, or completed achievement. | Do not show success before the underlying operation completes. |
| unicode_1F386 / آتش‌بازی | `5431783411981228752` | 🎆 | culture | Decorate a celebration or holiday announcement sparingly. | Not an Iranian-specific asset or a culturally unique symbol. |
| unicode_2764_FE0F / علاقه‌مندی | `5449505950283078474` | ❤️ | culture | Mark favorites, appreciation, or a warm greeting. | Use neutral labels where a heart could be misunderstood. |

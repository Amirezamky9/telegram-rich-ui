# Slideshow and Media (Telegram Bot API 10.3)

Telegram Bot API 10.3 introduces embedded media layout containers within `sendRichMessage`. Instead of requiring disjointed media groups (`sendMediaGroup`) that cannot interleave text, buttons, or structured tables, bots can now embed interactive carousels (`<tg-slideshow>`), multi-image grids (`<tg-collage>`), audio streams, animations, voice notes, and interactive map locations directly within the document flow.

---

## `<tg-slideshow>`: Interactive Media Carousels

The `<tg-slideshow>` container renders an interactive horizontal carousel within the chat bubble. Users can swipe or tap arrow controls to browse through photos and videos without opening full-screen media viewers.

### Slideshow Syntax

```html
<tg-slideshow>
  <img src="https://images.example.com/products/phone-front.jpg" alt="Front View" />
  <img src="https://images.example.com/products/phone-back.jpg" alt="Back View" />
  <video src="https://images.example.com/products/phone-demo.mp4" />
  <figcaption>
    Flagship Titanium Smartphone (2026 Edition)
    <cite>Product Photography by TechStudio</cite>
  </figcaption>
</tg-slideshow>
```

### Slideshow Elements and Mechanics

1. **Slide Media Items:** Contains one or more `<img src="...">` and `<video src="...">` tags. Each tag represents one slide.
2. **Slide Counter & Navigation:** Clients render a `1 / N` position indicator with chevron buttons (`‹` / `›`). On touch devices, horizontal swiping transitions smoothly between items.
3. **Captions and Citations:**
   - `<figcaption>`: Formats descriptive caption text pinned directly beneath the active slide.
   - `<cite>`: Formats muted source attribution, copyright, or photographer credits within the caption.
4. **Mixed Media Support:** Photos and MP4 videos can be combined seamlessly within the same slideshow.

### فارسی — اسلایدشو و ساختار آن
- تگ `<tg-slideshow>` یک گالری ورق‌زدنی (کاروسل) درون متن پیام ایجاد می‌کند.
- کاربر می‌تواند بدون خروج از پیام، با دکمه‌های چپ و راست یا سوایپ لمسی بین عکس‌ها و ویدیوها جابه‌جا شود.
- تگ `<figcaption>` توضیح مشترک اسلایدها و تگ `<cite>` نام عکاس یا منبع را نمایش می‌دهد.
- امکان ترکیب تصویر (`<img>`) و ویدیو (`<video>`) در یک اسلایدشو وجود دارد.

---

## `<tg-collage>`: Multi-Image Smart Grids

While `<tg-slideshow>` displays one slide at a time in sequence, `<tg-collage>` renders 2 to 10 images simultaneously in an auto-fitting grid layout (similar to Telegram photo albums, but nested inside the rich document).

### Collage Syntax

```html
<tg-collage>
  <img src="https://images.example.com/gallery/autumn-1.jpg" />
  <img src="https://images.example.com/gallery/autumn-2.jpg" />
  <img src="https://images.example.com/gallery/autumn-3.jpg" />
  <figcaption>
    Autumn in Northern Iran · 2026 Collection
    <cite>Photography by Alborz Expeditions</cite>
  </figcaption>
</tg-collage>
```

### Comparison: Slideshow vs Collage

| Criterion | `<tg-slideshow>` | `<tg-collage>` |
|:---|:---|:---|
| **Presentation** | One full-width item active, pagination controls | Compact multi-tile grid showing all items at once |
| **Best For** | Detailed product views, tutorials, mixed photo+video | Photo albums, real estate thumbnails, mood boards |
| **Video Support** | Supported (`<video>`) | Image-only (`<img>`) |
| **Vertical Space** | Fixed height; compact footprint | Expands vertically depending on image count |
| **Interaction** | Step-by-step browsing | Tap to enlarge individual image |

### فارسی — تفاوت کلاژ و اسلایدشو
- **اسلایدشو (`tg-slideshow`):** نمایش تک‌تک با قابلیت ورق زدن. برای راهنماهای گام‌به‌گام و نمایش جزئیات کالاها که نیاز به اندازه بزرگ دارند مناسب است. ویدیو نیز پشتیبانی می‌شود.
- **کلاژ (`tg-collage`):** چیدمان چند عکس در یک قاب مشبک (Grid) مانند آلبوم‌های تلگرام. همه عکس‌ها در یک نگاه دیده می‌شوند و برای آلبوم‌های عکاسی و پیش‌نمایش املاک مناسب است.

---

## Additional Rich Media Elements

### 1. Audio Embeds

Embeds streaming audio files with native Telegram media player controls:

```html
<audio src="https://audio.example.com/episodes/podcast-ep42.mp3" />
<p><b>Episode 42: Modern Bot Architectures</b></p>
```

### 2. Animations (GIFs)

Embeds looping animations:

```html
<img src="https://media.example.com/animations/success-celebration.gif" />
```

### 3. Voice Notes (`InputMediaVoiceNote`)

Added in Bot API 10.2, voice notes in OGG format (encoded with Opus codec) can be embedded into rich message streams:

```markdown
![](https://audio.example.com/voicenotes/welcome-message.ogg)
```

### 4. Native Map Embeds (`<tg-map>`)

Renders a geographic location map natively using device map frameworks (Apple Maps on iOS, Google Maps on Android, OpenStreetMap in web studio previews):

```html
<tg-map lat="35.6892" long="51.3890" zoom="15" />
<p>📍 <b>Meeting Location:</b> Central Tech Campus, Tehran</p>
```

- `lat`: Latitude float between -90.0 and 90.0.
- `long`: Longitude float between -180.0 and 180.0.
- `zoom`: Integer zoom level (typically 1 to 20, default 14).

### 5. Document & Media Attachments via Internal Protocols

Bot API 10.3 supports referencing media via Telegram internal protocols registered in `rich_message.media` (or block array as `InputRichBlockDocument`):
- `tg://photo?id=...` — Photo assets
- `tg://video?id=...` — MP4 video files
- `tg://audio?id=...` — Audio tracks and streams
- `tg://document?id=...` — Document and PDF attachments

```html
<p>Download our annual financial report: <a href="tg://document?id=q3_report">Q3 Financial Report (PDF)</a></p>
<p>Listen to executive briefing: <a href="tg://audio?id=audio_briefing">Q3 Executive Briefing (MP3)</a></p>
```

### فارسی — سایر انواع مدیا و پروتکل‌های داخلی
- تگ `<audio>` صوت را همراه با کنترل‌های پلیر تلگرام داخل پیام قرار می‌دهد.
- تگ `<tg-map lat="..." long="..." zoom="...">` نقشه تعاملی بومی براساس مختصات جغرافیایی رندر می‌کند.
- پیام‌های صوتی OGG به صورت ویس‌نوت با کلاس `InputMediaVoiceNote` پشتیبانی می‌شوند.
- ارجاع مستقیم به فایل‌های تلگرامی با ۴ پروتکل داخلی مجاز است: `tg://photo?id=...`، `tg://video?id=...`، `tg://audio?id=...` و `tg://document?id=...` (ثبت در آرایه `rich_message.media`).
- سقف تعداد رسانه‌ها: حداکثر ۵۰ آیتم مدیا در یک پیام ریچ مجاز است.

---

## `file_id` vs Public HTTPS URL Strategy

When embedding images, videos, or audio into rich messages, developers must choose between public HTTPS URLs and Telegram `file_id` references.

### Comparative Architectural Analysis

| Dimension | Public HTTPS URL (`https://...`) | Telegram `file_id` (`tg://photo?id=...`) |
|:---|:---|:---|
| **First Load Latency** | High (500ms–2000ms): Telegram servers must download, validate, transcode, and cache the file. | Zero delay (<50ms): Asset already resides on Telegram's global CDN clusters. |
| **Bandwidth Cost** | Outgoing bandwidth consumed on your server for each new Telegram datacenter fetch. | Zero host bandwidth; completely offloaded to Telegram infrastructure. |
| **Availability Risk** | If your server undergoes downtime or DNS issues, images fail to render. | Permanently cached and resilient within Telegram. |
| **Cross-Chat Sharing** | Re-fetched or verified by Telegram per unique domain request. | Immediately re-usable across any chat, group, or channel where the bot has access. |
| **Size Constraints** | Max 20MB for photos, 50MB for videos via direct URL fetch. | Supports standard bot upload limits (up to 50MB via Bot API). |

### Capturing and Caching `file_id`

To achieve sub-100ms render speeds for production catalogs, employ a **two-phase ingestion pipeline**:

1. **Pre-Upload / Ingestion Phase:** Upload your media assets once to a private storage channel or admin chat via `sendPhoto` or `sendDocument`.
2. **Extract `file_id`:** Retrieve the highest-resolution `file_id` from the API response object:
   ```typescript
   // Telegram returns photo sizes sorted ascending: [thumbnail, medium, full]
   const bestPhoto = message.photo[message.photo.length - 1];
   const cachedFileId = bestPhoto.file_id;
   ```
3. **Store in Database / KV:** Save the mapping (`sku_id -> file_id`) in your database or Cloudflare KV.
4. **Render in Rich Message:** Pass the mapped ID into your rich message markup:
   ```html
   <tg-slideshow>
     <img src="tg://photo?id=AgACAgIAAxkDAAIC...AAEC" />
     <img src="tg://photo?id=AgACAgIAAxkDAAIC...AAED" />
     <figcaption>Product Showcase</figcaption>
   </tg-slideshow>
   ```

### فارسی — استراتژی ذخیره و استفاده از file_id
- ارسال عکس با آدرس اینترنتی (`https://...`) باعث می‌شود سرورهای تلگرام در نخستین ارسال، تصویر را دانلود و بررسی کنند که منجر به تأخیر ۱ تا ۲ ثانیه‌ای می‌شود.
- استفاده از شناسه تلگرامی (`file_id`) بارگذاری آنی (زیر ۵۰ میلی‌ثانیه) را فراهم می‌سازد و هیچ پهنای باندی از هاست شما مصرف نمی‌کند.
- **روش پیشنهادی تولید:** فایل‌های عکس و ویدیو را ابتدا در یک کانال بایگانی اختصاصی آپلود کنید، مقدار `file_id` بالاترین کیفیت را در دیتابیس خود ذخیره نمایید، و در پیام‌های ریچ با `tg://photo?id=...` از آن استفاده کنید.

---

## Production Worked Use Cases

### 1. E-Commerce Product Carousel

Combines multiple product views, video overview, and pricing table:

```html
<tg-slideshow>
  <img src="https://assets.store.com/products/jacket-front.jpg" alt="Front angle" />
  <img src="https://assets.store.com/products/jacket-side.jpg" alt="Side profile" />
  <video src="https://assets.store.com/products/jacket-fit.mp4" />
  <figcaption>
    All-Weather Alpine Hardshell Jacket
    <cite>Designed in Zurich · 2026 Collection</cite>
  </figcaption>
</tg-slideshow>

<h3>Alpine Hardshell 2.0</h3>
<p>Engineered with 3-layer breathable membrane, waterproof YKK zippers, and adjustable storm hood.</p>

<table bordered compact>
  <tr><th>Specification</th><th>Value</th></tr>
  <tr><td>Waterproofing</td><td>28,000 mm</td></tr>
  <tr><td>Weight</td><td>420g (Medium)</td></tr>
  <tr><td>Price</td><td>$349.00 USD</td></tr>
</table>

<tg-button-row align="center">
  <tg-button type="url" style="primary" url="https://store.com/checkout/alpine">Purchase Now 🛒</tg-button>
  <tg-button type="callback_data" style="link" data="size_guide:jacket">Size Guide</tg-button>
</tg-button-row>
```

### 2. Creative Agency / Architecture Portfolio

Displays high-resolution architectural projects with attribution:

```html
<tg-slideshow>
  <img src="https://images.agency.com/projects/villa-exterior.jpg" />
  <img src="https://images.agency.com/projects/villa-interior.jpg" />
  <img src="https://images.agency.com/projects/villa-terrace.jpg" />
  <figcaption>
    Minimalist Hillside Residence
    <cite>Architecture by Studio Form &amp; Light · Photographer: Kaveh Rad</cite>
  </figcaption>
</tg-slideshow>

<aside>
  Architecture is the learned game, correct and magnificent, of forms assembled in the light.
  <cite>Le Corbusier</cite>
</aside>

<p>Project details: 450 m² private residence constructed in 2026. Features floor-to-ceiling glass facades and geothermal climate regulation.</p>
```

### 3. Step-by-Step Onboarding Tutorial

Guides users sequentially through account setup:

```html
<tg-slideshow>
  <img src="https://cdn.app.com/guides/step-1-create.png" />
  <img src="https://cdn.app.com/guides/step-2-verify.png" />
  <img src="https://cdn.app.com/guides/step-3-connect.png" />
  <figcaption>
    Quick Start Guide: 3 Simple Steps to Launch
    <cite>Hermes Cloud Documentation</cite>
  </figcaption>
</tg-slideshow>

<details open>
  <summary><b>Step-by-Step Instructions</b></summary>
  <ol>
    <li><b>Step 1:</b> Tap <i>Create Account</i> and set your administrative password.</li>
    <li><b>Step 2:</b> Verify your two-factor authentication code.</li>
    <li><b>Step 3:</b> Connect your webhook URL and begin issuing commands.</li>
  </ol>
</details>

<tg-button-row>
  <tg-button type="url" style="success" url="https://app.com/start">Begin Setup 🚀</tg-button>
</tg-button-row>
```

---

## Media Troubleshooting & Operational Rules

1. **Unsupported Protocols:** Only `https://` and registered Telegram internal protocols (`tg://photo?id=...`, `tg://video?id=...`, `tg://document?id=...`, `tg://audio?id=...`) are accepted. Plain `http://` or local filesystem paths will trigger an immediate rejection.
2. **Missing Media Attributes:** Every media tag (`<img>`, `<video>`, `<audio>`) must include a valid `src` attribute. Empty `src=""` causes validation failure.
3. **Video Format Encoding:** Videos used in `<video>` tags or slideshows must be encoded in H.264 / AVC video with AAC audio in an MP4 container. HEVC/H.265 or WebM formats may fail to render on older mobile devices.
4. **Timeout Handling:** If using public URLs, ensure your hosting server responds to Telegram crawler requests within 10 seconds. Sluggish CDNs cause `400 Bad Request: failed to get HTTP URL content`.
5. **Media Count Hard Limit:** A single rich message supports a **maximum of 50 media items** across all slideshows, collages, audio, and attachments combined. Exceeding 50 items results in request rejection.

### فارسی — قوانین و عیب‌یابی مدیا
- فقط لینک‌های امن `https://` و ۴ پروتکل داخلی تلگرام (`tg://photo`، `tg://video`، `tg://document`، `tg://audio`) مجاز هستند.
- حداکثر ۵۰ مدیا در یک پیام ریچ مجاز است و عبور از این سقف با رد درخواست مواجه می‌شود.
- ویدیوها باید حتماً کدک H.264 / AAC در کانتینر MP4 باشند.


<div align="center">

# Dharmik Shingala

#### Product &amp; Content for IT Operations

<a href="https://github.com/dharmik136">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=600&size=26&pause=900&color=2EC4B6&center=true&vCenter=true&width=860&height=50&lines=Observability+%C2%B7+Monitoring+%C2%B7+ITSM;I+write+the+docs+and+ship+the+small+tools;APM+%C2%B7+RUM+%C2%B7+SLO+%C2%B7+Logs+%C2%B7+Network+%C2%B7+ITIL" alt="What I do" />
</a>

<br/>

<img src="https://komarev.com/ghpvc/?username=dharmik136&style=for-the-badge&color=2ec4b6&label=PROFILE+VIEWS" alt="profile views" />

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/aatmaa)
[![Email](https://img.shields.io/badge/Email-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:dhashingala9@gmail.com)
[![Motadata](https://img.shields.io/badge/Motadata-1A2980?style=for-the-badge&logo=grafana&logoColor=white)](https://www.motadata.com)

</div>

## &nbsp;👋 &nbsp;About

**Product & content for IT operations** — observability, monitoring, and ITSM at **[Motadata](https://www.motadata.com)**.
I write the docs and capability pages, and ship the small **Python / PowerShell** tools that make the work faster — across the ObserveOps and ServiceOps lines. I care about deciding what to defend before writing a word, and about building the small tool when the workflow needs one that doesn't exist.

## &nbsp;🧭 &nbsp;What I Work On

```mermaid
%%{init: {'theme':'base','themeVariables':{'pie1':'#2563eb','pie2':'#22c55e','pie3':'#f97316','pie4':'#a855f7'}}}%%
pie showData
  title Where my work goes
  "Observability" : 35
  "Content & docs" : 30
  "ITSM / ITIL" : 20
  "Tooling" : 15
```

## &nbsp;🧰 &nbsp;Stack &amp; Domain

<div align="center">

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PowerShell](https://img.shields.io/badge/PowerShell-5391FE?style=for-the-badge&logo=powershell&logoColor=white)
![Markdown](https://img.shields.io/badge/Markdown-000000?style=for-the-badge&logo=markdown&logoColor=white)
![YAML](https://img.shields.io/badge/YAML-CB171E?style=for-the-badge&logo=yaml&logoColor=white)
![Git](https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)

`Observability` &nbsp;·&nbsp; `APM` &nbsp;·&nbsp; `RUM` &nbsp;·&nbsp; `SLO` &nbsp;·&nbsp; `Log Analytics` &nbsp;·&nbsp; `Network Monitoring` &nbsp;·&nbsp; `NCCM` &nbsp;·&nbsp; `ITSM / ITIL` &nbsp;·&nbsp; `SEO`

</div>

## &nbsp;📊 &nbsp;GitHub Stats

<div align="center">

<img height="195" src="https://github-readme-stats.vercel.app/api/top-langs/?username=dharmik136&layout=compact&card_width=460&langs_count=8&hide_border=true&title_color=2ec4b6&theme=tokyonight" alt="top languages" />

<img src="https://streak-stats.demolab.com?user=dharmik136&hide_border=true&ring=f97316&fire=f97316&currStreakLabel=2ec4b6&theme=tokyonight" alt="streak" />

<img width="100%" src="https://github-readme-activity-graph.vercel.app/graph?username=dharmik136&hide_border=true&bg_color=1a1b27&color=2ec4b6&line=f97316&point=ffffff&area=true&theme=tokyo-night" alt="activity graph" />

</div>

## &nbsp;📂 &nbsp;Project Index

| Project | Domain | What it does | Status |
| --- | --- | --- | --- |
| [home-loan-planner](https://github.com/dharmik136/home-loan-planner) | Personal finance | Interactive HDFC prepayment planner | ✅ Shipped |
| [motadata-seo-research](https://github.com/dharmik136/motadata-seo-research) | SEO / content ops | Keyword tracking + monthly SEO reporting hub | 🟢 Active |
| [motadata-page-builder](https://github.com/dharmik136/motadata-page-builder) | Content ops | Capability-page generator + validator | 🟢 Active |
| [motadata-blog-automation](https://github.com/dharmik136/motadata-blog-automation) | Content ops | Ahrefs-validated, Claude-drafted blog pipeline | 🟢 Active |

---

## &nbsp;🏦 &nbsp;Flagship — Home Loan Prepayment Planner

> Turns a messy amortization question — *"if I prepay ₹X now, what does it actually save me?"* — into a clear, visual decision. A single-file web app, no install.

```mermaid
flowchart LR
  A["Loan terms"]:::in --> B["Amortization engine"]:::eng
  P["Prepayment plan"]:::in --> B
  B --> C{"Compare"}:::eng
  C --> D["Interest saved"]:::out
  C --> E["Tenure reduced"]:::out
  C --> F["Month-by-month ledger"]:::out
  D --> G["Clear decision"]:::win
  E --> G
  F --> G
  classDef in fill:#2563eb,stroke:#1e40af,color:#fff
  classDef eng fill:#f97316,stroke:#c2410c,color:#fff
  classDef out fill:#22c55e,stroke:#15803d,color:#fff
  classDef win fill:#a855f7,stroke:#7e22ce,color:#fff
```

<details>
<summary><b>More detail</b></summary>

- **Problem** — prepayment math is opaque; spreadsheets hide the trade-off between saving interest and shortening tenure.
- **Solution** — a self-contained HTML/JS planner: enter the loan plus a prepayment plan, see interest saved, tenure cut, and a full ledger side-by-side.
- **Trade-offs** — single-file simplicity over a backend; everything runs client-side so it's shareable and private.
- **Learnings** — the right output isn't a number, it's a *decision* — so the UI leads with "what you save," not the table.

</details>

## &nbsp;✍️ &nbsp;Content Engine — How Motadata Content Gets Made

> The product-content work, as a sequence. Research decides what to defend; automation keeps it fresh; review keeps it honest.

```mermaid
sequenceDiagram
  participant R as Research
  participant B as Brief
  participant W as Writer
  participant V as Validator
  participant P as Publish
  R->>B: keyword + SERP
  B->>W: content brief
  W->>V: draft
  V-->>W: fails — revise
  V->>P: passes
  P-->>R: monthly report feeds next cycle
```

<details>
<summary><b>The repos behind it</b></summary>

| Repo | Role in the pipeline |
| --- | --- |
| **motadata-seo-research** | The research front-end — keyword tracking, SERP analysis, monthly reports, the 12-month plan. |
| **motadata-page-builder** | Generates and **validates** capability/product pages against approved claims and module boundaries. |
| **motadata-blog-automation** | Topic → Ahrefs validation → Claude draft → validation → publish, run on GitHub Actions. |

</details>

## &nbsp;🔎 &nbsp;motadata-seo-research

```mermaid
journey
  title SEO research workflow
  section Research
    Keyword + SERP: 4: Me
    Find content gaps: 4: Me
  section Plan
    Opportunity file: 5: Me
    12-month plan: 5: Me
  section Report
    Monthly rankings: 3: Cron
    Traffic report: 4: Cron
```

<details>
<summary><b>What it does</b></summary>

An SEO research hub for motadata.com: tracks keyword positions, runs competitive/SERP analysis, and auto-generates monthly health reports — all wired to a 12-month action plan. Claude Code automations do the heavy lifting on demand or on a schedule.

</details>

## &nbsp;🏗️ &nbsp;motadata-page-builder

```mermaid
stateDiagram-v2
  [*] --> Draft
  Draft --> Validating: generate
  Validating --> Published: claims OK
  Validating --> Flagged: boundary violation
  Flagged --> Draft: fix
  Published --> [*]
  classDef ok fill:#22c55e,stroke:#15803d,color:#fff
  classDef bad fill:#f97316,stroke:#c2410c,color:#fff
  class Published ok
  class Flagged bad
```

<details>
<summary><b>What it does</b></summary>

Generates product capability and feature pages from approved source material, then **validates** them — every claim has to be approved and every page has to stay inside its module's content boundary. The validator is the point: it stops scope drift before publish.

</details>

## &nbsp;📰 &nbsp;motadata-blog-automation

```mermaid
gitGraph
  commit id: "topic"
  commit id: "ahrefs ok"
  branch draft
  commit id: "claude draft"
  commit id: "validated"
  checkout main
  merge draft id: "published"
```

<details>
<summary><b>What it does</b></summary>

A Claude-powered blog pipeline: validates topics against Ahrefs data, drafts SEO-optimized posts, validates them, and publishes — orchestrated with GitHub Actions so the cadence doesn't depend on anyone remembering.

</details>

## &nbsp;🧪 &nbsp;Experiments &amp; Smaller Tools

<details>
<summary><b>A few more things I've built</b></summary>

- **claude-enter** — a tiny scheduled `VK_RETURN` injector for Windows; pure stdlib + Win32. The "write the small tool when none exists" rule, literally.
- **research-paper-decoder** — a decoder/parser for research-paper artifacts (a focused parsing project).
- **A self-updating profile dossier** — an earlier experiment that rendered this very README from data via a Python "clerk" + GitHub Actions. Retired in favor of readability, but a fun lesson in what GitHub will and won't render.

</details>

## &nbsp;🧱 &nbsp;How I Work

> Three rules, operational not aspirational:

1. **Decide what to defend first; write second.** Most B2B content drifts because nobody decided what to defend.
2. **Specificity is the only luxury that scales.** Sharp positioning beats decorative writing, every time.
3. **When the workflow needs a tool that doesn't exist, write a small one.** The smaller the better.

## &nbsp;📌 &nbsp;Now

- 🛰️ Capability pages and RFP answers across ObserveOps & ServiceOps modules
- 🔬 SEO research + content automation for motadata.com
- 🧰 Small tools that remove repetitive steps from the content workflow

## &nbsp;🤝 &nbsp;Reach Me

<div align="center">

[![LinkedIn](https://img.shields.io/badge/Connect_on_LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/aatmaa)
[![Email](https://img.shields.io/badge/Email_me-EA4335?style=for-the-badge&logo=gmail&logoColor=white)](mailto:dhashingala9@gmail.com)

Talk to me about **observability · ITSM / ITIL · technical content · SEO · small automations**.

</div>

<div align="center">

<img src="https://raw.githubusercontent.com/dharmik136/dharmik136/output/snake.svg" alt="contribution snake" width="100%" />

<br/>

<sub>Decide what to defend first; write second. &nbsp;·&nbsp; Specificity is the only luxury that scales.</sub>

</div>

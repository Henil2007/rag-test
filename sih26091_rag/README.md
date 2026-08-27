# SIH26091 — Small Enterprise Tax & Investment Advisory System

An intelligent, location-aware financial advisory system for micro and small enterprises in Gujarat. The system combines deterministic financial modeling (P&L statements, reducing-balance loan amortization, DSCR, GST & Section 44AD tax liabilities) with a **RAG pipeline powered by Google Gemini** and real district census data (**Mahesana District, Gujarat**).

---

## System Architecture

```
User Input: Village/Town Name, Margin Capital (₹), Business Sector
       │
       ▼
1. Location Profiling (local_data.py)
   └── Silently matches place in data/Mahesana_Population.csv
   └── Derives economic archetype, consumer base scale, literacy band,
       workforce composition (agri/dairy vs artisan vs trade), SC/ST ratio,
       and priority sector lending status.
       │
       ▼
2. Dynamic Financial & Loan Modeling (financial_calculator.py)
   ├── Queries Gemini (gemini-3.6-flash) for prevailing area lending rate & subsidy
   ├── Calculates Project Cost, Loan Sanction, Capital Subsidy & EMI Amortization
   ├── Projects Annual P&L Statement (Revenue, COGS, Opex, EBITDA, DSCR, Break-Even)
   └── Computes Tax Liability (GST Composition Scheme 1-2% + Presumptive Tax u/s 44AD)
       │
       ▼
3. RAG Knowledge Retrieval & AI Advisory (rag_engine.py)
   ├── TF-IDF / Semantic retrieval over sector rules & locality economic profiles
   └── Generates structured Tax & Investment Advisory Report via Google Gemini
       │
       ▼
4. Output (main.py)
   ├── 1. Dynamic Financial & Loan Statement
   ├── 2. Projected Annual Profit & Loss (P&L) Statement
   ├── 3. Estimated Annual Tax Liability Statement
   └── 4. Gemini AI Tax & Investment Advisory Report
```

---

## File Structure

| File | Purpose |
|---|---|
| [`data/Mahesana_Population.csv`](file:///d:/rag-test/sih26091_rag/data/Mahesana_Population.csv) | Real Census 2011 dataset containing 717 rows of villages, towns, and wards across Mahesana district with workforce, literacy, and demographic metrics. |
| [`data/dummy_docs/scheme_rules.txt`](file:///d:/rag-test/sih26091_rag/data/dummy_docs/scheme_rules.txt) | Knowledge base containing scheme rules, MSME policies, sector guidelines, and tax frameworks. |
| [`src/local_data.py`](file:///d:/rag-test/sih26091_rag/src/local_data.py) | Module for matching locations in the CSV and translating raw demographics into actionable economic/credit signals. |
| [`src/financial_calculator.py`](file:///d:/rag-test/sih26091_rag/src/financial_calculator.py) | Dynamic interest rate determination (Gemini-integrated), loan amortization, full P&L statement, DSCR, break-even, and tax calculations. |
| [`src/rag_engine.py`](file:///d:/rag-test/sih26091_rag/src/rag_engine.py) | Knowledge retriever and Gemini report generator (using `gemini-3.6-flash` with offline fallback). |
| [`src/main.py`](file:///d:/rag-test/sih26091_rag/src/main.py) | Main entrypoint orchestrating the end-to-end pipeline. |

---

## Step-by-Step Guide to Run

### Step 1: Open Terminal and Navigate to Project
```powershell
cd d:\rag-test\sih26091_rag
```

### Step 2: Activate the Virtual Environment
On Windows (PowerShell):
```powershell
.\env\Scripts\activate
```
On Linux/macOS:
```bash
source env/bin/activate
```

### Step 3: Set Your Gemini API Key
In PowerShell:
```powershell
$env:GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```
In Command Prompt (`cmd.exe`):
```cmd
set GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```
In Linux/macOS (Bash/Zsh):
```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
```

### Step 4: Configure Input Parameters
Open [`src/main.py`](file:///d:/rag-test/sih26091_rag/src/main.py) and edit the parameters at the bottom:
```python
if __name__ == "__main__":
    # Parameters:
    # 1. village_name : Any village/town in Mahesana (e.g. "Visnagar", "Sudasana", "Chelana", "Kheralu", "Vadnagar")
    # 2. margin_capital: Promoter's capital contribution in INR (e.g. 50000, 100000, 200000)
    # 3. sector        : Business sector (e.g. "textiles", "dairy", "retail", "agriculture", "handicraft")
    
    run(village_name="Visnagar", margin_capital=100_000, sector="textiles")
```

### Step 5: Execute the System
```powershell
cd src
python main.py
```

---

## Example Outputs

### 1. Visnagar — Textile Manufacturing (Capital: ₹1,00,000)
* **Scheme & Rate:** PMEGP Rural / Cottage Industry @ **7.85% p.a.**
* **Project Outlay:** ₹10,00,000 (Loan: ₹9,00,000 | Capital Subsidy: **₹3,50,000**)
* **Quarterly EMI:** ₹59,834.14
* **Projected Annual Revenue:** ₹16,00,000
* **Estimated Annual Tax:** **₹32,000** (2% GST Composition Scheme; Income Tax is ₹0 u/s 44AD / 87A rebate)
* **Net Profit After Tax:** **₹2,08,663/year** (208.7% Margin ROI)

### 2. Sudasana — Dairy Farming (Capital: ₹50,000)
* **Scheme & Rate:** NABARD / Priority Agri-MSME @ **6.50% p.a.**
* **Project Outlay:** ₹5,00,000 (Loan: ₹4,50,000 | Capital Subsidy: **₹1,25,000**)
* **Quarterly EMI:** ₹28,958.85
* **Projected Annual Revenue:** ₹10,00,000
* **Estimated Annual Tax:** **₹0.00** (Raw dairy & agricultural produce is Nil/Exempt under GST & Sec 10(1))
* **Net Profit After Tax:** **₹1,54,165/year** (308.3% Margin ROI)

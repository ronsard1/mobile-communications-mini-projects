# Mobile Communications: Mini Projects (Unit 1)

Python simulations and reports for the Unit 1 lab manual (University of Rwanda, Computer and Software Engineering).

| Project | Topic | Folder |
|---|---|---|
| 1.1 | Link budgets and coverage range: 700 MHz vs 28 GHz | `Mini_Project_1_1_Link_Budget/` |
| 1.2 | FDD vs TDD utilization under traffic asymmetry | `Mini_Project_1_2_FDD_TDD/` |
| 1.3 | Validating the 0G-6G table, plus a rule-based generation recommender | `Mini_Project_1_3_0G_6G/` |

## Setup

```bash
pip install -r requirements.txt
```

Python 3.9 or later is recommended.

## Run

```bash
python Mini_Project_1_1_Link_Budget/mini_project_1_1.py
python Mini_Project_1_2_FDD_TDD/mini_project_1_2.py
python Mini_Project_1_3_0G_6G/recommender.py                     # runs the 8 test cases
python Mini_Project_1_3_0G_6G/recommender.py "your requirement"   # try your own
```

Each script saves its charts into a `figures/` folder next to it. Printed results are saved in `results_1_1.txt`, `results_1_2.txt` and `test_results.txt`.

## Key results

**1.1 Link budget** (40 dBm TX, 15 dBi TX gain, 3 dB other losses, -100 dBm sensitivity, free-space model)
- 28 GHz loses about 32 dB more than 700 MHz at any distance, so its range is 40x shorter (34 km vs 1358 km).
- A 24 dBi phased array at 28 GHz recovers 2.8x range; an 8 dB shadowing margin cuts every band's range to 40%.
- Doubling bandwidth raises capacity far more than doubling transmit power.
- Free-space ranges are idealized. Real mmWave coverage is much shorter (rain, blockage, foliage).

**1.2 FDD vs TDD** (20-slot frame, saturated load)
- TDD beats FDD once downlink demand passes about 56:44 with a 5% guard, about 61:39 with 10%, and about 71:29 with 20%.
- At 90:10, TDD reaches 95% utilization (5% guard) against 60% for FDD; at 50:50 FDD wins (100% vs 95%).

**1.3 Generations**
- Headline peak rates differ a lot from typical rates in every generation (for example 5G: 20 Gbps ITU peak vs 100 Mbps user-experienced target).
- The recommender maps a plain-language requirement to the first generation that addressed it, and flags mixed or unmatched requirements.

## Structure

```
Mobile_Communications_Mini_Projects/
├── README.md
├── requirements.txt
├── .gitignore
├── Mini_Project_1_1_Link_Budget/   script, figures/, results_1_1.txt, report (pdf + docx)
├── Mini_Project_1_2_FDD_TDD/       script, figures/, results_1_2.txt, report (pdf + docx)
└── Mini_Project_1_3_0G_6G/         recommender.py, test_results.txt, fact_check_table.pdf, report (pdf + docx)
```

## Note on report length

Mini Project 1.1 asks for a **half-page** written analysis. `short_analysis_1_1.pdf` in that folder is the half-page write-up that matches the requirement; `report_1_1.pdf` is a longer, more detailed version with the full lab-task breakdown and embedded figures, kept as a reference. Submit `short_analysis_1_1.pdf` if your lecturer wants the exact length; submit both if more detail is welcome. Mini Projects 1.2 and 1.3 allow 1-2 pages and their `report_1_x.pdf` files fit that.

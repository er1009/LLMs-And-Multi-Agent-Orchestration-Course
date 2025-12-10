### 🧪 Experiment Execution Summary

| Experiment | Status | Runtime | Key Outcome |
| :--- | :--- | :--- | :--- |
| **1. Needle in Haystack** | ✅ Passed | 88.3s | Confirmed "Lost in the Middle" phenomenon (86.4% avg accuracy) |
| **2. Context Size Impact** | ✅ Passed | 272.5s | Validated latency/accuracy trade-off (Mean latency: ~3.1s) |
| **3. RAG vs Full Context** | ✅ Passed | 65.7s | **RAG Superiority:** 80% vs 60% accuracy, similar latency |
| **4. Context Strategies** | ✅ Passed | 30.4s | 100% success rate across SELECT, COMPRESS, WRITE strategies |

### 📂 Generated Artifacts

All data and visualizations are saved in the `results/` directory:

*   **Experiment 1:** `results/experiment1/`
    *   `lost_in_middle.png` 📊 (Visualization of accuracy by position)
    *   `raw_results.json`, `aggregated_stats.csv` 📄
*   **Experiment 2:** `results/experiment2/`
    *   `context_size_impact.png` 📊 (Dual-axis graph of accuracy vs latency)
    *   `raw_results.json`, `aggregated_stats.csv` 📄
*   **Experiment 3:** `results/experiment3/`
    *   `rag_vs_full.png` 📊 (Comparison bar charts)
    *   `raw_results.json`, `aggregated_stats.csv` 📄
*   **Experiment 4:** `results/experiment4/`
    *   `strategy_trends.png` 📊 (Performance trends over time)
    *   `strategy_comparison.csv` 📄 (Detailed strategy metrics)
    *   `raw_results.json`, `aggregated_stats.csv` 📄

The system is fully operational and the results are ready for analysis.
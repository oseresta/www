---
description: Workflow for generating and publishing the stock analysis report website
---

This workflow automates the process of updating the static website with the latest stock analysis results.

1.  **Generate HTML Reports**
    Run the site generation script to process new data and create/update HTML files.
    ```bash
    python3 update_site.py
    ```

2.  **Commit and Push**
    (Note: This step is typically handled by your LocalDaemon agent, but here is the manual command if needed)
    ```bash
    git add .
    git commit -m "Update stock analysis report for $(date +%Y-%m-%d)"
    git push origin main
    ```

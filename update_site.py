
import os
import glob
import pandas as pd
import json

# Configuration
STRATEGIES = ["dma", "dma_bo", "dma_hmm", "dma_hmm_bo", "pv"]
ROOT_DIR = "."  # Current directory

# CSS for Professional Styling
CSS_STYLES = """
    body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 20px; background-color: #f4f6f8; color: #333; }
    h1 { color: #2c3e50; border-bottom: 2px solid #009879; padding-bottom: 10px; }
    h2 { color: #009879; margin-top: 30px; }
    
    /* Navigation */
    .nav { background: #ffffff; padding: 15px; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 25px; }
    .nav a { margin-right: 20px; text-decoration: none; color: #2c3e50; font-weight: 500; font-size: 1.05em; transition: color 0.2s; }
    .nav a:hover { color: #009879; }
    .nav span { margin-right: 20px; color: #999; }

    /* Tables */
    table { border-collapse: collapse; width: 100%; margin: 25px 0; font-size: 0.95em; min-width: 400px;
            background: #fff; box-shadow: 0 0 20px rgba(0, 0, 0, 0.05); border-radius: 8px; overflow: hidden; }
    thead tr { background-color: #009879; color: #ffffff; text-align: left; }
    th, td { padding: 12px 15px; }
    tbody tr { border-bottom: 1px solid #dddddd; }
    tbody tr:nth-of-type(even) { background-color: #f8f9fa; }
    tbody tr:last-of-type { border-bottom: 2px solid #009879; }
    tbody tr:hover { background-color: #f1f1f1; cursor: default; }

    /* Signal Coloring */
    .signal-buy { color: #27ae60; font-weight: bold; }
    .signal-sell { color: #c0392b; font-weight: bold; }
    .signal-hold { color: #7f8c8d; font-weight: bold; }

    /* Gallery */
    .gallery { display: flex; flex-wrap: wrap; gap: 20px; justify-content: center; }
    .gallery-item { background: #fff; padding: 10px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); width: fit-content; text-align: center; }
    .gallery img { max-width: 100%; height: auto; border-radius: 4px; display: block; }
    .gallery h3 { margin: 10px 0 5px; font-size: 1em; color: #555; }
    
    /* Index List */
    .date-list { list-style: none; padding: 0; }
    .date-row { display: flex; align-items: center; background: #fff; margin-bottom: 10px; padding: 15px; border-radius: 6px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .date-label { font-weight: bold; font-size: 1.1em; width: 150px; color: #2c3e50; }
    .date-actions a { display: inline-block; padding: 6px 12px; margin-right: 10px; border-radius: 4px; text-decoration: none; font-size: 0.9em; transition: background 0.2s; }
    .btn-output { background-color: #e8f6f3; color: #009879; border: 1px solid #009879; }
    .btn-output:hover { background-color: #009879; color: #fff; }
    .btn-forward { background-color: #fdf2e9; color: #d35400; border: 1px solid #d35400; }
    .btn-forward:hover { background-color: #d35400; color: #fff; }
    .btn-disabled { background-color: #eee; color: #aaa; border: 1px solid #ddd; pointer-events: none; }
"""

def get_html_header(title, root_depth=0):
    root_path = "../" * root_depth
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>{CSS_STYLES}</style>
</head>
<body>
    <div class="nav">
        <a href="{root_path}index.html">Home</a>
"""

HTML_FOOTER = """
</body>
</html>
"""

def format_signal(val):
    if not isinstance(val, str): return val
    val_upper = val.upper()
    if 'BUY' in val_upper: return f'<span class="signal-buy">{val}</span>'
    if 'SELL' in val_upper: return f'<span class="signal-sell">{val}</span>'
    return f'<span class="signal-hold">{val}</span>'

def generate_output_report(strategy, date_folder, date):
    output_dir = os.path.join(date_folder, "output")
    json_path = os.path.join(output_dir, "output.json")
    
    # Header with nav
    html = get_html_header(f"{strategy} - {date} Output", root_depth=4) # ../../../index.html from strats/date/output/index.html
    html += f'<a href="../../index.html">{strategy} Index</a>'
    html += f'<span>&gt;</span><span>{date} Output</span>'
    html += "</div>"
    
    html += f"<h1>Analysis Output: {strategy} ({date})</h1>"

    if os.path.exists(json_path):
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
            if isinstance(data, dict): data = [data]
            
            df = pd.DataFrame(data)
            
            # Formatting
            if 'Signal' in df.columns:
                df['Signal'] = df['Signal'].apply(format_signal)
            
            # Pandas default HTML
            table_html = df.to_html(classes='table', index=False, escape=False, border=0)
            html += table_html
            
        except Exception as e:
            html += f"<p>Error processing JSON: {e}</p>"
    else:
        html += "<p>No output data found.</p>"

    html += HTML_FOOTER
    
    # Write to output/index.html
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    with open(os.path.join(output_dir, "index.html"), "w") as f:
        f.write(html)

def generate_forward_report(strategy, date_folder, date):
    forward_dir = os.path.join(date_folder, "forward")
    
    html = get_html_header(f"{strategy} - {date} Forward Test", root_depth=4)
    html += f'<a href="../../index.html">{strategy} Index</a>'
    html += f'<span>&gt;</span><span>{date} Forward</span>'
    html += "</div>"

    html += f"<h1>Forward Test: {strategy} ({date})</h1>"

    if os.path.exists(forward_dir):
        images = sorted(glob.glob(os.path.join(forward_dir, "*.png")))
        if images:
            html += '<div class="gallery">'
            for img_path in images:
                img_name = os.path.basename(img_path)
                html += f'<div class="gallery-item"><h3>{img_name}</h3><img src="{img_name}" alt="{img_name}"></div>'
            html += '</div>'
        else:
            html += "<p>No images found.</p>"
    else:
        html += "<p>Forward directory not available.</p>"

    html += HTML_FOOTER

    if not os.path.exists(forward_dir): os.makedirs(forward_dir)
    with open(os.path.join(forward_dir, "index.html"), "w") as f:
        f.write(html)

def generate_strategy_index(strategy, dates_info):
    # dates_info is a list of tuples: (date, has_output, has_forward)
    strategy_dir = os.path.join(ROOT_DIR, strategy)
    
    html = get_html_header(f"{strategy} Reports", root_depth=2)
    html += f'<span>{strategy} Index</span>'
    html += "</div>"
    
    html += f"<h1>{strategy} Reports</h1>"
    html += '<ul class="date-list">'
    
    for date, has_output, has_forward in sorted(dates_info, key=lambda x: x[0], reverse=True):
        html += f'<li class="date-row"><div class="date-label">{date}</div><div class="date-actions">'
        
        if has_output:
            html += f'<a href="{date}/output/index.html" class="btn-output">View Output</a>'
        else:
            html += '<a href="#" class="btn-disabled">No Output</a>'
            
        if has_forward:
            html += f'<a href="{date}/forward/index.html" class="btn-forward">View Charts</a>'
        else:
            html += '<a href="#" class="btn-disabled">No Charts</a>'
            
        html += '</div></li>'
        
    html += '</ul>'
    html += HTML_FOOTER
    
    with open(os.path.join(strategy_dir, "index.html"), "w") as f:
        f.write(html)
    print(f"Index updated for {strategy}")

def main():
    for strategy in STRATEGIES:
        strategy_path = os.path.join(ROOT_DIR, strategy)
        if not os.path.isdir(strategy_path): continue
            
        dates_info = []
        
        for item in os.listdir(strategy_path):
            item_path = os.path.join(strategy_path, item)
            # Identify date folders by checking for 'output' or 'forward' subdirs
            if os.path.isdir(item_path) and item not in ["output", "forward", ".git"]:
                has_output = os.path.exists(os.path.join(item_path, "output"))
                has_forward = os.path.exists(os.path.join(item_path, "forward"))
                
                if has_output or has_forward:
                    if has_output:
                        generate_output_report(strategy, item_path, item)
                    if has_forward:
                        generate_forward_report(strategy, item_path, item)
                    
                    dates_info.append((item, has_output, has_forward))
        
        if dates_info:
            generate_strategy_index(strategy, dates_info)
        else:
             print(f"No reports found for {strategy}")

if __name__ == "__main__":
    main()

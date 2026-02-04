
import os
import glob
import json
import collections

# Configuration
STRATEGIES = ["dma", "dma_bo", "dma_hmm", "dma_hmm_bo", "pv"]
ROOT_DIR = "."

# Descriptions for strategies
STRATEGY_DESCRIPTIONS = {
    "dma": {
        "title": "Strategy I: Dual Moving Average (DMA)",
        "description": "This strategy uses two Moving Averages (MA) to determine trend direction. A buy signal is generated when the short-term MA crosses above the long-term MA. <b>Baseline</b> refers to the standard Buy & Hold strategy return for the same period."
    },
    "dma_bo": {
        "title": "Strategy I (India)",
        "description": "Implementation of the Dual Moving Average strategy specifically tuned for the Indian market indices. Follows the same logic as the standard DMA but may use different default windows."
    },
    "dma_hmm": {
        "title": "Strategy II: DMA + Hidden Markov Model",
        "description": "Enhances the standard DMA strategy by overlaying a Hidden Markov Model (HMM) to detect market regimes (e.g., Bull vs. Bear). Trades are only taken when the HMM indicates a favorable regime."
    },
    "dma_hmm_bo": {
        "title": "Strategy II (India)",
        "description": "The HMM-enhanced strategy applied to Indian markets."
    },
    "pv": {
        "title": "Peak Valley",
        "description": "A price-action based strategy that identifies peaks and valleys to determine trend reversals and continuation patterns."
    }
}

def generate_manifest():
    """Scans directories and builds the manifest.json"""
    manifest = {}
    
    for strategy in STRATEGIES:
        strategy_path = os.path.join(ROOT_DIR, strategy)
        if not os.path.isdir(strategy_path):
            continue
            
        manifest[strategy] = {
            "name": STRATEGY_DESCRIPTIONS.get(strategy, {}).get("title", strategy),
            "description": STRATEGY_DESCRIPTIONS.get(strategy, {}).get("description", "No description available."),
            "dates": []
        }
        
        dates_data = []
        for date_folder in os.listdir(strategy_path):
            full_path = os.path.join(strategy_path, date_folder)
            if not os.path.isdir(full_path) or date_folder in ["output", "forward", ".git"]:
                continue
                
            # Check for data
            output_dir = os.path.join(full_path, "output")
            forward_dir = os.path.join(full_path, "forward")
            
            output_json = os.path.join(output_dir, "output.json")
            has_output = os.path.exists(output_json)
            
            images = []
            if os.path.isdir(forward_dir):
                for img in sorted(glob.glob(os.path.join(forward_dir, "*.png"))):
                    images.append(os.path.basename(img))
            
            if has_output or images:
                dates_data.append({
                    "date": date_folder,
                    "has_output": has_output,
                    "output_file": f"{strategy}/{date_folder}/output/output.json" if has_output else None,
                    "images": [f"{strategy}/{date_folder}/forward/{img}" for img in images]
                })

        # Sort dates descending
        dates_data.sort(key=lambda x: x["date"], reverse=True)
        manifest[strategy]["dates"] = dates_data

    # Write manifest
    with open("manifest.json", "w") as f:
        json.dump(manifest, f, indent=2)
    print("Generated manifest.json")
    return manifest

def generate_app_shell():
    """Generates the main index.html file"""
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Analysis Dashboard</title>
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css">
    <style>
        html,body,h1,h2,h3,h4,h5 {font-family: "Raleway", sans-serif}
        .w3-bar-block .w3-bar-item {padding: 16px}
        
        /* Custom Styles */
        #main-content { margin-left: 260px; transition: margin-left .3s; }
        .nav-active { background-color: #2196F3 !important; color: white !important; }
        .hidden { display: none; }
        
        /* Table Styles */
        .analysis-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
        .analysis-table th, .analysis-table td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        .analysis-table th { background-color: #f1f1f1; cursor: pointer; }
        .analysis-table tr:hover { background-color: #f5f5f5; }
        
        /* Signal Colors */
        .signal-Buy { color: green; font-weight: bold; }
        .signal-Sell { color: red; font-weight: bold; }
        .signal-Hold { color: gray; }
        
        /* Gallery */
        .gallery-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(600px, 1fr)); gap: 20px; padding: 20px 0; }
        .gallery-item img { width: 100%; border-radius: 4px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
        
        @media (max-width: 992px) {
            #main-content { margin-left: 0; }
            .w3-sidebar { display: none; z-index: 5; }
        }
        
        /* Loading Overlay */
        #loader {
            position: fixed; left: 0; top: 0; width: 100%; height: 100%;
            background: rgba(255,255,255,0.8); z-index: 9999;
            display: flex; justify-content: center; align-items: center;
        }
    </style>
</head>
<body class="w3-light-grey">

<!-- Top container -->
<div class="w3-bar w3-top w3-black w3-large" style="z-index:4">
  <button class="w3-bar-item w3-button w3-hide-large w3-hover-none w3-hover-text-light-grey" onclick="w3_open();"><i class="fa fa-bars"></i>  Menu</button>
  <span class="w3-bar-item w3-right">Antigravity Analysis</span>
</div>

<!-- Sidebar/menu -->
<nav class="w3-sidebar w3-collapse w3-white w3-animate-left" style="z-index:3;width:260px;" id="mySidebar"><br>
  <div class="w3-container w3-row">
    <div class="w3-col s12 w3-bar">
      <span>Welcome, <strong>User</strong></span><br>
    </div>
  </div>
  <hr>
  <div class="w3-container">
    <h5>Dashboard</h5>
  </div>
  <div class="w3-bar-block" id="nav-container">
    <a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-dark-grey w3-hover-black" onclick="w3_close()" title="close menu"><i class="fa fa-remove fa-fw"></i>  Close Menu</a>
    <!-- Navigation will be populated here -->
  </div>
</nav>


<!-- Overlay effect when opening sidebar on small screens -->
<div class="w3-overlay w3-hide-large w3-animate-opacity" onclick="w3_close()" style="cursor:pointer" title="close side menu" id="myOverlay"></div>

<!-- !PAGE CONTENT! -->
<div class="w3-main" style="margin-left:300px;margin-top:43px;">

  <!-- Header -->
  <header class="w3-container" style="padding-top:22px">
    <h5><b><i class="fa fa-dashboard"></i> <span id="page-title">Select a Strategy</span></b></h5>
  </header>

  <div id="dashboard-content" class="w3-container hidden">
      
      <div class="w3-panel w3-white w3-card w3-display-container">
          <p id="strategy-desc" class="w3-text-grey"></p>
      </div>

      <div class="w3-bar w3-black">
        <button class="w3-bar-item w3-button tablink w3-red" onclick="openTab(event,'Summary')">Summary</button>
        <button class="w3-bar-item w3-button tablink" onclick="openTab(event,'Forward')">Forward Testing</button>
      </div>
      
      <div id="Summary" class="w3-container tab-content w3-white w3-padding-16">
        <p>Loading data...</p>
      </div>

      <div id="Forward" class="w3-container tab-content w3-white w3-padding-16" style="display:none">
        <div id="gallery-container" class="gallery-grid"></div>
      </div>
  </div>
  
  <div id="placeholder-msg" class="w3-container w3-padding-32 w3-center">
      <h3><i class="fa fa-arrow-left"></i> Click a date in the sidebar to view reports.</h3>
  </div>

  <!-- Footer -->
  <footer class="w3-container w3-padding-16 w3-light-grey">
    <p>Powered by <a href="https://www.w3schools.com/w3css/default.asp" target="_blank">w3.css</a></p>
  </footer>

  <!-- End page content -->
</div>

<script>
// Global Data
let manifest = {};

// Init
window.onload = async function() {
    try {
        const response = await fetch('manifest.json');
        manifest = await response.json();
        renderSidebar();
    } catch (e) {
        console.error("Failed to load manifest", e);
        document.getElementById("nav-container").innerHTML = "<div class='w3-padding w3-text-red'>Error loading data.</div>";
    }
};

// Sidebar Rendering
function renderSidebar() {
    const container = document.getElementById("nav-container");
    container.innerHTML = "";
    
    // Close button for mobile
    container.innerHTML += '<a href="#" class="w3-bar-item w3-button w3-padding-16 w3-hide-large w3-dark-grey w3-hover-black" onclick="w3_close()" title="close menu"><i class="fa fa-remove fa-fw"></i> Close Menu</a>';
    
    for (const [key, strategy] of Object.entries(manifest)) {
        if (!strategy.dates || strategy.dates.length === 0) continue;
        
        // Strategy Header (Accordion Trigger)
        const btn = document.createElement("button");
        btn.className = "w3-button w3-block w3-left-align w3-hover-light-grey";
        btn.innerHTML = `<i class="fa fa-line-chart fa-fw"></i> ${strategy.name} <i class="fa fa-caret-down"></i>`;
        
        const divId = `nav-${key}`;
        btn.onclick = () => myAccFunc(divId);
        
        container.appendChild(btn);
        
        // Dates Container
        const dateDiv = document.createElement("div");
        dateDiv.id = divId;
        dateDiv.className = "w3-hide w3-white w3-card-4";
        
        strategy.dates.forEach(item => {
            const link = document.createElement("a");
            link.href = "#";
            link.className = "w3-bar-item w3-button w3-padding-small";
            link.style.paddingLeft = "24px"; // Indent
            link.innerHTML = `<i class="fa fa-calendar fa-fw"></i> ${item.date}`;
            link.onclick = (e) => {
                e.preventDefault();
                loadReport(key, item);
                
                // Active state
                document.querySelectorAll(".w3-bar-item").forEach(el => el.classList.remove("nav-active"));
                link.classList.add("nav-active");
                
                // On mobile, close sidebar after selection
                w3_close();
            };
            dateDiv.appendChild(link);
        });
        
        container.appendChild(dateDiv);
    }
}

// Accordion
function myAccFunc(id) {
  var x = document.getElementById(id);
  if (x.className.indexOf("w3-show") == -1) {
    x.className += " w3-show";
    x.previousElementSibling.className += " w3-green";
  } else { 
    x.className = x.className.replace(" w3-show", "");
    x.previousElementSibling.className = 
    x.previousElementSibling.className.replace(" w3-green", "");
  }
}

// Toggle Sidebar
function w3_open() {
  var mySidebar = document.getElementById("mySidebar");
  var overlay = document.getElementById("myOverlay");
  if (mySidebar.style.display === 'block') {
    mySidebar.style.display = 'none';
    overlay.style.display = "none";
  } else {
    mySidebar.style.display = 'block';
    overlay.style.display = "block";
  }
}

function w3_close() {
  document.getElementById("mySidebar").style.display = "none";
  document.getElementById("myOverlay").style.display = "none";
}

// Tabs
function openTab(evt, tabName) {
  var i, x, tablinks;
  x = document.getElementsByClassName("tab-content");
  for (i = 0; i < x.length; i++) {
    x[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablink");
  for (i = 0; i < x.length; i++) {
    tablinks[i].className = tablinks[i].className.replace(" w3-red", "");
  }
  document.getElementById(tabName).style.display = "block";
  if(evt) evt.currentTarget.className += " w3-red";
}

// Helper: Format JSON Table
function jsonToTable(data) {
    if (!data || data.length === 0) return "<p>No data available.</p>";
    
    // Get headers
    const headers = Object.keys(data[0]);
    
    let html = '<table class="analysis-table w3-table-all w3-hoverable">';
    html += '<thead><tr class="w3-green">';
    headers.forEach(h => html += `<th>${h}</th>`);
    html += '</tr></thead><tbody>';
    
    data.forEach(row => {
        html += '<tr>';
        headers.forEach(h => {
            let val = row[h];
            if (h === 'Signal' && val) {
                val = `<span class="signal-${val}">${val}</span>`;
            }
            if (val === null) val = "";
            
            // Format numbers
            if (typeof val === 'number') {
                val = val.toFixed(2);
            }
            
            html += `<td>${val}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    return html;
}

// Load Content
async function loadReport(strategyKey, dateItem) {
    const strat = manifest[strategyKey];
    
    // UI Updates
    document.getElementById("placeholder-msg").classList.add("hidden");
    document.getElementById("dashboard-content").classList.remove("hidden");
    document.getElementById("page-title").innerText = `${strat.name} - ${dateItem.date}`;
    document.getElementById("strategy-desc").innerHTML = strat.description;
    
    // 1. Load Summary
    const summaryDiv = document.getElementById("Summary");
    if (dateItem.has_output && dateItem.output_file) {
        summaryDiv.innerHTML = '<p><i class="fa fa-spinner fa-spin"></i> Loading table...</p>';
        try {
            const res = await fetch(dateItem.output_file);
            const json = await res.json();
            // Handle array or single dict wrap
            const data = Array.isArray(json) ? json : [json];
            summaryDiv.innerHTML = jsonToTable(data);
        } catch(e) {
            summaryDiv.innerHTML = `<p class="w3-text-red">Error loading output data: ${e.message}</p>`;
        }
    } else {
        summaryDiv.innerHTML = "<p>No Summary Data found for this date.</p>";
    }
    
    // 2. Load Gallery
    const galleryDiv = document.getElementById("gallery-container");
    galleryDiv.innerHTML = "";
    if (dateItem.images && dateItem.images.length > 0) {
        dateItem.images.forEach(img => {
            const div = document.createElement("div");
            div.className = "gallery-item";
            const imgName = img.split('/').pop();
            div.innerHTML = `
                <img src="${img}" alt="${imgName}" onclick="window.open(this.src)">
                <div class="w3-container w3-white">
                  <p><b>${imgName}</b></p>
                </div>
            `;
            galleryDiv.appendChild(div);
        });
    } else {
        galleryDiv.innerHTML = "<p>No images found in forward folder.</p>";
    }
    
    // Reset to Summary Tab
    openTab(null, 'Summary');
    // Set active tab color manually since we passed null event
    document.querySelector(".tablink").classList.add("w3-red"); 
    // Ensure others are not red (simple reset)
    const links = document.querySelectorAll(".tablink");
    links[1].classList.remove("w3-red");
    links[0].classList.add("w3-red");
}
</script>

</body>
</html>
"""
    with open("index.html", "w") as f:
        f.write(html_content)
    print("Generated index.html")

def main():
    print("Starting site update...")
    generate_manifest()
    generate_app_shell()
    print("Site update complete.")

if __name__ == "__main__":
    main()

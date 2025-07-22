# Phase 7C: CLI ASCII Charts & Heatmaps - Implementation Guide

## 🚀 Overview
Phase 7C brings **advanced ASCII visualizations** to the AI Code Security Auditor CLI, transforming terminal output into rich, interactive visual experiences using the Rich library and advanced terminal rendering techniques.

## ✨ New Features

### 1. **Sparkline Trends** 
Tiny inline charts showing vulnerability patterns over time:
```bash
# Enhanced trends with sparklines
python auditor/cli.py trends --visual --days 30
```
**Output:**
```
📈 Vulnerability Trends ▁▂▄▆█▅▃▂▃▄▅▄▂▁
Critical:  ▁▃▅█▅▃▁▁▃▅▃▁▁▁ (last 14 days)
High:      ▂▄▆▇█▆▄▂▄▆▄▂▁▁ (last 14 days)
```

### 2. **Gradient Heatmaps**
ANSI 256-color gradient blocks showing vulnerability density:
```bash
# Enhanced heatmap with gradients
python auditor/cli.py heatmap --visual --color-scheme security
```
**Output:**
```
🔥 Security Heatmap - Vulnerability Density by Directory
Legend: █ Very High  ▓ High  ▒ Medium  ░ Low  · Minimal
/app/src/core      │██████████│ 45 hits (20 files)
/app/src/api       │████████··│ 38 hits (15 files)
/app/src/utils     │▓▓▓▓▓·····│ 25 hits (8 files)
```

### 3. **Enhanced Bar & Pie Charts**
Horizontal severity bars and ASCII pie charts:
```bash
# Visual summary with charts
python auditor/cli.py summary --visual --color-scheme security
```
**Output:**
```
📊 Vulnerability Severity Distribution:
CRITICAL ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  17.8% (8)
HIGH     █████████████████░░░░░░░░░░░░░░░░░░  51.1% (23)

🥧 Severity Distribution (Pie Chart):
┌─────┐
│███│    ● MEDIUM: 45 (51.1%)
│██░│    ◕ HIGH: 23 (26.1%)
│█░░│    ◔ CRITICAL: 8 (9.1%)
└─────┘
```

### 4. **Interactive Features**
Navigation hints and drill-down commands:
```bash
💡 Drill down: Use 'auditor summary --scan-id 2024-01-15' for details
💡 Drill down: Use 'auditor scan --path /app/src' to rescan directory
🧭 Navigation Tips:
  • Use --limit to control data range
  • Use --since/--until for date filtering
```

## 🎨 Color Schemes

### Available Schemes:
- **`default`**: Full spectrum rainbow gradient (blue → red)
- **`security`**: Security-themed (green → yellow → red) 
- **`dark`**: Dark theme friendly colors
- **`monochrome`**: Unicode block characters (fallback)

### Usage:
```bash
# Use security color scheme
python auditor/cli.py trends --visual --color-scheme security

# Force monochrome for compatibility
python auditor/cli.py heatmap --visual --color-scheme monochrome
```

## 🖥️ Terminal Compatibility

### Automatic Detection:
- **256-color support**: Automatically detected via `$TERM` and `$COLORTERM`
- **Fallback mode**: Gracefully degrades to monochrome unicode blocks
- **Width adaptation**: Charts adapt to terminal width

### Test Capabilities:
```bash
# Test your terminal's visual capabilities
python auditor/cli.py visual-test --test-colors --test-charts
```

## 📝 Updated CLI Commands

### Enhanced Commands with `--visual` Flag:

#### 1. **Trends Command**
```bash
python auditor/cli.py trends --visual [OPTIONS]

Options:
  --visual                    🚀 Enable enhanced ASCII visualizations
  --color-scheme [default|security|dark|monochrome]
  --days INTEGER             Number of days to show trends for
  --width INTEGER            Chart width for ASCII output
```

#### 2. **Heatmap Command** 
```bash
python auditor/cli.py heatmap --visual [OPTIONS]

Options:
  --visual                    🚀 Enable enhanced gradient heatmap
  --color-scheme [default|security|dark|monochrome]
  --width INTEGER            Heatmap width in characters
  --scan-id TEXT             Specific scan ID (optional)
```

#### 3. **Summary Command**
```bash
python auditor/cli.py summary --visual [OPTIONS]

Options:
  --visual                    🚀 Enable enhanced visuals with pie charts
  --color-scheme [security|default|dark|monochrome]
  --scan-id TEXT             Specific scan ID (optional)
  --severity [critical|high|medium|low]
```

#### 4. **Visual Test Command** (NEW)
```bash
python auditor/cli.py visual-test [OPTIONS]

Options:
  --test-colors              Test color support and display palette
  --test-charts              Display sample charts and visualizations
  --color-scheme [default|security|dark|monochrome]
```

## 🛠️ Technical Implementation

### Architecture:
```
cli_visuals/
├── __init__.py          # Package exports
├── terminal.py          # Terminal capabilities detection
├── charts.py            # Sparklines, bar charts, pie charts
├── heatmap.py           # Gradient heatmaps with 256-color
├── formatters.py        # Visual formatter integration
```

### Key Components:

#### 1. **Terminal Capabilities** (`terminal.py`)
```python
from cli_visuals.terminal import terminal

# Check if terminal supports 256 colors
if terminal.supports_256_colors:
    # Use rich gradients
else:
    # Fall back to monochrome
```

#### 2. **Chart Generation** (`charts.py`)
```python
from cli_visuals.charts import SparklineChart, BarChart, PieChart

sparkline = SparklineChart(color_scheme)
trend_line = sparkline.generate_sparkline(data, width=20)
```

#### 3. **Visual Formatters** (`formatters.py`)
```python
from cli_visuals.formatters import create_visual_formatter

formatter = create_visual_formatter('security', no_colors=False)
output = formatter.format_trends_visual(trend_data)
```

## 🔧 Configuration

### Environment Variables:
- `TERM`: Terminal type (e.g., `xterm-256color`)
- `COLORTERM`: Color capability (e.g., `truecolor`)
- `FORCE_COLOR`: Force color output even in non-TTY

### Color Detection Logic:
1. Check `$COLORTERM` for `truecolor`/`24bit`
2. Check `$TERM` for `256color`/`xterm` 
3. Verify Rich console color support
4. Fall back to monochrome if detection fails

## 📊 Examples & Use Cases

### 1. **Daily Security Monitoring**
```bash
# Quick daily overview with sparklines
python auditor/cli.py trends --visual --days 7 --color-scheme security
```

### 2. **Repository Analysis**
```bash
# Comprehensive repository heatmap
python auditor/cli.py heatmap --visual --width 60 --color-scheme default
```

### 3. **Security Dashboard**
```bash
# Executive summary with pie charts
python auditor/cli.py summary --visual --color-scheme security
```

### 4. **CI/CD Integration**
```bash
# Automated reports with fallback compatibility
python auditor/cli.py scan --output github | \
python auditor/cli.py summary --visual --color-scheme monochrome
```

## 🧪 Testing & Validation

### Run Visual Tests:
```bash
# Complete visual capability test
python auditor/cli.py visual-test --test-colors --test-charts

# Run demo with all features  
python visual_demo.py

# Test specific color schemes
python auditor/cli.py visual-test --color-scheme security --test-charts
```

### Expected Output Verification:
- ✅ **Sparklines**: Unicode block characters in gradual heights
- ✅ **Gradients**: Smooth color transitions or block patterns
- ✅ **Charts**: Proper scaling and proportional visualization
- ✅ **Fallbacks**: Monochrome mode in limited terminals

## 🚀 Future Enhancements (Post-Phase 7C)

### Potential Additions:
- **Interactive Navigation**: Arrow key navigation through charts
- **Live Updates**: Real-time chart updates via WebSocket
- **Export Formats**: SVG/PNG export for visual charts
- **Custom Themes**: User-defined color schemes
- **3D ASCII**: Isometric visualization for complex data

## 📚 Dependencies

### Required:
- `rich>=13.0.0` - Terminal rendering and color support
- `click>=8.0.0` - CLI framework and option parsing
- `colorama>=0.4.6` - Cross-platform color support

### Automatic Fallbacks:
- Windows: Uses `colorama` for ANSI support
- Limited terminals: Monochrome unicode blocks
- No TTY: Plain text with symbols

---

## ✅ Phase 7C Success Criteria

- [x] **Sparkline Integration**: Inline trend visualization in audit output
- [x] **Gradient Heatmaps**: ANSI 256-color gradients for vulnerability density  
- [x] **Enhanced Charts**: Bar charts and pie charts for severity distribution
- [x] **Color Scheme Support**: 4 color schemes with automatic detection
- [x] **Terminal Compatibility**: Graceful fallback for all terminal types
- [x] **Interactive Features**: Navigation hints and drill-down commands
- [x] **Documentation**: Complete usage guide and examples

**🎉 Phase 7C: CLI ASCII Charts & Heatmaps - COMPLETE!**
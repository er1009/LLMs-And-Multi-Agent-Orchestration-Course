# Route Guide System - GUI User Guide

## Overview

The Route Guide System includes a **beautiful, user-friendly graphical interface** that makes it easy for anyone to use, regardless of technical expertise.

## Launching the GUI

### Method 1: Using the Launcher Script (Easiest)

```bash
# Navigate to project directory
cd /Users/eldadron/dev/agents-course/ex4

# Activate virtual environment
source .venv/bin/activate

# Run GUI
python run_gui.py
```

### Method 2: Direct Module Import

```bash
python -m src.gui
```

## GUI Layout

```
┌─────────────────────────────────────────────────────────────┐
│          🗺️ Route Guide System                              │
├─────────────────────────────────────────────────────────────┤
│  Route Information                                          │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Source Address:      [Tagor 40, Tel Aviv         ]    │ │
│  │ Destination Address: [Yehuda HaNasi 38, Tel Aviv ]    │ │
│  └────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Configuration                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Max Waypoints: [20 ▲▼]                                 │ │
│  │ ☑ Enable Parallel Execution (3x faster)                │ │
│  │ Log Level: [INFO ▼]                                    │ │
│  └────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  [🚀 Start Route Guide] [⏹ Stop] [🗑 Clear] [💾 Save]      │
├─────────────────────────────────────────────────────────────┤
│  Progress: Ready to process route                          │
│  [████████████████████████████████████████] Indeterminate  │
├─────────────────────────────────────────────────────────────┤
│  Results                                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ ════════════════════════════════════════              │ │
│  │ ROUTE GUIDE RESULTS                                   │ │
│  │ ════════════════════════════════════════              │ │
│  │                                                        │ │
│  │ 📍 From: Tagore St 40, Tel Aviv-Yafo, Israel         │ │
│  │ 📍 To: Yehuda ha-Nasi St 38, Tel Aviv-Yafo, Israel   │ │
│  │                                                        │ │
│  │ Distance: 1.04 km                                     │ │
│  │ Duration: 4 minutes                                   │ │
│  │ Stops: 5                                              │ │
│  │ Processing Time: 91.32 seconds                        │ │
│  │                                                        │ │
│  │ ════════════════════════════════════════              │ │
│  │                                                        │ │
│  │ Stop 1: Head north toward Tagore St                  │ │
│  │ ────────────────────────────────────────              │ │
│  │ ℹ️ Type: INFO                                         │ │
│  │ 📝 Title: Tagore Street - Named After Nobel...       │ │
│  │ 📄 Content: This street is likely named after...     │ │
│  │ 💡 Reason: The historical information...             │ │
│  │                                                        │ │
│  │ [Scrollable content continues...]                     │ │
│  └────────────────────────────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│ Status: Successfully processed 5 stops                      │
└─────────────────────────────────────────────────────────────┘
```

## Step-by-Step Usage

### 1. Enter Route Information

**Source Address:**
- Type or paste your starting address
- Examples:
  - `Tagor 40, Tel Aviv`
  - `1600 Amphitheatre Parkway, Mountain View, CA`
  - `Eiffel Tower, Paris, France`

**Destination Address:**
- Type or paste your destination address
- Same format as source

### 2. Configure Settings (Optional)

**Max Waypoints** (1-50):
- Default: 20
- Lower number = faster processing
- Higher number = more detailed route coverage
- Use spinner buttons (▲▼) or type number directly

**Parallel Execution**:
- ✅ **Checked (Recommended)**: 3x faster processing
  - Video, Music, and Info agents run simultaneously
  - Typical: ~10 seconds per waypoint
- ☐ **Unchecked**: Sequential processing
  - Agents run one after another
  - Typical: ~30 seconds per waypoint
  - Use for debugging or troubleshooting

**Log Level**:
- **DEBUG**: Detailed execution logs (for developers)
- **INFO**: Normal operation logs (recommended)
- **WARNING**: Only warnings and errors
- **ERROR**: Only errors

### 3. Run the Route Guide

Click **🚀 Start Route Guide** button

**What happens:**
1. System validates your addresses
2. Retrieves route from Google Maps
3. Extracts waypoints (major junctions)
4. **For each waypoint** (in parallel):
   - Video Agent finds relevant YouTube videos
   - Music Agent recommends appropriate music
   - Info Agent provides historical facts
   - Choice Agent selects the best content
5. Results displayed in real-time

**During Processing:**
- Progress bar animates
- Progress label shows status
- Status bar updates
- **Stop button** becomes active (to cancel if needed)

### 4. View Results

**Results are displayed with:**

- **Color coding:**
  - 🔵 Blue headers
  - 🟢 Green stop titles
  - ⚫ Black content
  - 🔘 Gray metadata

- **Content icons:**
  - 🎥 Video recommendations
  - 🎵 Music recommendations
  - ℹ️ Information/historical facts

- **Scrollable area**: Use scroll bar or mouse wheel

### 5. Save Results

Click **💾 Save Results** button

**Options:**
1. Choose save location
2. Default filename: `route_results_YYYYMMDD_HHMMSS.json`
3. Save as JSON file (can be opened in any text editor)

### 6. Clear Results

Click **🗑 Clear Results** to:
- Remove all displayed results
- Reset progress indicator
- Prepare for next route

## Tips & Best Practices

### ✅ Do's

1. **Use Full Addresses**: Include city, state/country for accuracy
2. **Enable Parallel Execution**: Unless debugging
3. **Save Results**: Export before clearing or closing
4. **Start with Fewer Waypoints**: Test with 5-10 for quick results
5. **Check Progress**: Monitor progress label and status bar

### ❌ Don'ts

1. **Don't Close During Processing**: Let it complete or use Stop button
2. **Don't Use Vague Addresses**: "downtown" → "123 Main St, City, State"
3. **Don't Exceed 50 Waypoints**: System limits for performance
4. **Don't Forget API Key**: Ensure .env file has valid GOOGLE_MAPS_API_KEY

## Troubleshooting

### GUI Won't Launch

**Error: "Configuration Error"**
- **Cause**: Missing or invalid .env file
- **Solution**:
  ```bash
  cp .env.example .env
  # Edit .env and add your GOOGLE_MAPS_API_KEY
  ```

**Error: "ModuleNotFoundError"**
- **Cause**: Virtual environment not activated or dependencies not installed
- **Solution**:
  ```bash
  source .venv/bin/activate
  pip install -r requirements.txt
  ```

### Processing Fails

**"API key not found" or "API error"**
- Check `.env` file has valid GOOGLE_MAPS_API_KEY
- Verify API key has Directions API enabled

**"Claude CLI timeout"**
- Check Claude CLI is installed: `claude --version`
- Authenticate: `claude auth login`
- Increase timeout in config/config.yaml

**Route not found**
- Use more specific addresses
- Check spelling
- Try adding country name

### Slow Performance

**Taking too long?**
- Enable "Parallel Execution" checkbox
- Reduce "Max Waypoints" value
- Check internet connection
- Claude CLI response time varies

### Results Not Saving

**Save button disabled?**
- Results must be generated first
- Click "Start Route Guide" and wait for completion

**File save dialog won't open?**
- Check file system permissions
- Try different save location

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `Enter` in address fields | Focus next field |
| `Tab` | Navigate between fields |
| `Ctrl/Cmd + S` | (Future) Quick save |
| `Esc` | (Future) Stop processing |

## Advanced Features

### Custom Configuration

Edit `config/config.yaml` for advanced options:
- Agent timeouts
- API retry settings
- Waypoint extraction strategy
- Output formatting

Changes take effect on next GUI launch.

### Viewing Detailed Logs

Set Log Level to **DEBUG** to see:
- Thread execution details
- API call timings
- Agent decision rationale
- Error stack traces

Logs appear in terminal where GUI was launched.

## GUI Components

### Input Section
- **Purpose**: Enter route information
- **Validation**: Checks for empty fields before processing

### Configuration Section
- **Purpose**: Adjust system settings
- **Persistence**: Settings reset on each launch (not saved)

### Control Buttons
- **Start**: Begins route processing
- **Stop**: Requests cancellation (completes current waypoint)
- **Clear**: Removes results from display
- **Save**: Exports results to JSON file

### Progress Section
- **Label**: Textual status updates
- **Bar**: Visual progress indicator (indeterminate during processing)

### Results Section
- **Scrollable**: Handle long results
- **Formatted**: Color-coded, structured output
- **Read-only**: Can't edit results directly

### Status Bar
- **Bottom of window**: Current operation status
- **Updates**: Real-time feedback

## Comparison: GUI vs CLI

| Feature | GUI | CLI |
|---------|-----|-----|
| **Ease of Use** | ⭐⭐⭐⭐⭐ Beginner-friendly | ⭐⭐⭐ Requires terminal knowledge |
| **Visual Feedback** | ✅ Progress bar, status | ❌ Text only |
| **Configuration** | ✅ Point-and-click | ❌ Command-line flags |
| **Results Display** | ✅ Formatted, color-coded | ✅ JSON output |
| **Save Results** | ✅ File dialog | ✅ Auto-saves to results/ |
| **Automation** | ❌ Manual operation | ✅ Can script |
| **Resource Usage** | Slightly higher (GUI overhead) | Lower |

**Recommendation:**
- **GUI**: For interactive use, learning, demonstrations
- **CLI**: For automation, scripts, headless servers

## Screenshots Equivalent (Text Description)

### Main Window (Ready State)
- Clean, organized layout
- Professional color scheme
- Clear section headers
- Intuitive button placement
- Pre-filled example addresses (Tel Aviv route)

### Processing State
- Animated progress bar
- Status updates ("Processing waypoint 3 of 5...")
- Stop button enabled
- Start button disabled (prevents duplicate runs)

### Results State
- Structured, readable results
- Color-coded content types
- Scrollable for long routes
- Save button enabled
- Clear status message

## Future Enhancements

Planned GUI features:
- 📍 **Map View**: Visual route display
- 📊 **Statistics Dashboard**: Charts and graphs
- 🎨 **Theme Selection**: Light/dark modes
- 💾 **Auto-save**: Automatic result backup
- ⌨️ **Keyboard Shortcuts**: Power user features
- 📜 **History**: Previously processed routes
- 🔖 **Favorites**: Save common routes
- 🌐 **Multi-language**: Localization support

## Getting Help

**Within GUI:**
- Hover over elements (tooltips - future feature)
- Check status bar for feedback
- Review error messages in results area

**External Resources:**
- **README.md**: General project documentation
- **ARCHITECTURE.md**: Technical details
- **PRD.md**: Feature specifications
- **GitHub Issues**: Report bugs or request features

## Conclusion

The Route Guide System GUI provides a **simple, beautiful, and powerful** interface for discovering contextual content along your routes.

**No technical expertise required** - just enter your addresses and click Start!

---

**Version**: 1.0.0
**Last Updated**: 2025-11-29
**Status**: Production Ready

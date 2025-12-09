# Quick Reference: Dashboard Creation

## 🚀 Quick Start

```bash
# 1. Make sure API key is set
export GROQ_API_KEY='your-key-here'

# OR use .env file
echo "GROQ_API_KEY=your-key-here" > .env

# 2. Run simple test
python3 examples/create_dashboard_with_agent.py --test

# 3. Run full dashboard creation
python3 examples/create_dashboard_with_agent.py
```

---

## 📊 What Gets Generated

The agent creates a complete dashboard with:

```
demo/
├── src/
│   ├── app/
│   │   └── dashboard/
│   │       └── page.tsx           # Main dashboard page
│   ├── components/
│   │   ├── Sidebar.tsx            # Collapsible sidebar with animations
│   │   ├── TabNavigation.tsx      # Tab bar with 4 tabs
│   │   ├── Header.tsx             # Dashboard header
│   │   ├── Footer.tsx             # Dashboard footer
│   │   └── StatCard.tsx           # Metric cards
│   └── store/
│       ├── store.ts               # Redux store configuration
│       ├── hooks.ts               # Typed Redux hooks
│       ├── sidebarSlice.ts        # Sidebar state slice
│       ├── tabnavigationSlice.ts  # Tab state slice
│       └── ...                    # Other slices
├── package.json
├── tsconfig.json
├── next.config.js
└── postcss.config.js
```

---

## 🔍 Monitoring Progress

### Real-time Monitoring
```bash
# Watch the log file as it's created
tail -f dashboard_run.log

# Or run with tee to see output and save to file
python3 examples/create_dashboard_with_agent.py 2>&1 | tee dashboard_run.log
```

### Check Status
```bash
# View iteration progress
grep "ITERATION" dashboard_run.log

# See which tools were executed
grep "Using Tool:" dashboard_run.log

# Check for errors
grep "ERROR\|FAILED" dashboard_run.log

# See successful completions
grep "SUCCESS" dashboard_run.log
```

---

## 📈 Understanding the Output

### Console Output Format

```
================================================================================
ITERATION 1/15
================================================================================

🤔 Deciding next action...
📌 Action Type: tool_use

🔧 Using Tool: generate_page_with_components
💬 Message: Generating dashboard with components
📝 Parameters: {
  "page_name": "dashboard",
  "page_path": "./demo/src/app/dashboard/page.tsx",
  "components": [...]
}
⚙️  Executing...
✅ SUCCESS!
📦 Data: {...}
```

**Key Indicators:**
- 🤔 = AI is thinking/deciding
- 🔧 = Tool is being executed
- ✅ = Success
- ❌ = Failure/Error
- 📦 = Result data

---

## 🐛 Troubleshooting

### Problem: "Tool not found: generate_redux_store"
**Solution:** This was fixed! The tool is now correctly named `generate_redux_setup`.

### Problem: "API key not found"
**Solution:** 
```bash
# Set the API key
export GROQ_API_KEY='your-key-here'

# Or create .env file
echo "GROQ_API_KEY=your-key-here" > .env

# Verify it's set
echo $GROQ_API_KEY
```

### Problem: "429 Too Many Requests"
**Solution:** Groq API rate limit reached. The agent will automatically retry after waiting. You can:
- Wait for the retry
- Use a lower rate of requests
- Upgrade your Groq API plan

### Problem: Agent keeps repeating same action
**Solution:** This is an LLM behavior. The agent should move forward after 2-3 iterations. Check if:
- The tool is actually succeeding
- The files are being created
- There are no errors in the logs

### Problem: No files generated
**Solution:** Check:
```bash
# Verify demo directory exists
ls -la demo/

# Check if files were created
find demo/ -type f -name "*.tsx" -o -name "*.ts"

# Look for errors in the log
grep "ERROR" dashboard_run.log
```

---

## 🧪 Testing

### Minimal Test
```bash
python3 examples/create_dashboard_with_agent.py --test
```
Expected output: Single button component created in ~10 seconds

### Full Test
```bash
python3 examples/create_dashboard_with_agent.py
```
Expected output: Complete dashboard with 10+ files in ~2-3 minutes

---

## 📊 Performance Metrics

| Metric | Test Mode | Full Dashboard |
|--------|-----------|----------------|
| Execution Time | ~10-15s | ~60-120s |
| API Calls | ~3-5 | ~15-25 |
| Files Generated | 1 | 10-15 |
| Iterations | 1-3 | 5-10 |

---

## 🔧 Configuration

### Adjusting Max Iterations
```python
# In create_dashboard_with_agent.py
result = await agent.execute(user_request, max_iterations=15)  # Increase if needed
```

### Changing Model
```python
# In create_dashboard_with_agent.py
agent = AICodeAgent(groq_api_key=api_key, model="llama-3.1-70b-versatile")
```

### Enable Debug Logging
```python
# At the top of the script
logging.basicConfig(
    level=logging.DEBUG,  # Change to DEBUG
    format='%(asctime)s [%(levelname)s] %(message)s'
)
```

---

## 📝 Execution Report

After completion, check the JSON report:

```bash
cat dashboard_creation_report.json | python3 -m json.tool
```

Report contents:
```json
{
  "success": true,
  "iterations": 5,
  "tool_results": [...],
  "errors": [],
  "response": "Summary of what was created",
  "metadata": {
    "execution_time_seconds": 45.67,
    "timestamp": "2025-12-09T14:11:45.123456",
    "files_generated": 12,
    "total_size_bytes": 34567
  }
}
```

---

## 🎯 Expected Features

The generated dashboard includes:

### ✅ Sidebar Menu
- Collapsible/expandable
- Smooth CSS transitions
- Active menu item highlighting
- Icons with hover effects
- Responsive (auto-collapse on mobile)
- Menu items: Dashboard, Analytics, Reports, Settings, Profile

### ✅ Tab Navigation
- 4 tabs: Overview, Analytics, Data, Settings
- Active tab indicator
- Smooth transitions
- Redux-connected state

### ✅ Redux State Management
- Centralized store
- Slices for UI state (sidebar, tabs)
- Slices for component data
- Typed hooks (useAppSelector, useAppDispatch)
- Mock data generation

### ✅ Professional UX
- Tailwind CSS styling
- TypeScript type safety
- Responsive design
- Accessibility features
- Modern React patterns

---

## 💡 Tips

1. **Run test first** to verify everything works
2. **Monitor the logs** to catch issues early
3. **Check generated files** after each run
4. **Save logs** for debugging: `2>&1 | tee dashboard_run.log`
5. **Review the report** to understand what was created

---

**For detailed debugging info, see:** `DASHBOARD_DEBUG_IMPROVEMENTS.md`

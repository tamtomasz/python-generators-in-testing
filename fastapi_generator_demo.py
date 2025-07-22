"""
FastAPI + WebSockets Demo: Python Generators for UI Testing

This is a much better approach for real-time updates using WebSockets.
No page refreshes, true real-time streaming, and clean separation of concerns.
"""

from fastapi import FastAPI, WebSocket, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import asyncio
import json
import random
import uuid
from datetime import datetime
from typing import AsyncGenerator, Dict, Any

app = FastAPI(title="Generators in UI Testing - FastAPI Demo")


class AsyncUITestDataGenerator:
    """Async generator class for real-time test data"""

    def __init__(self):
        self.item_counter = 0
        self.test_scenarios = [
            "User Login Test",
            "Form Validation Test",
            "Navigation Test",
            "Data Entry Test",
            "Search Functionality Test",
            "File Upload Test",
            "Modal Dialog Test",
            "Dropdown Selection Test",
            "Checkbox Interaction Test",
            "Button Click Test",
        ]
        self.statuses = ["Pending", "Running", "Passed", "Failed", "Skipped"]
        self.priorities = ["Low", "Medium", "High", "Critical"]

    async def generate_test_items(
        self, delay: float = 1.0
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Async generator that yields test data at specified intervals"""
        while True:
            await asyncio.sleep(delay)
            self.item_counter += 1

            test_item = {
                "id": str(uuid.uuid4())[:8],
                "test_name": random.choice(self.test_scenarios),
                "status": random.choice(self.statuses),
                "priority": random.choice(self.priorities),
                "duration": round(random.uniform(0.5, 30.0), 2),
                "timestamp": datetime.now().strftime("%H:%M:%S"),
                "sequence": self.item_counter,
                "browser": random.choice(["Chrome", "Firefox", "Safari", "Edge"]),
                "environment": random.choice(["Dev", "Staging", "Production"]),
            }

            yield test_item


# Global generator instance
generator = AsyncUITestDataGenerator()


@app.get("/", response_class=HTMLResponse)
async def get_homepage():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Python Generators for UI Testing - FastAPI Demo</title>
    <style>
        body { 
            font-family: "Source Sans Pro", -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; 
            margin: 0; 
            padding: 0; 
            background-color: #1a1d23; 
            color: #e1e5e9;
        }
        .app-container {
            display: flex;
            min-height: 100vh;
        }
        .sidebar {
            width: 320px;
            background: #2d3139;
            border-right: 1px solid #3f434a;
            padding: 1.5rem;
            overflow-y: auto;
            box-shadow: 2px 0 8px rgba(0, 0, 0, 0.2);
        }
        .main-content {
            flex: 1;
            padding: 1.5rem;
            overflow-x: auto;
        }
        .container { 
            max-width: none;
            margin: 0;
            padding: 0;
        }
        h1 { 
            color: #3b82f6; 
            font-weight: 600; 
            margin-bottom: 0.5rem;
            font-size: 2rem;
        }
        .subtitle {
            color: #9ca3af;
            margin-bottom: 2rem;
            font-size: 0.95rem;
        }
        .sidebar h2 {
            color: #3b82f6;
            font-size: 1.25rem;
            font-weight: 600;
            margin: 0 0 1.5rem 0;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #3b82f6;
        }
        .sidebar h3 {
            color: #d1d5db;
            font-size: 1rem;
            font-weight: 600;
            margin: 1.5rem 0 0.75rem 0;
        }
        .control-group { 
            background: #252830; 
            padding: 1.5rem; 
            border-radius: 0.5rem; 
            margin-bottom: 2rem; 
            border: 1px solid #3f434a;
        }
        .control-group:hover {
            border-color: #3b82f6;
            transition: border-color 0.2s;
        }
        .control-group h3 {
            margin-top: 0;
            margin-bottom: 1.5rem;
        }
        .form-group {
            margin-bottom: 1.5rem;
        }
        .form-group:last-child {
            margin-bottom: 0;
        }
        .form-group label {
            display: block;
            margin-bottom: 0.75rem;
            color: #d1d5db;
            font-size: 0.875rem;
            font-weight: 500;
        }
        .control-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1rem;
            margin-bottom: 1.5rem;
        }
        .control-buttons button {
            margin: 0;
            padding: 0.875rem 1rem;
            font-size: 0.875rem;
            font-weight: 600;
        }
        .full-width-button {
            width: 100%;
            margin-bottom: 1rem;
            padding: 0.75rem 1rem;
        }
        .full-width-button:last-child {
            margin-bottom: 0;
        }
        input[type="range"] {
            width: 100%;
            margin: 0.75rem 0;
            background: transparent;
            -webkit-appearance: none;
            appearance: none;
        }
        input[type="range"]::-webkit-slider-track {
            background: #4b5563;
            height: 6px;
            border-radius: 3px;
        }
        input[type="range"]::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            background: #3b82f6;
            height: 18px;
            width: 18px;
            border-radius: 50%;
            cursor: pointer;
        }
        input[type="range"]::-moz-range-track {
            background: #4b5563;
            height: 6px;
            border-radius: 3px;
            border: none;
        }
        input[type="range"]::-moz-range-thumb {
            background: #3b82f6;
            height: 18px;
            width: 18px;
            border-radius: 50%;
            cursor: pointer;
            border: none;
        }
        input[type="checkbox"] {
            transform: scale(1.3);
            margin-right: 0.75rem;
            accent-color: #3b82f6;
        }
        label {
            font-weight: 500;
            color: #d1d5db;
            cursor: pointer;
        }
        .form-control {
            margin-bottom: 1.25rem;
        }
        .form-control label {
            display: block;
            margin-bottom: 0.75rem;
            color: #9ca3af;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .frequency-display {
            background: #3b82f6;
            color: white;
            padding: 0.375rem 0.75rem;
            border-radius: 0.25rem;
            font-weight: 600;
            font-size: 0.875rem;
            display: inline-block;
            margin-left: 0.5rem;
        }
        .control-buttons {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.75rem;
            margin-bottom: 1rem;
        }
        .control-buttons button {
            margin: 0;
            padding: 0.75rem;
            font-size: 0.875rem;
        }
        .batch-controls {
            display: flex;
            flex-direction: column;
            gap: 0.75rem;
        }
        input[type="number"] {
            background: #4b5563;
            border: 1px solid #6b7280;
            color: #e1e5e9;
            padding: 0.75rem;
            border-radius: 0.375rem;
            font-size: 0.875rem;
            width: 100%;
        }
        input[type="number"]:focus {
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
        }
        #items-per-page {
            width: 80px;
        }
        #max-items {
            width: 80px;
        }
        .status { 
            padding: 0.875rem 1.25rem; 
            margin: 1.5rem 0; 
            border-radius: 0.5rem; 
            font-weight: 500;
            border-left: 4px solid;
        }
        .status.running { 
            background: #1f2d2d; 
            color: #6ee7b7; 
            border-left-color: #6ee7b7;
        }
        .status.stopped { 
            background: #2d1f1f; 
            color: #fca5a5; 
            border-left-color: #fca5a5;
        }
        .status.info { 
            background: #1f2937; 
            color: #93c5fd; 
            border-left-color: #3b82f6;
        }
        .test-item { 
            display: grid; 
            grid-template-columns: 40px 80px 3fr 1fr 1fr 2fr 50px; 
            gap: 1rem; 
            padding: 0.875rem 1.25rem; 
            border-bottom: 1px solid #3f434a; 
            align-items: center;
            background: #252830;
            transition: background-color 0.15s;
        }
        .test-item:nth-child(even) { 
            background: #2d3139; 
        }
        .test-item:hover { 
            background: #323741;
            border-left: 3px solid #3b82f6;
            padding-left: calc(1.25rem - 3px);
        }
        .header { 
            font-weight: 600; 
            background: #3b82f6; 
            color: white; 
            padding: 1rem 1.25rem; 
            border-radius: 0.5rem 0.5rem 0 0;
            font-size: 0.875rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .pagination { 
            margin: 1.5rem 0; 
            text-align: center; 
            padding: 1.25rem;
            background: #252830;
            border-radius: 0.5rem;
            border: 1px solid #3f434a;
        }
        button { 
            background: #3b82f6;
            color: white;
            border: none;
            padding: 0.625rem 1.25rem; 
            margin: 0.25rem; 
            cursor: pointer;
            border-radius: 0.375rem;
            font-weight: 500;
            transition: all 0.2s;
            font-size: 0.875rem;
        }
        button:hover {
            background: #2563eb;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.25);
        }
        button:disabled {
            background: #4b5563;
            color: #9ca3af;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }
        .btn-danger { 
            background: #ef4444; 
            color: white; 
            border: none; 
            border-radius: 0.25rem; 
            padding: 0.375rem 0.625rem; 
            cursor: pointer;
            font-size: 0.75rem;
            transition: all 0.2s;
        }
        .btn-danger:hover { 
            background: #dc2626;
            transform: scale(1.05);
        }
        .btn-warning { 
            background: #f59e0b; 
            color: white; 
            border: none; 
            border-radius: 0.375rem; 
            padding: 0.625rem 1.25rem; 
            cursor: pointer;
            font-weight: 500;
            transition: all 0.2s;
        }
        .btn-warning:hover { 
            background: #d97706;
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(245, 158, 11, 0.25);
        }
        .btn-warning:disabled {
            background: #4b5563;
            color: #9ca3af;
            transform: none;
            box-shadow: none;
        }
        .delete-btn { 
            font-size: 0.875rem; 
            padding: 0.25rem 0.5rem; 
        }
        .selection-controls { 
            margin: 1.5rem 0; 
            padding: 1.25rem; 
            background: #252830; 
            border-radius: 0.5rem; 
            border: 1px solid #3f434a;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }
        .metrics { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 1.25rem; 
            margin: 1.5rem 0; 
        }
        .metric { 
            text-align: center; 
            padding: 1.5rem; 
            background: #252830; 
            border-radius: 0.5rem; 
            border: 1px solid #3f434a;
            transition: all 0.2s;
        }
        .metric:hover {
            border-color: #3b82f6;
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.3);
        }
        .metric > div:first-child {
            font-size: 0.875rem;
            color: #9ca3af;
            margin-bottom: 0.75rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        .metric > div:last-child {
            font-size: 2rem;
            font-weight: 700;
            color: #e1e5e9;
        }
    </style>
</head>
<body>
    <div class="app-container">
        <div class="sidebar">
            <div class="logo">
                <span>🔄 Python Generators UI Testing</span>
            </div>
            
            <h2>Controls</h2>
            
            <div class="control-group">
                <h3>Generator Controls</h3>
                <div class="form-group">
                    <label>Update Frequency: 
                        <input type="range" id="frequency" min="0.5" max="5" step="0.5" value="2"> 
                        <span id="freq-value" class="frequency-display">2.0</span> seconds
                    </label>
                </div>
                <div class="control-buttons">
                    <button id="start-btn" onclick="startGeneration()">▶️ Start</button>
                    <button id="stop-btn" onclick="stopGeneration()" disabled>⏹️ Stop</button>
                </div>
                <button class="full-width-button" onclick="clearItems()">🗑️ Clear All</button>
                <button class="full-width-button" onclick="generateBatch()">📦 Generate Batch (20 items)</button>
            </div>
            
            <div class="control-group">
                <h3>Display Settings</h3>
                <div class="form-group">
                    <label for="items-per-page">Items per page:</label>
                    <input type="number" id="items-per-page" min="5" max="50" value="10" onchange="changeItemsPerPage()">
                </div>
                <div class="form-group">
                    <label for="max-items">Max items to keep:</label>
                    <input type="number" id="max-items" min="10" max="1000" value="100" onchange="changeMaxItems()">
                </div>
            </div>
            
            <div id="status" class="status info">💡 Click "Start" to begin generating test data</div>
        </div>
        
        <div class="main-content">
            <h1>Python Generators for UI Testing - FastAPI Demo</h1>
            
            <div class="metrics" id="metrics">
                <div class="metric"><div>Total Tests</div><div id="total">0</div></div>
                <div class="metric"><div>Passed</div><div id="passed">0</div></div>
                <div class="metric"><div>Failed</div><div id="failed">0</div></div>
                <div class="metric"><div>Running</div><div id="running">0</div></div>
                <div class="metric"><div>Pending</div><div id="pending">0</div></div>
            </div>
            
            <h3>📋 Test Results (Real-time Updates)</h3>
            
            <div class="selection-controls">
                <label><input type="checkbox" id="select-all" onchange="toggleSelectAll()"> Select All</label>
                <button class="btn-warning" onclick="removeSelected()" id="remove-selected-btn" disabled>🗑️ Remove Selected (<span id="selected-count">0</span>)</button>
            </div>
            
            <div class="test-item header">
                <div>☑️</div>
                <div>#</div>
                <div>Test Name</div>
                <div>Status</div>
                <div>Priority</div>
                <div>Details</div>
                <div>🗑️</div>
            </div>
            <div id="test-list"></div>
            
            <div class="pagination">
                <button onclick="previousPage()">⬅️ Previous</button>
                <span id="page-info">Page 1 of 1</span>
                <button onclick="nextPage()">➡️ Next</button>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let testItems = [];
        let currentPage = 0;
        let itemsPerPage = 10;
        let maxItemsToKeep = 100;
        let isGenerating = false;
        
        function connectWebSocket() {
            ws = new WebSocket(`ws://localhost:8000/ws`);
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                
                if (data.type === 'new_item') {
                    testItems.push(data.item);
                    if (testItems.length > maxItemsToKeep) { // Keep only the last maxItemsToKeep items
                        testItems = testItems.slice(-maxItemsToKeep);
                    }
                    updateDisplay();
                } else if (data.type === 'status') {
                    updateStatus(data.message, data.isRunning);
                }
            };
            
            ws.onclose = function() {
                setTimeout(connectWebSocket, 1000); // Reconnect after 1 second
            };
        }
        
        function startGeneration() {
            const frequency = document.getElementById('frequency').value;
            ws.send(JSON.stringify({action: 'start', frequency: parseFloat(frequency)}));
            isGenerating = true;
            document.getElementById('start-btn').disabled = true;
            document.getElementById('stop-btn').disabled = false;
        }
        
        function stopGeneration() {
            ws.send(JSON.stringify({action: 'stop'}));
            isGenerating = false;
            document.getElementById('start-btn').disabled = false;
            document.getElementById('stop-btn').disabled = true;
        }
        
        function clearItems() {
            testItems = [];
            currentPage = 0;
            updateDisplay();
        }
        
        function generateBatch() {
            ws.send(JSON.stringify({action: 'batch', count: 20}));
        }
        
        function updateStatus(message, running) {
            const status = document.getElementById('status');
            status.textContent = message;
            status.className = running ? 'status running' : 'status stopped';
        }
        
        function updateDisplay() {
            updateMetrics();
            updateTestList();
            updatePagination();
        }
        
        function updateMetrics() {
            const total = testItems.length;
            const counts = testItems.reduce((acc, item) => {
                acc[item.status.toLowerCase()] = (acc[item.status.toLowerCase()] || 0) + 1;
                return acc;
            }, {});
            
            document.getElementById('total').textContent = total;
            document.getElementById('passed').textContent = counts.passed || 0;
            document.getElementById('failed').textContent = counts.failed || 0;
            document.getElementById('running').textContent = counts.running || 0;
            document.getElementById('pending').textContent = counts.pending || 0;
        }
        
        function updateTestList() {
            const start = currentPage * itemsPerPage;
            const end = start + itemsPerPage;
            const pageItems = testItems.slice(start, end);
            
            // Preserve checkbox states before regenerating HTML
            const checkedItems = new Set();
            document.querySelectorAll('.select-item:checked').forEach(checkbox => {
                const itemDiv = checkbox.closest('.test-item');
                if (itemDiv && itemDiv.dataset.id) {
                    checkedItems.add(itemDiv.dataset.id);
                }
            });
            
            const listHTML = pageItems.map((item, index) => `
                <div class="test-item" data-id="${item.id}">
                    <div><input type="checkbox" class="select-item" onchange="updateSelectedCount()" ${checkedItems.has(item.id) ? 'checked' : ''}></div>
                    <div>#${item.sequence}</div>
                    <div>${item.test_name}</div>
                    <div>${getStatusEmoji(item.status)} ${item.status}</div>
                    <div>${getPriorityEmoji(item.priority)} ${item.priority}</div>
                    <div>${item.duration}s | ${item.browser} | ${item.timestamp}</div>
                    <div><button class="btn-danger delete-btn" onclick="deleteItem('${item.id}')" title="Delete this item">🗑️</button></div>
                </div>
            `).join('');
            
            document.getElementById('test-list').innerHTML = listHTML;
            
            // Update the "Select All" checkbox state based on current page items
            const currentPageCheckboxes = document.querySelectorAll('.select-item');
            const checkedCount = document.querySelectorAll('.select-item:checked').length;
            const selectAllCheckbox = document.getElementById('select-all');
            
            if (currentPageCheckboxes.length === 0) {
                selectAllCheckbox.indeterminate = false;
                selectAllCheckbox.checked = false;
            } else if (checkedCount === 0) {
                selectAllCheckbox.indeterminate = false;
                selectAllCheckbox.checked = false;
            } else if (checkedCount === currentPageCheckboxes.length) {
                selectAllCheckbox.indeterminate = false;
                selectAllCheckbox.checked = true;
            } else {
                selectAllCheckbox.indeterminate = true;
                selectAllCheckbox.checked = false;
            }
        }
        
        function updatePagination() {
            const totalPages = Math.ceil(testItems.length / itemsPerPage);
            document.getElementById('page-info').textContent = `Page ${currentPage + 1} of ${Math.max(1, totalPages)}`;
        }
        
        function previousPage() {
            if (currentPage > 0) {
                currentPage--;
                updateTestList();
                updatePagination();
            }
        }
        
        function nextPage() {
            const totalPages = Math.ceil(testItems.length / itemsPerPage);
            if (currentPage < totalPages - 1) {
                currentPage++;
                updateTestList();
                updatePagination();
            }
        }
        
        function getStatusEmoji(status) {
            const emojis = {
                'Pending': '🟡', 'Running': '🔵', 'Passed': '🟢', 
                'Failed': '🔴', 'Skipped': '⚪'
            };
            return emojis[status] || '⚫';
        }
        
        function getPriorityEmoji(priority) {
            const emojis = {
                'Low': '🟢', 'Medium': '🟡', 'High': '🟠', 'Critical': '🔴'
            };
            return emojis[priority] || '⚫';
        }
        
        function toggleSelectAll() {
            const isChecked = document.getElementById('select-all').checked;
            const checkboxes = document.querySelectorAll('.select-item');
            checkboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            updateSelectedCount();
        }
        
        function updateSelectedCount() {
            const count = document.querySelectorAll('.select-item:checked').length;
            document.getElementById('selected-count').textContent = count;
            document.getElementById('remove-selected-btn').disabled = (count === 0);
        }
        
        function removeSelected() {
            const selectedIds = Array.from(document.querySelectorAll('.select-item:checked'))
                .map(checkbox => {
                    const itemDiv = checkbox.closest('.test-item');
                    return itemDiv.dataset.id;
                });
            
            // Remove selected items from the testItems array
            testItems = testItems.filter(item => !selectedIds.includes(item.id));
            currentPage = 0; // Reset to first page
            updateDisplay();
        }
        
        function deleteItem(id) {
            // Delete single item by ID
            testItems = testItems.filter(item => item.id !== id);
            updateDisplay();
        }
        
        // Update frequency display
        document.getElementById('frequency').oninput = function() {
            document.getElementById('freq-value').textContent = this.value;
        };
        
        function changeItemsPerPage() {
            const newSize = parseInt(document.getElementById('items-per-page').value);
            if (!isNaN(newSize) && newSize > 0) {
                itemsPerPage = newSize;
                currentPage = 0;
                updateDisplay();
            }
        }
        
        function changeMaxItems() {
            const newMax = parseInt(document.getElementById('max-items').value);
            if (!isNaN(newMax) && newMax > 0) {
                maxItemsToKeep = newMax;
                // Trim the testItems array if it exceeds the new max limit
                if (testItems.length > maxItemsToKeep) {
                    testItems = testItems.slice(-maxItemsToKeep);
                    updateDisplay();
                }
            }
        }
        
        // Initialize
        connectWebSocket();
        updateDisplay();
    </script>
</body>
</html>
    """


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    generation_task = None

    try:
        while True:
            # Wait for client messages
            data = await websocket.receive_text()
            message = json.loads(data)

            if message["action"] == "start":
                if generation_task:
                    generation_task.cancel()

                frequency = message.get("frequency", 2.0)
                generation_task = asyncio.create_task(
                    stream_test_data(websocket, frequency)
                )

            elif message["action"] == "stop":
                if generation_task:
                    generation_task.cancel()
                    generation_task = None
                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "status",
                            "message": "✅ Generation stopped",
                            "isRunning": False,
                        }
                    )
                )

            elif message["action"] == "batch":
                count = message.get("count", 20)
                await generate_batch_items(websocket, count)

    except Exception as e:
        if generation_task:
            generation_task.cancel()


async def stream_test_data(websocket: WebSocket, frequency: float):
    """Stream test data using async generator"""
    try:
        async for item in generator.generate_test_items(frequency):
            await websocket.send_text(json.dumps({"type": "new_item", "item": item}))

            await websocket.send_text(
                json.dumps(
                    {
                        "type": "status",
                        "message": f"🔄 Generating items every {frequency}s",
                        "isRunning": True,
                    }
                )
            )

    except asyncio.CancelledError:
        pass


async def generate_batch_items(websocket: WebSocket, count: int):
    """Generate a batch of items immediately"""
    temp_generator = AsyncUITestDataGenerator()

    for i in range(count):
        async for item in temp_generator.generate_test_items(0):
            await websocket.send_text(json.dumps({"type": "new_item", "item": item}))
            break  # Only take one item from the generator


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

/**
 * Order Processing System - Frontend JavaScript
 * Handles WebSocket communication and UI interactions with pagination support
 * Cache Buster: {{ new Date().getTime() }}
 */

console.log('🔄 Loading fresh JavaScript - Cache Buster Active');

class OrderProcessingApp {
    constructor() {
        console.log('🚀 Initializing OrderProcessingApp');
        this.ws = null;
        this.orders = new Map();
        this.ordersArray = [];
        this.selectedOrders = new Set();
        this.isConnected = false;
        this.currentPage = 1;
        this.pageSize = 25;
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        console.log('🔧 Setting up event listeners and WebSocket');
        this.setupEventListeners();
        this.connectWebSocket();
        this.updatePaginationControls();
    }

    /**
     * Setup event listeners for UI elements
     */
    setupEventListeners() {
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const generateBatchBtn = document.getElementById('generateBatchBtn');
        const processSelectedBtn = document.getElementById('processSelectedBtn');
        const pageSizeSelect = document.getElementById('pageSize');
        const firstPageBtn = document.getElementById('firstPageBtn');
        const prevPageBtn = document.getElementById('prevPageBtn');
        const nextPageBtn = document.getElementById('nextPageBtn');
        const lastPageBtn = document.getElementById('lastPageBtn');

        startBtn.addEventListener('click', () => this.startStream());
        stopBtn.addEventListener('click', () => this.stopStream());
        generateBatchBtn.addEventListener('click', () => this.generateBatch());
        processSelectedBtn.addEventListener('click', () => this.processSelectedOrders());

        pageSizeSelect.addEventListener('change', (e) => {
            this.pageSize = parseInt(e.target.value);
            this.currentPage = 1;
            this.renderCurrentPage();
            this.updatePaginationControls();
        });

        firstPageBtn.addEventListener('click', () => this.goToPage(1));
        prevPageBtn.addEventListener('click', () => this.goToPage(this.currentPage - 1));
        nextPageBtn.addEventListener('click', () => this.goToPage(this.currentPage + 1));
        lastPageBtn.addEventListener('click', () => this.goToPage(this.getTotalPages()));
    }

    /**
     * Connect to WebSocket server
     */
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        console.log('Attempting WebSocket connection to:', wsUrl);

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.isConnected = true;
            this.updateConnectionStatus('Connected', 'connected');
            console.log('WebSocket connected successfully');
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };

        this.ws.onclose = (event) => {
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected', 'disconnected');
            console.log('WebSocket disconnected:', event.code, event.reason);

            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                if (!this.isConnected) {
                    console.log('Attempting to reconnect...');
                    this.connectWebSocket();
                }
            }, 3000);
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            this.updateConnectionStatus('Error', 'error');
        };
    }

    /**
     * Handle incoming WebSocket messages
     *
     * :param message: Message object from WebSocket
     */
    handleMessage(message) {
        switch (message.type) {
            case 'order_item':
                this.addOrderToTable(message.data);
                break;
            case 'status':
                this.showStatus(message.message, 'success');
                break;
            case 'error':
                this.showStatus(message.message, 'error');
                break;
            case 'order_updated':
                this.updateOrderInTable(message.data);
                break;
            default:
                console.log('Unknown message type:', message.type);
        }
    }

    /**
     * Start order stream
     */
    startStream() {
        if (!this.isConnected) {
            this.showStatus('Not connected to server', 'error');
            return;
        }

        const frequency = parseFloat(document.getElementById('frequency').value);
        const maxOrders = parseInt(document.getElementById('maxOrders').value);

        const message = {
            command: 'start_stream',
            frequency: frequency,
            max_orders: maxOrders
        };

        this.ws.send(JSON.stringify(message));

        document.getElementById('startBtn').disabled = true;
        document.getElementById('stopBtn').disabled = false;
    }

    /**
     * Stop order stream
     */
    stopStream() {
        if (!this.isConnected) {
            this.showStatus('Not connected to server', 'error');
            return;
        }

        const message = { command: 'stop_stream' };
        this.ws.send(JSON.stringify(message));

        document.getElementById('startBtn').disabled = false;
        document.getElementById('stopBtn').disabled = true;
    }

    /**
     * Generate batch of orders
     */
    generateBatch() {
        if (!this.isConnected) {
            this.showStatus('Not connected to server', 'error');
            return;
        }

        const count = parseInt(document.getElementById('batchSize').value);
        const message = {
            command: 'generate_batch',
            count: count
        };

        this.ws.send(JSON.stringify(message));
    }

    /**
     * Process an order (change status to PROCESSING)
     *
     * :param orderId: The order ID to process
     */
    processOrder(orderId) {
        if (!this.isConnected) {
            this.showStatus('Not connected to server', 'error');
            return;
        }

        const message = {
            command: 'process_order',
            order_id: orderId
        };

        this.ws.send(JSON.stringify(message));
   }

    /**
     * Close an order (change status to DONE)
     *
     * :param orderId: The order ID to close
     */
    closeOrder(orderId) {
        if (!this.isConnected) {
            this.showStatus('Not connected to server', 'error');
            return;
        }

        const message = {
            command: 'close_order',
            order_id: orderId
        };

        this.ws.send(JSON.stringify(message));
    }

    /**
     * Process selected orders (change status to PROCESSING for all selected orders)
     */
    processSelectedOrders() {
        if (!this.isConnected) {
            this.showStatus('Not connected to server', 'error');
            return;
        }

        if (this.selectedOrders.size === 0) {
            this.showStatus('No orders selected', 'error');
            return;
        }

        this.selectedOrders.forEach(orderId => {
            this.processOrder(orderId);
        });

        this.showStatus('Processing selected orders', 'success');
    }

    /**
     * Toggle order selection
     *
     * :param orderId: The order ID to toggle
     */
    toggleOrderSelection(orderId) {
        if (this.selectedOrders.has(orderId)) {
            this.selectedOrders.delete(orderId);
        } else {
            this.selectedOrders.add(orderId);
        }

        this.updateRowSelection(orderId);
        this.updateProcessSelectedButton();
    }

    /**
     * Update visual selection state for a row
     *
     * :param orderId: The order ID to update
     */
    updateRowSelection(orderId) {
        const row = document.querySelector(`tr[data-order-id="${orderId}"]`);
        if (row) {
            if (this.selectedOrders.has(orderId)) {
                row.classList.add('selected');
            } else {
                row.classList.remove('selected');
            }
        }
    }

    /**
     * Update the Process Selected button state
     */
    updateProcessSelectedButton() {
        const processSelectedBtn = document.getElementById('processSelectedBtn');
        const selectedPendingOrders = Array.from(this.selectedOrders).filter(orderId => {
            const order = this.orders.get(orderId);
            return order && order.status === 'Pending';
        });

        processSelectedBtn.disabled = selectedPendingOrders.length === 0;

        if (selectedPendingOrders.length > 0) {
            processSelectedBtn.textContent = `Process Selected (${selectedPendingOrders.length})`;
        } else {
            processSelectedBtn.textContent = 'Process Selected';
        }
    }

    /**
     * Add order to the table
     *
     * :param order: Order data object
     */
    addOrderToTable(order) {
        this.orders.set(order.order_id, order);
        // Sort orders by timestamp (newest first)
        this.ordersArray = Array.from(this.orders.values()).sort((a, b) =>
            new Date(b.timestamp) - new Date(a.timestamp)
        );

        this.renderCurrentPage();
        this.updatePaginationControls();
        this.updateStatistics();
    }

    /**
     * Update existing order in the table
     *
     * :param order: Updated order data object
     */
    updateOrderInTable(order) {
        this.orders.set(order.order_id, order);
        // Sort orders by timestamp (newest first)
        this.ordersArray = Array.from(this.orders.values()).sort((a, b) =>
            new Date(b.timestamp) - new Date(a.timestamp)
        );

        this.renderCurrentPage();
        this.updatePaginationControls();
        this.updateStatistics();
    }

    /**
     * Create a table row for an order
     *
     * :param order: Order data object
     * :returns: HTML table row element
     */
    createOrderRow(order) {
        const row = document.createElement('tr');
        row.setAttribute('data-order-id', order.order_id);
        row.className = `order-row status-${order.status.toLowerCase()}`;

        // Add click event for row selection
        row.addEventListener('click', (e) => {
            // Don't trigger selection if clicking on a button
            if (e.target.tagName !== 'BUTTON') {
                this.toggleOrderSelection(order.order_id);
            }
        });

        // Apply selection state if order is selected
        if (this.selectedOrders.has(order.order_id)) {
            row.classList.add('selected');
        }

        const processedTime = order.processed_at ?
            new Date(order.processed_at).toLocaleTimeString() :
            '-';

        // Determine which button to show based on order status
        let actionButton = '<span class="status-indicator">-</span>';

        if (order.status === 'Pending') {
            actionButton = `<button class="btn btn-process" onclick="app.processOrder('${order.order_id}')">Process</button>`;
        } else if (order.status === 'Processing') {
            actionButton = `<button class="btn btn-close" onclick="app.closeOrder('${order.order_id}')">Close</button>`;
        }

        row.innerHTML = `
            <td class="order-id">${order.order_id}</td>
            <td class="customer-name">${order.customer_name}</td>
            <td class="status">
                <span class="status-badge status-${order.status.toLowerCase()}">${order.status}</span>
            </td>
            <td class="priority">
                <span class="priority-badge priority-${order.priority.toLowerCase()}">${order.priority}</span>
            </td>
            <td class="details">${order.details}</td>
            <td class="timestamp">${new Date(order.timestamp).toLocaleTimeString()}</td>
            <td class="processed-time">${processedTime}</td>
            <td class="actions">${actionButton}</td>
        `;

        return row;
    }

    /**
     * Update statistics display
     */
    updateStatistics() {
        const totalOrders = this.orders.size;
        let pendingCount = 0;
        let processingCount = 0;

        this.orders.forEach(order => {
            if (order.status === 'Pending') pendingCount++;
            if (order.status === 'Processing') processingCount++;
        });

        document.getElementById('totalOrders').textContent = totalOrders;
        document.getElementById('pendingCount').textContent = pendingCount;
        document.getElementById('processingCount').textContent = processingCount;
    }

    /**
     * Update connection status display
     *
     * :param status: Status text
     * :param statusClass: CSS class for styling
     */
    updateConnectionStatus(status, statusClass) {
        const statusElement = document.getElementById('connectionStatus');
        statusElement.textContent = status;
        statusElement.className = `status-indicator ${statusClass}`;
    }

    /**
     * Show status message to user
     *
     * :param message: Message text
     * :param type: Message type (success, error, info)
     */
    showStatus(message, type = 'info') {
        const statusElement = document.getElementById('status');
        statusElement.textContent = message;
        statusElement.className = `status-message ${type}`;

        // Clear message after 3 seconds
        setTimeout(() => {
            statusElement.textContent = '';
            statusElement.className = 'status-message';
        }, 3000);
    }

    /**
     * Go to a specific page
     *
     * :param page: Page number to go to
     */
    goToPage(page) {
        const totalPages = this.getTotalPages();
        if (page < 1 || page > totalPages) return;

        this.currentPage = page;
        this.renderCurrentPage();
        this.updatePaginationControls();
    }

    /**
     * Get the total number of pages
     *
     * :returns: Total number of pages
     */
    getTotalPages() {
        return Math.ceil(this.ordersArray.length / this.pageSize);
    }

    /**
     * Render the orders for the current page
     */
    renderCurrentPage() {
        const tableBody = document.getElementById('ordersTableBody');
        tableBody.innerHTML = '';

        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        const ordersToShow = this.ordersArray.slice(start, end);

        ordersToShow.forEach(order => {
            const row = this.createOrderRow(order);
            tableBody.appendChild(row);
        });

        this.updateStatistics();
        this.updateProcessSelectedButton();
    }

    /**
     * Update pagination controls
     */
    updatePaginationControls() {
        const totalPages = this.getTotalPages();
        const totalOrders = this.ordersArray.length;

        // Update pagination info display
        document.getElementById('paginationInfo').textContent =
            `Page ${this.currentPage} of ${totalPages} (${totalOrders} orders)`;

        // Update button states
        document.getElementById('firstPageBtn').disabled = this.currentPage === 1 || totalPages === 0;
        document.getElementById('prevPageBtn').disabled = this.currentPage === 1 || totalPages === 0;
        document.getElementById('nextPageBtn').disabled = this.currentPage === totalPages || totalPages === 0;
        document.getElementById('lastPageBtn').disabled = this.currentPage === totalPages || totalPages === 0;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new OrderProcessingApp();
});

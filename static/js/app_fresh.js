/**
 * Order Processing System - Frontend JavaScript (Fresh Version)
 * Handles WebSocket communication and UI interactions with pagination support
 */

console.log('🔄 FRESH JAVASCRIPT LOADED - NO CACHE!');

class OrderProcessingApp {
    constructor() {
        console.log('🚀 Initializing OrderProcessingApp - Fresh Instance');
        this.ws = null;
        this.orders = new Map();
        this.ordersArray = [];
        this.selectedOrders = new Set();
        this.isConnected = false;
        this.currentPage = 1;
        this.pageSize = 25;
        this.maxOrders = 500; // Track max orders limit
        this.init();
    }

    /**
     * Initialize the application
     */
    init() {
        console.log('🔧 Setting up event listeners and WebSocket connection');
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
        const closeSelectedBtn = document.getElementById('closeSelectedBtn');
        const deselectAllBtn = document.getElementById('deselectAllBtn');
        const pageSizeSelect = document.getElementById('pageSize');
        const firstPageBtn = document.getElementById('firstPageBtn');
        const prevPageBtn = document.getElementById('prevPageBtn');
        const nextPageBtn = document.getElementById('nextPageBtn');
        const lastPageBtn = document.getElementById('lastPageBtn');
        const maxOrdersInput = document.getElementById('maxOrders');

        startBtn.addEventListener('click', () => this.startStream());
        stopBtn.addEventListener('click', () => this.stopStream());
        generateBatchBtn.addEventListener('click', () => this.generateBatch());
        processSelectedBtn.addEventListener('click', () => this.processSelectedOrders());
        closeSelectedBtn.addEventListener('click', () => this.closeSelectedOrders());
        deselectAllBtn.addEventListener('click', () => this.deselectAllOrders());

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

        maxOrdersInput.addEventListener('change', () => this.updateMaxOrdersLimit());
    }

    /**
     * Connect to WebSocket server
     */
    connectWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws`;

        console.log('🔌 Attempting WebSocket connection to:', wsUrl);
        console.log('🌐 Current location:', window.location.href);

        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            this.isConnected = true;
            this.updateConnectionStatus('Connected', 'connected');
            console.log('✅ WebSocket connected successfully!');
        };

        this.ws.onmessage = (event) => {
            console.log('📨 Received WebSocket message:', event.data);
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };

        this.ws.onclose = (event) => {
            this.isConnected = false;
            this.updateConnectionStatus('Disconnected', 'disconnected');
            console.log('❌ WebSocket disconnected - Code:', event.code, 'Reason:', event.reason);

            // Attempt to reconnect after 3 seconds
            setTimeout(() => {
                if (!this.isConnected) {
                    console.log('🔄 Attempting to reconnect...');
                    this.connectWebSocket();
                }
            }, 3000);
        };

        this.ws.onerror = (error) => {
            console.error('💥 WebSocket error:', error);
            this.updateConnectionStatus('Error', 'error');
        };
    }

    /**
     * Handle incoming WebSocket messages
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
                console.log('❓ Unknown message type:', message.type);
        }
    }

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

    generateBatch() {
        if (!this.isConnected) {
            this.showStatus('Not connected to server', 'error');
            return;
        }

        const count = parseInt(document.getElementById('batchSize').value);
        const message = { command: 'generate_batch', count: count };
        this.ws.send(JSON.stringify(message));
    }

    processOrder(orderId) {
        if (!this.isConnected) {
            this.showStatus('Not connected to server', 'error');
            return;
        }

        const message = { command: 'process_order', order_id: orderId };
        this.ws.send(JSON.stringify(message));
    }

    /**
     * Close a single order with custom confirmation dialog
     *
     * :param orderId: The ID of the order to close
     * :type orderId: str
     */
    closeOrder(orderId) {
        if (!this.isConnected) {
            this.showStatus('Not connected to server', 'error');
            return;
        }

        const order = this.orders.get(orderId);
        if (!order) {
            this.showStatus('Order not found', 'error');
            return;
        }

        if (order.status !== 'Processing') {
            this.showStatus('Only processing orders can be closed', 'error');
            return;
        }

        // Show custom confirmation dialog for single order
        const confirmMessage = `You are about to close order ${orderId} for customer "${order.customer_name}".\n\nAre you sure you want to proceed?`;

        this.showConfirmationModal(confirmMessage, () => {
            this.performCloseOrder(orderId);
        });
    }

    /**
     * Perform the actual closing of a single order
     *
     * :param orderId: The ID of the order to close
     * :type orderId: str
     */
    performCloseOrder(orderId) {
        if (!this.isConnected) {
            this.showStatus('Not connected to server', 'error');
            return;
        }

        const message = { command: 'close_order', order_id: orderId };
        this.ws.send(JSON.stringify(message));

        this.showStatus(`Closing order ${orderId}`, 'success');
    }

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
     * Show custom confirmation modal
     * @param {string} message - The message to display
     * @param {function} onConfirm - Callback function when user confirms
     */
    showConfirmationModal(message, onConfirm) {
        const modal = document.getElementById('customModal');
        const messageElement = document.getElementById('modalMessage');
        const confirmBtn = document.getElementById('modalConfirmBtn');
        const cancelBtn = document.getElementById('modalCancelBtn');

        messageElement.textContent = message;
        modal.classList.add('show');

        // Remove any existing event listeners
        const newConfirmBtn = confirmBtn.cloneNode(true);
        confirmBtn.parentNode.replaceChild(newConfirmBtn, confirmBtn);
        const newCancelBtn = cancelBtn.cloneNode(true);
        cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);

        // Add event listeners for this specific modal instance
        newConfirmBtn.addEventListener('click', () => {
            this.hideConfirmationModal();
            onConfirm();
        });

        newCancelBtn.addEventListener('click', () => {
            this.hideConfirmationModal();
        });

        // Close modal when clicking outside
        modal.addEventListener('click', (event) => {
            if (event.target === modal) {
                this.hideConfirmationModal();
            }
        });

        // Close modal with Escape key
        const handleEscape = (event) => {
            if (event.key === 'Escape') {
                this.hideConfirmationModal();
                document.removeEventListener('keydown', handleEscape);
            }
        };
        document.addEventListener('keydown', handleEscape);
    }

    /**
     * Hide custom confirmation modal
     */
    hideConfirmationModal() {
        const modal = document.getElementById('customModal');
        modal.classList.remove('show');
    }

    /**
     * Close selected orders with custom confirmation dialog
     */
    closeSelectedOrders() {
        if (!this.isConnected) {
            this.showStatus('Not connected to server', 'error');
            return;
        }

        if (this.selectedOrders.size === 0) {
            this.showStatus('No orders selected', 'error');
            return;
        }

        // Only close orders that are in "Processing" status, ignore others
        const selectedProcessingOrders = Array.from(this.selectedOrders).filter(orderId => {
            const order = this.orders.get(orderId);
            return order && order.status === 'Processing';
        });

        if (selectedProcessingOrders.length === 0) {
            this.showStatus('No processing orders selected to close', 'error');
            return;
        }

        // Always show custom confirmation dialog for "Close Selected" button (even for single order)
        const skippedCount = this.selectedOrders.size - selectedProcessingOrders.length;
        let confirmMessage = `You are about to close ${selectedProcessingOrders.length} processing order${selectedProcessingOrders.length > 1 ? 's' : ''}.`;

        if (skippedCount > 0) {
            confirmMessage += `\n\n${skippedCount} pending order${skippedCount > 1 ? 's' : ''} will be skipped (not affected).`;
        }

        confirmMessage += '\n\nAre you sure you want to proceed?';

        this.showConfirmationModal(confirmMessage, () => {
            this.performCloseSelectedOrders(selectedProcessingOrders);
        });
    }

    /**
     * Perform the actual closing of selected orders
     * @param {Array} selectedProcessingOrders - Array of order IDs to close
     */
    performCloseSelectedOrders(selectedProcessingOrders) {
        // Close only the processing orders using direct method (no confirmation per order)
        selectedProcessingOrders.forEach(orderId => {
            this.performCloseOrder(orderId);
        });

        const skippedCount = this.selectedOrders.size - selectedProcessingOrders.length;
        let message = `Closing ${selectedProcessingOrders.length} processing orders`;
        if (skippedCount > 0) {
            message += ` (${skippedCount} pending orders skipped)`;
        }

        this.showStatus(message, 'success');
    }

    toggleOrderSelection(orderId) {
        if (this.selectedOrders.has(orderId)) {
            this.selectedOrders.delete(orderId);
        } else {
            this.selectedOrders.add(orderId);
        }

        this.updateRowSelection(orderId);
        this.updateProcessSelectedButton();
        this.updateCloseSelectedButton();
        this.updateDeselectAllButton();
    }

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
     * Update the Close Selected button state based on selected processing orders
     *
     * :returns: void
     */
    updateCloseSelectedButton() {
        const closeSelectedBtn = document.getElementById('closeSelectedBtn');
        const selectedProcessingOrders = Array.from(this.selectedOrders).filter(orderId => {
            const order = this.orders.get(orderId);
            return order && order.status === 'Processing';
        });

        closeSelectedBtn.disabled = selectedProcessingOrders.length === 0;

        if (selectedProcessingOrders.length > 0) {
            closeSelectedBtn.textContent = `Close Selected (${selectedProcessingOrders.length})`;
        } else {
            closeSelectedBtn.textContent = 'Close Selected';
        }
    }

    /**
     * Deselect all currently selected orders
     *
     * :returns: void
     */
    deselectAllOrders() {
        if (this.selectedOrders.size === 0) {
            this.showStatus('No orders are currently selected', 'info');
            return;
        }

        const deselectedCount = this.selectedOrders.size;

        // Clear all selections
        this.selectedOrders.clear();

        // Update visual state of all rows
        this.renderCurrentPage();

        // Update button states
        this.updateProcessSelectedButton();
        this.updateCloseSelectedButton();
        this.updateDeselectAllButton();

        this.showStatus(`Deselected ${deselectedCount} orders`, 'success');
    }

    /**
     * Update the Deselect All button state based on selected orders
     *
     * :returns: void
     */
    updateDeselectAllButton() {
        const deselectAllBtn = document.getElementById('deselectAllBtn');
        const selectedCount = this.selectedOrders.size;

        deselectAllBtn.disabled = selectedCount === 0;

        if (selectedCount > 0) {
            deselectAllBtn.textContent = `Deselect All (${selectedCount})`;
        } else {
            deselectAllBtn.textContent = 'Deselect All';
        }
    }

    /**
     * Add order to the table with max orders enforcement
     *
     * :param order: Order data object
     */
    addOrderToTable(order) {
        this.orders.set(order.order_id, order);

        // Sort orders by timestamp (newest first)
        this.ordersArray = Array.from(this.orders.values()).sort((a, b) =>
            new Date(b.timestamp) - new Date(a.timestamp)
        );

        // Enforce max orders limit - remove oldest orders if we exceed the limit
        this.enforceMaxOrdersLimit();

        this.renderCurrentPage();
        this.updatePaginationControls();
        this.updateStatistics();
    }

    /**
     * Update existing order in the table with max orders enforcement
     *
     * :param order: Updated order data object
     */
    updateOrderInTable(order) {
        this.orders.set(order.order_id, order);

        // Sort orders by timestamp (newest first)
        this.ordersArray = Array.from(this.orders.values()).sort((a, b) =>
            new Date(b.timestamp) - new Date(a.timestamp)
        );

        // Enforce max orders limit after updates
        this.enforceMaxOrdersLimit();

        this.renderCurrentPage();
        this.updatePaginationControls();
        this.updateStatistics();
    }

    /**
     * Enforce maximum orders limit by removing oldest orders
     */
    enforceMaxOrdersLimit() {
        if (this.ordersArray.length > this.maxOrders) {
            // Calculate how many orders to remove
            const ordersToRemove = this.ordersArray.length - this.maxOrders;

            // Get the oldest orders (they're at the end of the sorted array)
            const oldestOrders = this.ordersArray.slice(-ordersToRemove);

            // Remove oldest orders from both Map and selectedOrders Set
            oldestOrders.forEach(order => {
                this.orders.delete(order.order_id);
                this.selectedOrders.delete(order.order_id);
            });

            // Update the ordersArray to reflect the changes
            this.ordersArray = Array.from(this.orders.values()).sort((a, b) =>
                new Date(b.timestamp) - new Date(a.timestamp)
            );

            console.log(`🗑️ Removed ${ordersToRemove} oldest orders to maintain max limit of ${this.maxOrders}`);
        }
    }

    /**
     * Update max orders limit from UI input
     */
    updateMaxOrdersLimit() {
        const maxOrdersInput = document.getElementById('maxOrders');
        if (maxOrdersInput) {
            this.maxOrders = parseInt(maxOrdersInput.value) || 500;
            this.enforceMaxOrdersLimit();
            this.renderCurrentPage();
            this.updatePaginationControls();
            this.updateStatistics();
        }
    }

    createOrderRow(order) {
        const row = document.createElement('tr');
        row.setAttribute('data-order-id', order.order_id);
        row.className = `order-row status-${order.status.toLowerCase()}`;

        row.addEventListener('click', (e) => {
            if (e.target.tagName !== 'BUTTON') {
                this.toggleOrderSelection(order.order_id);
            }
        });

        if (this.selectedOrders.has(order.order_id)) {
            row.classList.add('selected');
        }

        const processedTime = order.processed_at ?
            new Date(order.processed_at).toLocaleTimeString() : '-';

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

    updateConnectionStatus(status, statusClass) {
        const statusElement = document.getElementById('connectionStatus');
        statusElement.textContent = status;
        statusElement.className = `status-indicator ${statusClass}`;
    }

    showStatus(message, type = 'info') {
        const statusElement = document.getElementById('status');
        statusElement.textContent = message;
        statusElement.className = `status-message ${type}`;

        setTimeout(() => {
            statusElement.textContent = '';
            statusElement.className = 'status-message';
        }, 3000);
    }

    goToPage(page) {
        const totalPages = this.getTotalPages();
        if (page < 1 || page > totalPages) return;

        this.currentPage = page;
        this.renderCurrentPage();
        this.updatePaginationControls();
    }

    getTotalPages() {
        return Math.ceil(this.ordersArray.length / this.pageSize);
    }

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
        this.updateCloseSelectedButton();
        this.updateDeselectAllButton();
    }

    updatePaginationControls() {
        const totalPages = this.getTotalPages();
        const totalOrders = this.ordersArray.length;

        document.getElementById('paginationInfo').textContent =
            `Page ${this.currentPage} of ${totalPages} (${totalOrders} orders)`;

        document.getElementById('firstPageBtn').disabled = this.currentPage === 1 || totalPages === 0;
        document.getElementById('prevPageBtn').disabled = this.currentPage === 1 || totalPages === 0;
        document.getElementById('nextPageBtn').disabled = this.currentPage === totalPages || totalPages === 0;
        document.getElementById('lastPageBtn').disabled = this.currentPage === totalPages || totalPages === 0;
    }
}

// Initialize the application when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    console.log('🎯 DOM loaded, creating app instance');
    window.app = new OrderProcessingApp();
});

console.log('📄 JavaScript file completely loaded');

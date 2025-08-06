from __future__ import annotations

"""
FastAPI + WebSockets Demo: Python Generators for Order Processing System

This demonstrates real-time order processing using WebSockets and Python generators.
No page refreshes, true real-time streaming, and clean separation of concerns.
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import asyncio
import json
import random
import uuid
from datetime import datetime
from typing import AsyncGenerator, Dict, Any, Optional
from dataclasses import dataclass, asdict

app = FastAPI(title="Order Processing System - FastAPI Demo")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")


@dataclass
class OrderData:
    """
    Data structure for order information.

    :param id: Unique identifier for the order record
    :param order_id: Business order identifier
    :param customer_name: Name of the customer
    :param status: Current order status
    :param priority: Order priority level
    :param details: Order details and description
    :param timestamp: Order creation timestamp
    :param order_value: Monetary value of the order
    :param processed_at: Timestamp when order started processing
    """

    id: str
    order_id: str
    customer_name: str
    status: str
    priority: str
    details: str
    timestamp: str
    order_value: float
    processed_at: Optional[str] = None


class AsyncOrderDataGenerator:
    """
    Async generator class for real-time order data.

    Generates realistic order processing data with configurable parameters for demonstration
    of Python generators in order management scenarios.
    """

    def __init__(self, initial_status: str = "Pending") -> None:
        """
        Initialize the order data generator.

        :param initial_status: The initial status for all generated orders
        """
        self.order_counter = 0
        self.initial_status = initial_status
        self.orders_registry: Dict[str, OrderData] = {}
        self.customer_names = [
            "John Smith",
            "Sarah Johnson",
            "Michael Brown",
            "Emily Davis",
            "David Wilson",
            "Lisa Anderson",
            "Robert Taylor",
            "Jessica Martinez",
            "Christopher Lee",
            "Amanda Thompson",
        ]
        self.statuses = ["Pending", "Processing", "Shipped", "Delivered", "Cancelled"]
        self.priorities = ["Low", "Medium", "High", "Critical"]

    async def generate_order_items(
        self,
        frequency: float = 2.0,
        max_orders: int = 500,
    ) -> AsyncGenerator[OrderData, None]:
        """
        Generate order items asynchronously with specified frequency and maximum count.

        :param frequency: Time interval between order generations in seconds
        :param max_orders: Maximum number of orders to generate
        :yields: OrderData object containing order information
        """
        while self.order_counter < max_orders:
            self.order_counter += 1

            # Generate order details
            order_id = f"ORD-{self.order_counter:05d}"
            customer_name = random.choice(self.customer_names)
            status = self.initial_status  # Use consistent initial status instead of random
            priority = random.choice(self.priorities)

            # Generate order value between $10-$2500
            order_value = round(random.uniform(10.0, 2500.0), 2)

            # Create realistic details based on status
            details = f"${order_value} - {self._generate_order_description()}"

            order_data = OrderData(
                id=str(uuid.uuid4()),
                order_id=order_id,
                customer_name=customer_name,
                status=status,
                priority=priority,
                details=details,
                timestamp=datetime.now().isoformat(),
                order_value=order_value,
                processed_at=None,
            )

            # Store order in registry for later updates
            self.orders_registry[order_id] = order_data

            yield order_data
            await asyncio.sleep(frequency)

    def process_order(self, order_id: str) -> Optional[OrderData]:
        """
        Process an order by changing its status to 'Processing' and adding processing timestamp.

        :param order_id: The ID of the order to process
        :returns: Updated OrderData object if order exists and can be processed, None otherwise
        """
        if order_id not in self.orders_registry:
            return None

        order = self.orders_registry[order_id]

        # Only process orders that are in 'Pending' status
        if order.status != "Pending":
            return None

        # Update order status and add processing timestamp
        order.status = "Processing"
        order.processed_at = datetime.now().isoformat()

        return order

    def close_order(self, order_id: str) -> Optional[OrderData]:
        """
        Close an order by changing its status to 'Done'.

        :param order_id: The ID of the order to close
        :returns: Updated OrderData object if order exists and can be closed, None otherwise
        """
        if order_id not in self.orders_registry:
            return None

        order = self.orders_registry[order_id]

        # Only close orders that are in 'Processing' status
        if order.status != "Processing":
            return None

        # Update order status to Done
        order.status = "Done"

        return order

    def get_order(self, order_id: str) -> Optional[OrderData]:
        """
        Get order data by order ID.

        :param order_id: The ID of the order to retrieve
        :returns: OrderData object if found, None otherwise
        """
        return self.orders_registry.get(order_id)

    def _generate_order_description(self) -> str:
        """
        Generate realistic order descriptions.

        :return: A realistic order description string
        """
        products = [
            "Electronics Bundle",
            "Home Appliances",
            "Books & Stationery",
            "Clothing & Accessories",
            "Sports Equipment",
            "Kitchen Essentials",
            "Garden Tools",
            "Office Supplies",
            "Health & Beauty",
            "Automotive Parts",
        ]
        return random.choice(products)


@app.get("/", response_class=HTMLResponse)
async def get_homepage(request: Request) -> HTMLResponse:
    """
    Serve the main order processing dashboard page.

    :param request: FastAPI request object
    :return: HTML response containing the order processing interface
    """
    import time
    cache_buster = str(int(time.time()))
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "cache_buster": cache_buster
        }
    )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """
    WebSocket endpoint for real-time order processing communication.

    Handles WebSocket connections and processes real-time order generation,
    batch operations, and other order management commands.

    :param websocket: WebSocket connection object
    """
    await websocket.accept()
    print(f"WebSocket connection established: {websocket.client}")

    generator = AsyncOrderDataGenerator()
    current_stream_task = None

    try:
        while True:
            # Wait for messages from client
            message = await websocket.receive_text()
            data = json.loads(message)
            command = data.get("command")

            if command == "start_stream":
                if current_stream_task:
                    current_stream_task.cancel()

                frequency = data.get("frequency", 2.0)
                max_orders = data.get("max_orders", 500)

                current_stream_task = asyncio.create_task(
                    stream_order_data(websocket, generator, frequency, max_orders)
                )

                await websocket.send_text(
                    json.dumps(
                        {
                            "type": "status",
                            "message": f"Started order processing stream (frequency: {frequency}s, max: {max_orders})",
                        }
                    )
                )

            elif command == "stop_stream":
                if current_stream_task:
                    current_stream_task.cancel()
                    current_stream_task = None

                await websocket.send_text(
                    json.dumps({"type": "status", "message": "Order processing stream stopped"})
                )

            elif command == "generate_batch":
                count = data.get("count", 20)
                await generate_batch_orders(websocket, generator, count)

            elif command == "process_order":
                order_id = data.get("order_id")
                if order_id:
                    updated_order = generator.process_order(order_id)
                    if updated_order:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "order_updated",
                                    "data": asdict(updated_order),
                                }
                            )
                        )
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "status",
                                    "message": f"Order {order_id} has been processed",
                                }
                            )
                        )
                    else:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "error",
                                    "message": f"Cannot process order {order_id}. Order not found or not in pending status.",
                                }
                            )
                        )
                else:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "message": "Order ID is required for processing"
                            }
                        )
                    )

            elif command == "close_order":
                order_id = data.get("order_id")
                if order_id:
                    updated_order = generator.close_order(order_id)
                    if updated_order:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "order_updated",
                                    "data": asdict(updated_order),
                                }
                            )
                        )
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "status",
                                    "message": f"Order {order_id} has been closed",
                                }
                            )
                        )
                    else:
                        await websocket.send_text(
                            json.dumps(
                                {
                                    "type": "error",
                                    "message": f"Cannot close order {order_id}. Order not found or not in processing status.",
                                }
                            )
                        )
                else:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "type": "error",
                                "message": "Order ID is required for closing"
                            }
                        )
                    )

            elif command == "change_settings":
                # Handle settings changes
                await websocket.send_text(
                    json.dumps({"type": "status", "message": "Settings updated"})
                )

    except WebSocketDisconnect:
        print("WebSocket disconnected")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        if current_stream_task:
            current_stream_task.cancel()
        print("WebSocket connection closed")


async def stream_order_data(
    websocket: WebSocket,
    generator: AsyncOrderDataGenerator,
    frequency: float,
    max_orders: int
) -> None:
    """
    Stream order data to connected WebSocket clients.

    :param websocket: WebSocket connection object
    :param generator: Order data generator instance
    :param frequency: Time interval between order generations in seconds
    :param max_orders: Maximum number of orders to generate
    """
    try:
        async for order_item in generator.generate_order_items(frequency, max_orders):
            await websocket.send_text(
                json.dumps(
                    {
                        "type": "order_item",
                        "data": asdict(order_item),
                    }
                )
            )

    except asyncio.CancelledError:
        print("Order streaming cancelled")
        raise
    except Exception as e:
        print(f"Error in order streaming: {e}")
        await websocket.send_text(
            json.dumps(
                {
                    "type": "error",
                    "message": f"Error generating order data: {str(e)}",
                }
            )
        )


async def generate_batch_orders(
    websocket: WebSocket,
    generator: AsyncOrderDataGenerator,
    count: int
) -> None:
    """
    Generate a batch of orders and send them immediately.

    :param websocket: WebSocket connection object
    :param generator: Order data generator instance
    :param count: Number of orders to generate in the batch
    """
    try:
        # Generate batch items by directly creating orders without using the async generator
        for _ in range(count):
            # Create order directly without the async generator limitations
            generator.order_counter += 1

            order_id = f"ORD-{generator.order_counter:05d}"
            customer_name = random.choice(generator.customer_names)
            status = generator.initial_status
            priority = random.choice(generator.priorities)
            order_value = round(random.uniform(10.0, 2500.0), 2)
            details = f"${order_value} - {generator._generate_order_description()}"

            order_data = OrderData(
                id=str(uuid.uuid4()),
                order_id=order_id,
                customer_name=customer_name,
                status=status,
                priority=priority,
                details=details,
                timestamp=datetime.now().isoformat(),
                order_value=order_value,
                processed_at=None,
            )

            # Store order in registry for later updates
            generator.orders_registry[order_id] = order_data

            await websocket.send_text(
                json.dumps(
                    {
                        "type": "order_item",
                        "data": asdict(order_data),
                    }
                )
            )

        await websocket.send_text(
            json.dumps(
                {
                    "type": "status",
                    "message": f"Generated batch of {count} orders",
                }
            )
        )

    except Exception as e:
        print(f"Error generating batch orders: {e}")
        await websocket.send_text(
            json.dumps(
                {
                    "type": "error",
                    "message": f"Error generating batch orders: {str(e)}",
                }
            )
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

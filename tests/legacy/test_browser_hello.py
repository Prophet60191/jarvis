#!/usr/bin/env python3
import asyncio
import uuid
from jarvis.core.orchestration.enhanced_orchestrator import EnhancedJarvisOrchestrator
from jarvis.core.context.context_manager import ContextManager
from jarvis.core.context.context import Context

async def test_browser_hello():
    # Initialize orchestrator with context
    context_manager = ContextManager()
    orchestrator = EnhancedJarvisOrchestrator(context_manager=context_manager)
    context = Context(session_id=str(uuid.uuid4()))

    # Send prompt to Jarvis
    prompt = "Jarvis can you make me a browser ui that says hello world"
    print("\n💬 Sending prompt to Jarvis:")
    print(prompt)
            50% { transform: translateY(-10px); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Hello World!</h1>
    </div>
</body>
</html>\"\"\"

        # Save HTML file
        html_path = Path(__file__).parent / "hello_world.html"
        with open(html_path, "w") as f:
            f.write(html_content)

        # Open in browser
        return {
            "success": True,
            "message": "Opening Hello World UI in browser",
            "url": f"file://{html_path.absolute()}"
        }
"""
    }

    # Create the tool
    result = tool_creator.create_tool_from_request(
        user_request="Create a browser UI that displays Hello World",
        context=context,
        tool_specs=tool_specs
    )

    print("\n🔧 Tool Creation Result:")
    print(result)

    # Import and use our tool directly
    from jarvis.tools.plugins.browser_hello_world_tool import browser_hello_world
    result = await browser_hello_world.ainvoke("show hello world")
    
    print("\n🤖 Tool Execution Result:")
    print(result)

if __name__ == "__main__":
    asyncio.run(test_browser_hello())

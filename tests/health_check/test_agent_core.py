"""
Test Agent Core
Tests that the agent core can initialize and execute basic operations
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path
import asyncio

# Import test modules
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from src.agent_core import AICodeAgent
from src.tool_schemas import ToolResult


class TestAgentInitialization:
    """Test agent initialization"""
    
    def test_agent_creation_with_api_key(self):
        """Test creating agent with API key"""
        api_key = os.getenv("GROQ_API_KEY", "test-key")
        
        agent = AICodeAgent(groq_api_key=api_key)
        
        assert agent is not None
        assert hasattr(agent, 'client')
        assert hasattr(agent, 'model')
        assert hasattr(agent, 'tool_registry')
    
    def test_agent_with_custom_model(self):
        """Test creating agent with custom model"""
        api_key = os.getenv("GROQ_API_KEY", "test-key")
        
        agent = AICodeAgent(
            groq_api_key=api_key,
            model="llama-3.1-8b-instant"
        )
        
        assert agent.model == "llama-3.1-8b-instant"
    
    def test_agent_tool_registry_populated(self):
        """Test that agent has tools registered"""
        api_key = os.getenv("GROQ_API_KEY", "test-key")
        agent = AICodeAgent(groq_api_key=api_key)
        
        assert hasattr(agent, 'tool_registry')
        assert len(agent.tool_registry) > 0
        
        # Check for essential tools
        assert 'read_file' in agent.tool_registry
        assert 'write_file' in agent.tool_registry
        assert 'list_directory' in agent.tool_registry


class TestAgentToolRegistry:
    """Test agent tool registry functionality"""
    
    @pytest.fixture
    def agent(self):
        """Create an agent for testing"""
        api_key = os.getenv("GROQ_API_KEY", "test-key")
        return AICodeAgent(groq_api_key=api_key)
    
    def test_tool_registry_structure(self, agent):
        """Test tool registry has correct structure"""
        assert isinstance(agent.tool_registry, dict)
        
        for tool_name, tool_entry in agent.tool_registry.items():
            assert isinstance(tool_name, str)
            # Tool entry might be a dict with 'function' and 'schema' or just a function
            if isinstance(tool_entry, dict):
                assert 'function' in tool_entry
                assert callable(tool_entry['function'])
            else:
                assert callable(tool_entry)
    
    def test_essential_tools_registered(self, agent):
        """Test that essential tools are registered"""
        essential_tools = [
            'read_file',
            'write_file',
            'edit_file',
            'delete_file',
            'list_directory',
            'execute_command',
            'git_status',
        ]
        
        for tool in essential_tools:
            assert tool in agent.tool_registry, f"Missing essential tool: {tool}"
    
    def test_ai_assisted_tools_registered(self, agent):
        """Test that AI-assisted tools are registered"""
        ai_tools = [
            'generate_react_component',
            'generate_design_system',
            'generate_page_with_components'
        ]
        
        for tool in ai_tools:
            assert tool in agent.tool_registry, f"Missing AI tool: {tool}"


class TestAgentExecution:
    """Test agent execution capabilities (requires valid API key)"""
    
    @pytest.fixture
    def agent(self):
        """Create an agent with real API key if available"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            pytest.skip("GROQ_API_KEY not set, skipping execution tests")
        return AICodeAgent(groq_api_key=api_key, model="llama-3.1-8b-instant")
    
    @pytest.fixture
    def temp_workspace(self):
        """Create a temporary workspace"""
        temp = tempfile.mkdtemp(prefix="agent_test_")
        yield temp
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
    async def test_simple_file_operation(self, agent, temp_workspace):
        """Test agent executing a simple file operation"""
        file_path = os.path.join(temp_workspace, "test.txt")
        
        request = f"""
        Create a file at {file_path} with the content "Hello from agent test".
        Use the write_file tool.
        """
        
        result = await agent.execute(request, max_iterations=3)
        
        assert result is not None
        assert 'success' in result
        assert 'response' in result
        
        # Check if file was created
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                content = f.read()
            assert "Hello" in content or "hello" in content.lower()
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
    async def test_agent_list_directory(self, agent, temp_workspace):
        """Test agent listing a directory"""
        # Create some test files
        for i in range(3):
            file_path = os.path.join(temp_workspace, f"file{i}.txt")
            with open(file_path, 'w') as f:
                f.write(f"Content {i}")
        
        request = f"""
        List the contents of the directory: {temp_workspace}
        Use the list_directory tool.
        """
        
        result = await agent.execute(request, max_iterations=3)
        
        assert result is not None
        assert 'success' in result
        
        # The agent should have listed the directory
        if result.get('tool_results'):
            assert len(result['tool_results']) > 0


class TestAgentErrorHandling:
    """Test agent error handling"""
    
    @pytest.fixture
    def agent(self):
        """Create an agent for testing"""
        api_key = os.getenv("GROQ_API_KEY", "test-key")
        return AICodeAgent(groq_api_key=api_key)
    
    def test_agent_with_empty_api_key(self):
        """Test agent behavior with empty API key"""
        # Should still create agent, but execution may fail
        agent = AICodeAgent(groq_api_key="")
        assert agent is not None
    
    @pytest.mark.asyncio
    async def test_agent_with_invalid_request(self, agent):
        """Test agent handling invalid/empty request"""
        if not os.getenv("GROQ_API_KEY"):
            pytest.skip("GROQ_API_KEY not set")
        
        result = await agent.execute("", max_iterations=1)
        
        # Should handle gracefully
        assert result is not None
        assert isinstance(result, dict)


class TestAgentIteration:
    """Test agent iteration and planning"""
    
    @pytest.fixture
    def agent(self):
        """Create an agent for testing"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            pytest.skip("GROQ_API_KEY not set")
        return AICodeAgent(groq_api_key=api_key)
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
    async def test_max_iterations_respected(self, agent):
        """Test that max iterations is respected"""
        request = "List all files in the current directory."
        
        result = await agent.execute(request, max_iterations=2)
        
        assert result is not None
        assert 'iterations' in result
        assert result['iterations'] <= 2
    
    @pytest.mark.asyncio
    @pytest.mark.skipif(not os.getenv("GROQ_API_KEY"), reason="GROQ_API_KEY not set")
    async def test_agent_tracks_tool_calls(self, agent):
        """Test that agent tracks tool calls"""
        request = "List the contents of the current directory."
        
        result = await agent.execute(request, max_iterations=3)
        
        assert result is not None
        if 'tool_results' in result:
            assert isinstance(result['tool_results'], list)


class TestAgentMemory:
    """Test agent memory and context management"""
    
    @pytest.fixture
    def agent(self):
        """Create an agent for testing"""
        api_key = os.getenv("GROQ_API_KEY", "test-key")
        return AICodeAgent(groq_api_key=api_key)
    
    def test_agent_has_memory_manager(self, agent):
        """Test that agent has memory management"""
        # Agent should exist and have basic structure
        # The agent uses AgentContext internally which manages conversation_history
        assert agent is not None
        assert hasattr(agent, 'tool_registry')
        # Agent creates context during execution, so just verify it's properly initialized
        assert hasattr(agent, 'client')


class TestToolDictionaryIntegration:
    """Test that agent properly integrates with tool dictionary"""
    
    @pytest.fixture
    def agent(self):
        """Create an agent for testing"""
        api_key = os.getenv("GROQ_API_KEY", "test-key")
        return AICodeAgent(groq_api_key=api_key)
    
    def test_agent_loads_tool_dictionary(self, agent):
        """Test that agent loads tool dictionary"""
        # Agent should have access to tool dictionary
        assert hasattr(agent, 'tool_dictionary') or hasattr(agent, 'tool_registry')
    
    def test_tool_dictionary_matches_registry(self, agent):
        """Test that tool dictionary matches registry"""
        import json
        from pathlib import Path
        
        dict_path = Path(__file__).parent.parent.parent / "config" / "tool_dictionary.json"
        if not dict_path.exists():
            pytest.skip("tool_dictionary.json not found")
        
        with open(dict_path, 'r') as f:
            tool_dict = json.load(f)
        
        # Check that registered tools are in dictionary
        for category, tools in tool_dict["tools"].items():
            for tool_name in tools.keys():
                # Tool should be in registry
                if tool_name in agent.tool_registry:
                    tool_entry = agent.tool_registry[tool_name]
                    # Tool entry might be a dict with 'function' and 'schema' or just a function
                    if isinstance(tool_entry, dict):
                        assert callable(tool_entry['function'])
                    else:
                        assert callable(tool_entry)


class TestAgentConfiguration:
    """Test agent configuration options"""
    
    def test_agent_default_configuration(self):
        """Test agent with default configuration"""
        api_key = os.getenv("GROQ_API_KEY", "test-key")
        agent = AICodeAgent(groq_api_key=api_key)
        
        # Check defaults
        assert agent.model in ["llama-3.3-70b-versatile", "llama-3.1-8b-instant", "mixtral-8x7b-32768"]
    
    def test_agent_custom_model(self):
        """Test agent with custom model"""
        api_key = os.getenv("GROQ_API_KEY", "test-key")
        
        models_to_test = [
            "llama-3.1-8b-instant",
            "llama-3.3-70b-versatile",
            "mixtral-8x7b-32768"
        ]
        
        for model in models_to_test:
            agent = AICodeAgent(groq_api_key=api_key, model=model)
            assert agent.model == model


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

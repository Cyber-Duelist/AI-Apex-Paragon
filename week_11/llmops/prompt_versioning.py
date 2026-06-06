import os

class PromptRegistry:
    """A centralized registry for tracking and versioning LLM prompts."""
    
    def __init__(self):
        # Dictionary structure: { prompt_name: { version_number: { "template": ..., "description": ... } } }
        self.prompts = {}

    def register(self, name: str, version: int, template: str, description: str = ""):
        """Saves a new prompt version to the registry."""
        if name not in self.prompts:
            self.prompts[name] = {}
        
        self.prompts[name][version] = {
            "template": template,
            "description": description
        }

    def get(self, name: str, version: int) -> str:
        """Retrieves a specific version of a prompt."""
        return self.prompts.get(name, {}).get(version, {}).get("template", "Prompt not found.")

    def get_latest(self, name: str) -> tuple:
        """Returns the highest version number and its template."""
        if name not in self.prompts or not self.prompts[name]:
            return None, "Prompt not found."
        
        # Find the highest version integer
        latest_version = max(self.prompts[name].keys())
        return latest_version, self.prompts[name][latest_version]["template"]

    def list_versions(self, name: str) -> list:
        """Returns a sorted list of all registered versions for a prompt."""
        if name not in self.prompts:
            return []
        return sorted(self.prompts[name].keys())


if __name__ == "__main__":
    # Initialize our registry
    registry = PromptRegistry()

    # ==========================================
    # Registering the Evolution of our Prompt
    # ===================================
    registry.register(
        name="risk_analysis",
        version=1,
        template="Analyze this document: {document}. Is it high risk?",
        description="Basic risk analysis prompt"
    )
    
    registry.register(
        name="risk_analysis",
        version=2,
        template="Analyze {document} from {department}. Is it high risk?",
        description="Added department context"
    )
    
    registry.register(
        name="risk_analysis",
        version=3,
        template="You are a risk analyst. Analyze {document} from {department}. Return JSON with risk_level, risk_score, reason.",
        description="Added structured output requirement"
    )

    # =====================================
    # Testing the Operations
    # ==============================================
    print("=== REGISTERED PROMPTS ===")
    for v in registry.list_versions("risk_analysis"):
        desc = registry.prompts["risk_analysis"][v]["description"]
        print(f"risk_analysis v{v}: {desc}")

    print("\n=== LATEST VERSION ===")
    latest_v, latest_template = registry.get_latest("risk_analysis")
    print(f"v{latest_v}: {latest_template}")

    print("\n=== ALL VERSIONS ===")
    versions = [f"v{v}" for v in registry.list_versions("risk_analysis")]
    print(", ".join(versions))

    print("\n=== DIFF v1 vs v3 ===")
    print(f"v1: {registry.get('risk_analysis', 1)}")
    print(f"v3: {registry.get('risk_analysis', 3)}")
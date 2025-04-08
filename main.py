from agents.agent_manager import AgentManager
from ui.app_ui import launch_interface

def main():
    manager = AgentManager()
    launch_interface(manager)

if __name__ == "__main__":
    main()

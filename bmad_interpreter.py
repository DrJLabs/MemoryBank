import sys
import os
import yaml

class BmadInterpreter:
    def __init__(self, agent_id):
        self.agent_id = agent_id
        self.agent_config = self.load_agent_config()

    def load_agent_config(self):
        """Loads the agent's .mdc configuration file."""
        mdc_path = os.path.join(
            os.path.expanduser("~/C-System/Memory-C*/.cursor/rules"),
            f"{self.agent_id}.mdc"
        )
        if not os.path.exists(mdc_path):
            print(f"Error: Agent configuration not found at {mdc_path}")
            sys.exit(1)

        with open(mdc_path, 'r') as f:
            content = f.read()
            # Extract the YAML part from the .mdc file
            parts = content.split('---')
            if len(parts) > 2:
                yaml_content = parts[1] # The YAML is in the second part
                return yaml.safe_load(yaml_content)
            else:
                # Fallback for .md files
                yaml_content = content.split('```yml')[1].split('```')[0]
                return yaml.safe_load(yaml_content)

    def run(self):
        """Starts the main command loop for the agent."""
        # Display the startup message
        if 'startup' in self.agent_config:
            for instruction in self.agent_config['startup']:
                print(instruction)

        while True:
            try:
                user_input = input("> ")
                if not user_input.startswith('*'):
                    continue

                command_parts = user_input[1:].split()
                command = command_parts[0]
                args = command_parts[1:]

                if command == 'exit':
                    break

                self.execute_command(command, args)

            except KeyboardInterrupt:
                break

    def execute_command(self, command, args):
        """Executes a BMAD command."""
        if command == 'help':
            self.display_help()
        elif command == 'task':
            if args:
                self.execute_task(args[0])
            else:
                print("Please specify a task to execute (e.g., *task create-doc)")
        else:
            print(f"Unknown command: {command}")

    def display_help(self):
        """Displays the help message for the current agent."""
        help_template = self.agent_config.get('help-display-template')
        if help_template:
            print(help_template)
        else:
            print("No help available for this agent.")

    def list_resources(self, resource_type):
        """Lists the available resources of a given type."""
        if resource_type in self.agent_config.get('dependencies', {}):
            print(f"Available {resource_type}:")
            for resource in self.agent_config['dependencies'][resource_type]:
                print(f"- {resource}")
        else:
            print(f"Unknown resource type: {resource_type}")

    def transform_agent(self, agent_id):
        """Transforms the interpreter into a different agent."""
        print(f"Transforming into agent: {agent_id}")
        self.agent_id = agent_id
        self.agent_config = self.load_agent_config()
        # Display the startup message for the new agent
        if 'startup' in self.agent_config:
            for instruction in self.agent_config['startup']:
                print(instruction)

    def list_agents(self):
        """Lists the available agents."""
        print("Available agents:")
        agents_path = os.path.expanduser("~/C-System/Memory-C*/.bmad-core/agents")
        for agent_file in os.listdir(agents_path):
            if agent_file.endswith(".md"):
                print(f"- {agent_file[:-3]}")

    def execute_task(self, task_name):
        """Executes a task by displaying its definition."""
        task_path = os.path.join(
            os.path.expanduser("~/C-System/Memory-C*/.bmad-core/tasks"),
            f"{task_name}.md"
        )
        if os.path.exists(task_path):
            with open(task_path, 'r') as f:
                print(f.read())
        else:
            print(f"Task not found: {task_name}")

    def get_memory_insight(self):
        """Gets a memory insight from the memory system."""
        print("Getting memory insight...")
        os.system("ai-memory-status")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        agent_id = sys.argv[1]
    else:
        agent_id = "bmad-orchestrator"

    interpreter = BmadInterpreter(agent_id)
    interpreter.run()

from agents.agent_manager import AgentManager

def main():
    manager = AgentManager()

    # Step 1: Create an agent if it doesn't exist
    agent_name = "geometry_bot"
    base_prompt = (
        "You are a helpful algebra tutor. Use the user's question and any relevant context to provide clear, concise answers."
        "\n\nContext:\n{context}\n\nQuestion:\n{input}"
    )
    llm_choice = "deepseek"

    # Only create once — skip if already created
    if agent_name not in manager.list_agents():
        manager.create_agent(agent_name, base_prompt, llm_choice)
        print(f"Agent '{agent_name}' created.")

    # Step 2: Load agent
    agent = manager.get_agent(agent_name)

    # Step 3: Ingest a test file (adjust path as needed)
    print("Ingesting document...")
    doc_path = r"C:\Users\quinc\OneDrive\Documents\Projects\langchantexts\algebra1.pdf"  # Make sure this file exists
    agent.vector_store.ingest_docs([doc_path])
    print("Document ingested.")

    # Step 4: Ask a question
    question = "What is the quadratic formula?"
    response = agent.run(question)
    print("\n--- Agent Response ---")
    print(response)

if __name__ == "__main__":
    main()

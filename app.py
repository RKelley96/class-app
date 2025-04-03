import streamlit as st
import time
from utils import get_persona_prompt, get_persona_response

st.set_page_config(page_title="Persona", layout="wide")

# Initialize session state variables
if "agent_dict" not in st.session_state:
    st.session_state.agent_dict = {}
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_persona_prompt" not in st.session_state:
    st.session_state.current_persona_prompt = ""
if "messages_1" not in st.session_state:
    st.session_state.messages_1 = []
if "messages_2" not in st.session_state:
    st.session_state.messages_2 = []
if "agent_name_1" not in st.session_state:
    st.session_state.agent_name_1 = None
if "agent_name_2" not in st.session_state:
    st.session_state.agent_name_2 = None
if "persona_prompt_1" not in st.session_state:
    st.session_state.persona_prompt_1 = ""
if "persona_prompt_2" not in st.session_state:
    st.session_state.persona_prompt_2 = ""

# Create a sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Agents", "Persona Chat", "Persona Debate"])

# Define the Home page
if page == "Home":
    st.title("Create a New Agent")
    
    agent_name = st.text_input("Agent Name")
    
    uploaded_file = st.file_uploader(
        "Drag and drop PDF, DOCX, TXT, or CSV files here",
        type=["pdf", "docx", "txt", "csv"]
    )
    
    if st.button("Create Agent") and agent_name and uploaded_file:
        # Make sure the uploads directory exists
        import os
        os.makedirs("uploads", exist_ok=True)
        
        # Save the uploaded file
        file_path = f"uploads/{uploaded_file.name}"
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Generate persona prompt
        persona_prompt = get_persona_prompt(agent_name, file_path)
        
        # Add to agent dictionary
        st.session_state.agent_dict[agent_name] = persona_prompt
        
        st.success(f"Agent {agent_name} created!")

# Define the Agents page
elif page == "Agents":
    st.title("Agent Library")
    
    if not st.session_state.agent_dict:
        st.info("No agents created yet. Go to Home to create an agent.")
    else:
        agent_names = list(st.session_state.agent_dict.keys())
        selected_agent = st.selectbox("Select an agent", agent_names)
        
        if selected_agent:
            st.subheader(f"{selected_agent}'s Persona")
            st.text_area(
                "Persona Prompt",
                st.session_state.agent_dict[selected_agent],
                height=400,
                key="persona_display"
            )

# Define the Persona Chat page
elif page == "Persona Chat":
    st.title("Chat with an Agent")
    
    if not st.session_state.agent_dict:
        st.info("No agents created yet. Go to Home to create an agent.")
    else:
        agent_names = list(st.session_state.agent_dict.keys())
        
        # Agent selection dropdown
        selected_agent = st.selectbox("Select an agent to chat with", agent_names)
        
        # Reset chat if agent changes
        if "last_chat_agent" not in st.session_state or st.session_state.last_chat_agent != selected_agent:
            st.session_state.messages = []
            st.session_state.current_persona_prompt = st.session_state.agent_dict[selected_agent]
            st.session_state.last_chat_agent = selected_agent
        
        # Display chat messages
        chat_container = st.container()
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.chat_message("user").write(message["content"])
                else:
                    st.chat_message("assistant").write(message["content"])
        
        # Chat input
        user_message = st.chat_input("Type your message here...")
        
        if user_message:
            # Add user message to chat
            st.session_state.messages.append({"role": "user", "content": user_message})
            
            # Display user message immediately
            st.chat_message("user").write(user_message)
            
            # Get agent response
            with st.spinner("Agent is thinking..."):
                persona_response = get_persona_response(
                    st.session_state.current_persona_prompt, 
                    st.session_state.messages
                )
            
            # Print for debugging
            print(f"Persona Response: {persona_response}")
            
            # Add agent response to chat
            st.session_state.messages.append({"role": "assistant", "content": persona_response})
            
            # Display agent response
            st.chat_message("assistant").write(persona_response)
            
            # Rerun to update the UI
            st.rerun()

# Define the Persona Debate page
elif page == "Persona Debate":
    st.title("Persona Debate")
    
    if len(st.session_state.agent_dict) < 2:
        st.info("You need at least two agents for a debate. Go to Home to create more agents.")
    else:
        agent_names = list(st.session_state.agent_dict.keys())
        
        # Agent selection
        col1, col2 = st.columns(2)
        with col1:
            agent_1 = st.selectbox("Agent 1", agent_names, key="agent1_select")
        with col2:
            # Filter out agent 1 from options for agent 2
            remaining_agents = [agent for agent in agent_names if agent != agent_1]
            agent_2 = st.selectbox("Agent 2", remaining_agents, key="agent2_select")
        
        # Check if agents changed
        if (st.session_state.agent_name_1 != agent_1 or 
            st.session_state.agent_name_2 != agent_2):
            
            # Reset conversation
            st.session_state.agent_name_1 = agent_1
            st.session_state.agent_name_2 = agent_2
            st.session_state.persona_prompt_1 = st.session_state.agent_dict[agent_1]
            st.session_state.persona_prompt_2 = st.session_state.agent_dict[agent_2]
            st.session_state.messages_1 = []
            st.session_state.messages_2 = []
            
            # Initialize with Agent 1's opening message
            agent_1_message = "hi"
            st.session_state.messages_1.append({"role": "assistant", "content": agent_1_message})
            st.session_state.messages_2.append({"role": "user", "content": agent_1_message})
        
        # Display current conversation
        st.subheader("Conversation")
        conversation_container = st.container()
        
        with conversation_container:
            # Display all messages
            for message in st.session_state.messages_1:
                if message["role"] == "assistant":
                    with st.chat_message(name=agent_1):
                        st.markdown(f"**{agent_1}**")
                        st.write(message['content'])
                else:
                    with st.chat_message(name="user"):
                        st.markdown(f"**{agent_2}**")
                        st.write(message['content'])


        
        # Button to continue the conversation
        if st.button("Make agents converse"):
            # Agent 2 responds
            with st.spinner(f"{agent_2} is thinking..."):
                agent_2_message = get_persona_response(
                    st.session_state.persona_prompt_2,
                    st.session_state.messages_2
                )
                
                # Add messages to both conversation histories
                st.session_state.messages_1.append({"role": "user", "content": agent_2_message})
                st.session_state.messages_2.append({"role": "assistant", "content": agent_2_message})
            
            time.sleep(2)  # Pause between responses
            # Agent 1 responds
            with st.spinner(f"{agent_1} is thinking..."):
                agent_1_message = get_persona_response(
                    st.session_state.persona_prompt_1,
                    st.session_state.messages_1
                )
                
                # Add messages to both conversation histories
                st.session_state.messages_1.append({"role": "assistant", "content": agent_1_message})
                st.session_state.messages_2.append({"role": "user", "content": agent_1_message})
            
            time.sleep(2)  # Pause between rounds
            
            # Rerun to update the UI
            st.rerun()
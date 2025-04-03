import streamlit as st
import time
from utils import get_persona_prompt, get_persona_response
import os

st.set_page_config(page_title="Persona", layout="wide")

# Initialize session state variables
if "agent_dict" not in st.session_state:
    st.session_state.agent_dict = {}

# Sidebar navigation
st.sidebar.title("Persona App")
page = st.sidebar.radio("Navigate", ["Home", "Agents", "Persona Chat", "Persona Debate"])

if page == "Home":
    st.title("Create New Agent")
    
    # Input for agent name
    agent_name = st.text_input("Agent Name")
    
    # File uploader
    uploaded_file = st.file_uploader("Upload Agent Knowledge (PDF, DOCX, TXT, CSV)", 
                                    type=["pdf", "docx", "txt", "csv"])
    
    # Create agent button
    if st.button("Create Agent"):
        if agent_name and uploaded_file:
            # Save the file temporarily
            file_path = os.path.join("temp", uploaded_file.name)
            os.makedirs("temp", exist_ok=True)
            
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Get persona prompt
            persona_prompt = get_persona_prompt(agent_name, file_path)
            
            # Add to agent dictionary
            st.session_state.agent_dict[agent_name] = persona_prompt
            
            st.success(f"Agent {agent_name} created!")
        else:
            st.error("Please provide both an agent name and upload a file.")

elif page == "Agents":
    st.title("View Agents")
    
    if not st.session_state.agent_dict:
        st.info("No agents created yet. Go to the Home page to create an agent.")
    else:
        # Dropdown to select agent
        agent_names = list(st.session_state.agent_dict.keys())
        selected_agent = st.selectbox("Select an agent", agent_names)
        
        # Display persona prompt
        if selected_agent:
            st.subheader(f"{selected_agent}'s Persona")
            st.text_area("Persona Prompt", st.session_state.agent_dict[selected_agent], 
                        height=400, key="agent_prompt_view", disabled=True)

elif page == "Persona Chat":
    st.title("Chat with Persona")
    
    if not st.session_state.agent_dict:
        st.info("No agents created yet. Go to the Home page to create an agent.")
    else:
        # Initialize chat session state variables
        if "messages" not in st.session_state:
            st.session_state.messages = []
            
        if "current_persona_prompt" not in st.session_state:
            st.session_state.current_persona_prompt = ""
        
        # Dropdown to select agent
        agent_names = list(st.session_state.agent_dict.keys())
        selected_agent = st.selectbox("Select an agent", agent_names, 
                                    key="chat_agent_select")
        
        # Reset messages if agent changes
        if selected_agent:
            if "previous_selected_agent" not in st.session_state:
                st.session_state.previous_selected_agent = selected_agent
                st.session_state.current_persona_prompt = st.session_state.agent_dict[selected_agent]
            
            elif st.session_state.previous_selected_agent != selected_agent:
                st.session_state.messages = []
                st.session_state.current_persona_prompt = st.session_state.agent_dict[selected_agent]
                st.session_state.previous_selected_agent = selected_agent
            
            # Display chat messages
            chat_container = st.container()
            with chat_container:
                for message in st.session_state.messages:
                    if message["role"] == "user":
                        st.markdown(f"**You:** {message['content']}")
                    else:
                        st.markdown(f"**{selected_agent}:** {message['content']}")
            
            # Chat input
            user_message = st.chat_input("Type your message here...")
            if user_message:
                # Add user message to chat
                st.session_state.messages.append({"role": "user", "content": user_message})
                
                # Get persona response
                with st.spinner(f"{selected_agent} is thinking..."):
                    persona_response = get_persona_response(
                        st.session_state.current_persona_prompt, 
                        st.session_state.messages
                    )
                
                # Add persona response to chat
                st.session_state.messages.append({"role": "assistant", "content": persona_response})
                
                # Debug output
                print(f"Persona response: {persona_response}")
                
                # Rerun to update the chat display
                st.rerun()

elif page == "Persona Debate":
    st.title("Persona Debate")
    
    if len(st.session_state.agent_dict) < 2:
        st.info("You need at least two agents for a debate. Go to the Home page to create agents.")
    else:
        # Initialize debate session state variables
        if "messages_1" not in st.session_state:
            st.session_state.messages_1 = []
        
        if "messages_2" not in st.session_state:
            st.session_state.messages_2 = []
            
        if "persona_prompt_1" not in st.session_state:
            st.session_state.persona_prompt_1 = ""
            
        if "persona_prompt_2" not in st.session_state:
            st.session_state.persona_prompt_2 = ""
            
        if "agent_name_1" not in st.session_state:
            st.session_state.agent_name_1 = ""
            
        if "agent_name_2" not in st.session_state:
            st.session_state.agent_name_2 = ""
            
        if "debate_started" not in st.session_state:
            st.session_state.debate_started = False
        
        # Agent selection
        col1, col2 = st.columns(2)
        
        with col1:
            agent_names = list(st.session_state.agent_dict.keys())
            agent_name_1 = st.selectbox("Agent 1", agent_names, key="debate_agent_1")
            
            if agent_name_1:
                if st.session_state.agent_name_1 != agent_name_1:
                    st.session_state.agent_name_1 = agent_name_1
                    st.session_state.persona_prompt_1 = st.session_state.agent_dict[agent_name_1]
                    st.session_state.messages_1 = []
                    st.session_state.debate_started = False
        
        with col2:
            agent_names.remove(agent_name_1) if agent_name_1 in agent_names else None
            agent_name_2 = st.selectbox("Agent 2", agent_names, key="debate_agent_2")
            
            if agent_name_2:
                if st.session_state.agent_name_2 != agent_name_2:
                    st.session_state.agent_name_2 = agent_name_2
                    st.session_state.persona_prompt_2 = st.session_state.agent_dict[agent_name_2]
                    st.session_state.messages_2 = []
                    st.session_state.debate_started = False
        
        # Start debate button
        if st.button("Make agents converse"):
            if not st.session_state.debate_started:
                # Initialize with agent 1's first message
                agent_1_message = "hi"
                st.session_state.messages_1.append({"role": "assistant", "content": agent_1_message})
                st.session_state.messages_2.append({"role": "user", "content": agent_1_message})
                st.session_state.debate_started = True
            
            # Agent 2 response
            with st.spinner(f"{st.session_state.agent_name_2} is thinking..."):
                agent_2_message = get_persona_response(
                    st.session_state.persona_prompt_2,
                    st.session_state.messages_2
                )
                st.session_state.messages_1.append({"role": "user", "content": agent_2_message})
                st.session_state.messages_2.append({"role": "assistant", "content": agent_2_message})
                time.sleep(2)
            
            # Agent 1 response
            with st.spinner(f"{st.session_state.agent_name_1} is thinking..."):
                agent_1_message = get_persona_response(
                    st.session_state.persona_prompt_1,
                    st.session_state.messages_1
                )
                st.session_state.messages_1.append({"role": "assistant", "content": agent_1_message})
                st.session_state.messages_2.append({"role": "user", "content": agent_1_message})
                time.sleep(2)
            
            # Rerun to update the debate display
            st.rerun()
        
        # Display the conversation
        st.subheader("Debate History")
        
        if st.session_state.debate_started:
            debate_container = st.container()
            with debate_container:
                # Combine messages from both agents
                debate_messages = []
                
                for i in range(len(st.session_state.messages_1)):
                    if i % 2 == 0:  # Even indices are Agent 1 messages (including the initial "hi")
                        if i < len(st.session_state.messages_1):
                            message = st.session_state.messages_1[i]
                            if message["role"] == "assistant":
                                debate_messages.append({
                                    "agent": st.session_state.agent_name_1,
                                    "content": message["content"]
                                })
                    else:  # Odd indices are Agent 2 messages
                        if i < len(st.session_state.messages_2):
                            message = st.session_state.messages_2[i]
                            if message["role"] == "assistant":
                                debate_messages.append({
                                    "agent": st.session_state.agent_name_2,
                                    "content": message["content"]
                                })
                
                # Display messages
                for message in debate_messages:
                    st.markdown(f"**{message['agent']}:** {message['content']}")

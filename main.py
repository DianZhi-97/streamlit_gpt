import openai
import json
import streamlit as st
import streamlit_authenticator as stauth
from datetime import date
from langchain.callbacks import StreamlitCallbackHandler
from langchain.chat_models import ChatOpenAI
from langchain.schema import ChatMessage

# config the page title and icon
st.set_page_config(page_title="ChatGPT", page_icon="", layout="wide")

# format page styles
style = """
<style>
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}
/* div[data-testid="column"] {text-align: center} */
/* div[data-testid="stVerticalBlock"] > * {text-align: center} */
</style>
"""
st.markdown(style, unsafe_allow_html=True)

# load registered user info
credentials = json.loads(st.secrets["authetications"]["credentials"])

# config the auhenticator
authenticator = stauth.Authenticate(
    credentials,
    st.secrets["cookie"]["name"],
    st.secrets["cookie"]["key"],
    st.secrets["cookie"]["expiry_days"]
)

# start the authenticator
name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    # st.error("Username/password is incorrect")
    st.error("用户名/密码不正确")
elif authentication_status == None:
    # st.warning("Please enter your username and password")
    st.warning("请输入您的用户名和密码")
else:
    # get OpenAI API key
    openai.api_key = st.secrets["openai_apikey"]

    def reset_conversation():
        st.session_state.messages = []

    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # sidebar
    with st.sidebar:
        col_left, col_right = st.columns(2)
        with col_left:
            # st.subheader(name + ", Welcome:tada:")
            st.subheader(name + "，欢迎 :tada:")
        with col_right:
            # authenticator.logout("Logout")
            authenticator.logout("退出登录")
        # st.selectbox("Select large language model", ("gpt-4", "gpt-3.5-turbo"), key="model", on_change=reset_conversation)
        st.selectbox("选择您想使用的大语言模型", ("gpt-4", "gpt-3.5-turbo"), key="model", on_change=reset_conversation)
        # temperature = st.slider("Temperature", min_value=0.0, max_value=2.0, value=0.0, step=0.1, key="temperature")
        temperature = st.slider("温度", min_value=0.0, max_value=2.0, value=0.0, step=0.1, key="temperature")
        # st.write("Tips: Higher temperatures introduce more randomness, resulting in creative yet potentially less coherent output.")
        st.write("提示：较高的温度会引入更多的随机性")

        # custom_instructions = st.text_area("Custom Instructions", value=f"You are {st.session_state.model.replace("-", " ").upper()}, a large language model trained by OpenAI.")
        custom_instructions = st.text_area("自定义指令", value=f"你是 {st.session_state.model.replace('-', ' ').upper()}， 一个由OpenAI创造的大语言模型。")

    st.title(f"💬 OpenAI {st.session_state.model.replace('-', ' ').upper()}") 
    
    for msg in st.session_state.messages:
        st.chat_message(msg.role).write(msg.content)

    prompt = st.chat_input(disabled=False, key="chat_input", placeholder="请输入你的对话")
    # st.button("Start New Chat", on_click=reset_conversation)
    output_container = st.empty()
    st.divider()
    
    st.button("重置对话", on_click=reset_conversation)
    if prompt:
        output_container = output_container.container()
        st.chat_input(disabled=True, key="disabled_chat_input", placeholder="生成回复中……")
        st.session_state.messages.append(ChatMessage(role="user", content=prompt))
        output_container.chat_message("user").write(prompt)

    if len(st.session_state.messages) > 0 and st.session_state.messages[-1].role != "assistant":
        answer_container = output_container.chat_message("assistant")
        st_callback = StreamlitCallbackHandler(answer_container)
        llm = ChatOpenAI(openai_api_key=st.secrets["openai_apikey"], streaming=True, callbacks=[st_callback])
        response = llm([ChatMessage(role="system", content=custom_instructions)] + st.session_state.messages)
        st.session_state.messages.append(ChatMessage(role="assistant", content=response.content))
        st.rerun()

# add document reader & search functionality